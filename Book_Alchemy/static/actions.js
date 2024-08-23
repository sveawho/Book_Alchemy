document.addEventListener('DOMContentLoaded', () => {
    // Existing code for sortable headers
    const headers = document.querySelectorAll('th.sortable');

    headers.forEach(header => {
        // Set initial ARIA sort state
        const currentSort = header.dataset.sort;
        header.setAttribute('aria-sort', header.classList.contains('sorted-asc') ? 'ascending' : 'descending');

        header.addEventListener('click', () => {
            const currentSort = header.dataset.sort;
            let newSortOrder = 'asc';

            // Determine the new sort order
            if (header.classList.contains('sorted-asc')) {
                newSortOrder = 'desc';
            } else if (header.classList.contains('sorted-desc')) {
                newSortOrder = 'asc';
            }

            // Remove current sorting classes
            headers.forEach(h => {
                h.classList.remove('sorted-asc', 'sorted-desc');
                h.setAttribute('aria-sort', 'none'); // Reset ARIA sort state
            });

            // Add new sorting class and ARIA sort state
            header.classList.add(`sorted-${newSortOrder}`);
            header.setAttribute('aria-sort', newSortOrder === 'asc' ? 'ascending' : 'descending');

            // Redirect with new sort parameters
            const url = new URL(window.location.href);
            url.searchParams.set('sort_by', currentSort);
            url.searchParams.set('sort_order', newSortOrder);
            window.location.href = url.toString();
        });
    });

    // New code to hide flash messages after 3 seconds
    const flashMessages = document.querySelectorAll('.flash-messages li');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300); // Match this time with the CSS transition duration
        }, 3000); // Show for 3 seconds
    });
});
