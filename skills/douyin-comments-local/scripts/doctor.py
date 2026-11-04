#!/usr/bin/env python3
"""SPDX-License-Identifier: MIT. Local prerequisites only; no browser access."""
import json
import sys
from pathlib import Path


def main():
    for stream in (sys.stdout,sys.stderr):
        if hasattr(stream,'reconfigure'):stream.reconfigure(encoding='utf-8')
    skill=Path(__file__).resolve().parents[1]
    required=['SKILL.md','agents/openai.yaml','scripts/read_comments.js','scripts/export.py',
              'references/browser.md','references/schema.md','references/analysis.md','references/troubleshooting.md']
    missing=[name for name in required if not (skill/name).is_file()]
    result={'python':sys.version.split()[0],'python_ok':sys.version_info>=(3,9),
            'skill_directory':str(skill),'missing_files':missing,
            'browser_connection':'not_checked','douyin_login':'not_checked',
            'next':'In the agent host, discover local Chrome and verify actual page body reading. This local check is not an end-to-end test.'}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0 if result['python_ok'] and not missing else 2


if __name__=='__main__':
    raise SystemExit(main())
