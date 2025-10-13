// main.js - Handles Masonry grid and image loading for photo portfolio

    // Lightbox render function
    function showLightbox(imgObj) {
      const lightbox = document.getElementById('lightbox');
      let tagsHtml = '';
      if (imgObj.tags && imgObj.tags.length > 0) {
        tagsHtml = '<div class="lightbox-tags">' + imgObj.tags.map(tag =>
          `<span class="lightbox-tag">${tag}</span>`
        ).join('') + '</div>';
      }
      let dateHtml = imgObj.date_added ? `<div class="lightbox-date">Date added: ${imgObj.date_added}</div>` : '';
      let locationHtml = imgObj.location ? `<div class="lightbox-location">Location: ${imgObj.location}</div>` : '';
      let linkHtml = imgObj.original_link ? `<a href="${imgObj.original_link}" target="_blank" class="lightbox-link">View original</a>` : '';

      // Visible download icon, label only on hover
      let downloadHtml = `
        <a href="${imgObj.path}" download class="lightbox-download" title="Download original">
          <svg class="icon-download" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-label="Download original">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="7 10 12 15 17 10"/>
            <line x1="12" y1="15" x2="12" y2="3"/>
          </svg>
          <span class="download-label">Download original</span>
        </a>
      `;
      // Official CC BY-NC-SA badge and link
      let ccHtml = `
        <span class="lightbox-cc">
          <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank"
             title="Some rights reserved. Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International">
            <img
              src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png"
              alt="Creative Commons BY-NC-SA License"
              class="cc-license-img"
            >
          </a>
        </span>
      `;

      lightbox.innerHTML = `
        <div class="lightbox-overlay" id="lightbox-overlay">
          <div class="lightbox-content">
            <button class="lightbox-close" id="lightbox-close" title="Close">&times;</button>
            <img class="lightbox-img" src="${imgObj.path}" alt="${imgObj.title || ''}">
            <div class="lightbox-info">
              <div class="lightbox-title">${imgObj.title || ''}</div>
              ${dateHtml}
              ${locationHtml}
              ${tagsHtml}
              ${linkHtml}
              <div class="lightbox-utils">
                ${downloadHtml}
                ${ccHtml}
              </div>
            </div>
          </div>
        </div>
      `;
      lightbox.style.display = 'block';
      document.body.style.overflow = 'hidden';

      document.getElementById('lightbox-close').onclick = closeLightbox;
      document.getElementById('lightbox-overlay').onclick = function(e) {
        if (e.target === this) closeLightbox();
      };
      document.addEventListener('keydown', onLightboxKey);
    }
    function closeLightbox() {
      document.getElementById('lightbox').style.display = 'none';
      document.body.style.overflow = '';
      document.removeEventListener('keydown', onLightboxKey);
    }
    function onLightboxKey(e) {
      if (e.key === "Escape") closeLightbox();
    }

    // Main Masonry gallery
    fetch('images.json')
      .then(response => response.json())
      .then(data => {
        const images = Array.isArray(data) ? data : data.images;
        const grid = document.getElementById('grid');
        var msnry = new Masonry(grid, {
          itemSelector: '.grid-item',
          columnWidth: 320,
          gutter: 32,
          fitWidth: true
        });

        images.forEach((img, idx) => {
          const div = document.createElement('div');
          div.className = 'grid-item';
          div.tabIndex = 0;
          const imageElem = document.createElement('img');
          imageElem.src = img.path;
          imageElem.alt = img.title || '';
          div.appendChild(imageElem);

          if (img.title || (img.tags && img.tags.length > 0)) {
            const info = document.createElement('div');
            info.className = 'image-info';

            if (img.title) {
              const titleDiv = document.createElement('div');
              titleDiv.className = 'image-title';
              titleDiv.textContent = img.title;
              info.appendChild(titleDiv);
            }
            if (img.tags && img.tags.length > 0) {
              const tagsDiv = document.createElement('div');
              tagsDiv.className = 'image-tags';
              img.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.className = 'image-tag';
                tagSpan.textContent = tag;
                tagsDiv.appendChild(tagSpan);
              });
              info.appendChild(tagsDiv);
            }
            div.appendChild(info);
          }

          grid.appendChild(div);

          imagesLoaded(div).on('progress', function() {
            msnry.appended(div);
            msnry.layout();
          });

          div.onclick = function() { showLightbox(img); };
          div.onkeydown = function(e) {
            if (e.key === "Enter" || e.key === " ") showLightbox(img);
          };
        });
      })
      .catch(err => {
        document.getElementById('grid').innerHTML = '<p style="color:red;text-align:center;">Could not load images.json.</p>';
        console.error(err);
      });