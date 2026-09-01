#!/usr/bin/env python3
"""Build the dev Plugin variant from production manifests.

Rewrites Plugin identity, the three MCP Domain Entries, the Claude hook
namespace, and every version field from production (springbrand /
connector.springbrand.ai) to development (springbrand-dev /
devconnector.springbrand.ai). Run on a dev release branch only. The rewrite
is deterministic and idempotent; it fails loudly when an expected production
pattern is missing.
"""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ENTRY_NAMES = {
    "springbrand-platform": "springbrand-dev-platform",
    "springbrand-action-api": "springbrand-dev-action-api",
    "springbrand-connector": "springbrand-dev-connector",
}
PROD_URL = "https://connector.springbrand.ai/mcp/"
DEV_URL = "https://devconnector.springbrand.ai/mcp/"
PROD_NAME = "springbrand"
DEV_NAME = "springbrand-dev"
PROD_DISPLAY_NAME = "SpringBrand"
DEV_DISPLAY_NAME = "SpringBrand Dev"
PROD_DESCRIPTION = "Discover and use SpringBrand Plugins through the production connector."
DEV_DESCRIPTION = "Discover and use SpringBrand Plugins through the development connector. Internal testing only."
PROD_PACKAGE_DESCRIPTION = "Discover and use SpringBrand Plugins through the production connector"
DEV_PACKAGE_DESCRIPTION = "Discover and use SpringBrand Plugins through the development connector. Internal testing only."
PROD_SHORT_DESCRIPTION = "Discover and use SpringBrand Plugins"
DEV_SHORT_DESCRIPTION = "Test SpringBrand Plugins"
PROD_LONG_DESCRIPTION = "Search for reusable SpringBrand Plugins and apply them to your work through the production connector."
DEV_LONG_DESCRIPTION = "Search for reusable SpringBrand Plugins and apply them through the development connector. Internal testing only."
PROD_DEFAULT_PROMPT = "Find a SpringBrand Plugin for this task."
DEV_DEFAULT_PROMPT = "Find a SpringBrand Plugin using the development environment."
PROD_CURSOR_METADATA = "SpringBrand Plugin Discovery for Cursor"
DEV_CURSOR_METADATA = "SpringBrand Plugin Discovery through the development connector"
PROD_MARKETPLACE = "SpringBrand plugins for discovering and using reusable Plugins."
DEV_MARKETPLACE = "SpringBrand development Plugin for internal Plugin testing."


def fail(message):
    raise SystemExit(f"build_dev_variant: {message}")


def dev_value(value, prod, dev, where):
    if value == prod:
        return dev
    if value == dev:
        return value
    fail(f"{where}: unexpected {value!r} (expected {prod!r} or the already-dev form)")


def dev_name(value, where):
    return dev_value(value, PROD_NAME, DEV_NAME, where)


def read_json(path):
    return json.loads(path.read_text())


def write_json(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def dev_server_name(name, where):
    if name in ENTRY_NAMES or name in ENTRY_NAMES.values():
        return ENTRY_NAMES.get(name, name)
    fail(f"{where}: unexpected MCP entry {name!r}")


def dev_server_url(url, where):
    if url.startswith(PROD_URL):
        return DEV_URL + url[len(PROD_URL):]
    if url.startswith(DEV_URL):
        return url
    fail(f"{where}: unexpected MCP url {url!r}")


def dev_mcp_servers(path, servers):
    dev = {}
    for name, entry in servers.items():
        where = f"{path}: mcpServers[{name!r}]"
        if "url" not in entry:
            fail(f"{where}: missing url")
        entry = dict(entry)
        entry["url"] = dev_server_url(entry["url"], where)
        dev[dev_server_name(name, where)] = entry
    return dev


def rewrite_mcp_manifest(path):
    data = read_json(path)
    data["mcpServers"] = dev_mcp_servers(path, data["mcpServers"])
    write_json(path, data)


def rewrite_claude_plugin(path, version):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["version"] = version
    data["description"] = dev_value(data["description"], PROD_DESCRIPTION, DEV_DESCRIPTION, f"{path} description")
    data["mcpServers"] = dev_mcp_servers(path, data["mcpServers"])
    write_json(path, data)


def rewrite_codex_plugin(path, version):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["version"] = version
    data["description"] = dev_value(data["description"], PROD_DESCRIPTION, DEV_DESCRIPTION, f"{path} description")
    interface = data["interface"]
    interface["displayName"] = dev_value(interface["displayName"], PROD_DISPLAY_NAME, DEV_DISPLAY_NAME, f"{path} interface.displayName")
    interface["shortDescription"] = dev_value(interface["shortDescription"], PROD_SHORT_DESCRIPTION, DEV_SHORT_DESCRIPTION, f"{path} interface.shortDescription")
    interface["longDescription"] = dev_value(interface["longDescription"], PROD_LONG_DESCRIPTION, DEV_LONG_DESCRIPTION, f"{path} interface.longDescription")
    interface["defaultPrompt"] = [
        dev_value(prompt, PROD_DEFAULT_PROMPT, DEV_DEFAULT_PROMPT, f"{path} interface.defaultPrompt")
        for prompt in interface["defaultPrompt"]
    ]
    write_json(path, data)


def rewrite_cursor_plugin(path, version):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["displayName"] = dev_value(data["displayName"], PROD_DISPLAY_NAME, DEV_DISPLAY_NAME, f"{path} displayName")
    data["version"] = version
    data["description"] = dev_value(data["description"], PROD_DESCRIPTION, DEV_DESCRIPTION, f"{path} description")
    if "dev" not in data["keywords"]:
        data["keywords"].append("dev")
    write_json(path, data)


def rewrite_workbuddy_plugin(path, version):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["version"] = version
    data["description"] = dev_value(data["description"], PROD_DESCRIPTION, DEV_DESCRIPTION, f"{path} description")
    write_json(path, data)


def rewrite_agents_marketplace(path):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["interface"]["displayName"] = dev_value(data["interface"]["displayName"], PROD_DISPLAY_NAME, DEV_DISPLAY_NAME, f"{path} interface.displayName")
    data["plugins"][0]["name"] = dev_name(data["plugins"][0]["name"], f"{path} plugins[0].name")
    write_json(path, data)


def rewrite_claude_marketplace(path):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["plugins"][0]["name"] = dev_name(data["plugins"][0]["name"], f"{path} plugins[0].name")
    data["description"] = dev_value(data["description"], PROD_MARKETPLACE, DEV_MARKETPLACE, f"{path} description")
    write_json(path, data)


def rewrite_codebuddy_marketplace(path):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    plugin = data["plugins"][0]
    plugin["name"] = dev_name(plugin["name"], f"{path} plugins[0].name")
    plugin["description"] = dev_value(plugin["description"], PROD_PACKAGE_DESCRIPTION, DEV_PACKAGE_DESCRIPTION, f"{path} plugins[0].description")
    write_json(path, data)


def rewrite_cursor_marketplace(path, version):
    data = read_json(path)
    data["name"] = dev_name(data["name"], f"{path} name")
    data["metadata"]["description"] = dev_value(data["metadata"]["description"], PROD_CURSOR_METADATA, DEV_CURSOR_METADATA, f"{path} metadata.description")
    data["metadata"]["version"] = version
    plugin = data["plugins"][0]
    plugin["name"] = dev_name(plugin["name"], f"{path} plugins[0].name")
    plugin["description"] = dev_value(plugin["description"], PROD_PACKAGE_DESCRIPTION, DEV_PACKAGE_DESCRIPTION, f"{path} plugins[0].description")
    plugin["version"] = version
    write_json(path, data)


def rewrite_hook(path):
    text = path.read_text()
    if "`/springbrand:" in text:
        count = text.count("`/springbrand:")
        if count != 1:
            fail(f"{path}: expected exactly one Claude namespace reference, found {count}")
        text = text.replace("`/springbrand:", "`/springbrand-dev:")
    elif "`/springbrand-dev:" not in text:
        fail(f"{path}: no Claude namespace reference found")
    path.write_text(text)


def rewrite_workflow(path):
    text = path.read_text()
    text = text.replace('"springbrand"', '"springbrand-dev"')
    text = text.replace(
        "codex plugin add springbrand --marketplace springbrand",
        "codex plugin add springbrand-dev --marketplace springbrand-dev",
    )
    if '== "springbrand-dev",' not in text or "codex plugin add springbrand-dev" not in text:
        fail(f"{path}: dev smoke assertions missing after rewrite")
    if '== "springbrand",' in text or "plugin add springbrand --marketplace" in text:
        fail(f"{path}: leftover production assertions")
    path.write_text(text)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--version", required=True, help="dev version for VERSION and every manifest version field")
    args = parser.parse_args()

    for name in (".mcp.json", "plugins/springbrand/mcp.json", "plugins/springbrand-workbuddy/.mcp.json"):
        rewrite_mcp_manifest(ROOT / name)

    rewrite_claude_plugin(ROOT / ".claude-plugin/plugin.json", args.version)
    rewrite_codex_plugin(ROOT / ".codex-plugin/plugin.json", args.version)
    rewrite_cursor_plugin(ROOT / "plugins/springbrand/.cursor-plugin/plugin.json", args.version)
    rewrite_workbuddy_plugin(ROOT / "plugins/springbrand-workbuddy/.workbuddy-plugin/plugin.json", args.version)
    rewrite_agents_marketplace(ROOT / ".agents/plugins/marketplace.json")
    rewrite_claude_marketplace(ROOT / ".claude-plugin/marketplace.json")
    rewrite_codebuddy_marketplace(ROOT / ".codebuddy-plugin/marketplace.json")
    rewrite_cursor_marketplace(ROOT / ".cursor-plugin/marketplace.json", args.version)
    for name in ("hooks/user-prompt-submit", "plugins/springbrand-workbuddy/hooks/user-prompt-submit"):
        rewrite_hook(ROOT / name)
    rewrite_workflow(ROOT / ".github/workflows/validate-plugin.yml")
    (ROOT / "VERSION").write_text(args.version + "\n")


if __name__ == "__main__":
    main()
