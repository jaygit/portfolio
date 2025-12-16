<!-- Purpose: Project description and quick local preview instructions -->
# github-web

Minimal static personal site for showcasing public GitHub repositories and projects.

Quick local preview
- Serve the repository root and open http://localhost:8000:

```bash
python3 -m http.server 8000
```

Install dependencies
- If you use `uv` to manage your environment, run:

```bash
uv sync
```

- As an alternative, install with `pip` (if not using `uv`):

```bash
pip install python-dotenv PyGithub PyYAML
```

GitHub Pages
- This repo includes a GitHub Actions workflow at [.github/workflows/pages.yml](.github/workflows/pages.yml) that uploads the repository contents and deploys them to GitHub Pages on pushes to the `main` branch. To publish, push your changes to `main` and the workflow will deploy automatically.

License
- This site is released under the MIT License (see `LICENSE`).
