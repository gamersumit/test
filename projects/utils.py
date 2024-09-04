from datetime import datetime, timedelta, timezone

def convert_timestamp_iso8601(timestamp, offset_minutes):
    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
    offset = timedelta(minutes=offset_minutes)
    dt_with_offset = dt - offset
    date = dt_with_offset.strftime("%b %d, %Y")
    time = dt_with_offset.strftime("%I:%M %p")    
    return date, time

