// ===============================
// Theme Variables and Config
// ===============================
const THEME = {
  dateIcon: `<svg viewBox="0 0 16 16" width="16" height="16"><rect x="2" y="4" width="12" height="10" rx="2" fill="currentColor"/><path d="M4 2v2M12 2v2" stroke="currentColor" stroke-width="1.5"/></svg>`,
  locationIcon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-geo-alt-fill" viewBox="0 0 16 16"><path d="M8 16s6-5.686 6-10A6 6 0 0 0 2 6c0 4.314 6 10 6 10m0-7a3 3 0 1 1 0-6 3 3 0 0 1 0 6"/></svg>`,
  tagIcon: `<svg viewBox="0 0 16 16" width="16" height="16"><path d="M2 9V2h7l5 5-7 7-5-5z" fill="currentColor"/></svg>`,
  licenseIcon: `<img src="https://mirrors.creativecommons.org/presskit/buttons/88x31/png/by-nc-sa.png" alt="CC BY-NC-SA License" class="cc-license-img" />`,
  downloadIcon: `<svg class="icon-download" viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2" aria-label="Download"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>`,
  flickrIcon: `<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><circle cx="7" cy="12" r="4" /><circle cx="17" cy="12" r="4" />`,
  instagramIcon: `<svg viewBox="0 0 24 24" width="24" height="24" aria-hidden="true"><path d="M7.75 2h8.5A5.75 5.75 0 0 1 22 7.75v8.5A5.75 5.75 0 0 1 16.25 22h-8.5A5.75 5.75 0 0 1 2 16.25v-8.5A5.75 5.75 0 0 1 7.75 2zm8.5 1.5h-8.5A4.25 4.25 0 0 0 3.5 7.75v8.5A4.25 4.25 0 0 0 7.75 20.5h8.5A4.25 4.25 0 0 0 20.5 16.25v-8.5A4.25 4.25 0 0 0 16.25 3.5zm-4.25 3.25a5.25 5.25 0 1 1 0 10.5 5.25 5.25 0 0 1 0-10.5zm0 1.5a3.75 3.75 0 1 0 0 7.5 3.75 3.75 0 0 0 0-7.5zm5.25.75a1 1 0 1 1-2 0 1 1 0 0 1 2 0z"/></svg>`,
  twitterIcon: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" class="bi bi-twitter" viewBox="0 0 16 16"><path d="M5.026 15c6.038 0 9.341-5.003 9.341-9.334q.002-.211-.006-.422A6.7 6.7 0 0 0 16 3.542a6.7 6.7 0 0 1-1.889.518 3.3 3.3 0 0 0 1.447-1.817 6.5 6.5 0 0 1-2.087.793A3.286 3.286 0 0 0 7.875 6.03a9.32 9.32 0 0 1-6.767-3.429 3.29 3.29 0 0 0 1.018 4.382A3.3 3.3 0 0 1 .64 6.575v.045a3.29 3.29 0 0 0 2.632 3.218 3.2 3.2 0 0 1-.865.115 3 3 0 0 1-.614-.057 3.28 3.28 0 0 0 3.067 2.277A6.6 6.6 0 0 1 .78 13.58a6 6 0 0 1-.78-.045A9.34 9.34 0 0 0 5.026 15"/></svg>`,
  genericIcon: `<svg aria-label="External link" viewBox="0 0 20 20" width="24" height="24"><path d="M14 3h3v3m0-3L10 10m4 7H5a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h7" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>`
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
  return `<span class="chip chip-tag">${tag}</span>`;
}
function createTagList(tags) {
  if (!tags || !tags.length) return '';
  return `
    <span class="row-tags">
      ${createSVG('tag')}
      ${tags.map(createTagChip).join('')}
    </span>
  `;
}
function createRowTimePlace(date, location) {
  return `
    <div class="row-timeplace">
      ${date ? `<span class="row-date">${createSVG('date')}<span class="chip chip-date">${formatDate(date)}</span></span>` : ''}
      ${location ? `<span class="row-place">${createSVG('location')}<span class="chip chip-place">${location}</span></span>` : ''}
    </div>
  `;
}
function createLicense(licenseUrl) {
  return `<a href="${licenseUrl}" target="_blank" class="lightbox-license" title="CC BY-NC-SA 4.0">${THEME.licenseIcon}</a>`;
}
function createDownloadButton(imgObj) {
  return `<a href="${imgObj.path}" download class="lightbox-download-icon" title="Download image">
    ${THEME.downloadIcon}
  </a>`;
}
function createSourceButton(link) {
  const platform = getPlatformFromUrl(link);
  const icon = THEME[platform + "Icon"] || THEME.genericIcon;
  return `
    <a href="${link}" target="_blank" class="image-source" title="View on ${platform.charAt(0).toUpperCase() + platform.slice(1)}">
      ${icon}
    </a>
  `;
}
function getPlatformFromUrl(url) {
  if (/flickr\.com/.test(url)) return "flickr";
  if (/instagram\.com/.test(url)) return "instagram";
  if (/twitter\.com/.test(url)) return "twitter";
  // Add more platforms as needed
  return "generic";
}

// ===============================
// Masonry Grid & Gallery Rendering
// ===============================
function renderGalleryImage(imgObj) {
  const div = document.createElement('div');
  div.className = 'grid-item';
  div.tabIndex = 0;

  const imageElem = document.createElement('img');
  imageElem.src = imgObj.path;
  imageElem.alt = getImageDisplayTitle(imgObj);

  if (imgObj.width && imgObj.height) {
    imageElem.width = imgObj.width;
    imageElem.height = imgObj.height;
    imageElem.setAttribute('width', imgObj.width);
    imageElem.setAttribute('height', imgObj.height);
    imageElem.loading = 'lazy'; // Enable native lazy loading
    div.style.aspectRatio = `${imgObj.width}/${imgObj.height}`; // Optional
  }

  div.appendChild(imageElem);
  div.appendChild(renderOverlayTop('gallery', imgObj));
  div.appendChild(renderOverlayBottom('gallery', imgObj));

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

  let html = createRowTimePlace(imgObj.taken, imgObj.location);
  html += createTagList(imgObj.tags);

  // For lightbox, add meta row
  if (context === 'lightbox') {
    html += `<div class="lightbox-license-download-bar">
      ${(imgObj.original_link ? createSourceButton(imgObj.original_link) : createDownloadButton(imgObj))}
      ${createLicense("https://creativecommons.org/licenses/by-nc-sa/4.0/")}
    </div>`;
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