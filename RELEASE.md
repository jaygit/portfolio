# Release notes

## v0.2.0 - 2025-12-16

Highlights
- Move visual banner to site header and use `assets/images/bio-bg.png` as the default banner image.
- Ensure header text (`site-name` and `site-tagline`) is visible over the banner.
- Add configurable header and bio image support via template variables `header_image` and `bio_image`.
- Remove bio background by default (biography appears on plain background); bio image can be enabled via template/context.
- Update card sizing and font scale: larger project cards, slightly smaller base font-size for improved density.
- Add `python-dotenv` to `pyproject.toml` dependencies.
- Add placeholder `assets/images/bio-bg.svg` and add header/banner CSS for responsive display.

Notes
- Banner display uses a fixed CSS height of `200px` on desktop and `140px` on small screens. Recommended image aspect ratio is 4:1 (e.g., `1600x400`, `3200x800` for retina).
- To customize the header or bio image when generating the site, set `header_image` or `bio_image` in the template context or configuration used by `src/generate_index.py`.

Full changelog
- See commit history for full file-level changes.
