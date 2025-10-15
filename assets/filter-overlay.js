// Enhanced filter logic for multi-category memory, clear buttons, and AND/OR filtering
document.addEventListener("DOMContentLoaded", function() {
  const filterRow = document.querySelector('.filter-row');
  const overlay = document.querySelector('.filter-overlay');
  const overlayHeader = overlay.querySelector('.filter-overlay-header');
  const overlayTitle = overlay.querySelector('.filter-overlay-title');
  const chipsList = overlay.querySelector('.filter-chips-list');
  const cancelBtn = overlay.querySelector('.filter-cancel');
  const applyBtn = overlay.querySelector('.filter-apply');
  const grid = document.querySelector('.grid'); // Change selector if needed

  // Add "Clear All" button to main page
  let clearAllBtn = document.querySelector('.clear-all');
  if (!clearAllBtn) {
    clearAllBtn = document.createElement('span');
    clearAllBtn.className = 'chip chip-date clear-all';
    clearAllBtn.textContent = 'Clear All';
    clearAllBtn.style.marginLeft = '12px';
    filterRow.appendChild(clearAllBtn);
  }

  // Add "Clear Category" button to overlay header
  let clearCategoryBtn = document.querySelector('.clear-category');
  if (!clearCategoryBtn) {
    clearCategoryBtn = document.createElement('span');
    clearCategoryBtn.className = 'chip chip-date clear-category';
    clearCategoryBtn.textContent = 'Clear Filter';
    clearCategoryBtn.style.marginRight = '12px';
    overlayHeader.insertBefore(clearCategoryBtn, cancelBtn);
  }

  let images = [];
  let tags = [];
  let dates = [];
  let places = [];

  // Memory for selections across categories
  let selectedTags = new Set();
  let selectedDates = new Set();
  let selectedPlaces = new Set();

  let filterType = null;
  let overlaySelections = new Set(); // temp for overlay

  // Fetch images.json and extract unique values
  fetch('images.json')
    .then(res => res.json())
    .then(data => {
      const imagesArray = Array.isArray(data) ? data : data.images;
      if (!Array.isArray(imagesArray)) {
        console.error('images.json does not contain an array or images property');
        return;
      }
      images = imagesArray;
      const tagsSet = new Set();
      const datesSet = new Set();
      const placesSet = new Set();
      images.forEach(img => {
        if (img.tags && Array.isArray(img.tags)) {
          img.tags.forEach(tag => tagsSet.add(tag));
        }
        if (img.taken) {
          const yearMatch = img.taken.match(/^(\d{4})/);
          if (yearMatch) datesSet.add(yearMatch[1]);
        }
        if (img.location) placesSet.add(img.location);
      });
      tags = Array.from(tagsSet).sort();
      dates = Array.from(datesSet).sort((a, b) => b - a);
      places = Array.from(placesSet).sort();
      renderGrid(images); // Initial display
    });

  function populateChips(type, values, selectedSet) {
    chipsList.innerHTML = '';
    values.forEach(val => {
      const chip = document.createElement('span');
      chip.className = `chip chip-${type}`;
      chip.textContent = val;
      chip.tabIndex = 0;
      if (selectedSet.has(val)) {
        chip.classList.add('selected');
        overlaySelections.add(val);
      }
      chip.addEventListener('click', () => {
        chip.classList.toggle('selected');
        if (chip.classList.contains('selected')) {
          overlaySelections.add(val);
        } else {
          overlaySelections.delete(val);
        }
      });
      chip.addEventListener('keydown', (e) => {
        if (e.key === ' ' || e.key === 'Enter') chip.click();
      });
      chipsList.appendChild(chip);
    });
  }

  function showOverlay(type) {
    filterType = type;
    overlaySelections = new Set();
    overlay.style.display = 'flex';
    overlayTitle.textContent = `Select ${type.charAt(0).toUpperCase() + type.slice(1)}${type === 'tag' ? 's' : ''}`;
    if (type === 'tag') populateChips('tag', tags, selectedTags);
    if (type === 'date') populateChips('date', dates, selectedDates);
    if (type === 'place') populateChips('place', places, selectedPlaces);
    const firstChip = chipsList.querySelector('.chip');
    if (firstChip) firstChip.focus();
  }

  function hideOverlay() {
    overlay.style.display = 'none';
    chipsList.innerHTML = '';
    overlaySelections.clear();
  }

  // Filter row chip event listeners
  filterRow.querySelector('.chip-date').addEventListener('click', () => showOverlay('date'));
  filterRow.querySelector('.chip-place').addEventListener('click', () => showOverlay('place'));
  filterRow.querySelector('.chip-tag').addEventListener('click', () => showOverlay('tag'));

  cancelBtn.addEventListener('click', hideOverlay);

  // Apply filters from overlay to main memory, then filter images
  applyBtn.addEventListener('click', () => {
    if (filterType === 'tag') selectedTags = new Set(overlaySelections);
    if (filterType === 'date') selectedDates = new Set(overlaySelections);
    if (filterType === 'place') selectedPlaces = new Set(overlaySelections);
    renderGrid(filterImages());
    hideOverlay();
  });

  // Clear All Filters button
  clearAllBtn.addEventListener('click', () => {
    selectedTags.clear();
    selectedDates.clear();
    selectedPlaces.clear();
    renderGrid(images);
  });

  // Clear Category button in overlay
  clearCategoryBtn.addEventListener('click', () => {
    overlaySelections.clear();
    Array.from(chipsList.children).forEach(chip => chip.classList.remove('selected'));
  });

  // AND/OR filtering: inclusive within each category, exclusive between categories
  // E.g., img must match (any selectedTag) AND (any selectedDate) AND (any selectedPlace)
  function filterImages() {
    let filtered = images.filter(img => {
      // Tags: match if no filter, or if at least one selectedTag present
      const tagsOk = selectedTags.size === 0 ||
        (img.tags && Array.from(selectedTags).some(tag => img.tags.includes(tag)));
      // Dates: match if no filter, or if img date in selectedDates
      const dateYear = img.taken && img.taken.match(/^(\d{4})/) ? img.taken.match(/^(\d{4})/)[1] : null;
      const datesOk = selectedDates.size === 0 ||
        (dateYear && selectedDates.has(dateYear));
      // Places: match if no filter, or if img location in selectedPlaces
      const placesOk = selectedPlaces.size === 0 ||
        (img.location && selectedPlaces.has(img.location));
      // Must match all active categories
      return tagsOk && datesOk && placesOk;
    });
    return filtered;
  }

  // Basic grid renderer (replace with your actual rendering logic!)
  function renderGrid(imgs) {
    grid.innerHTML = '';
    imgs.forEach(img => {
      const el = document.createElement('div');
      el.className = 'grid-item';
      el.innerHTML = `<img src="${img.path}" alt="${img.title || ''}" />`;
      grid.appendChild(el);
    });
  }
});