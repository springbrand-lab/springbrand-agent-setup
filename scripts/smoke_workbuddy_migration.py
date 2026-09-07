#!/usr/bin/env python3
"""Isolated native GitHub -> R2 migration evidence; never operates on user config.

Bootstrap uses real GitHub. Migration blocks GitHub with the same controlled
network harness as smoke_workbuddy_r2. Preservation sentinels are synthetic,
not live OAuth credentials; this does not prove OAuth refresh/token validity.
"""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import threading
from http.server import ThreadingHTTPServer
from urllib.parse import urlsplit

from smoke_workbuddy_r2 import CLI_PATHS, HOST, PROFILE, Proxy

PLUGIN = 'springbrand@springbrand'
CONTROL = 'migration-control@migration-control'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + '\n')


def preserved(config):
    settings = read(config / 'settings.json')
    settings.get('enabledPlugins', {}).pop(PLUGIN, None)
    installed = read(config / 'plugins/installed_plugins.json')
    installed['plugins'].pop(PLUGIN, None)
    markets = read(config / 'plugins/known_marketplaces.json')
    markets.pop('springbrand', None)
    return {'settings': settings, 'installed': installed, 'markets': markets,
            'files': {name: digest(config / name) for name in
                      ['mcp.json', 'mcp-approvals.json', '.credentials.json']}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--url', required=True)
    parser.add_argument('--disabled', action='store_true')
    args = parser.parse_args()
    config = args.config.resolve()
    # Fresh directories only: no implicit consent to touch existing installations.
    if config.exists() or config.is_relative_to((Path.home() / '.workbuddy-ai').resolve()):
        raise ValueError('Migration probe requires a new isolated directory')
    parsed = urlsplit(args.url)
    if parsed.scheme != 'https' or parsed.hostname != HOST or not parsed.path.startswith('/releases/'):
        raise ValueError('Use an immutable official R2 release URL')
    manifest = read(args.manifest)
    cli = next(p for p in CLI_PATHS if p.is_file())
    config.mkdir(parents=True)
    env = {k: v for k, v in os.environ.items() if not k.startswith(('AWS_', 'R2_'))}
    env.update(CODEBUDDY_CONFIG_DIR=str(config), DISABLE_TELEMETRY='1')
    env.pop('NODE_OPTIONS', None)
    transcript = []
    guard = []
    server = None
    passed = False

    def run(parts, success=True):
        result = subprocess.run(guard + list(map(str, parts)), cwd=config, env=env,
                                capture_output=True, text=True, timeout=120)
        transcript.append({'command': list(map(str, parts)), 'exit': result.returncode,
                           'stdout': result.stdout, 'stderr': result.stderr})
        if success and (result.returncode or '✘' in result.stdout or '✘' in result.stderr):
            raise RuntimeError(f'Native command failed: {parts}; see isolated transcript')
        return result

    def native(*parts):
        return run([cli, 'plugin', *parts])

    try:
        native('marketplace', 'add', 'springbrand-lab/springbrand-agent-setup')
        native('install', PLUGIN, '--scope', 'user')
        if args.disabled:
            native('disable', PLUGIN, '--scope', 'user')
        old = json.loads(native('list', '--json').stdout)
        assert len(old) == 1 and old[0]['id'] == PLUGIN, old
        assert old[0]['enabled'] == (not args.disabled), old
        markets = read(config / 'plugins/known_marketplaces.json')
        assert markets['springbrand']['type'] == 'github'
        assert markets['springbrand']['source']['repo'] == 'springbrand-lab/springbrand-agent-setup'
        write(config / 'migration-before.json', {'plugins': old, 'markets': markets})

        # Synthetic preservation fixtures. Never read or copy the user's credentials.
        write(config / '.credentials.json', {'migrationProbe': 'not-a-real-token'})
        write(config / 'mcp.json', {'mcpServers': {}})
        write(config / 'mcp-approvals.json', {'migrationProbe': {'approved': True}})
        settings = read(config / 'settings.json')
        settings['migrationProbe'] = {'keep': True}
        settings.setdefault('enabledPlugins', {})[CONTROL] = False
        write(config / 'settings.json', settings)
        control_path = config / 'plugins/cache/migration-control/migration-control/fixture'
        shutil.copytree(old[0]['installPath'], control_path)
        registry = read(config / 'plugins/installed_plugins.json')
        control = copy.deepcopy(registry['plugins'][PLUGIN])
        for entry in control:
            entry['installPath'] = str(control_path)
        registry['plugins'][CONTROL] = control
        write(config / 'plugins/installed_plugins.json', registry)
        markets['migration-control'] = {'type': 'directory',
            'source': {'source': 'directory', 'path': str(control_path)},
            'installLocation': str(control_path), 'autoUpdate': False}
        write(config / 'plugins/known_marketplaces.json', markets)
        before = preserved(config)
        control_hashes = {str(p.relative_to(control_path)): digest(p)
                          for p in control_path.rglob('*') if p.is_file()}

        Proxy.events = []
        server = ThreadingHTTPServer(('127.0.0.1', 0), Proxy)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        proxy = f'http://127.0.0.1:{server.server_port}'
        for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','http_proxy','https_proxy','all_proxy'):
            env[key] = proxy
        env['NO_PROXY'] = env['no_proxy'] = ''
        env['NODE_OPTIONS'] = '--require=' + str(Path(__file__).resolve().parents[1] / 'tests/fixtures/r2_proxy.cjs')
        guard = ['/usr/bin/sandbox-exec', '-p', PROFILE]
        for host in ('github.com','raw.githubusercontent.com','api.github.com','codeload.github.com'):
            assert run(['/usr/bin/curl','-sS','--max-time','8','--proxy',proxy,f'https://{host}'], False).returncode != 0
        assert run(['/usr/bin/curl','-sS','--max-time','3','--noproxy','*','https://1.1.1.1'], False).returncode != 0
        # Verify destination accessibility before the destructive native operations.
        run(['/usr/bin/curl','--fail','--silent','--show-error','--head','--max-time','30',args.url])
        if not args.disabled:
            native('disable', PLUGIN, '--scope', 'user')
        native('uninstall', PLUGIN, '--scope', 'user')
        assert not any(p['id'] == PLUGIN for p in json.loads(native('list','--json').stdout))
        native('marketplace', 'remove', 'springbrand')
        assert 'springbrand' not in read(config / 'plugins/known_marketplaces.json')
        native('marketplace', 'add', args.url)
        native('install', PLUGIN, '--scope', 'user')
        native('disable' if args.disabled else 'enable', PLUGIN, '--scope', 'user')
        final = json.loads(native('list', '--json').stdout)
        target = [p for p in final if p['id'] == PLUGIN]
        assert len(target) == 1 and target[0]['version'] == manifest['version'], final
        assert target[0]['enabled'] == (not args.disabled), final
        installed = Path(target[0]['installPath']).resolve()
        assert installed.is_relative_to(config)
        for name, expected in manifest['files'].items():
            prefix = 'plugins/springbrand-workbuddy/'
            if name.startswith(prefix):
                assert digest(installed / name.removeprefix(prefix)) == expected, name
        after_market = read(config / 'plugins/known_marketplaces.json')['springbrand']
        assert after_market['type'] == 'zip' and after_market['source']['url'] == args.url
        assert preserved(config) == before, 'Unrelated configuration or credential fixture changed'
        assert {str(p.relative_to(control_path)): digest(p)
                for p in control_path.rglob('*') if p.is_file()} == control_hashes
        write(config / 'migration-after.json', {'plugins': final, 'market': after_market,
                                               'preservation': before})
        passed = True
        print('PASS: native GitHub -> R2 migration; GitHub blocked; enabled state, unrelated fixtures and package hashes preserved')
    finally:
        if server:
            server.shutdown()
        write(config / 'migration-evidence.json', {'passed': passed, 'initial_disabled': args.disabled,
                                                  'commands': transcript, 'proxy': Proxy.events})


if __name__ == '__main__':
    main()
