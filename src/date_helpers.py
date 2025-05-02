from datetime import timezone, datetime, timedelta
from dateutil import parser as date_parser
from tzlocal import get_localzone


def parse_datetime_to_utc(date_str: str) -> str:
    """Parse a datetime string and convert to UTC ISO format."""
    local_tz = get_localzone()
    dt = date_parser.parse(date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)

    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.isoformat()


def get_start_of_yesterday() -> str:
    """Get the ISO 8601 date for yesterday at 00:00."""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
