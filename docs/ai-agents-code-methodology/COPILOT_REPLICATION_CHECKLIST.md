# Claude Code → GitHub Copilot replication checklist

Use this runbook when an established Claude Code workspace is the behavioral reference and the goal is to
verify the same workflow in GitHub Copilot. It complements the install guide; it does not install
configuration, authorize external actions, or prove that two products have identical behavior.

The acceptance target is **equivalent outcomes with the same guardrails**, not identical prompts or UI:
Copilot discovers the intended skills and tools, invokes safe operations correctly, respects ownership and
data boundaries, and produces evidence that meets the same output contract as the Claude Code baseline.

For Copilot-specific setup and the five day-to-day tools, see
[`AGENT_SETUP_TOOLS.md`](./AGENT_SETUP_TOOLS.md). For product-surface differences, see
[`COPILOT_ADAPTATION.md`](./COPILOT_ADAPTATION.md).

## 1. Establish the test boundary before running anything

Record the exact workspace, repository, branch, host, agent surface, client version, model, and date. Do
not assume that VS Code on Windows and a CLI in WSL share configuration, credentials, filesystem paths,
MCP servers, or skill folders. Test the surface the team will actually use.

| Field | Record |
|---|---|
| Target repository and root | |
| Repository ownership; read-only neighbouring repos | |
| Host / OS (for example WSL distro or Windows) | |
| WSL mode (CLI in distro, VS Code Remote - WSL, or Windows-local) | |
| Agent surface (Claude Code, Copilot CLI, VS Code Copilot harness, VS Code Local) | |
| Client version and model | |
| Branch / commit and working-tree state | |
| Orientation and scoped instruction files actually observed | |
| Claude Code baseline evidence and its date | |
| Approved non-production test fixture / synthetic identifier | |

Before testing, agree which repository may be changed, which repositories are context-only, who owns shared
records, and what is safe to use as test data. If another agent owns a shared-record cycle, or the record
may be stale, do not run its start/end routine or sync commands. Do not repeat a completed daily sync as a
Copilot smoke test.

Treat captured documents, logs, tickets, URLs, identifiers, credentials, and previews as potentially
sensitive. Keep raw output local and out of chat, reports, screenshots, commits, and presentation material.
Record only a redacted command, exit status, and a short non-identifying result. Never open or copy a
credential file to prove that it exists.

Classify each check before running it:

- **Static/local read:** inspect configuration, skill metadata, or file existence.
- **Offline/local execution:** tests or `--help`; may create local caches or temporary environments.
- **Remote read:** may expose confidential data in output or consume service quotas.
- **External write / paid operation:** changes shared state, posts content, deploys, or incurs model/API
  charges. Requires explicit authorization and a suitable isolated test target. A smoke test is not an
  authorization.

## 2. WSL is an execution environment, not a Copilot surface

Record both the Copilot surface and where its process/extensions run. For a Windows checkout at
`D:\<workspace-root>\<main-repo>`, the matching Ubuntu WSL path is
`/mnt/d/<workspace-root>/<main-repo>`. If the workspace contains several independent Git repos, the
workspace parent may not itself be a Git root; follow the workspace ownership instructions and run Git
commands from the owned repository. Use one of these repeatable modes:

| Mode | How to open/run | What to verify |
|---|---|---|
| **Copilot CLI in WSL** | Install the Copilot CLI in the selected WSL distro, open a WSL terminal, `cd /mnt/d/<workspace-root>/<main-repo>`, then launch `copilot` from the repo root. | `pwd` and `git rev-parse --show-toplevel` identify the expected Linux path; `command -v copilot` resolves inside that distro; trust the repo when prompted; inspect `/mcp`, `/skills`, and `/instructions`. |
| **VS Code Remote - WSL** | Install the VS Code WSL extension on Windows. From the WSL terminal at the repo root, run `code .`; alternatively use **WSL: Connect to WSL** and open the repo from that window. For a multi-repo workspace, open the parent only when its workspace-level ownership instructions are needed, and keep Git commands scoped to the target repo. | The window status bar names the distro (for example, `WSL: Ubuntu`); the integrated terminal is Linux and resolves the same repo root; install Copilot extensions into WSL when VS Code offers that option; inspect the active skills, MCP servers, and instructions in that window. |
| **VS Code Windows-local / UNC path** | Opening `\\wsl$\Ubuntu\...` or `\\wsl.localhost\Ubuntu\...` from a regular Windows-local window is not the WSL Remote workflow. | Record this as Windows-local, not as proof that WSL tools, paths, environment variables, or credentials are being used. Reopen through Remote - WSL for a WSL acceptance run. |

The VS Code WSL extension runs commands and remote-capable extensions in WSL. The `code .` workflow also
works for a repository on a mounted Windows drive such as `/mnt/d`. A WSL Copilot CLI is a separate
installation from the Windows VS Code extension; having one does not establish that the other is installed.

Keep each environment's credentials in that environment. Never copy or print credential files to bridge
Windows and WSL. For CLI personal skills, `~/.copilot/skills/` is relative to the WSL user's home when the
CLI runs in WSL. For a VS Code Remote - WSL session, verify skill discovery in that remote window rather
than assuming Windows and Linux personal customization directories are interchangeable.

Official setup references: [Developing in WSL](https://code.visualstudio.com/docs/remote/wsl) and
[Remote Development FAQ](https://code.visualstudio.com/docs/remote/faq).

## 3. Verify discovery before behavior

In the exact Copilot surface under test, record the active workspace root and inspect the available
customizations using that surface's supported UI or commands. For the Copilot CLI, the setup guide uses
`/mcp`, `/skills`, and `/instructions`; do not assume those commands apply to VS Code Local. Confirm:

1. The expected orientation and scoped instruction files are active, not merely present on disk.
2. The intended skills appear once, with the expected names and descriptions.
3. MCP servers connect and expose the expected tools; a configured server that is offline is not a pass.
4. No personal-only credentialed skill has accidentally been committed or exposed to a cloud agent.
5. The tool and instruction precedence is consistent with the team's intended policy.

Static checks are necessary but do not prove discovery. A file in `~/.claude/skills/` is not evidence that
Copilot CLI loaded it; follow the surface-specific paths in `COPILOT_ADAPTATION.md`.

## 4. Skill-by-skill acceptance

Run low-risk checks first. For each skill, record **DISCOVERED**, **BEHAVIOR PASS**, **BLOCKED**, or
**NOT RUN** separately. A skill can be discovered but not safe or authorized to execute. Use the actual
skill name from the installed pack; do not invoke side-effecting operations just to complete a table.

| Skill | Safe discovery / behavior check | Do not treat as a smoke test |
|---|---|---|
| `methodology-plan` | Invoke with a synthetic issue and verify it produces the planning sections without editing files. | A real change plan is not agreement to implement. |
| `sanitise-diff` | Use a disposable repository/fixture with fake names and fake secret patterns; verify it reports the expected findings without printing real blocklist content. | Do not expose `.sanitise-names` or use a real client name as a test string in chat. |
| `kg` | Query a non-sensitive known node and check that the response distinguishes graph results from the STATUS fallback. | Do not paste ticket text or graph output containing client identifiers into the report. |
| `atlassian` | First check help and credential availability without displaying credentials. If approved, read one designated non-sensitive test issue/page; confirm the read path and expected exit status. | No Jira create/edit/comment/transition. No Confluence write-plan/apply test without page-specific approval. |
| `evidence` | Check `--help` or `discover --list` for a narrow approved non-production window. An end-to-end fetch needs an approved document/run and local retention approval. | Do not download an arbitrary matter URL or copy raw evidence into the report. |
| `preview` | Check `--help` and prerequisites first. End-to-end requires an approved non-production fixture, Docker, the consumer app, and explicit approval for real model/API calls. Verify the compare and stop the preview process afterward. | Do not use a client document or treat a successful page load alone as a pass. Never put preview output under shared `data/`. |
| `day` | Check discovery and review the documented actions/role gate only. Record the already-completed Claude Code run as the baseline if its redacted evidence is available. | Do not rerun start/end or any pull/push/delete operation when another agent owns the shared record. |
| `kg-refresh` | Check discovery and verify the contributor/publisher guard from documentation or an offline test fixture. | Do not rebuild, publish, clear a queue, or sync to test skill invocation. Publisher-only remains a real role boundary. |

For tool-backed skills, a final behavior pass requires both the skill to select the right tool and the tool
to produce the expected result. A manually running an equivalent shell command verifies the tool path, not
Copilot skill selection.

## 5. MCP and local tool checks

Use the matching smoke tests in [`AGENT_SETUP_TOOLS.md`](./AGENT_SETUP_TOOLS.md), from the same host and
surface that Copilot will use. Record server connection and a small expected result, not a full response.

| Capability | Minimum useful evidence | Boundary |
|---|---|---|
| CodeGraph | A known symbol query returns relevant source/call-path information for the target repo. | Index creation changes local files; do it only where authorized. |
| Serena | A known symbol/reference query returns the expected definition or references. | Initial `uvx` setup may download packages and populate caches. |
| Playwright | In the CLI, open a harmless public test page and verify its title; for VS Code Local, test only if configured there. | Do not test against a production or authenticated client page. |
| Context7 | A small documentation query returns relevant library documentation. | Network request to the configured provider. |
| `kg` query helper | Run the same non-sensitive known-node lookup as above. | Query results may contain private project history. |
| Evidence CLI | `--help` is a local check; `discover --list` is a remote read, even though it does not download documents. | Use the read-only profile and a narrow window. |
| Preview viewer | A successful approved fixture run produces the expected before/after view and comparison. | Docker containers, local copies of source/documents, and real model/API charges. |
| Atlassian CLI | Help is local; one approved test issue/page read verifies the authenticated path. | Remote private content; never include raw response in the report. |

Do not infer a pass from a config file existing, a server starting, or a skill name appearing. Test a
representative operation and verify its expected shape. Conversely, do not start real services or make
remote calls just to turn a check green when the target is unauthorized or sensitive.

## 6. Course-pack checks

These checks verify the portable examples, not the target team's credentials or runtime integration:

1. Confirm all eight skill folders contain `SKILL.md`; frontmatter `name` matches the folder, descriptions
   are within Copilot's documented limit, and no Claude-only `trigger:` key was carried over.
2. Run the offline tests under `examples/methodology/tools/` using the repository's documented command.
   They test the genericised tool cores; they do not call the target AWS, Atlassian, or preview services.
3. Run the hook's offline test from a disposable checkout. Do not test a denial against a real remote.
4. Check the exact documentation claims against the current Copilot product docs before presenting them;
   the product-specific research in this pack is dated and must not be treated as a live guarantee.

Do not report the course-pack tests as proof that the target repository's skills, credentials, or MCP
servers work.

## 7. Results and pass criteria

Use this compact record. Keep raw tool output and sensitive identifiers out of it.

| Check | Status | Evidence (redacted command/result) | Host / surface | Side-effect class |
|---|---|---|---|---|
| Orientation loaded | | | | |
| Skill discovery (8 expected) | | | | |
| Skill behavior checks | | | | |
| MCP server/tool checks | | | | |
| Course offline tests | | | | |
| Guardrails and ownership | | | | |

Status meanings:

- **PASS** — the expected result was observed on the named surface, with safe evidence.
- **FAIL** — an authorized check ran and the expected result was not observed.
- **BLOCKED** — a prerequisite, permission, or safe test fixture is missing.
- **NOT RUN** — intentionally not executed, including actions prohibited by ownership or side-effect rules.

Claim **replication verified** only when discovery and the required safe behavior checks pass on the
intended Copilot surface, guardrails remain intact, and any deferred external/paid checks are explicitly
listed as blocked/not run. Do not turn “documented”, “configured”, or “works in Claude Code” into a Copilot
PASS.
