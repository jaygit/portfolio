"""Configurable logger helper.

Reads `config.yaml` (project root) and configures logging to console and/or
file according to the settings. Provides `get_logger(name)` to obtain a
configured logger instance.
"""
from __future__ import annotations
import logging
import logging.handlers
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import yaml
except Exception:  # pragma: no cover - fallback if PyYAML is not installed
    yaml = None


DEFAULT_CONFIG = {
    'level': 'INFO',
    'console': True,
    'file': None,  # e.g. 'logs/app.log'
}


def _load_config(path: Optional[str]) -> Dict[str, Any]:
    if not path:
        return DEFAULT_CONFIG
    p = Path(path)
    if not p.exists() or yaml is None:
        return DEFAULT_CONFIG
    try:
        with p.open('r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
            cfg = DEFAULT_CONFIG.copy()
            cfg.update({k: v for k, v in data.items() if v is not None})
            return cfg
    except Exception:
        return DEFAULT_CONFIG


def get_logger(name: Optional[str] = None, config_path: Optional[str] = 'config.yaml') -> logging.Logger:
    cfg = _load_config(config_path)
    level_name = str(cfg.get('level', 'INFO')).upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    # Avoid duplicate handlers when called multiple times
    if logger.handlers:
        return logger

    fmt = '%(asctime)s %(levelname)s %(name)s: %(message)s'
    formatter = logging.Formatter(fmt)

    if cfg.get('console'):
        ch = logging.StreamHandler()
        ch.setLevel(level)
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    file_path = cfg.get('file')
    if file_path:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        fh = logging.handlers.RotatingFileHandler(str(p), maxBytes=10_000_00, backupCount=3)
        fh.setLevel(level)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
