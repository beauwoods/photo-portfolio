# Photo Portfolio

A beautiful, responsive photo portfolio website with masonry layout, infinite scroll, and lightbox functionality. Hosted on GitHub Pages.

## Features

- **Masonry Layout**: Beautiful grid layout that adapts to different image sizes
- **Infinite Scroll**: Images load progressively as you scroll down
- **Lightbox**: Click any image to view it in full size with navigation
- **Dark Theme**: Modern dark theme with rounded corners
- **Responsive Design**: Adapts from 1 to 4 columns based on screen size
  - 1 column on mobile (< 480px)
  - 2 columns on small tablets (480px - 767px)
  - 3 columns on tablets (768px - 1199px)
  - 4 columns on desktop (≥ 1200px)
- **Auto-Generated Metadata**: GitHub Action automatically generates images.json when you add photos
- **Metadata Preservation**: Manual edits to image titles and tags are preserved during regeneration

## Quick Start

1. **Add Your Photos**: Upload your images to the `images/` folder
2. **Run the Script**: The GitHub Action will automatically generate `images.json` when you push to main
3. **Deploy**: Enable GitHub Pages in your repository settings (Settings → Pages → Source: main branch)
4. **Visit**: Your portfolio will be live at `https://[username].github.io/photo-portfolio/`

## Manual Setup

If you want to generate `images.json` locally:

```bash
python generate-images-json.py
```

This will:
- Scan the `images/` folder for image files
- Generate `images.json` with metadata
- Preserve any manual edits you've made to titles and tags

## Customizing Image Metadata

Edit `images.json` to add custom titles and tags:

```json
[
  {
    "path": "images/photo1.jpg",
    "title": "Beautiful Sunset",
    "tags": ["nature", "sunset", "landscape"]
  },
  {
    "path": "images/photo2.jpg",
    "title": "City Lights",
    "tags": ["urban", "night", "cityscape"]
  }
]
```

Your custom titles and tags will be preserved when new images are added.

## Testing

Run the test suite to verify the image generation script:

```bash
python test-generate-images-json.py
```

## File Structure

```
photo-portfolio/
├── index.html                      # Main portfolio page
├── images.json                     # Image metadata (auto-generated)
├── generate-images-json.py         # Script to generate images.json
├── test-generate-images-json.py    # Test suite for the generator
├── images/                         # Your photos go here
│   ├── photo1.jpg
│   ├── photo2.jpg
│   └── ...
└── .github/
    └── workflows/
        └── generate-images-json.yml  # GitHub Action workflow
```

## Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)
- BMP (.bmp)
- SVG (.svg)

## GitHub Action

The included GitHub Action (`generate-images-json.yml`) automatically:
1. Triggers when files are added/modified in the `images/` folder
2. Runs `generate-images-json.py` to update `images.json`
3. Preserves your manual edits to titles and tags
4. Commits and pushes the updated `images.json`

You can also manually trigger it from the Actions tab.

## Browser Support

Works on all modern browsers:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers

## Keyboard Shortcuts (Lightbox)

- `←` / `→`: Navigate between images
- `Esc`: Close lightbox

## Technology

Built with plain HTML, CSS, and JavaScript - no frameworks or dependencies required!

## License

MIT License - feel free to use this for your own portfolio!