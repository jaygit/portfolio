"""
Simple YAML parser utilities for the projects config.
Prefer using `yaml.safe_load` for robust parsing but helper functions
are provided for compatibility with the original JS behaviour.
"""
import yaml
from typing import List, Dict, Any


def parse_projects_yaml(yaml_text: str) -> List[Dict[str, Any]]:
    """Parse the projects YAML and return a list of project dicts.

    This uses PyYAML to safely load the document and normalizes the
    structure to a list of project dicts (similar output to the JS parser).
    """
    try:
        data = yaml.safe_load(yaml_text) or {}
    except Exception:
        return []

    projects = data.get('projects') if isinstance(data, dict) else []
    if not isinstance(projects, list):
        return []

    # Ensure each project contains keys we expect
    normalized = []
    for p in projects:
        proj = {
            'name': p.get('name'),
            'description': p.get('description', ''),
            'url': p.get('url', ''),
            'classification': p.get('classification', ''),
            'image': p.get('image', ''),
            'language': p.get('language', ''),
            'stars': p.get('stars', 0),
            'forks': p.get('forks', 0),
            'topics': p.get('topics', []) or [],
            'updated_at': p.get('updated_at', '')
        }
        normalized.append(proj)

    return normalized


def load_projects_config(path: str = './projects-config.yaml') -> List[Dict[str, Any]]:
    try:
        with open(path, 'r', encoding='utf8') as f:
            return parse_projects_yaml(f.read())
    except FileNotFoundError:
        return []
    except Exception:
        return []
