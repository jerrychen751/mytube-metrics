# Standard Library Imports
from typing import Any, List
from urllib.parse import unquote

def parse_topic_urls(topic_details: Any) -> List[str]:
    """Convert the topicDetails object from YouTube Data API into a list of user-friendly topic tags."""
    topic_urls = topic_details.get('topicCategories', [])
    parsed_topics = []

    for url in topic_urls:
        topic = unquote(url.split('/')[-1]).replace('_', ' ')
        if '(sociology)' in topic.lower():
            topic = topic.lower().replace(' (sociology)', '')
        parsed_topics.append(topic.title())

    return parsed_topics