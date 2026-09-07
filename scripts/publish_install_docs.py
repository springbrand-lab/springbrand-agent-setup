#!/usr/bin/env python3
"""Build exact canonical copies; optionally publish with AWS CLI's R2 endpoint."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
FILES = ('INSTALL.md', 'INSTALL.claude.md', 'INSTALL.cursor.md', 'INSTALL.workbuddy.md')
BUCKET = 'springbrand-plugin-distribution'
ORIGIN = 'https://plugin.springbrand.ai'
ENDPOINT = 'https://a046b52313a86ecd2ce47e418d8b0f28.r2.cloudflarestorage.com'


def build(source, output, commit):
    if not re.fullmatch(r'[0-9a-f]{40}', commit):
        raise ValueError('Expected a full source commit SHA')
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output directory must be empty')
    contents = {}
    for name in FILES:
        path = source / name
        if path.is_symlink():
            raise ValueError(f'Symlink is not a canonical document: {name}')
        data = path.read_bytes()
        text = data.decode('utf-8')
        if re.search(r'-dev\.\d+|devconnector\.springbrand\.ai|^## Development install', text, re.M):
            raise ValueError(f'Development installation leaked into {name}')
        for link in re.findall(r'\]\(([^)]+)\)', text):
            url = urlsplit(link)
            if url.scheme or url.netloc or not url.path:
                continue
            if url.path.removeprefix('./') not in FILES:
                raise ValueError(f'Unpublished local link in {name}: {link}')
        contents[name] = data
    output.mkdir(parents=True, exist_ok=True)
    manifest = {'source_commit': commit, 'files': {}}
    for name, data in contents.items():
        (output / name).write_bytes(data)
        manifest['files'][name] = hashlib.sha256(data).hexdigest()
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def verify(output):
    for name in (*FILES, 'manifest.json'):
        expected = (output / name).read_bytes()
        for attempt in range(5):
            try:
                request = Request(f'{ORIGIN}/{name}', headers={
                    'Cache-Control': 'no-cache',
                    # Identify the public verifier honestly; the default Python
                    # user agent receives Cloudflare 1010 on this domain.
                    'User-Agent': 'SpringBrand-Install-Docs-Verifier/1.0',
                })
                with urlopen(request, timeout=20) as response:
                    if response.read() != expected:
                        raise ValueError(f'Published content mismatch: {name}')
                break
            except Exception:
                if attempt == 4:
                    raise
                time.sleep(3)


def publish(output, commit):
    if os.environ.get('GITHUB_REF') != 'refs/heads/main':
        raise ValueError('Production publishing requires GitHub Actions main ref')
    if os.environ.get('GITHUB_ACTIONS') != 'true':
        raise ValueError('Use the GitHub Actions workflow to publish')
    for key in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'):
        if not os.environ.get(key):
            raise ValueError(f'Missing {key}')
    current = subprocess.check_output(['git', 'ls-remote', 'origin', 'refs/heads/main'], text=True).split()[0]
    if current != commit:
        raise ValueError('Stale run: source commit is no longer main HEAD')
    # Child documents first, entry point next, provenance last. Never sync/delete
    # the bucket: releases/ and other future artifacts must remain untouched.
    for name in (*FILES[1:], FILES[0], 'manifest.json'):
        subprocess.run([
            'aws', 's3', 'cp', str(output / name), f's3://{BUCKET}/{name}',
            '--endpoint-url', ENDPOINT, '--region', 'auto', '--no-progress',
            '--cache-control', 'no-store', '--content-type',
            'application/json' if name.endswith('.json') else 'text/markdown; charset=utf-8',
        ], check=True)
    verify(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--publish', action='store_true')
    args = parser.parse_args()
    commit = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    if args.publish and subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip():
        raise ValueError('Refusing to publish modified tracked files')
    with tempfile.TemporaryDirectory() as temp:
        output = args.output or Path(temp) / 'docs'
        manifest = build(ROOT, output, commit)
        print(json.dumps(manifest, indent=2))
        if args.publish:
            publish(output, commit)
            print('Public document verification passed')


if __name__ == '__main__':
    main()
