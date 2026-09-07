#!/usr/bin/env python3
"""Publish immutable release objects. Production promotion is a separate gated step."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.request import Request, urlopen

from build_release_package import build, ORIGIN, ROOT, validate_tag
from publish_install_docs import BUCKET, ENDPOINT


def aws(*args, check=True):
    result = subprocess.run(['aws', 's3api', *args, '--bucket', BUCKET,
                             '--endpoint-url', ENDPOINT, '--region', 'auto'],
                            capture_output=True, text=True)
    if check and result.returncode:
        # Never echo environment/credentials or unfiltered upstream errors.
        raise RuntimeError(f'R2 {args[0]} failed (exit {result.returncode})')
    return result


def read_object(key):
    with tempfile.TemporaryDirectory() as temp:
        dest = Path(temp) / 'object'
        result = aws('get-object', '--key', key, str(dest), check=False)
        if result.returncode:
            if '(NoSuchKey)' in result.stderr or '(404)' in result.stderr:
                return None
            raise RuntimeError('Unable to read existing R2 object; refusing to overwrite')
        return dest.read_bytes()


def put(path, key, immutable=True):
    if immutable:
        existing = read_object(key)
        if existing is not None:
            if existing != path.read_bytes():
                raise ValueError(f'Immutable release collision: {key}')
            return
    args = ['put-object', '--key', key, '--body', str(path), '--content-type',
            'application/zip' if key.endswith('.zip') else 'application/json',
            '--cache-control', 'public, max-age=31536000, immutable' if immutable else 'no-store']
    if immutable:
        args.extend(['--if-none-match', '*'])
    aws(*args)


def verify(path, key):
    for attempt in range(5):
        try:
            req = Request(f'{ORIGIN}/{key}', headers={
                'User-Agent': 'SpringBrand-Release-Verifier/1.0', 'Cache-Control': 'no-cache'})
            with urlopen(req, timeout=30) as response:
                if response.read() != path.read_bytes():
                    raise ValueError(f'Public object mismatch: {key}')
            return
        except Exception:
            if attempt == 4:
                raise
            time.sleep(3)


def publish(output, tag, promote=False):
    validate_tag(tag)
    if promote and (os.environ.get('GITHUB_ACTIONS') != 'true' or
                    os.environ.get('GITHUB_REF') != 'refs/heads/main' or
                    os.environ.get('WORKBUDDY_R2_PRODUCTION_ENABLED') != 'true'):
        raise ValueError('Production promotion requires gated Actions on main')
    manifest = json.loads((output / 'manifest.json').read_text())
    data = (output / 'springbrand-workbuddy.zip').read_bytes()
    if manifest['tag'] != tag or manifest['package']['sha256'] != hashlib.sha256(data).hexdigest():
        raise ValueError('Artifact validation failed')
    for name in ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'):
        if not os.environ.get(name):
            raise ValueError(f'Missing {name}')
    for name in ('springbrand-workbuddy.zip', 'manifest.json'):
        key = f'releases/{tag}/workbuddy/{name}'
        put(output / name, key)
        verify(output / name, key)
    if promote:
        # Promotion deliberately remains opt-in until WorkBuddy desktop Native
        # Evidence is recorded. Immutable release downloads work before promotion.
        # One complete ZIP is the native client's source of truth. The JSON is
        # informational; clients must not assume a multi-object atomic switch.
        key = 'channels/production/workbuddy.zip'
        put(output / 'springbrand-workbuddy.zip', key, immutable=False)
        verify(output / 'springbrand-workbuddy.zip', key)
        key = 'channels/production/workbuddy.json'
        put(output / 'manifest.json', key, immutable=False)
        verify(output / 'manifest.json', key)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--publish', action='store_true')
    parser.add_argument('--promote', action='store_true')
    args = parser.parse_args()
    if args.promote and not args.publish:
        parser.error('--promote requires --publish')
    if args.publish and subprocess.check_output(
            ['git', 'status', '--porcelain', '--untracked-files=no'], cwd=ROOT, text=True).strip():
        raise ValueError('Commit tracked changes before publishing')
    with tempfile.TemporaryDirectory() as temp:
        output = Path(temp) / 'release'
        manifest = build(args.tag, output)
        print(json.dumps({k: manifest[k] for k in ('tag', 'host', 'source_commit', 'package')}, indent=2))
        if args.publish:
            publish(output, args.tag, args.promote)
            print('Public release bytes verified' + ('; production promoted' if args.promote else '; production unchanged'))


if __name__ == '__main__':
    main()
