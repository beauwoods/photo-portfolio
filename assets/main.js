// ===============================
// Theme Variables and Config
// ===============================
const THEME = {
  dateIcon: `<svg viewBox="0 0 16 16" width="16" height="16"><rect x="2" y="4" width="12" height="10" rx="2" fill="#90ee90"/><path d="M4 2v2M12 2v2" stroke="#90ee90" stroke-width="1.5"/></svg>`,
  locationIcon: `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M8 2a5 5 0 0 1 5 5c0 3.5-5 7-5 7S3 10.5 3 7a5 5 0 0 1-5-5zm0 2a3 3 0 1 0 0 6a3 3 0 0 0 0-6z" fill="#90ee90"/></svg>`,
  tagIcon: `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 9V2h7l5 5-7 7-5-5z" fill="#ffee00"/></svg>`,
  licenseIcon: `<img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png" alt="CC BY-NC-SA License" class="cc-license-img" />`,
  originalIcon: `<svg width="16" height="16" viewBox="0 0 16 16"><path d="M7 7h6m0 0V1m0 6L6.25 13.75a3 3 0 1 1-4.24-4.24L9 2" stroke="#90ee90" stroke-width="1.5" fill="none"/></svg>`,
};

// ===============================
// Utility Functions
// ===============================
function getImageDisplayTitle(img) {
  return img.title && img.title.trim() ? img.title : img.path.split('/').pop();
}
function formatDate(dateString) {
  if (!dateString) return '';
  const dateObj = new Date(dateString);
  return dateObj.toLocaleString('en-US', { month: 'long', year: 'numeric' });
}
function createSVG(iconType) {
  return THEME[iconType + 'Icon'] || '';
}
function createTagChip(tag) {
  return `<span class="image-tag-chip">${tag}</span>`;
}
function createTagList(tags) {
  if (!tags || !tags.length) return '';
  return `
    <span class="image-tags">
      ${createSVG('tag')}
      ${tags.map(createTagChip).join('')}
    </span>
  `;
}
function createOverlayRow(date, location) {
  return `
    <div class="overlay-row">
      ${date ? `<span class="image-date">${createSVG('date')}${formatDate(date)}</span>` : ''}
      ${location ? `<span class="image-location">${createSVG('location')}${location}</span>` : ''}
    </div>
  `;
}
function createLicense(licenseUrl) {
  return `<a href="${licenseUrl}" target="_blank" class="lightbox-license" title="CC BY-NC-SA 4.0">${THEME.licenseIcon}</a>`;
}
function createOriginalLink(link) {
  return `
    <a href="${link}" target="_blank" class="lightbox-original-link">
      ${THEME.originalIcon}View original
    </a>
  `;
}

// ===============================
// Masonry Grid & Gallery Rendering
// ===============================
function renderGalleryImage(imgObj) {
  const div = document.createElement('div');
  div.className = 'grid-item';
  div.tabIndex = 0;

  // Image
  const imageElem = document.createElement('img');
  imageElem.src = imgObj.path;
  imageElem.alt = getImageDisplayTitle(imgObj);
  div.appendChild(imageElem);

  // Overlays
  div.appendChild(renderOverlayTop('gallery', imgObj));
  div.appendChild(renderOverlayBottom('gallery', imgObj));

  // Events
  div.onclick = () => showLightbox(imgObj);
  div.onkeydown = (e) => {
    if (e.key === "Enter" || e.key === " ") showLightbox(imgObj);
  };

  return div;
}

function initMasonryGrid(images) {
  const grid = document.getElementById('grid');
  var msnry = new Masonry(grid, {
    itemSelector: '.grid-item',
    columnWidth: 320,
    gutter: 32,
    fitWidth: true
  });

  images.forEach((img) => {
    const div = renderGalleryImage(img);
    grid.appendChild(div);
    imagesLoaded(div).on('progress', function() {
      msnry.appended(div);
      msnry.layout();
    });
  });
}

// ===============================
// Overlay Rendering (Shared)
// ===============================
function renderOverlayTop(context, imgObj) {
  const top = document.createElement('div');
  top.className = context === 'gallery' ? 'gallery-overlay-top' : 'lightbox-top-overlay';
  top.innerHTML = `<div class="image-title">${getImageDisplayTitle(imgObj)}</div>`;
  return top;
}
function renderOverlayBottom(context, imgObj) {
  const bottom = document.createElement('div');
  bottom.className = context === 'gallery' ? 'gallery-overlay-bottom' : 'lightbox-bottom-overlay';

  let html = createOverlayRow(imgObj.added, imgObj.location);
  html += createTagList(imgObj.tags);

  // For lightbox, add meta row
  if (context === 'lightbox') {
    html += `<div class="lightbox-bottom-meta-row">` +
      (imgObj.original_link ? createOriginalLink(imgObj.original_link) : '') +
      createLicense("https://creativecommons.org/licenses/by-nc-sa/4.0/") +
      `</div>`;
  }
  bottom.innerHTML = html;
  return bottom;
}

// ===============================
// Lightbox / Modal Logic
// ===============================
function showLightbox(imgObj) {
  const lightbox = document.getElementById('lightbox');
  lightbox.innerHTML = `
    <div class="lightbox-overlay" id="lightbox-overlay">
      <div class="lightbox-content">
        <button class="lightbox-close" id="lightbox-close" title="Close">&times;</button>
        ${renderOverlayTop('lightbox', imgObj).outerHTML}
        <img class="lightbox-img" src="${imgObj.path}" alt="${getImageDisplayTitle(imgObj)}">
        ${renderOverlayBottom('lightbox', imgObj).outerHTML}
        <div class="lightbox-scroll-cue"></div>
      </div>
    </div>
  `;
  lightbox.style.display = 'block';
  document.body.style.overflow = 'hidden';

  attachLightboxEventListeners();
}
function closeLightbox() {
  document.getElementById('lightbox').style.display = 'none';
  document.body.style.overflow = '';
  document.removeEventListener('keydown', onLightboxKey);
}
function onLightboxKey(e) {
  if (e.key === "Escape") closeLightbox();
}
function attachLightboxEventListeners() {
  document.getElementById('lightbox-close').onclick = closeLightbox;
  document.getElementById('lightbox-overlay').onclick = function(e) {
    if (e.target === this) closeLightbox();
  };
  document.addEventListener('keydown', onLightboxKey);
}

// ===============================
// QR Code Popup / Modal
// ===============================
function showQRModal() {
  const qrPopup = document.getElementById('qr-popup');
  qrPopup.style.display = 'flex';
  attachQRModalEventListeners();
}
function closeQRModal() {
  document.getElementById('qr-popup').style.display = 'none';
}
function onQRModalKey(e) {
  if (e.key === "Escape") closeQRModal();
}
function attachQRModalEventListeners() {
  const qrPopup = document.getElementById('qr-popup');
  qrPopup.onclick = (e) => { if (e.target === qrPopup) closeQRModal(); };
  document.addEventListener('keydown', onQRModalKey);
}

// ===============================
// Event Listeners & Handlers
// ===============================
function setupGlobalEventListeners() {
  // QR profile pic
  const profilePic = document.getElementById('profile-pic');
  profilePic.onclick = showQRModal;
  profilePic.onkeydown = (e) => {
    if (e.key === "Enter" || e.key === " ") showQRModal();
  };
}

// ===============================
// Initialization
// ===============================
function initPortfolioApp() {
  fetch('images.json')
    .then(response => response.json())
    .then(data => {
      const images = Array.isArray(data) ? data : data.images;
      initMasonryGrid(images);
    })
    .catch(err => {
      document.getElementById('grid').innerHTML = '<p style="color:red;text-align:center;">Could not load images.json.</p>';
      console.error(err);
    });

  setupGlobalEventListeners();
}

// Run app on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initPortfolioApp);