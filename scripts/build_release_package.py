#!/usr/bin/env python3
"""Build a deterministic, self-contained WorkBuddy ZIP from an immutable prod tag."""
import argparse
import hashlib
import io
import json
from pathlib import Path
import re
import stat
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ORIGIN = 'https://plugin.springbrand.ai'
PREFIX = 'plugins/springbrand-workbuddy'
SKILLS = ('ask-springbrand', 'springbrand-platform', 'springbrand-action-api', 'springbrand-connector', 'springbrand-gtm')
TAG_PATTERN = r'v\d+\.\d+\.\d+(?:-(?:alpha|beta|rc)\.\d+)?'


def validate_tag(tag):
    if not re.fullmatch(TAG_PATTERN, tag):
        raise ValueError('Expected a production version tag (no dev marker)')


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT)


def release_files(tag):
    validate_tag(tag)
    ref = f'refs/tags/{tag}'
    commit = git('rev-parse', f'{ref}^{{commit}}').decode().strip()
    raw = git('archive', '--format=tar', ref)
    files = {}
    with tarfile.open(fileobj=io.BytesIO(raw)) as archive:
        for item in archive:
            if item.isfile():
                files[item.name] = (archive.extractfile(item).read(), item.mode)
            elif not item.isdir():
                # Reject tracked symlinks, including links outside the package.
                raise ValueError(f'Non-regular release asset: {item.name}')
    return commit, files


def package_files(files, tag):
    validate_tag(tag)
    if files['VERSION'][0].decode().strip() != tag[1:]:
        raise ValueError('Tag and VERSION disagree')
    marketplace = json.loads(files['.codebuddy-plugin/marketplace.json'][0])
    if marketplace['name'] != 'springbrand' or len(marketplace['plugins']) != 1:
        raise ValueError('Expected one production Marketplace entry')
    entry = marketplace['plugins'][0]
    if entry['name'] != 'springbrand' or entry['source'] != f'./{PREFIX}':
        raise ValueError('Marketplace must use the bundled relative Plugin source')
    plugin = json.loads(files[f'{PREFIX}/.workbuddy-plugin/plugin.json'][0])
    if plugin['name'] != 'springbrand' or plugin['version'] != tag[1:]:
        raise ValueError('Plugin identity/version does not match production tag')
    for key, expected in [('skills', './skills/'), ('hooks', './hooks/hooks.json'), ('mcpServers', './.mcp.json')]:
        if plugin.get(key) != expected:
            raise ValueError(f'Unsupported non-local Plugin {key}')
    mcp = json.loads(files[f'{PREFIX}/.mcp.json'][0])
    if mcp != {'mcpServers': {'springbrand': {'type': 'http', 'url': 'https://connector.springbrand.ai/mcp'}}}:
        raise ValueError('Expected only the production MCP entry, without credentials')
    hooks = json.loads(files[f'{PREFIX}/hooks/hooks.json'][0])
    if hooks != {'hooks': {'UserPromptSubmit': [{'hooks': [{'type': 'command', 'command': '${CODEBUDDY_PLUGIN_ROOT}/hooks/user-prompt-submit'}]}]}}:
        raise ValueError('Unexpected Hook registration')
    selected = {'.codebuddy-plugin/marketplace.json': files['.codebuddy-plugin/marketplace.json']}
    for name, value in files.items():
        if name.startswith(f'{PREFIX}/'):
            selected[name] = value
    for name, (data, mode) in selected.items():
        if any(marker in data for marker in (b'springbrand-dev', b'devconnector.springbrand.ai', b'SpringBrand Dev')):
            raise ValueError(f'Development identity in {name}')
        if name.startswith(f'{PREFIX}/skills/'):
            canonical = name.removeprefix(f'{PREFIX}/')
            if canonical not in files or files[canonical][0] != data:
                raise ValueError(f'Distribution Mirror drift: {name}')
    canonical_skills = {name for name in files if name.startswith('skills/')}
    mirrored_skills = {name.removeprefix(f'{PREFIX}/') for name in selected if name.startswith(f'{PREFIX}/skills/')}
    if canonical_skills != mirrored_skills:
        raise ValueError('Incomplete Skill Distribution Mirror')
    for skill in SKILLS:
        if f'{PREFIX}/skills/{skill}/SKILL.md' not in selected:
            raise ValueError(f'Missing Canonical Skill: {skill}')
    hook = selected[f'{PREFIX}/hooks/user-prompt-submit']
    if hook[0] != files['hooks/user-prompt-submit'][0] or not hook[1] & 0o111:
        raise ValueError('Hook drift or missing executable permission')
    for name in ('LICENSE', 'VERSION'):
        if name in files:
            selected[name] = files[name]
    return selected


def build(tag, output):
    if output.exists() and any(output.iterdir()):
        raise ValueError('Output must be empty')
    commit, files = release_files(tag)
    selected = package_files(files, tag)
    output.mkdir(parents=True, exist_ok=True)
    package = output / 'springbrand-workbuddy.zip'
    # ZIP_STORED makes the bytes reproducible across Python/zlib versions. The
    # entire package is small. A single root also matches native ZIP extraction.
    with zipfile.ZipFile(package, 'w', compression=zipfile.ZIP_STORED) as archive:
        for name, (data, mode) in sorted(selected.items()):
            item = zipfile.ZipInfo(f'springbrand/{name}', date_time=(1980, 1, 1, 0, 0, 0))
            item.create_system = 3
            item.external_attr = (stat.S_IFREG | (0o755 if mode & 0o111 else 0o644)) << 16
            archive.writestr(item, data)
    data = package.read_bytes()
    manifest = {
        'schema_version': 1, 'host': 'workbuddy', 'tag': tag,
        'version': tag[1:], 'source_commit': commit,
        'package': {'url': f'{ORIGIN}/releases/{tag}/workbuddy/{package.name}',
                    'sha256': hashlib.sha256(data).hexdigest(), 'size': len(data)},
        'files': {name: hashlib.sha256(data).hexdigest() for name, (data, _) in sorted(selected.items())},
    }
    (output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tag', required=True)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    print(json.dumps(build(args.tag, args.output), indent=2))


if __name__ == '__main__':
    main()
