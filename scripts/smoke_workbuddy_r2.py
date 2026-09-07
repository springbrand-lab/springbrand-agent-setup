#!/usr/bin/env python3
"""macOS native ZIP lifecycle probe: only the R2 distribution host is reachable.

Runs in an explicitly isolated config, not the user's WorkBuddy config. The
sandbox blocks direct networking; an allowlisted CONNECT proxy permits only R2.
No OAuth or model request is performed. A zero exit requires registry + assets,
not merely the CLI's success text.
"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import select
import socket
import subprocess
import threading
from urllib.parse import urlsplit

HOST = 'plugin.springbrand.ai'
CLI_PATHS = [Path('/Applications/WorkBuddy AI.app/Contents') / part / 'app.asar.unpacked/cli/bin/codebuddy'
             for part in ('Resources', 'Plugins')]
PROFILE = '''(version 1)
(allow default)
(deny network*)
(allow network-outbound (remote ip "127.0.0.1:*"))
(allow network* (local unix-socket) (remote unix-socket))
'''


class Proxy(BaseHTTPRequestHandler):
    events = []
    def log_message(self, *args): pass
    def do_CONNECT(self):
        allowed = self.path.lower() == f'{HOST}:443'
        self.events.append({'target': self.path, 'allowed': allowed})
        if not allowed:
            self.send_error(403, 'Only the R2 distribution host is allowed'); return
        try:
            with socket.create_connection((HOST, 443), timeout=20) as upstream:
                self.send_response(200, 'Connection established'); self.end_headers()
                sockets = [self.connection, upstream]
                while True:
                    ready, _, _ = select.select(sockets, [], [], 35)
                    if not ready: return
                    for src in ready:
                        data = src.recv(65536)
                        if not data: return
                        (upstream if src is self.connection else self.connection).sendall(data)
        except (OSError, TimeoutError):
            return


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', required=True, type=Path)
    parser.add_argument('--url', required=True)
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--remove', action='store_true')
    args = parser.parse_args()
    if urlsplit(args.url).hostname != HOST or urlsplit(args.url).scheme != 'https':
        raise ValueError('Use the official R2 HTTPS origin')
    config = args.config.resolve()
    marker = config / '.springbrand-isolated-probe'
    if config == (Path.home()/'.workbuddy-ai').resolve() or (config.exists() and not marker.exists()):
        raise ValueError('Refusing a real or unowned config directory')
    config.mkdir(parents=True, exist_ok=True); marker.touch()
    cli = next((p for p in CLI_PATHS if p.is_file()), None)
    if cli is None: raise ValueError('WorkBuddy native CLI not found')
    manifest = json.loads(args.manifest.read_text())
    server = ThreadingHTTPServer(('127.0.0.1', 0), Proxy)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    env = os.environ.copy()
    proxy = f'http://127.0.0.1:{server.server_port}'
    for name in ('HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'http_proxy', 'https_proxy', 'all_proxy'): env[name] = proxy
    for name in ('NO_PROXY', 'no_proxy'): env[name] = ''
    env['CODEBUDDY_CONFIG_DIR'] = str(config)
    env['DISABLE_TELEMETRY'] = '1'
    sandbox = ['/usr/bin/sandbox-exec', '-p', PROFILE]
    transcript = []

    def run(cmd, success=True):
        result = subprocess.run(sandbox + list(map(str, cmd)), cwd=config, env=env,
                                capture_output=True, text=True, timeout=120)
        transcript.append({'command': list(map(str, cmd)), 'exit': result.returncode,
                           'stdout': result.stdout, 'stderr': result.stderr})
        print(result.stdout.strip())
        if success and result.returncode:
            raise RuntimeError(f'Command failed: {cmd}; {result.stderr[-1500:]}')
        return result

    try:
        for host in ('github.com', 'raw.githubusercontent.com', 'api.github.com', 'codeload.github.com'):
            result = run(['/usr/bin/curl', '--silent', '--show-error', '--max-time', '8', '--proxy', proxy, f'https://{host}'], success=False)
            if result.returncode == 0: raise AssertionError(f'GitHub was reachable: {host}')
        # Prove that a client ignoring the proxy cannot bypass the guard either.
        result = run(['/usr/bin/curl', '--silent', '--max-time', '3', '--noproxy', '*', 'https://1.1.1.1'], success=False)
        if result.returncode == 0: raise AssertionError('Direct network bypass succeeded')
        run(['/usr/bin/curl', '--fail', '--silent', '--show-error', '--head', '--max-time', '30', '--proxy', proxy, args.url])
        existing = json.loads(run([cli, 'plugin', 'marketplace', 'list']).stdout)
        if any(m['name'] == 'springbrand' for m in existing):
            run([cli, 'plugin', 'marketplace', 'update', 'springbrand'])
            run([cli, 'plugin', 'update', 'springbrand@springbrand', '--scope', 'user'])
        else:
            run([cli, 'plugin', 'marketplace', 'add', args.url])
            run([cli, 'plugin', 'install', 'springbrand@springbrand', '--scope', 'user'])
        run([cli, 'plugin', 'enable', 'springbrand@springbrand', '--scope', 'user'])
        listed = json.loads(run([cli, 'plugin', 'list', '--json']).stdout)
        plugins = [p for p in listed if p['id'] == 'springbrand@springbrand']
        assert len(plugins) == 1 and plugins[0]['enabled'], plugins
        assert plugins[0]['version'] == manifest['version'], plugins
        installed = Path(plugins[0]['installPath'])
        assert installed.is_relative_to(config), installed
        for name, digest in manifest['files'].items():
            prefix = 'plugins/springbrand-workbuddy/'
            if name.startswith(prefix):
                path = installed / name.removeprefix(prefix)
                assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, name
        assert os.access(installed/'hooks/user-prompt-submit', os.X_OK), 'Hook not executable'
        if args.remove:
            run([cli, 'plugin', 'disable', 'springbrand@springbrand', '--scope', 'user'])
            run([cli, 'plugin', 'uninstall', 'springbrand@springbrand', '--scope', 'user'])
            listed = json.loads(run([cli, 'plugin', 'list', '--json']).stdout)
            assert not any(p['id']=='springbrand@springbrand' for p in listed), listed
            run([cli, 'plugin', 'marketplace', 'remove', 'springbrand'])
        print('PASS: GitHub blocked; native R2 lifecycle and installed asset hashes verified.')
    finally:
        server.shutdown()
        (config/'r2-smoke-evidence.json').write_text(json.dumps({'commands': transcript, 'proxy': Proxy.events}, indent=2)+'\n')


if __name__ == '__main__': main()
