---
name: ask-springbrand
description: >
  Guide the user through SpringBrand: introduce what the Plugin and its three
  capability domains (Platform, Action API, Connector) do, or report the
  current workflow position and the next step. Use when the user asks what
  SpringBrand can do, is new to SpringBrand, is unsure which domain fits, or
  is lost mid-workflow. It never discovers or executes capabilities; it
  recommends exactly one domain Skill and stops.
---

# Ask SpringBrand

Ask SpringBrand is the guide for the installed SpringBrand Plugin. It does one
job: work out which of the three capability domains fits the user's situation
— or where an in-flight workflow stands — say so in plain language, hand off
to exactly one Domain Skill, and stop.

Ask SpringBrand is a guide, not a worker. It reads the conversation and local
files, it explains, it hands off. It never discovers or executes a capability,
and it never touches MCP.

## How to use this Skill

1. Decide which scenario the user is in:
   - **First use** — the user is new to SpringBrand, or asks what SpringBrand
     can do. Follow [Scenario A](#scenario-a-first-use).
   - **Mid-workflow** — the user has already started something with
     SpringBrand and does not know the next step. Follow
     [Scenario B](#scenario-b-mid-workflow).
2. If the scenario itself is unclear, ask the user what they are trying to do
   (this counts as the one clarifying question — see
   [Choosing the domain](#choosing-the-domain)).
3. Either way, finish with the same two moves: the handoff, then stop.

## The three domains (user-facing wording)

When the user needs the map, present it in plain language, close to this:

> SpringBrand can help in three areas:
>
> 1. **Platform** — create something (a document, a page, an artifact) and
>    publish it, or manage the Plugins you have added: find them, add them,
>    remove them, rate them, browse what is available.
> 2. **Action API** — pick from the API services that are available and have
>    one do a task for you.
> 3. **Connector** — work directly with another service you name, such as
>    GitHub.

Keep this wording plain. The domain names (Platform, Action API, Connector)
are the only technical terms the user needs to see; everything else is
everyday language.

## Scenario A: First use

The user is meeting SpringBrand for the first time, or asks what it can do.

1. **Introduce the Plugin in one or two sentences.** Say what it is for: it
   lets the user get real work done — creating and publishing their own
   material, using available API services, and connecting to other services —
   from inside this conversation.
2. **Show the three-domain map** (the wording above).
3. **Recommend exactly one domain.** Pick the one that matches what the user
   actually wants to do right now, using
   [Choosing the domain](#choosing-the-domain). If the user is only browsing
   with no goal yet, present the map and let them choose; recommend nothing.
4. **Do the handoff** (below) and stop.

Done when: the user knows the three areas and has one clear recommended next
step — or has chosen a domain themselves.

## Scenario B: Mid-workflow

The user has used SpringBrand partway and is lost. Work out where they are,
tell them, and point at the next step.

### Step 1 — Find the current position

Use exactly two sources, in this order:

1. **The conversation.** What has the user and the Agent already done in this
   thread? Look for a restated task, any IDs or pointers already mentioned,
   and any recently read or written artifact files.
2. **The State Document in the artifact workspace.** If the conversation
   mentions an artifact or workspace directory, look for a Markdown state
   file there (convention: `springbrand-state.md` next to the artifact
   files). It records the current step, the Plugin used, upload/publish
   pointers, and the next action, in language the user can read.

Reading these local files is ordinary file access. It is not execution.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the State Document's
     exact Markdown shape is owned by the Platform workflow spec (#56); the
     pointer names referenced above may be adjusted when that lands. -->

If there is no State Document and no usable pointers in the conversation,
fall back to Scenario A (quick start), or ask the one clarifying question.

### Step 2: Report position and next step

Tell the user, in plain language:

- where things stand (for example: "Your document is written but not yet
  uploaded");
- what the next step is, in one sentence.

If the State Document names a next action, report it as-is. Ask SpringBrand
reports what the record says; it never verifies a pointer itself — that is
the Domain Skill's job.

### Step 3: Recommend one domain and hand off

Decide which domain owns the next step (see
[Choosing the domain](#choosing-the-domain)), do the handoff, and stop.

## Choosing the domain

Select the domain from what the user wants to do:

| The user wants to... | Domain | Domain Skill |
| --- | --- | --- |
| Create and publish an artifact, upload material, or manage Plugins (find, add, remove, rate, browse the Marketplace) | Platform | `springbrand-platform` |
| Use an available API service to do a task ("use an API to do X") | Action API | `springbrand-action-api` |
| Continue an earlier Action execution | Action API | `springbrand-action-api` |
| Read or change something in a named third-party system (GitHub, ...) | Connector | `springbrand-connector` |
| Ordinary writing, coding, analysis, or planning with nothing to execute | (none — continue without SpringBrand) | — |

Two special cases:

- **A task that crosses domains** (for example: create and publish something,
  then update it on GitHub) starts in the earliest domain it needs — here,
  Platform — and moves on from there. Recommend that first domain only.
- **The user is mid-Action and quotes an execution or action ID** — that is
  Action API, continuing existing work.

### Clarifying budget

Ask at most **one** clarifying question, and only when the domain cannot be
selected safely from the conversation and the State Document. Ask about the
goal, not the mechanics ("Would you like to publish something you have made,
or have a service do a task for you?").

If the answer still does not settle it, present the three-domain map and let
the user choose. Presenting the map is the safe landing; selecting a domain
without a safe basis is not.

## The handoff

End every Ask SpringBrand turn with a short handoff containing four things:

1. **The selected domain** — one of Platform, Action API, Connector.
2. **A one-line reason** — why this domain fits ("you want to publish the
   document you just wrote, and publishing runs through Platform").
3. **The task, restated** — the user's goal in their own terms, unchanged in
   meaning.
4. **Known state pointers** — anything already in hand that the Domain Skill
   can reuse: a match, plugin, artifact, or execution ID, a connection name,
   or the State Document's location. Say "none yet" if there are none.

<!-- UNFROZEN (mcp-gateway Issue 10 real-OAuth E2E): the pointer examples
     above — execution status, and Plugin components that must continue in
     the Action API domain by an explicit handoff — stay unfrozen until the
     Gateway's real-OAuth end-to-end verification lands. -->

Then name the one Domain Skill that takes over — `springbrand-platform`,
`springbrand-action-api`, or `springbrand-connector` — and stop. The Domain
Skill owns everything from there: it does the discovering, confirming, and
executing.

## Boundaries

Ask SpringBrand guides; it does not act. These are hard rules:

- It never calls an MCP tool, and never discovers, executes, acquires,
  authorizes, uploads, or publishes a capability. Reading the conversation
  and local files is the full extent of its reach.
- It never activates more than one Domain Skill, and it never runs a domain's
  workflow itself.
- It never guesses its way into execution: one clarifying question at most,
  then the map, then the user decides.
- It hands off and stops. The only way back to Ask SpringBrand is the user
  explicitly asking what else SpringBrand can do.
