from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from datetime import datetime, timedelta
import pytz

def get_calendar_service(creds: Credentials):
    return build("calendar", "v3", credentials=creds)

def get_todays_events(creds: Credentials):
    """Get all events for today"""
    service = get_calendar_service(creds)
    now = datetime.utcnow()
    start = now.replace(hour=0, minute=0, second=0).isoformat() + "Z"
    end   = now.replace(hour=23, minute=59, second=59).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=start,
        timeMax=end,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return "📅 No events scheduled for today!"

    output = f"📅 Today's events ({len(events)}):\n\n"
    for e in events:
        start_time = e["start"].get("dateTime", e["start"].get("date", ""))
        if "T" in start_time:
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            time_str = dt.strftime("%I:%M %p")
        else:
            time_str = "All day"
        output += f"• {e.get('summary', 'Untitled')} at {time_str}\n"
    return output

def get_upcoming_events(creds: Credentials, days: int = 7):
    """Get upcoming events for the next N days"""
    service = get_calendar_service(creds)
    now = datetime.utcnow().isoformat() + "Z"
    end = (datetime.utcnow() + timedelta(days=days)).isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        timeMax=end,
        maxResults=10,
        singleEvents=True,
        orderBy="startTime"
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return f"📅 No upcoming events in the next {days} days."

    output = f"📅 Upcoming events (next {days} days):\n\n"
    for e in events:
        start_time = e["start"].get("dateTime", e["start"].get("date", ""))
        if "T" in start_time:
            dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            time_str = dt.strftime("%b %d, %I:%M %p")
        else:
            time_str = start_time
        output += f"• {e.get('summary', 'Untitled')} — {time_str}\n"
    return output

def create_event(creds: Credentials, title: str, date_str: str, time_str: str, duration_hours: int = 1, description: str = ""):
    """Create a new calendar event"""
    service = get_calendar_service(creds)

    # Parse date and time
    dt_str = f"{date_str} {time_str}"
    try:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M")
    except ValueError:
        dt = datetime.strptime(dt_str, "%Y-%m-%d %I:%M %p")

    start = dt.isoformat()
    end   = (dt + timedelta(hours=duration_hours)).isoformat()

    event = {
        "summary":     title,
        "description": description,
        "start":       {"dateTime": start, "timeZone": "Asia/Kolkata"},
        "end":         {"dateTime": end,   "timeZone": "Asia/Kolkata"},
    }

    created = service.events().insert(calendarId="primary", body=event).execute()
    return f"✅ Event '{title}' created for {date_str} at {time_str}!\nLink: {created.get('htmlLink', '')}"

def delete_event(creds: Credentials, event_title: str):
    """Delete an event by title (deletes first match)"""
    service = get_calendar_service(creds)
    now = datetime.utcnow().isoformat() + "Z"

    events_result = service.events().list(
        calendarId="primary",
        timeMin=now,
        maxResults=20,
        singleEvents=True,
        orderBy="startTime",
        q=event_title
    ).execute()

    events = events_result.get("items", [])
    if not events:
        return f"❌ No upcoming event found with title '{event_title}'"

    event = events[0]
    service.events().delete(calendarId="primary", eventId=event["id"]).execute()
    return f"✅ Event '{event.get('summary')}' deleted successfully."
