import os
import calendar
import requests
import icalendar
from datetime import datetime, date, time, timezone, timedelta
from dateutil.rrule import rrulestr
from dateutil import tz
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from dotenv import load_dotenv
from widgets.base_widget import WidgetCard
from widgets.calendar_common import to_naive_utc, to_local_display, get_parsed_event, connect_to_calendar


# Load the .env file from the project root
project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=project_root)

try:
    import caldav
    from caldav.elements import dav
except ImportError:
    caldav = None

class CalendarWidget(WidgetCard):
    def __init__(self, **kwargs):
        self.username = os.getenv("CALDAV_USERNAME")
        self.app_password = os.getenv("CALDAV_APP_PASSWORD")
        self.calendar_url = kwargs.pop('calendar_url', 'https://caldav.icloud.com/')
        self.target_calendar_name = os.getenv("CALENDAR_NAME")
        
        super().__init__(**kwargs)
        
        self.title = "Calendar"
        self.calendars = []
        self.events = []  # Raw events from the calendar
        
        now = datetime.now()
        self.current_year = now.year
        self.current_month = now.month

        # Create a container for the monthly calendar view.
        self.calendar_view = BoxLayout(orientation='vertical', spacing=5)
        # Instead of a ScrollView, add calendar_view directly.
        # Enforce a minimum height so that it doesn't squish too small.
        min_calendar_height = 300
        self.calendar_view.height = max(self.height, min_calendar_height)
        self.add_widget(self.calendar_view)

        # Re-render when size changes.
        self.bind(size=self.on_size)

        self.calendars, default_cal = connect_to_calendar(self.calendar_url, self.username, self.app_password, self.target_calendar_name)
        if default_cal:
            self.events = default_cal.events()
            print(f"Fetched {len(self.events)} event(s) from the selected calendar.")
        self.render_month(self.current_month, self.current_year)

    def on_size(self, *args):
        # Re-render the month when the widget's size changes.
        if not hasattr(self, 'current_month') or not hasattr(self, 'current_year'):
            return
        self.render_month(self.current_month, self.current_year)

    def compute_occurrences_for_month(self, month, year):
        """
        Compute occurrences for all events in the current month.
        Returns a dictionary mapping local date objects to lists of occurrence dicts.
        Each occurrence dict has keys:
          'dtstart' (naive UTC datetime),
          'dtend' (naive UTC datetime),
          'summary',
          'location'
        """
        occurrences_by_date = {}
        from calendar import monthrange
        last_day = monthrange(year, month)[1]
        # Compute local month boundaries.
        month_start_local = datetime(year, month, 1, 0, 0, 0)
        month_end_local = datetime(year, month, last_day, 23, 59, 59)
        # Convert local boundaries to naive UTC for recurrence expansion.
        month_start_utc = to_naive_utc(month_start_local)
        month_end_utc = to_naive_utc(month_end_local)

        for event in self.events:
            try:
                parsed = get_parsed_event(event)
                dtstart_prop = parsed.get('dtstart')
                if not dtstart_prop:
                    continue
                dtstart = dtstart_prop.dt
                if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
                    dtstart = datetime.combine(dtstart, time.min)
                dtstart_utc = to_naive_utc(dtstart)
                # Determine event duration.
                if parsed.get('dtend'):
                    dtend = parsed.get('dtend').dt
                    if isinstance(dtend, date) and not isinstance(dtend, datetime):
                        dtend = datetime.combine(dtend, time.min)
                    duration = dtend - dtstart
                else:
                    duration = timedelta(hours=1)
                rrule_prop = parsed.get('rrule')
                if rrule_prop:
                    # Expand recurring events over the month window.
                    rule_str = rrule_prop.to_ical().decode('utf-8')
                    rule = rrulestr(rule_str, dtstart=dtstart_utc)
                    occs = rule.between(month_start_utc, month_end_utc, inc=True)
                    # Also include the original dtstart if it falls within the window.
                    if dtstart_utc >= month_start_utc and dtstart_utc <= month_end_utc and dtstart_utc not in occs:
                        occs.insert(0, dtstart_utc)
                    for occ in occs:
                        # Convert occurrence to local time to check if it falls in the target month.
                        occ_local = to_local_display(occ)
                        if occ_local.year == year and occ_local.month == month:
                            occ_date = occ_local.date()
                            occ_event = {
                                'dtstart': occ,
                                'dtend': occ + duration,
                                'summary': parsed.get('summary', 'Unnamed'),
                                'location': parsed.get('location', 'No Location')
                            }
                            occurrences_by_date.setdefault(occ_date, []).append(occ_event)
                else:
                    # Non-recurring event.
                    dtstart_local = to_local_display(dtstart_utc)
                    if dtstart_local.year == year and dtstart_local.month == month:
                        occ_date = dtstart_local.date()
                        event_dict = {
                            'dtstart': dtstart_utc,
                            'dtend': dtstart_utc + duration,
                            'summary': parsed.get('summary', 'Unnamed'),
                            'location': parsed.get('location', 'No Location')
                        }
                        occurrences_by_date.setdefault(occ_date, []).append(event_dict)
            except Exception as e:
                print(f"Failed to process event for recurrence expansion: {e}")
                continue
        return occurrences_by_date

    def render_month(self, month, year):
        self.calendar_view.clear_widgets()
        # Compute occurrences for the month.
        occ_by_date = self.compute_occurrences_for_month(month, year)
        
        # Calculate dynamic heights.
        header_height = max(30, self.height * 0.1)
        cal = calendar.Calendar(firstweekday=0)
        month_days = cal.monthdatescalendar(year, month)
        num_weeks = len(month_days)
        total_spacing = self.calendar_view.spacing * (num_weeks + 1)
        available_height = max(self.height - header_height - total_spacing, 0)
        week_height = max(30, available_height / num_weeks)

        # Header row for day abbreviations.
        header_layout = GridLayout(cols=7, spacing=5, size_hint_y=None, height=header_height)
        for day in calendar.day_abbr:
            header = Label(text=day, bold=True)
            header_layout.add_widget(header)
        self.calendar_view.add_widget(header_layout)

        # Weekly rows.
        for week in month_days:
            week_layout = GridLayout(cols=7, spacing=5, size_hint_y=None, height=week_height)
            for day in week:
                day_box = BoxLayout(orientation='vertical', spacing=2)
                # Add a border around the day_box.
                with day_box.canvas.before:
                    from kivy.graphics import Color, Line
                    Color(0, 0, 0, 1) # Black border
                    day_box.border = Line(rectangle=(day_box.x, day_box.y, day_box.width, day_box.height), width=1)
                def update_rect(instance, value):
                    instance.border.rectangle = (instance.x, instance.y, instance.width, instance.height)
                day_box.bind(pos=update_rect, size=update_rect)

                # Create a container for the day number with fixed height.
                date_container = BoxLayout(size_hint_y=None, height=header_height * 0.5)
                day_number = Label(text=str(day.day), halign='center', valign='middle')
                # Force the label to render its text centered.
                day_number.bind(size=day_number.setter('text_size'))
                if day.month != month:
                    day_number.opacity = 0.5
                date_container.add_widget(day_number)
                day_box.add_widget(date_container)

                # Create an event container that takes the remaining space.
                event_container = BoxLayout(orientation='vertical', size_hint_y=1)
                # Add event labels for this day.
                day_events = occ_by_date.get(day, [])
                for ev in day_events:
                    try:
                        local_start = to_local_display(ev['dtstart'])
                        event_summary = ev['summary']
                        label_text = f"{event_summary}"
                    except Exception as ex:
                        label_text = "Unnamed"
                    event_label = Label(
                        markup=True,
                        text=label_text,
                        font_size=10,
                        size_hint=(None, None),
                        width=self.width / 7 - 10,  # fixed width per day cell
                        height=15,
                        shorten=True,
                        shorten_from='right',
                        color=(1, 0, 0, 1),
                        text_size=(self.width / 7 - 10, 15),
                        halign='left',
                        valign='middle'
                    )
                    event_container.add_widget(event_label)
                day_box.add_widget(event_container)
                week_layout.add_widget(day_box)
            self.calendar_view.add_widget(week_layout)
