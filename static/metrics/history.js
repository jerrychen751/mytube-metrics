document.addEventListener('DOMContentLoaded', function() {
    // Chart rendering placeholder
    const ctx = document.getElementById('viewingEvolutionChart');
    if (ctx) {
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: [], // Dates
                datasets: [{
                    label: 'Videos Watched',
                    data: [], // Number of videos
                    borderColor: 'rgb(75, 192, 192)',
                    tension: 0.1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    // File upload handling
    const uploadForm = document.getElementById('takeoutUploadForm');
    const uploadMessageDiv = document.getElementById('uploadMessage');

    if (uploadForm) {
        uploadForm.addEventListener('submit', async function(event) {
            event.preventDefault(); // Prevent default form submission

            const formData = new FormData(uploadForm);
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

            uploadMessageDiv.innerHTML = '<div class="alert alert-info">Uploading and analyzing...</div>';

            try {
                const response = await fetch('/viewing-evolution/', {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'X-CSRFToken': csrfToken
                    }
                });

                const data = await response.json();

                if (response.ok) {
                    uploadMessageDiv.innerHTML = `<div class="alert alert-success">${data.message || 'Upload successful!'}</div>`;
                    // Maybe refresh the page or update charts here
                } else {
                    uploadMessageDiv.innerHTML = `<div class="alert alert-danger">Error: ${data.message || 'An unknown error occurred.'}</div>`;
                }
            } catch (error) {
                console.error('Network error or unexpected issue:', error);
                uploadMessageDiv.innerHTML = '<div class="alert alert-danger">A network error occurred. Please try again.</div>';
            }
        });
    }
});