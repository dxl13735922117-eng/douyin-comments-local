#!/usr/bin/env python3
"""Install only the bundled skill. No downloads or browser configuration."""
import argparse
import json
import shutil
import sys
from pathlib import Path

NAME = 'douyin-comments-local'


def install(parent):
    source = Path(__file__).resolve().parent / 'skills' / NAME
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Run install.py from the complete extracted source package.')
    if any(p.is_symlink() for p in source.rglob('*')):
        raise ValueError('The skill source must not contain symbolic links.')
    parent = Path(parent).expanduser().resolve()
    target = parent / NAME
    if target.exists() or target.is_symlink():
        raise ValueError(f'Already exists: {target}. Existing skills are never overwritten. Choose another --destination or review the old installation yourself.')
    if parent == source or source in parent.parents:
        raise ValueError('Destination must be outside the bundled skill source.')
    parent.mkdir(parents=True, exist_ok=True)
    # copytree fails rather than merging if another process creates target.
    shutil.copytree(source, target, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    return target


def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, default=Path.home()/'.agents'/'skills',
                        help='Parent skill directory (default: ~/.agents/skills).')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    if sys.version_info < (3, 9):
        parser.error('Python 3.9+ is required.')
    if args.dry_run:
        print(json.dumps({'destination':str(args.destination.expanduser().resolve()/NAME),'writes':False},ensure_ascii=False))
        return 0
    try:
        target = install(args.destination)
    except (ValueError, OSError) as exc:
        print(f'Install failed: {exc}', file=sys.stderr)
        return 2
    print(json.dumps({'installed':str(target),'invoke':'$'+NAME,
                      'next':'Enable local Chrome browser control in your host; sign in to Douyin. If the skill is missing, restart the host.'},ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
