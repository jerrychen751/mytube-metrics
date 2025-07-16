document.addEventListener('DOMContentLoaded', function() {
    const recommendedVideosContainer = document.getElementById('recommended-videos-container');
    const loadingSpinner = document.getElementById('loading-spinner');
    let nextPageToken = null;
    let isLoading = false;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function fetchRecommendedVideos() {
        if (isLoading) return;
        isLoading = true;
        loadingSpinner.style.display = 'block';

        let url = '/recommended-videos/ajax/';
        if (nextPageToken) {
            url += `?page_token=${nextPageToken}`;
        }

        fetch(url, {
            method: 'GET',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json',
            },
        })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    window.location.href = '/'; // Redirect to login if unauthorized
                }
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            nextPageToken = data.next_page_token;
            data.recommended_videos.forEach(video => {
                const videoCard = `
                    <div class="col-md-6 mb-4">
                        <div class="card h-100">
                            <div class="row g-0">
                                <div class="col-md-4">
                                    <img src="${video.recommended_video_thumbnail}" class="img-fluid rounded-start" alt="${video.recommended_video_title}">
                                </div>
                                <div class="col-md-8">
                                    <div class="card-body">
                                        <h5 class="card-title">${video.recommended_video_title}</h5>
                                        <p class="card-text">Reason: ${video.recommendation_reason}</p>
                                        ${video.seed_video_thumbnail ? 
                                            `<p class="card-text"><small class="text-muted">Recommended because you watched:</small></p>
                                             <img src="${video.seed_video_thumbnail}" class="img-fluid rounded-start" alt="Seed Video Thumbnail" style="max-width: 100px;">
                                            ` : ''}
                                        <a href="https://www.youtube.com/watch?v=${video.recommended_video_id}" target="_blank" class="btn btn-sm btn-outline-primary mt-2">Watch Video</a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;
                recommendedVideosContainer.insertAdjacentHTML('beforeend', videoCard);
            });

            isLoading = false;
            loadingSpinner.style.display = 'none';

            // If there's no next page token and no videos were loaded, display a message
            if (!nextPageToken && data.recommended_videos.length === 0 && recommendedVideosContainer.children.length === 0) {
                recommendedVideosContainer.innerHTML = '<p class="text-center col-12">No recommended videos found.</p>';
            }
        })
        .catch(error => {
            console.error('Error fetching recommended videos:', error);
            isLoading = false;
            loadingSpinner.style.display = 'none';
            recommendedVideosContainer.innerHTML = '<p class="text-center col-12 text-danger">Failed to load recommended videos. Please try again later.</p>';
        });
    }

    // Infinite scrolling logic
    window.addEventListener('scroll', () => {
        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;
        if (scrollTop + clientHeight >= scrollHeight - 500 && !isLoading && nextPageToken !== null) {
            fetchRecommendedVideos();
        }
    });

    // Initial load
    fetchRecommendedVideos();
});