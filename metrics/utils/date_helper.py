from datetime import datetime
from typing import Optional

def isostr_to_datetime(published_at_str: str | None) -> datetime | None:
    """
    Convert publishedAt datetime ISO 8601 formatted string to datetime object.

    Args:
        published_at_str (Optional[str]): ISO 8601 format.

    Returns:
        A datetime object. None if there's an error.

    Raises:
        ValueError if no valid date string is provided.
    """
    if not published_at_str:
        return None
    
    try:
        publish_date = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        return publish_date
    except ValueError:
        return None

def is_valid_datetime_range(start_time_str: Optional[str], end_time_str: Optional[str]) -> bool:
    """
    Checks if a given datetime range is valid (start_time is before end_time).

    Args:
        start_time_str (Optional[str]): The start datetime string in ISO 8601 format.
        end_time_str (Optional[str]): The end datetime string in ISO 8601 format.

    Returns:
        bool: True if the range is valid (start_time is before end_time), False otherwise.
              Returns True if both are None, or if only one is provided.
    """
    if not start_time_str and not end_time_str:
        return True
    
    if not start_time_str or not end_time_str:
        return True # If only one is provided, it's considered a valid "range" for filtering

    start_time = isostr_to_datetime(start_time_str)
    end_time = isostr_to_datetime(end_time_str)

    if start_time is None or end_time is None:
        return False # Invalid datetime string provided

    return start_time < end_time