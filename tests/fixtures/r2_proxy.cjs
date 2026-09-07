// Test-only HTTPS transport bridge. WorkBuddy's ZIP downloader uses https.get
// without honoring HTTPS_PROXY. Route that native request through our local
// allowlist proxy so the OS sandbox can deny all direct Internet connections.
// TLS is end-to-end, hostname/certificate verification is NOT disabled.
const https = require('node:https');
const net = require('node:net');
const tls = require('node:tls');
const proxy = new URL(process.env.HTTPS_PROXY);
class GuardedAgent extends https.Agent {
  createConnection(options, callback) {
    const host = options.host || options.hostname;
    const socket = net.connect(Number(proxy.port), proxy.hostname);
    let headers = Buffer.alloc(0);
    let called = false;
    const fail = (error) => {
      if (called) return;
      called = true;
      socket.destroy();
      callback(error);
    };
    socket.setTimeout(30000, () => fail(new Error('Test proxy timeout')));
    socket.once('error', fail);
    socket.once('connect', () => socket.write(
      `CONNECT ${host}:${options.port || 443} HTTP/1.1\r\nHost: ${host}:${options.port || 443}\r\n\r\n`
    ));
    const onData = (data) => {
      headers = Buffer.concat([headers, data]);
      const end = headers.indexOf('\r\n\r\n');
      if (end < 0) {
        if (headers.length > 16384) fail(new Error('Oversized proxy response'));
        return;
      }
      socket.removeListener('data', onData);
      if (!/^HTTP\/1\.[01] 200 /.test(headers.toString('ascii'))) {
        fail(new Error(`Test proxy denied ${host}`));
        return;
      }
      if (headers.length > end + 4) socket.unshift(headers.subarray(end + 4));
      socket.removeListener('error', fail);
      socket.setTimeout(0);
      called = true;
      callback(null, tls.connect({ ...options, socket, servername: options.servername || host,
                                  rejectUnauthorized: true }));
    };
    socket.on('data', onData);
  }
}
https.globalAgent = new GuardedAgent({keepAlive: false});
