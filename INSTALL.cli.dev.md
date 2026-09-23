# SpringBrand CLI development installation prompt

Set up SpringBrand in every supported client detected on this machine.
Detect every supported client installed on this machine. Configure each detected client and do not configure clients that are not installed.
Run exactly one command now. Do not run --help, doctor, auth status, or any other preflight command first.
All detected clients command: `npx -y @springbrand/cli@alpha connect --all --skip-launch --url https://devconnector.springbrand.ai/mcp --api-key {{INSTALL_KEY}}`
The --all mode is intentional. Do not replace it with per-client commands and do not run another install command.
If copied text contains Markdown artifacts such as backslash escapes or link wrappers, remove those artifacts before running the command.
The command includes a one-time installation key. Run it once and do not print the key in your response.
Do not install the legacy Plugin. Do not run a separate upgrade or reinstall command. Let this command handle existing registrations.
After the command finishes, report every detected client, each command outcome without revealing credentials, each auth method, MCP and Skill status, restart or reload requirements, and any failed phase. If the CLI says restart or reload is required, report it and stop there. Do not attempt MCP tool discovery or a business operation in this same session. If the command fails, report the failed client, failed phase, and the CLI's next action. Do not rerun the command with the same one-time key. If the CLI reports the key as invalid, expired, or already used, ask the user to copy a fresh setup prompt. If the key is accepted but the MCP connection or authorization fails, run the same command once without the --api-key argument and complete the browser OAuth authorization it opens. Never blind-retry.
If the CLI reports an existing SpringBrand Plugin registration, pass that note to the user: the Plugin and this CLI registration can coexist, though a single install method is recommended. Leave the Plugin as it is; if SpringBrand tools appear twice, `/springbrand:doctor` shows the plugin removal command when one exists.
Close your report with a one-sentence capability note: SpringBrand gives this client one Skill covering social and competitor research, audience insight, SEO and website analysis, creator discovery, and copy, image, video, and voiceover generation, plus connected services such as GitHub. Then ask the user what they would like to build first.
