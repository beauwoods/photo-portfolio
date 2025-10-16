# MeanderingWoods Photo Portfolio

A modern, responsive, and filterable photo portfolio powered by HTML, CSS, and vanilla JavaScript.

## Features

- **Responsive grid gallery** using Masonry layout for optimal photo arrangement.
- **Image overlays** display title, date, location, and tags on hover/focus.
- **Lightbox modal** for viewing images in detail with metadata, download/source links, and licensing info.
- **Advanced filtering:**  
  - Filter images by **date**, **place**, and **tags** with a modal overlay.
  - **Multi-category filtering**: combine date, place, and tag filters using an AND logic across categories, OR logic within each.
  - **Clear** selected filters per category or **Clear All** filters at once.
- **Profile header** with avatar, tagline, and a QR code popup modal for easy sharing.
- **Accessible navigation** and semantic markup.
- **CC BY-NC-SA 4.0 license** for all images.

## Quick Start

1. **Clone the repository:**
   ```sh
   git clone https://github.com/beauwoods/photo-portfolio.git
   cd photo-portfolio
   ```

2. **Add your images and data:**
   - Place image files in the appropriate directory (see `images.json` for structure).
   - Update `images.json` with your photo metadata (title, path, tags, date, location, etc).

3. **Preview locally:**
   Open `index.html` in your web browser. No build step or server required.

## Project Structure

```
.
├── index.html
├── assets/
│   ├── styles.css         # Styles for layout, overlays, lightbox, and filter modal
│   ├── main.js            # All gallery, overlay, lightbox, and filtering logic
│   ├── beau_headshot.jpg  # Profile avatar
│   ├── qr.png             # QR code for sharing
│   └── ...                # Other static assets (icons, etc)
├── images.json            # Your photo data (not included in this repo)
└── README.md
```

## Key Components

- **index.html:**  
  - Loads the navigation, profile header, filter row, gallery grid, filter overlay modal, and lightbox modal.
- **assets/styles.css:**  
  - Theme variables, responsive layout, overlay and modal styles, custom chip designs for tags/places/dates.
- **assets/main.js:**  
  - Image grid rendering using Masonry and imagesLoaded.
  - Overlay rendering for each image.
  - Lightbox modal logic and event handling.
  - QR code popup logic.
  - **Filter logic:** Extracts unique tags, dates, and places from `images.json`, manages selected filters, and updates the grid accordingly.

## Filtering & Overlay Details

- **Filter Row:**  
  - Three filter chips: Dates, Places, Tags. Click to open a modal overlay.
- **Filter Modal Overlay:**  
  - Shows all available chips for the chosen category (dynamically generated from your data).
  - Select chips to filter; you can combine filters across categories.
  - "Clear" button resets current filter category; "Clear All" resets all filters.
- **Gallery Overlays:**  
  - On each image, overlays show the title on top and date/location/tags below.
- **Lightbox Modal:**  
  - Click an image to see it fullscreen with all metadata, download/source options, and licensing.

## Accessibility & Responsive Design

- Focus indicators and accessible modal dialogs.
- Keyboard navigation for overlays and filter chips.
- Scales elegantly from mobile to desktop.

## License

All photos are © [meanderingwoods.com](https://meanderingwoods.com/) and licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

---

**Made with ❤️ by [Beau Woods](https://meanderingwoods.com/).**