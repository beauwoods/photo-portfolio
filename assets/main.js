// main.js - Handles Masonry grid and image loading for photo portfolio

// Lightbox render function with improved spacing, meta row, and no horizontal overflow
function showLightbox(imgObj) {
  const lightbox = document.getElementById('lightbox');

  const displayTitle = imgObj.title && imgObj.title.trim() ? imgObj.title : imgObj.path.split('/').pop();

  let dateHtml = '';
  if (imgObj.added) {
    const dateObj = new Date(imgObj.added);
    const monthYear = dateObj.toLocaleString('en-US', { month: 'long', year: 'numeric' });
    dateHtml = `
      <span class="lightbox-date">
        <svg viewBox="0 0 16 16" width="16" height="16"><rect x="2" y="4" width="12" height="10" rx="2" fill="#90ee90"/><path d="M4 2v2M12 2v2" stroke="#90ee90" stroke-width="1.5"/></svg>
        ${monthYear}
      </span>
    `;
  }

  let locationHtml = '';
  if (imgObj.location) {
    locationHtml = `
      <span class="lightbox-location">
        <svg viewBox="0 0 16 16" width="16" height="16"><path d="M8 2a5 5 0 0 1 5 5c0 3.5-5 7-5 7S3 10.5 3 7a5 5 0 0 1-5-5zm0 2a3 3 0 1 0 0 6a3 3 0 0 0 0-6z" fill="#90ee90"/></svg>
        ${imgObj.location}
      </span>
    `;
  }

  let tagsHtml = '';
  if (imgObj.tags && imgObj.tags.length > 0) {
    tagsHtml = `
      <span class="lightbox-tags">
        <svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 9V2h7l5 5-7 7-5-5z" fill="#ffee00"/></svg>
        ${imgObj.tags.map(tag => `<span class="tag-chip">${tag}</span>`).join('')}
      </span>
    `;
  }

  // License and view original on same meta row
  let ccHtml = `
    <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/" target="_blank"
      title="Some rights reserved. Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International"
      class="lightbox-license">
      <img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png"
        alt="Creative Commons BY-NC-SA License" class="cc-license-img" />
    </a>
  `;

  let linkHtml = '';
  if (imgObj.original_link) {
    linkHtml = `
      <a href="${imgObj.original_link}" target="_blank" class="lightbox-original-link">
        <svg width="16" height="16" viewBox="0 0 16 16"><path d="M7 7h6m0 0V1m0 6L6.25 13.75a3 3 0 1 1-4.24-4.24L9 2" stroke="#90ee90" stroke-width="1.5" fill="none"/></svg>
        View original
      </a>
    `;
  }

  lightbox.innerHTML = `
    <div class="lightbox-overlay" id="lightbox-overlay">
      <div class="lightbox-content">
        <button class="lightbox-close" id="lightbox-close" title="Close">&times;</button>
        <div class="lightbox-top-overlay">
          <div class="lightbox-title">${displayTitle}</div>
        </div>
        <img class="lightbox-img" src="${imgObj.path}" alt="${displayTitle}">
        <div class="lightbox-bottom-overlay">
          <div class="lightbox-row">
            ${dateHtml}
            ${locationHtml}
          </div>
          ${tagsHtml}
          <div class="lightbox-bottom-meta-row">
            ${linkHtml}
            ${ccHtml}
          </div>
        </div>
        <div class="lightbox-scroll-cue"></div>
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

  // --- Overlay code START ---
  // Top overlay (title or filename)
  const topOverlay = document.createElement('div');
  topOverlay.className = 'image-overlay-top';
  const displayTitle = img.title && img.title.trim() ? img.title : img.path.split('/').pop();
  const titleDiv = document.createElement('div');
  titleDiv.className = 'overlay-title';
  titleDiv.textContent = displayTitle;
  topOverlay.appendChild(titleDiv);
  div.appendChild(topOverlay);

  // Bottom overlay (date/location/tags)
  const bottomOverlay = document.createElement('div');
  bottomOverlay.className = 'image-overlay-bottom';

  const rowDiv = document.createElement('div');
  rowDiv.className = 'overlay-row';
  if (img.added) {
    const dateObj = new Date(img.added);
    const monthYear = dateObj.toLocaleString('en-US', { month: 'long', year: 'numeric' });
    const dateDiv = document.createElement('span');
    dateDiv.className = 'overlay-date';
    dateDiv.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16"><rect x="2" y="4" width="12" height="10" rx="2" fill="#90ee90"/><path d="M4 2v2M12 2v2" stroke="#90ee90" stroke-width="1.5"/></svg> ${monthYear}`;
    rowDiv.appendChild(dateDiv);
  }
  if (img.location) {
    const locationDiv = document.createElement('span');
    locationDiv.className = 'overlay-location';
    locationDiv.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M8 2a5 5 0 0 1 5 5c0 3.5-5 7-5 7S3 10.5 3 7a5 5 0 0 1-5-5zm0 2a3 3 0 1 0 0 6a3 3 0 0 0 0-6z" fill="#90ee90"/></svg> ${img.location}`;
    rowDiv.appendChild(locationDiv);
  }
  bottomOverlay.appendChild(rowDiv);

  // Tags (below date/location row)
  if (img.tags && img.tags.length > 0) {
    const tagsDiv = document.createElement('span');
    tagsDiv.className = 'overlay-tags';
    tagsDiv.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 9V2h7l5 5-7 7-5-5z" fill="#ffee00"/></svg>`;
    img.tags.forEach(tag => {
      const tagSpan = document.createElement('span');
      tagSpan.className = 'tag-chip';
      tagSpan.textContent = tag;
      tagsDiv.appendChild(tagSpan);
    });
    bottomOverlay.appendChild(tagsDiv);
  }
  div.appendChild(bottomOverlay);
  // --- Overlay code END ---

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

// Show QR on profile pic click or keyboard activation
const profilePic = document.getElementById('profile-pic');
const qrPopup = document.getElementById('qr-popup');
const qrInner = document.getElementById('qr-inner');

profilePic.onclick = () => {
  qrPopup.style.display = 'flex';
};
profilePic.onkeydown = (e) => {
  if (e.key === "Enter" || e.key === " ") qrPopup.style.display = 'flex';
};

// Close QR popup when clicking outside the QR code (shadowbox)
qrPopup.onclick = (e) => {
  if (e.target === qrPopup) qrPopup.style.display = 'none';
};