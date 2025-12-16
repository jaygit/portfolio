#!/usr/bin/env python3
"""
Generate a static `index.html` from GitHub public repositories.
Usage: set `GITHUB_TOKEN` and optionally `GITHUB_USERNAME`, then run `python generate_index.py`.
This script fetches public repos, writes `projects-config.yaml`, and renders `index.html` via Jinja2.
"""
import os
import sys
import yaml
from datetime import datetime
try:
    # Newer PyGithub exposes Auth for token-based auth
    from github import Github, Auth  # type: ignore
except Exception:
    from github import Github  # type: ignore

# Load environment variables from a .env file when present
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    # dotenv is optional; continue if not installed
    pass

# Try to import the project's logger helper
try:
    from src.logger import get_logger
except Exception:
    try:
        from logger import get_logger
    except Exception:
        def get_logger(name=None, config_path='config.yaml'):
            import logging
            return logging.getLogger(name)

logger = get_logger(__name__)

# Configuration
GITHUB_USERNAME = os.environ.get('GITHUB_USERNAME', 'jaygit')
CONFIG_FILE = './projects-config.yaml'

animals = [
    '🦁', '🐯', '🐻', '🐼', '🐨', '🐵', '🐶', '🐺', '🦊', '🦝',
    '🐱', '🦁', '🐴', '🦄', '🦓', '🦌', '🐮', '🐷', '🐗', '🐭',
    '🐹', '🐰', '🐇', '🐿️', '🦔', '🦇', '🐻‍❄️', '🐨', '🐼', '🦥',
    '🦦', '🦨', '🦘', '🦡', '🐾', '🦃', '🐔', '🐓', '🐣', '🐤',
    '🐥', '🐦', '🐧', '🕊️', '🦅', '🦆', '🦢', '🦉', '🦤', '🪶',
    '🦩', '🦚', '🦜', '🐸', '🐊', '🐢', '🦎', '🐍', '🐲', '🐉',
    '🦕', '🦖', '🐳', '🐋', '🐬', '🦭', '🐟', '🐠', '🐡', '🦈',
    '🐙', '🐚', '🪸', '🐌', '🦋', '🐛', '🐝', '🪲', '🐞', '🦗',
    '🕷️', '🦂', '🦟', '🪰', '🪱', '🦠'
]


def get_animal_for_project(project_name: str) -> str:
    """Return a consistent animal emoji for a project name."""
    h = 0
    for ch in project_name:
        h = ((h << 5) - h) + ord(ch)
        h = h & 0xFFFFFFFF
    index = abs(h) % len(animals)
    return animals[index]


def get_auto_classification(repo) -> str:
    """Decide whether a repo should be classified as 'training' or 'project'."""
    name = (getattr(repo, 'name', '') or '').lower()
    description = (getattr(repo, 'description', '') or '').lower()
    try:
        topics = repo.get_topics() if hasattr(repo, 'get_topics') else []
    except Exception:
        topics = []

    training_keywords = [
        'tutorial', 'course', 'learning', 'practice', 'exercise',
        'training', 'workshop', 'lesson', 'bootcamp', 'skill',
        'learn', 'study', 'example', 'sample', 'demo'
    ]

    for keyword in training_keywords:
        if keyword in name:
            return 'training'
    for keyword in training_keywords:
        if keyword in description:
            return 'training'
    for topic in topics:
        for keyword in training_keywords:
            if keyword in topic.lower():
                return 'training'

    # Low-engagement fork heuristic
    is_fork = getattr(repo, 'fork', False)
    stars = getattr(repo, 'stargazers_count', 0)
    if is_fork and stars == 0 and not description:
        return 'training'

    return 'project'


def fetch_github_repos(username: str):
    token = os.environ.get('GITHUB_TOKEN')
    # Use modern auth=Auth.Token(...) when available to avoid deprecation warnings
    try:
        if token and 'Auth' in globals():
            gh = Github(auth=Auth.Token(token))
        else:
            gh = Github(token) if token else Github()
    except Exception:
        # Fallback for older PyGithub versions
        gh = Github(token) if token else Github()

    try:
        user = gh.get_user(username)
        # Get up to 100 most recently updated public repos
        repos = []
        for i, repo in enumerate(user.get_repos(type='public')):
            repos.append(repo)
            if i >= 99:
                break
        # Return both the user object and the repo list so callers can access profile fields
        return user, repos
    except Exception as e:
        logger.error('Error fetching GitHub repositories: %s', e)
        raise


def load_existing_config(path: str):
    if not os.path.exists(path):
        return {'projects': []}
    try:
        with open(path, 'r', encoding='utf8') as f:
            return yaml.safe_load(f) or {'projects': []}
    except Exception:
        return {'projects': []}


def generate_index():
    logger.info('Fetching repositories from GitHub for user: %s', GITHUB_USERNAME)
    user, repos = fetch_github_repos(GITHUB_USERNAME)
    public_repos = [r for r in repos if not getattr(r, 'private', False)]
    logger.info('Found %d public repositories', len(public_repos))

    existing = load_existing_config(CONFIG_FILE)
    existing_map = {p.get('name'): p for p in existing.get('projects', [])}

    # Merge fetched metadata with existing config while preserving manual fields
    new_projects = []
    for repo in public_repos:
        existing_proj = existing_map.get(repo.name, {}) or {}
        try:
            topics = repo.get_topics() if hasattr(repo, 'get_topics') else []
        except Exception:
            topics = []

        classification = existing_proj.get('classification') or get_auto_classification(repo)
        image = existing_proj.get('image') or get_animal_for_project(repo.name)

        # Start with preserved fields from existing, then update standard metadata
        proj = dict(existing_proj)
        proj.update({
            'name': repo.name,
            'description': repo.description or '',
            'url': getattr(repo, 'html_url', ''),
            'classification': classification,
            'image': image,
            'language': getattr(repo, 'language', 'Unknown') or 'Unknown',
            'stars': getattr(repo, 'stargazers_count', 0) or 0,
            'forks': getattr(repo, 'forks_count', 0) or 0,
            'topics': topics or [],
            'updated_at': getattr(repo, 'updated_at', '').isoformat() if getattr(repo, 'updated_at', None) else ''
        })
        new_projects.append(proj)

    # Sort by updated_at desc
    new_projects.sort(key=lambda x: x.get('updated_at') or '', reverse=True)

    config = {'projects': new_projects}

    # Ensure assets/images directory exists for generated logos
    images_dir = os.path.join(os.getcwd(), 'assets', 'images')
    os.makedirs(images_dir, exist_ok=True)

    def _slug(name: str) -> str:
        # simple slug for filenames
        return ''.join(c if c.isalnum() else '-' for c in name).lower()

    def _color_from_name(name: str) -> str:
        # deterministic color from name (hue based)
        h = 0
        for ch in name:
            h = (h * 31 + ord(ch)) & 0xFFFFFFFF
        hue = h % 360
        return f'hsl({hue} 80% 50%)'

    def _initials(name: str, limit: int = 2) -> str:
        parts = [p for p in name.replace('-', ' ').split() if p]
        if not parts:
            return name[:limit].upper()
        if len(parts) == 1:
            return parts[0][:limit].upper()
        return ''.join(p[0] for p in parts[:limit]).upper()

    # Generate a small SVG logo per project and set p['logo'] path
    for p in new_projects:
        safe = _slug(p.get('name') or 'proj')
        logo_path = os.path.join('assets', 'images', f'{safe}.svg')
        full_path = os.path.join(os.getcwd(), logo_path)
        initials = _initials(p.get('name') or '')
        color = _color_from_name(p.get('name') or '')
        svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 64 64" role="img" aria-label="{p.get('name')}">
  <rect width="100%" height="100%" rx="10" fill="{color}" />
  <text x="50%" y="50%" dominant-baseline="middle" text-anchor="middle" font-family="Inter, system-ui, -apple-system, sans-serif" font-size="24" fill="#ffffff">{initials}</text>
</svg>'''
        try:
            with open(full_path, 'w', encoding='utf8') as fh:
                fh.write(svg)
            p['logo'] = logo_path
        except Exception:
            # fallback to emoji image/data URL could be used; keep existing image
            p['logo'] = ''

    yaml_str = yaml.dump(config, sort_keys=False, allow_unicode=True)

    header = f"""# Projects Configuration
# This file is dynamically updated with all public repositories from GitHub
# You can manually edit the 'classification' field for each project
# Classification options: training, project
# The 'image' field is automatically generated based on the project name (animal emoji)
#
# To update this file, run: python generate_index.py
#
# Last updated: {datetime.utcnow().isoformat()}\n\n"""

    try:
        with open(CONFIG_FILE, 'w', encoding='utf8') as f:
            f.write(header)
            f.write(yaml_str)

        logger.info('Config file updated successfully: %s', CONFIG_FILE)
        logger.info('Total projects: %d', len(new_projects))
        logger.info('Training: %d', len([p for p in new_projects if p.get('classification') == 'training']))
        logger.info('Projects: %d', len([p for p in new_projects if p.get('classification') == 'project']))
    except Exception as e:
        logger.error('Failed to write config file: %s', e)
        raise

    # Server-side render index.html from templates/index.j2 if Jinja2 is available
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape
    except Exception:
        logger.debug('Jinja2 not installed; skipping HTML render')
        return

    try:
        templates_dir = os.path.join(os.getcwd(), 'templates')
        env = Environment(
            loader=FileSystemLoader(templates_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )
        tmpl = env.get_template('index.j2')

        # Prefer the GitHub profile name for the site title; fall back to env or login
        site_name = getattr(user, 'name', None) or os.environ.get('SITE_NAME') or getattr(user, 'login', 'Your Name')
        site_tagline = os.environ.get('SITE_TAGLINE', 'Developer • Designer • Builder')
        # Prefer the GitHub profile bio when available, fallback to SITE_BIO env or a default string
        site_bio = (getattr(user, 'bio', None) or os.environ.get('SITE_BIO') or
                'Hi — I build small web apps, experiment with design, and open-source useful utilities. This site is a minimal static scaffold you can customise.')

        # Group projects by classification for the template
        projects_by_class = {}
        for p in new_projects:
            cls = p.get('classification') or 'project'
            projects_by_class.setdefault(cls, []).append(p)

        rendered = tmpl.render(
            projects_by_class=projects_by_class,
            site_name=site_name,
            site_tagline=site_tagline,
            site_bio=site_bio,
        )

        out_path = os.path.join(os.getcwd(), 'index.html')
        with open(out_path, 'w', encoding='utf8') as fh:
            fh.write(rendered)

        logger.info('Rendered static site to %s', out_path)
    except Exception as e:
        logger.error('Failed to render index.html: %s', e)


if __name__ == '__main__':
    try:
        generate_index()
    except Exception as e:
        logger.exception('Failed to generate index: %s', e)
        sys.exit(1)
