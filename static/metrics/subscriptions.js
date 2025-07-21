document.addEventListener('DOMContentLoaded', function() {
    var collapseElements = document.querySelectorAll('.collapse');

    collapseElements.forEach(function(collapseEl) {
        // When a collapse element is shown
        collapseEl.addEventListener('shown.bs.collapse', function () {
            var wrapper = this.querySelector('.description-wrapper');
            if (!wrapper) return;

            var text = wrapper.querySelector('.description-text');
            var btn = wrapper.querySelector('.read-more-btn');

            // Temporarily remove collapsed class to get natural height
            text.classList.remove('collapsed');
            var naturalHeight = text.scrollHeight;

            // Re-add collapsed class and check if it overflows
            text.classList.add('collapsed');
            var collapsedHeight = text.clientHeight;

            if (naturalHeight > collapsedHeight) {
                btn.classList.add('d-block');
                btn.innerHTML = 'Read more <i class="bi bi-chevron-down ms-2"></i>';
            } else {
                text.classList.remove('collapsed'); // Ensure it's not collapsed if it fits
                btn.classList.remove('d-block');
            }
        });

        // When a collapse element is hidden
        collapseEl.addEventListener('hidden.bs.collapse', function () {
            var wrapper = this.querySelector('.description-wrapper');
            if (!wrapper) return;

            var text = wrapper.querySelector('.description-text');
            var btn = wrapper.querySelector('.read-more-btn');

            // Reset the state
            text.classList.add('collapsed');
            btn.classList.remove('d-block');
            btn.innerHTML = 'Read more <i class="bi bi-chevron-down ms-2"></i>'; // Reset button text
        });
    });

    // Attach click listeners to all read-more buttons once
    document.querySelectorAll('.read-more-btn').forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            var wrapper = btn.closest('.description-wrapper');
            if (!wrapper) {
                return;
            }

            var text = wrapper.querySelector('.description-text');
            if (!text) {
                return;
            }

            if (text.classList.contains('collapsed')) {
                text.classList.remove('collapsed');
                btn.innerHTML = 'Show less <i class="bi bi-chevron-up ms-2"></i>';
            } else {
                text.classList.add('collapsed');
                btn.innerHTML = 'Read more <i class="bi bi-chevron-down ms-2"></i>';
            }
            
        });
    });
});
