# GitHub Copilot for developers: a course in two sessions

Versión en español: [README_ES.md](./README_ES.md).

This repository holds the material for a course on GitHub Copilot used as a coding agent, not as
autocomplete. It is the Copilot volume of a series that teaches the same method with different tools:
[Claude Code](https://github.com/olonok69/claude_code_ml_engineer),
[Cursor](https://github.com/olonok69/cursor_code_ml_engineer),
GitHub Copilot (this repository) and [Pi](https://github.com/olonok69/pi_code_ml_engineer).

The course was delivered in two sessions, recorded in English and in Spanish. It is aimed at developers.
Every claim about Copilot was checked against docs.github.com and code.visualstudio.com on 17 October 2026,
and the methodology was field-tested with Copilot in VS Code on 28 October 2026. Where the official
documentation is silent or contradicts itself, the material says so. Copilot changes quickly: check the
sources again before reusing the material.

## The two sessions

### Session 1: GitHub Copilot, the tool (sections 00 to 11, slides 1 to 24)

The session starts from one structural fact: "Copilot" is not a single product. It is a terminal agent, two
different engines inside VS Code, a JetBrains plugin, a cloud agent that opens pull requests and a pull
request reviewer. Most wrong statements about Copilot come from mixing these pieces up.

| Section | Topic | Key points |
|---|---|---|
| 00 | Surfaces map | Copilot CLI (`copilot`, not the retired `gh copilot`), VS Code with the Copilot and Local harnesses, JetBrains, Copilot cloud agent, Copilot code review; feature by surface matrix |
| 01 | Install, auth, headless, models, billing | Token order, fine-grained PAT, `copilot -p`, default model, billing in GitHub AI Credits since 2026-06-01 and how a credit relates to tokens |
| 02 | Memory and instructions | Two-level pattern with `AGENTS.md`, `.github/copilot-instructions.md` and `.instructions.md` with `applyTo`; what each surface loads |
| 03 | Permissions, trust, sandbox | Allow and deny rules (deny wins), trusted folders, local sandbox, structural limits of the cloud agent; a repository cannot ship an allow/deny list, so team rules become hooks |
| 04 | Sessions | Resume, fork, rewind, share, delegate to the cloud agent |
| 05 | Context window | `/context`, compaction, large tool outputs, six context hygiene habits |
| 06 | Prompt caching | There is no user control; caching happens and is billed; how to stop breaking it |
| 07 | MCP | One protocol, four configuration files (`mcpServers` versus `servers`), built-in servers, cloud agent rules |
| 08 | Skills and plugins | One `SKILL.md` for almost every surface; porting traps from Claude Code; plugins and marketplaces |
| 09 | Custom agents and subagents | `.agent.md` with a tool list that enforces the limit; subagent versus `/fleet` versus cloud agent |
| 10 | Hooks | The deterministic veto; a portable recipe that blocks push, pull request and merge |
| 11 | Automation | `copilot -p` in GitHub Actions, cloud agent tasks over REST, Copilot SDK, automatic code review |

### Session 2: the methodology and the ticket knowledge graph (sections 12 to 16, slides 25 to 42)

A powerful agent without a method produces chaos quickly. This session shows how to work with a coding
agent on a production project. The method does not depend on the tool: it was born in Claude Code, moved to
Cursor and now runs in Copilot. The agent is a disciplined collaborator; the person decides what gets done
and owns push, pull requests, merge and deploy.

| Section | Topic | Key points |
|---|---|---|
| 12 | Workflow and exit gate | Eleven stages linked by gates; the exit gate is five checks, and five real cases where a green check proved nothing |
| 13 | The method's tools | Order from cheap and deterministic to expensive: knowledge graph, CodeGraph, Serena, deterministic oracles, Playwright; GSD only in Claude Code and its substitutes in Copilot |
| 14 | Transfer from Claude Code to Copilot | Five rules that travel unchanged, the surface that changes, new holes (`/pr automerge`, code review approvals) and how "the human owns the merge" becomes enforceable with a `preToolUse` hook |
| 15 | Operations | Machine sync with a tarball and a shared engineering record over S3, with a single publisher and dry run by default |
| 16 | Ticket knowledge graph | graphify over the project's memory; `kg` and `kg-refresh` skills; queries without calling a model |
| Field test | 2026-10-28 | A real working day with Copilot in VS Code and a past ticket replayed through the gates; what was verified and what is still pending |

## Documentation

| File | Language | Content |
|---|---|---|
| [GUIA_PRESENTACION.md](./GUIA_PRESENTACION.md) | Spanish | Speaker guide, slide by slide: the thread to tell, key points, demos and a closing line per section |
| [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md) | English | Technical implementation guide with commands and configuration for every section, the Claude Code, Cursor and Copilot equivalence table and the sources |
| [GUIA_TECNICA.md](./GUIA_TECNICA.md) | Spanish | Spanish version of the technical guide |
| [VIDEOS_YOUTUBE.md](./VIDEOS_YOUTUBE.md) | English and Spanish | Titles and descriptions for the four recorded sessions |
| [docs/KNOWLEDGE_GRAPH.md](./docs/KNOWLEDGE_GRAPH.md) | English | The ticket knowledge graph case study |
| [docs/research/COPILOT_FINDINGS_2026-10-17.md](./docs/research/COPILOT_FINDINGS_2026-10-17.md) | English | Dated research notes with a source for each claim |
| [docs/ai-agents-code-methodology/field-reports/](./docs/ai-agents-code-methodology/field-reports/) | English | Field test reports from 2026-10-28 |

Section numbers (00 to 17, plus appendices A and B) match across the speaker guide, the technical guides,
the deck and the sibling volumes.

## Repository layout

| Path | Content |
|---|---|
| [presentation/](./presentation/) | The deck (`Copilot_Presentation.pptx`) and its generator `build_pptx_copilot.py` |
| [examples/](./examples/) | Runnable material by course section |
| [docs/ai-agents-code-methodology/](./docs/ai-agents-code-methodology/) | Methodology starter kit, the adaptation guide `COPILOT_ADAPTATION.md` and a ready-to-copy `copilot/` surface with instructions, skills, agents and hooks |
| [docs/knowledge-graph/](./docs/knowledge-graph/) | Knowledge graph pipeline, scripts, tests and a sanitised snapshot of the graph |
| [docs/synchro/](./docs/synchro/) | Machine sync and S3 runbooks |
| [ex_npm/](./ex_npm/), [ex_app/](./ex_app/), [ex_staging/](./ex_staging/) | Small demo targets for the `/audit`, `/audit-python` and `/deploy-staging` skills |
| [AGENTS.md](./AGENTS.md), [.github/](./.github/), [.mcp.json](./.mcp.json) | The live Copilot surface of this repository |

### Examples by section

Session 1: [agents-md](./examples/agents-md/) (02), [permissions](./examples/permissions/) (03),
[context](./examples/context/) (05), [prompt-caching](./examples/prompt-caching/) (06),
[mcp](./examples/mcp/) (07), [skills-plugins](./examples/skills-plugins/) (08),
[subagents](./examples/subagents/) (09), [hooks](./examples/hooks/) (10),
[automation](./examples/automation/) (11).

Session 2: [methodology](./examples/methodology/) (workflow, real example, tools, machine sync and S3
scripts), [codegraph](./examples/codegraph/), [serena](./examples/serena/), [gsd](./examples/gsd/) (13),
the methodology kit in [docs/ai-agents-code-methodology/](./docs/ai-agents-code-methodology/) (14) and the
graph in [docs/knowledge-graph/](./docs/knowledge-graph/) (16).

## Trying the live surface

Run `copilot` from the repository root and trust the folder when asked, or open the repository in VS Code
with the Copilot harness.

| Piece | Path | How to try it |
|---|---|---|
| Always-on instructions | `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/` | `/instructions` in the CLI |
| Skills | `.github/skills/audit`, `audit-python`, `deploy-staging` | `/audit ex_npm`, `/audit-python ex_app`, `/deploy-staging ex_staging` |
| Read-only agent | `.github/agents/refactor-scout.agent.md` | `copilot --agent refactor-scout` |
| Hook that blocks external git | `.github/hooks/block-external-git.json` | Ask the agent to `git push`: it is denied |
| MCP | `.mcp.json` (Context7 and CodeGraph) | `copilot mcp list`; Playwright is built into the CLI and is not configured here |

## Regenerating and testing

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_copilot.py   # deck
python examples/methodology/render_flow.py      # 11-stage workflow diagram
python examples/subagents/render_agents.py      # subagent, /fleet and cloud agent diagram

bash .github/hooks/test-block-external-git.sh   # git-block hook (PS=1 also tests PowerShell)
cd examples/methodology/tools && uv run -q --with pytest --with boto3 python -m pytest -q
cd docs/knowledge-graph && uv run -q --with pytest python -m pytest -q
```

All of these run offline.

## Technology references

| Technology | Role | Documentation |
|---|---|---|
| GitHub Copilot | The tool (Session 1) | https://docs.github.com/en/copilot |
| VS Code agents | Copilot and Local harnesses | https://code.visualstudio.com/docs/agents/concepts/agent-harnesses |
| MCP | Tool connection standard (07) | https://modelcontextprotocol.io |
| CodeGraph | Code graph (13) | https://colbymchenry.github.io/codegraph/ |
| Serena | Symbol navigation over LSP (13) | https://github.com/oraios/serena |
| GSD | Productised method, Claude Code only (13) | https://github.com/tomascortereal/claude-code-setup |
| Spec Kit | Spec-driven templates (13) | https://github.com/github/spec-kit |
| graphify | Ticket knowledge graph (16) | https://graphify.net |
| Context7 | Up-to-date library documentation | https://context7.com |

The full list of sources is in [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md#sources).

## Note on the data

Material derived from a real professional project is sanitised: no client names, ticket identifiers,
account identifiers, people or secrets. The knowledge graph material, sync runbooks and methodology examples
use the same pseudonyms as the Pi volume (tickets `TKT-1xx` and `CHG-1xx`, clients `ClientB` to `ClientV`),
so the volumes stay consistent with each other. The real engineering record lives under `data/`, which is
ignored by git.
