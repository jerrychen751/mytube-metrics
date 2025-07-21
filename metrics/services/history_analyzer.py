# Standard Library Imports
import json
import zipfile
from collections import Counter
from datetime import datetime
from typing import Any, Dict, List

# Third-Party Imports
from django.http import HttpRequest

# Local App Imports
from .visualizer import create_plotly_chart_dict

def get_viewing_evolution_context(request: HttpRequest) -> Dict[str, Any]:
    """
    Processes the viewing evolution data from a YouTube Takeout zip file upload.

    Args:
        request (HttpRequest): The Django HTTP request object.

    Returns:
        Dict[str, Any]: A context dictionary for the viewing_evolution template.
    """
    context: Dict[str, Any] = {}
    daily_watch_freq: Dict[str, int] = {}
    monthly_watch_freq: Dict[str, int] = {}
    if request.method == 'POST' and 'takeout-zip' in request.FILES:
        uploaded_zip = request.FILES['takeout-zip']

        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as zf:
                watch_history_file = None
                for file_name in zf.namelist():
                    if 'watch-history.json' in file_name:
                        watch_history_file = file_name
                        break
                
                if watch_history_file:
                    with zf.open(watch_history_file) as json_file:
                        file_content = json_file.read().decode('utf-8')
                        analysis_results = process_takeout_data(file_content)
                        monthly_watch_freq = analysis_results.get('monthly_watch_freq', {})
                        daily_watch_freq = analysis_results.get('daily_watch_freq', {})

                        context['analysis_results'] = analysis_results
                        if monthly_watch_freq:
                            context['monthly_watch_freq_chart'] = json.dumps(create_plotly_chart_dict(
                            freq_data=monthly_watch_freq,
                            data_name="Videos Watched",
                            chart_type='timeseries_bar',
                            chart_title="Monthly Watch Frequency"
                        ))
                        
                        if daily_watch_freq:
                            context['daily_watch_freq_chart'] = json.dumps(create_plotly_chart_dict(
                                freq_data=daily_watch_freq,
                                data_name="Videos Watched",
                                chart_type='daily_needle_chart',
                                chart_title="Daily Watch Frequency"
                            ))
                        context['success_message'] = 'File uploaded successfully.'
                else:
                    context['error'] = 'watch-history.json not found in the uploaded .zip file.'

        except zipfile.BadZipFile:
            context['error'] = 'Invalid .zip file.'
            
    return context

def get_monthly_watch_freq(watch_history: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculates the number of videos watched per month from a list of watch history entries.

    Args:
        watch_history (List[Dict[str, Any]]): A list of watch history entries from the Takeout data.

    Returns:
        Dict[str, int]: A dictionary mapping dates (YYYY-MM) to the number of videos watched in that month.
    """
    monthly_counts = Counter()
    for entry in watch_history:
        if 'time' in entry:
            try:
                watch_month = datetime.fromisoformat(entry['time'].replace('Z', '+00:00')).strftime('%Y-%m')
                monthly_counts[watch_month] += 1
            except (ValueError, TypeError):
                continue
    
    sorted_monthly_counts = dict(sorted(monthly_counts.items()))
    return sorted_monthly_counts


def get_daily_watch_freq(watch_history: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Calculates the number of videos watched per day from a list of watch history entries.

    Args:
        watch_history (List[Dict[str, Any]]): A list of watch history entries from the Takeout data.

    Returns:
        Dict[str, int]: A dictionary mapping dates (YYYY-MM-DD) to the number of videos watched on that day.
    """
    daily_counts = Counter()
    for entry in watch_history:
        # Some entries might not have a 'time' field (e.g., ads)
        if 'time' in entry:
            try:
                # Extract the date part from the ISO 8601 timestamp
                watch_date = datetime.fromisoformat(entry['time'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                daily_counts[watch_date] += 1
            except (ValueError, TypeError):
                # Ignore entries with invalid time formats
                continue
    
    # Sort the results by date
    sorted_daily_counts = dict(sorted(daily_counts.items()))
    return sorted_daily_counts


def get_top_channels_by_videos_watched(watch_history: List[Dict[str, Any]], top_n: int = 10) -> Dict[str, int]:
    """
    Finds the top N channels by the number of videos watched.

    Args:
        watch_history (List[Dict[str, Any]]): A list of watch history entries from the Takeout data.
        top_n (int): The number of top channels to return.

    Returns:
        Dict[str, int]: A dictionary mapping channel titles to the number of videos watched.
    """
    channel_counts = Counter()
    for entry in watch_history:
        # Filter out entries that are ads or don't have channel information
        if 'subtitles' in entry and entry['subtitles']:
            channel_name = entry['subtitles'][0]['name']
            channel_counts[channel_name] += 1

    return dict(channel_counts.most_common(top_n))


def process_takeout_data(file_content: str) -> Dict[str, Any]:
    """
    Processes the content of a YouTube Takeout JSON file.

    Args:
        file_content (str): The content of the uploaded JSON file as a string.

    Returns:
        Dict[str, Any]: A dictionary containing the processed data.
    """
    try:
        data = json.loads(file_content) # `json.loads()` reads from a string
        
        # Get the daily watch frequency
        daily_watch_freq = get_daily_watch_freq(data)

        # Get the monthly watch frequency
        monthly_watch_freq = get_monthly_watch_freq(data)

        # Get top channels by videos watched
        top_channels = get_top_channels_by_videos_watched(data)
        
        # Get the monthly watch frequency
        monthly_watch_freq = get_monthly_watch_freq(data)
        
        return {
            'status': 'success',
            'message': 'Takeout data processed successfully.',
            'data_length': len(data),
            'daily_watch_freq': daily_watch_freq,
            'monthly_watch_freq': monthly_watch_freq,
            'top_channels': top_channels,
        }
    except json.JSONDecodeError:
        return {'status': 'error', 'message': 'Invalid JSON file.'}
    except Exception as e:
        return {'status': 'error', 'message': f'An error occurred: {str(e)}'}