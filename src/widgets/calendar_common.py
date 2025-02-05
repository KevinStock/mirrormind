# File: src/widgets/calendar_common.py
import os
import icalendar
import requests
from datetime import datetime, date, time, timezone
from dateutil.rrule import rrulestr
from dateutil import tz

try:
    from caldav.elements import dav
except ImportError:
    dav = None

def to_naive_utc(dt):
    """
    Convert a datetime to a naive UTC datetime.
    If dt is timezone-aware, convert to UTC and drop tzinfo.
    Otherwise, assume dt is already UTC.
    """
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def to_local_display(dt):
    """
    Convert a naive UTC datetime to the local time zone.
    If dt is naive, assume it's UTC.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(tz.tzlocal())

def get_parsed_event(event):
    """
    Return a parsed VEVENT component from an event.
    First try event.data, then event.instance if needed.
    """
    data = getattr(event, 'data', None)
    if data:
        try:
            cal = icalendar.Calendar.from_ical(data)
            for component in cal.walk():
                if component.name == "VEVENT":
                    return component
            raise ValueError("No VEVENT component found in event.data")
        except Exception as e:
            print(f"Error parsing event.data: {e}")
    
    instance = getattr(event, 'instance', None)
    if instance is None:
        raise ValueError("Event does not have data or instance information.")
    
    if isinstance(instance, str):
        response = requests.get(instance)
        response.raise_for_status()
        cal = icalendar.Calendar.from_ical(response.content)
        for component in cal.walk():
            if component.name == "VEVENT":
                return component
        raise ValueError("No VEVENT component found in ICS from instance URL")
    elif hasattr(instance, 'get'):
        return instance
    else:
        return instance

def connect_to_calendar(calendar_url, username, app_password, target_calendar_name=None):
    """
    Connect to CalDAV using the provided credentials.
    Returns a tuple (calendars, selected_calendar) where:
      - calendars is the list of calendars available.
      - selected_calendar is the matching calendar (or the default first one).
    """
    from caldav import DAVClient

    client = DAVClient(url=calendar_url, username=username, password=app_password)
    principal = client.principal()
    calendars = principal.calendars()
    print(f"Connected to CalDAV. Found {len(calendars)} calendar(s).")
    
    if not calendars:
        print("No calendars were found for this account.")
        return calendars, None

    default_cal = calendars[0]
    if target_calendar_name:
        found = False
        for cal in calendars:
            try:
                props = cal.get_properties([dav.DisplayName()])
                display_name = props.get('{DAV:}displayname')
                if display_name and display_name.strip() == target_calendar_name.strip():
                    default_cal = cal
                    found = True
                    break
            except Exception as e:
                print(f"Failed to get calendar display name: {e}")
        if not found:
            print(f"Calendar with name '{target_calendar_name}' not found. Using default calendar.")
        else:
            print(f"Using calendar named '{target_calendar_name}'.")
    else:
        print("No CALENDAR_NAME provided. Using default calendar.")
    
    return calendars, default_cal