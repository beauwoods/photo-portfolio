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
    locationDiv.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M8 2a5 5 0 0 1 5 5c0 3.5-5 7-5 7S3 10.5 3 7a5 5 0 0 1-5-5zm0 2a3 3 0 1 0 0 6a3 3 0 0 0 0-6z" fill="#8fd6ff"/></svg> ${img.location}`;
    rowDiv.appendChild(locationDiv);
  }
  bottomOverlay.appendChild(rowDiv);

  // Tags (below date/location row)
  if (img.tags && img.tags.length > 0) {
    const tagsDiv = document.createElement('span');
    tagsDiv.className = 'overlay-tags';
    tagsDiv.innerHTML = `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 9V2h7l5 5-7 7-5-5z" fill="#ffeb6e"/></svg>`;
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