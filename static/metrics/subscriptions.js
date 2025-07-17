document.addEventListener('DOMContentLoaded', function() {
    var collapseElements = document.querySelectorAll('.collapse');

    collapseElements.forEach(function(collapseEl) {
        // When a collapse element is shown
        collapseEl.addEventListener('show.bs.collapse', function () {
            setTimeout(() => {
                var wrapper = this.querySelector('.description-wrapper');
                if (!wrapper) return;

                var text = wrapper.querySelector('.description-text');
                var btn = wrapper.querySelector('.read-more-btn');

                // Check if the text is overflowing now that it's visible
                if (text.scrollHeight > text.clientHeight) {
                    btn.style.display = 'block';
                } else {
                    text.classList.remove('collapsed');
                }

                btn.addEventListener('click', function(e) {
                    e.preventDefault();
                    text.classList.remove('collapsed');
                    btn.style.display = 'none';
                }, { once: true }); // Use { once: true } to avoid attaching multiple listeners
            }, 100);
        });

        // When a collapse element is hidden
        collapseEl.addEventListener('hidden.bs.collapse', function () {
            var wrapper = this.querySelector('.description-wrapper');
            if (!wrapper) return;

            var text = wrapper.querySelector('.description-text');
            var btn = wrapper.querySelector('.read-more-btn');

            // Reset the state
            text.classList.add('collapsed');
            btn.style.display = 'none';
        });
    });
});
