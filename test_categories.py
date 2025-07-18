
import os
import sys
import django
from pprint import pprint

# Add the project root to the Python path
sys.path.append('/Users/jerry/Desktop/python/projects/mytube_metrics')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mytube_metrics.settings')
django.setup()

from metrics.models import UserCredential
from metrics.utils.api_client import YouTubeClient

def test_video_categories():
    """
    Tests each video category to see if it can be listed.
    """
    # Get the first user's credentials to initialize the YouTubeClient
    user_credential = UserCredential.objects.first()
    if not user_credential:
        print("No user credentials found in the database.")
        return

    client = YouTubeClient(credentials=user_credential)

    # 1. Get all available video categories
    all_categories_response = client.videos.list_video_category(part="snippet", region_code="US")
    if not all_categories_response or 'items' not in all_categories_response:
        print("Could not retrieve video categories.")
        return

    categories = all_categories_response.get('items', [])
    pprint(categories)
    print("-" * 30)
    print(f"Found {len(categories)} categories to test.")
    print("-" * 30)

    # 2. Iterate through each category and test it
    for category in categories:
        category_id = category['id']
        category_name = category['snippet']['title']
        
        print(f"Testing Category: '{category_name}' (ID: {category_id})")

        try:
            # 3. Try to list the most popular videos for the category
            response = client.videos.list_video(
                part="snippet",
                chart='mostPopular',
                video_category_id=category_id,
                max_results=1
            )

            # 4. Print the results
            if response and response.get('items'):
                print(f"  -> SUCCESS: Successfully listed videos for '{category_name}'.")
            elif response is not None and not response.get('items'):
                print(f"  -> SUCCESS (No Items): The API call for '{category_name}' was successful, but returned no videos.")
            else:
                # This case handles when the response is None
                print(f"  -> FAILED: The API call for '{category_name}' failed and returned None.")

        except Exception as e:
            print(f"  -> FAILED with exception for '{category_name}': {e}")
        
        print("-" * 30)

if __name__ == "__main__":
    test_video_categories()
