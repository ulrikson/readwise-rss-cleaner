from datetime import timezone, datetime, timedelta
from dateutil import parser as date_parser
from tzlocal import get_localzone


DEFAULT_HOURS_AGO = 2


def parse_datetime_to_utc(date_str: str) -> str:
    """Parse a datetime string and convert to UTC ISO format."""
    local_tz = get_localzone()
    dt = date_parser.parse(date_str)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=local_tz)

    utc_dt = dt.astimezone(timezone.utc)
    return utc_dt.isoformat()


def get_default_updated_after() -> str:
    """Get the default ISO 8601 d  ate."""
    past = datetime.now().astimezone(timezone.utc) - timedelta(
        hours=DEFAULT_HOURS_AGO
    )  # running every 2 hours
    return past.replace(minute=0, second=0, microsecond=0).isoformat()
