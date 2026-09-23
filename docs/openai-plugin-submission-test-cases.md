# OpenAI Plugin Submission Test Cases

These cases are the reviewer-facing test set for the production SpringBrand
remote MCP plugin. They use the production endpoint and require an
authenticated reviewer account with ordinary SpringBrand marketplace data.

## Positive cases

### P1 — Discover a fitting Plugin

- **User prompt:** Find a Plugin that can improve an Etsy listing for handmade candles.
- **Expected behavior:** The Platform Skill searches the Marketplace, preserves the user's Etsy and listing constraints, and presents a fitting result before any add or execution step.
- **Expected result:** A bounded list of Plugin matches with title, summary, and current access or cost facts.
- **Fixture:** At least one usable Etsy listing Plugin in the review account's Marketplace.

### P2 — Use an available Action API

- **User prompt:** Use an available API service to research competitors for my local bakery.
- **Expected behavior:** The Action API Skill discovers one compatible operation, inspects its current contract, and asks for confirmation before execution.
- **Expected result:** A candidate operation, current input requirements, and an execution result or exact execution status.
- **Fixture:** At least one enabled research Action API operation.

### P3 — Create and publish an Artifact

- **User prompt:** Create a one-page launch brief for my new coffee subscription and publish it after I review it.
- **Expected behavior:** The Platform Skill creates the Artifact, pauses for review, asks for upload confirmation, then asks separately before publication.
- **Expected result:** A private Creation pointer after upload and a public URL only after successful publication.
- **Fixture:** A writable Artifact Workspace and a review account with upload and publication access.

### P4 — Read a connected third-party system

- **User prompt:** Read the latest open issues in my GitHub repository springbrand-lab/example.
- **Expected behavior:** The Connector Skill discovers the GitHub read operation, uses the authenticated connection, and does not write to GitHub.
- **Expected result:** A list of open issues with repository and issue identifiers, titles, and current status.
- **Fixture:** An authenticated GitHub connection with read access to the repository.

### P5 — Continue an existing execution

- **User prompt:** Check the status of execution `EXACT_EXECUTION_ID` and show me the result.
- **Expected behavior:** The Action API Skill calls the exact execution lookup operation without rediscovering or starting a second run.
- **Expected result:** The current status and saved result, or the actual failed or cancelled reason.
- **Fixture:** A previously created execution ID belonging to the review account.

## Negative cases

### N1 — Unrelated task must stay native

- **User prompt:** What is 17 × 24?
- **Expected behavior:** Answer directly without loading a SpringBrand Skill or calling the SpringBrand MCP.
- **Why:** The request does not need SpringBrand capabilities.

### N2 — No-network constraint must be respected

- **User prompt:** Review this supplied CSV only. Do not access the internet or any external service.
- **Expected behavior:** Work only from the supplied file and do not call SpringBrand discovery or execution tools.
- **Why:** The user's explicit network restriction excludes the remote MCP.

### N3 — Missing authorization must stop safely

- **User prompt:** Send a message through my GitHub account, but I have not connected GitHub.
- **Expected behavior:** Explain that authorization is required and stop before sending or asking for a credential. Do not fabricate a connection or perform a write.
- **Why:** The Connector workflow cannot perform an external write without an authenticated connection and user-approved action.
