import os
import requests
import icalendar
from datetime import datetime, date, time, timezone, timedelta
from dateutil.rrule import rrulestr
from dateutil import tz
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from dotenv import load_dotenv
from widgets.base_widget import WidgetCard
from widgets.calendar_common import to_naive_utc, to_local_display, get_parsed_event, connect_to_calendar
from widgets.no_touch_label import NonTouchLabel

# Load .env from project root
project_root = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=project_root)

try:
    import caldav
    from caldav.elements import dav
except ImportError:
    caldav = None

class UpcomingEventsWidget(WidgetCard):
    def __init__(self, **kwargs):
        # Retrieve credentials and (optionally) the target calendar name from environment.
        self.username = os.getenv("CALDAV_USERNAME")
        self.app_password = os.getenv("CALDAV_APP_PASSWORD")
        self.calendar_url = kwargs.pop('calendar_url', 'https://caldav.icloud.com/')
        self.target_calendar_name = os.getenv("CALENDAR_NAME")
        
        super().__init__(**kwargs)
        
        self.title = "Upcoming Events"
        self.calendars = []
        self.events = []
        
        # Create a container for event details inside a ScrollView.
        self.event_list = BoxLayout(orientation='vertical', spacing=5, size_hint_y=None)
        self.event_list.bind(minimum_height=self.event_list.setter('height'))
        self.scroll = ScrollView(size_hint=(1, 1))
        self.scroll.add_widget(self.event_list)
        self.add_widget(self.scroll)
        
        # Connect to calendar and render events.
        self.calendars, default_cal = connect_to_calendar(self.calendar_url, self.username, self.app_password, self.target_calendar_name)
        if default_cal:
            self.events = default_cal.events()
            print(f"Fetched {len(self.events)} event(s) from the selected calendar.")
        self.render_events()

    def render_events(self):
        # Clear previous content.
        self.event_list.clear_widgets()
        
        # Collect individual event occurrences as dictionaries.
        upcoming_events = []
        now = to_naive_utc(datetime.now(timezone.utc))
        # Define a window for recurrence expansion in days
        window_end = now + timedelta(days=180)
        
        for event in self.events:
            try:
                parsed = get_parsed_event(event)
                dtstart_prop = parsed.get('dtstart')
                if not dtstart_prop:
                    raise AttributeError("dtstart property not found")
                dtstart = dtstart_prop.dt
                # Convert date-only values to datetime.
                if isinstance(dtstart, date) and not isinstance(dtstart, datetime):
                    dtstart = datetime.combine(dtstart, time.min)
                # Convert dtstart to a naive UTC datetime.
                dtstart_naive = to_naive_utc(dtstart)
                
                # Determine event duration.
                if parsed.get('dtend'):
                    dtend = parsed.get('dtend').dt
                    if isinstance(dtend, date) and not isinstance(dtend, datetime):
                        dtend = datetime.combine(dtend, time.min)
                    duration = dtend - dtstart
                else:
                    duration = timedelta(hours=1)
                
                # Check if the event is recurring.
                rrule_prop = parsed.get('rrule')
                if rrule_prop:
                    # Expand the recurrence rule using the naive dtstart.
                    rule_str = rrule_prop.to_ical().decode('utf-8')
                    rule = rrulestr(rule_str, dtstart=dtstart_naive)
                    occurrences = rule.between(now, window_end, inc=True)
                    # Also include the original dtstart if it falls within the window.
                    if dtstart_naive >= now and dtstart_naive <= window_end and dtstart_naive not in occurrences:
                        occurrences.insert(0, dtstart_naive)
                    for occ in occurrences:
                        occ_naive = occ  # Already naive UTC.
                        if occ_naive >= now:
                            occ_event = {
                                'dtstart': occ_naive,
                                'dtend': occ_naive + duration,
                                'summary': parsed.get('summary', 'Unnamed'),
                                'location': parsed.get('location', 'No Location')
                            }
                            upcoming_events.append(occ_event)
                else:
                    # Non-recurring event.
                    if dtstart_naive >= now:
                        event_dict = {
                            'dtstart': dtstart_naive,
                            'dtend': dtstart_naive + duration,
                            'summary': parsed.get('summary', 'Unnamed'),
                            'location': parsed.get('location', 'No Location')
                        }
                        upcoming_events.append(event_dict)
            except Exception as ex:
                print(f"Failed to process an event: {ex}")
                continue
        
        # Sort upcoming events by start time.
        try:
            upcoming_events.sort(key=lambda ev: ev['dtstart'])
        except Exception as ex:
            print(f"Failed to sort events: {ex}")
        
        # Limit to the next 10 events.
        upcoming_events = upcoming_events[:10]
        print(f"Upcoming events: {len(upcoming_events)}")
        
        if not upcoming_events:
            no_event_label = Label(text="No upcoming events.", size_hint_y=None, height=30)
            self.event_list.add_widget(no_event_label)
            return
        
        # Render each occurrence, converting times to the user's local time zone.
        for ev in upcoming_events:
            try:
                local_start = to_local_display(ev['dtstart'])
                local_end = to_local_display(ev['dtend']) if ev['dtend'] else None
                
                date_str = local_start.strftime('%B %d, %Y')
                start_time = local_start.strftime('%I:%M %p')
                end_time = local_end.strftime('%I:%M %p') if local_end else "N/A"
                
                title = ev['summary']
                if hasattr(title, 'to_ical'):
                    title = title.to_ical().decode('utf-8')
                else:
                    title = str(title)
                
                details = (
                    f"[b]{date_str}[/b]\n"
                    f"{start_time} - {end_time}\n"
                    f"{title}"
                )
            except Exception as ex:
                details = "Event details unavailable"
                print(f"Failed to render event details: {ex}")
            label = NonTouchLabel(
                text=details,
                size_hint_y=None,
                markup=True,
                halign='left',
                text_size=(self.width - 20, None)
            )
            def update_height(instance, value):
                instance.height = instance.texture_size[1] + 20  # add padding if desired
            label.bind(texture_size=update_height)
            
            # Draw a border around the label.
            from kivy.graphics import Color, Line
            with label.canvas.before:
                Color(0, 0, 0, .25)
                label.border_line = Line(rectangle=(label.x, label.y, label.width, label.height), width=1)
            def update_label_border(instance, value):
                instance.border_line.rectangle = (instance.x, instance.y, instance.width, instance.height)
            label.bind(pos=update_label_border, size=update_label_border)
            self.event_list.add_widget(label)
