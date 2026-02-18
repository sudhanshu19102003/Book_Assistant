(function() {
    const uniqueId = '___UNIQUE_ID__';
    
    function showBookDetails(title, authors, publisher, date, description, thumbnail, row) {
        const detailsDiv = document.getElementById('bookDetails_' + uniqueId);
        const contentDiv = document.getElementById('detailsContent_' + uniqueId);
        
        if (!detailsDiv || !contentDiv) {
            console.error('Could not find details elements for ID:', uniqueId);
            return;
        }

        // Remove selected class from all rows with this unique ID
        document.querySelectorAll('.book-row[data-unique-id="' + uniqueId + '"]').forEach(r => r.classList.remove('selected'));
        row.classList.add('selected');

        let coverHtml = '';
        if (thumbnail) {
            coverHtml = '<img src="' + thumbnail + '" class="cover-large" alt="' + title.replace(/"/g, '&quot;') + '">';
        }

        contentDiv.innerHTML = coverHtml +
            '<h3>' + title.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</h3>' +
            '<div class="info-label">Authors:</div>' +
            '<div class="info-value">' + authors.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>' +
            '<div class="info-label">Publisher:</div>' +
            '<div class="info-value">' + publisher.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>' +
            '<div class="info-label">Published Date:</div>' +
            '<div class="info-value">' + date.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>' +
            '<div class="info-label">Description:</div>' +
            '<div class="description">' + description.replace(/</g, '&lt;').replace(/>/g, '&gt;') + '</div>';

        detailsDiv.classList.add('visible');
    }

    function closeDetails() {
        const detailsDiv = document.getElementById('bookDetails_' + uniqueId);
        if (!detailsDiv) {
            console.error('Could not find details div for ID:', uniqueId);
            return;
        }
        detailsDiv.classList.remove('visible');
        document.querySelectorAll('.book-row[data-unique-id="' + uniqueId + '"]').forEach(r => r.classList.remove('selected'));
    }

    function attachEventListeners() {
        // Add click handlers to all book rows
        const rows = document.querySelectorAll('.book-row[data-unique-id="' + uniqueId + '"]');
        console.log('Found', rows.length, 'rows for ID:', uniqueId);
        
        rows.forEach(function(row) {
            row.addEventListener('click', function() {
                const title = row.getAttribute('data-title');
                const authors = row.getAttribute('data-authors');
                const publisher = row.getAttribute('data-publisher');
                const date = row.getAttribute('data-date');
                const description = row.getAttribute('data-description');
                const thumbnail = row.getAttribute('data-thumbnail');
                showBookDetails(title, authors, publisher, date, description, thumbnail, row);
            });
        });

        // Add click handler to close button
        const closeBtn = document.querySelector('.close-details[data-unique-id="' + uniqueId + '"]');
        if (closeBtn) {
            closeBtn.addEventListener('click', closeDetails);
        }
    }

    // Attach event listeners after DOM is loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', attachEventListeners);
    } else {
        // DOM is already loaded, run immediately
        attachEventListeners();
    }
})();
