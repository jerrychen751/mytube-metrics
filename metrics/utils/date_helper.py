from datetime import datetime
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
        raise ValueError("No date string provided.")
    
    try:
        publish_date = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
        return publish_date
    except ValueError:
        return None