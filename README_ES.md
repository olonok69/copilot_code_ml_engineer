# GitHub Copilot — Un curso en dos sesiones (deck + guías)

> English version: [`README.md`](./README.md).

> **El volumen GitHub Copilot** de una serie de cursos: mismo curso, mismo método, otra herramienta:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer) ·
> **GitHub Copilot (este repo)** ·
> [Pi](https://github.com/olonok69/pi_code_ml_engineer).

Material para un **curso/workshop** sobre **GitHub Copilot** como *agente* (no como autocompletado): una
presentación (`.pptx`) en **dos sesiones**, dos guías escritas, un runbook para las demos en vivo y
ejemplos ejecutables. Dirigido a **desarrolladores**. La documentación de la charla está en inglés y en
español; el deck y los ejemplos están en inglés. Cada afirmación sobre Copilot se contrastó con
docs.github.com y code.visualstudio.com el **17 de octubre de 2026**; donde la documentación no dice nada o
se contradice, el material lo indica.

- **Sesión 1 — GitHub Copilot.** Empieza con un **mapa de superficies**: Copilot CLI (`copilot`, no el
  retirado `gh copilot`), VS Code con sus dos harnesses (harness Copilot = el runtime de la CLI; harness
  Local = modo agente clásico, con prompt files, handoffs y otro esquema de hooks), JetBrains, el **Copilot
  cloud agent** (antes "coding agent") y Copilot code review, más una matriz funcionalidad × superficie.
  Después: instalación, autenticación, `copilot -p` en headless, modelos, facturación en **GitHub AI
  Credits** (las premium requests terminaron el 2026-06-01) · memoria e instrucciones (`AGENTS.md`,
  `.github/copilot-instructions.md`, `.instructions.md` con `applyTo`) · permisos, confianza y sandbox ·
  sesiones · ventana de contexto · prompt caching (con honestidad: no hay control para el usuario) · MCP ·
  skills y plugins · agentes personalizados y subagentes · hooks · automatización.
- **Sesión 2 — La metodología + el grafo de tickets (independiente de la herramienta):** el flujo de 11
  etapas con puertas · prevalencia de herramientas (CodeGraph, Serena, GSD y sus sustitutos) · la
  transferencia **de Claude Code a Copilot**, con una guía de adaptación reescrita y una superficie
  `.github/` lista para copiar · sincronización de máquinas y el registro de ingeniería compartido sobre S3
  · el grafo de conocimiento de tickets con graphify. La puerta de salida son **cinco comprobaciones**
  (validar el instrumento · contrato a través del *wrapper* · lista de miembros, no totales · imagen
  desplegada · mirar la salida). "La persona es dueña del merge" ahora **se puede imponer** (un hook
  `preToolUse` versionado + los límites del cloud agent), y se señalan dos agujeros nuevos
  (`/pr automerge`, aprobaciones del code review).

La Sesión 1 también señala el paquete reutilizable de skills de la metodología en
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/):
las skills se enseñan en la Sesión 1 y se ejercitan de forma segura en la Sesión 2.

## Nombres en este volumen

Los volúmenes anteriores usan nombres de fichero en español con gemelos en inglés terminados en `_EN`.
Este volumen nació en inglés, así que los ficheros originales tienen nombres en inglés y las versiones en
español usan los mismos nombres que los volúmenes hermanos:

| Inglés (este volumen) | Español (este volumen) | Volumen Cursor / Claude Code |
|---|---|---|
| [`README.md`](./README.md) | [`README_ES.md`](./README_ES.md) | `README.md` / `README_EN.md` |
| [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md) | [`GUIA_TECNICA.md`](./GUIA_TECNICA.md) | `GUIA_TECNICA.md` / `GUIA_TECNICA_EN.md` |
| [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md) | [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) | `GUIA_PRESENTACION.md` / `GUIA_PRESENTACION_EN.md` |
| [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md) | [`DEMO_RUNBOOK_ES.md`](./DEMO_RUNBOOK_ES.md) | `DEMO_RUNBOOK.md` / `DEMO_RUNBOOK_EN.md` |
| [`examples/`](./examples/) | (compartido) | `ejemplos/` |
| [`presentation/`](./presentation/) | (compartido) | `presentacion/` |

La numeración de secciones (§00–§16) coincide en las guías, el deck y los volúmenes hermanos; §00 (mapa
de superficies) es nueva en este volumen.

## Contenido

| Fichero | Qué es |
|---|---|
| [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) | Guía de presentación: hilo por slide + frases de cierre + enlaces al código. |
| [`GUIA_TECNICA.md`](./GUIA_TECNICA.md) | Referencia de implementación copy-paste, con la tabla de equivalencias **Claude Code → Cursor → Copilot**. |
| [`DEMO_RUNBOOK_ES.md`](./DEMO_RUNBOOK_ES.md) | Chuleta para las demos en vivo: comprobaciones previas, comando por slide, tiempos, fallos habituales. |
| [`presentation/Copilot_Presentation.pptx`](./presentation/) | El deck (16:9), con el mismo sistema visual que los decks hermanos. |
| [`presentation/build_pptx_copilot.py`](./presentation/build_pptx_copilot.py) | Generador del deck (regenerable). |
| [`examples/`](./examples/) | Artefactos ejecutables por sección del curso. |
| [`docs/`](./docs/) | Paquete de la metodología (con la superficie de Copilot), pipeline del grafo de conocimiento, runbooks de sincronización y las notas de investigación de la Sesión 1. |
| [`AGENTS.md`](./AGENTS.md) · [`.github/`](./.github/) · [`.mcp.json`](./.mcp.json) | La superficie de Copilot activa en este repo: ábrelo con la CLI o con VS Code y pruébala. |

## La superficie activa (este repo)

| Pieza | Ruta | Cómo probarla |
|---|---|---|
| Instrucciones siempre activas | [`AGENTS.md`](./AGENTS.md), [`.github/copilot-instructions.md`](./.github/copilot-instructions.md) | `copilot` → `/instructions` |
| Skills | [`.github/skills/`](./.github/skills/) `audit`, `audit-python`, `deploy-staging` | `/audit` sobre [`ex_npm/`](./ex_npm/) · `/audit-python` sobre [`ex_app/`](./ex_app/) · `/deploy-staging` sobre [`ex_staging/`](./ex_staging/) |
| Agente de solo lectura | [`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md) | `copilot --agent refactor-scout` |
| Hook que bloquea git | [`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) | pide al agente `git push` → denegado · `bash .github/hooks/test-block-external-git.sh` |
| MCP | [`.mcp.json`](./.mcp.json) | `copilot mcp list` (requiere confianza en la carpeta) |

## Ejemplos (por sección del curso)

**Sesión 1:** [`examples/agents-md/`](./examples/agents-md/) (§02) ·
[`examples/context/`](./examples/context/) (§05) ·
[`examples/prompt-caching/`](./examples/prompt-caching/) (§06) ·
[`examples/mcp/`](./examples/mcp/) (§07) ·
[`examples/skills-plugins/`](./examples/skills-plugins/) (§08, incluye `day`, `atlassian`, `evidence`, `preview`; paquete de skills de la metodología en
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/)) ·
[`examples/subagents/`](./examples/subagents/) (§09) ·
[`examples/hooks/`](./examples/hooks/) (§10) ·
[`examples/permissions/`](./examples/permissions/) (§03) ·
[`examples/automation/`](./examples/automation/) (§11: workflow de Actions con `copilot -p`, API de tareas del cloud agent, SDK).

**Sesión 2:** [`examples/methodology/`](./examples/methodology/) (flujo, ejemplo real, prevalencia de
herramientas, sincronización de máquinas, scripts de S3) · [`examples/codegraph/`](./examples/codegraph/) ·
[`examples/serena/`](./examples/serena/) · [`examples/gsd/`](./examples/gsd/) ·
[`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/), el kit de arranque portable:
[`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) + la superficie lista para
copiar [`copilot/`](./docs/ai-agents-code-methodology/copilot/) · [`docs/synchro/`](./docs/synchro/).

También en la **Sesión 2:** [`docs/knowledge-graph/`](./docs/knowledge-graph/) · [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md) ·
[`presentation/kg_graph.png`](./presentation/kg_graph.png) (captura sanitizada del grafo real).

## Regenerar el deck y los diagramas

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_copilot.py   # -> presentation/Copilot_Presentation.pptx
python examples/methodology/render_flow.py      # -> flow.png (flujo de 11 etapas)
python examples/subagents/render_agents.py      # -> agents.png (subagente vs /fleet vs cloud agent)
```

## Tests que puedes ejecutar offline

```bash
bash .github/hooks/test-block-external-git.sh                         # el hook que bloquea git (bash; PS=1 añade PowerShell)
cd examples/methodology/tools && uv run -q --with pytest --with boto3 python -m pytest -q
cd docs/knowledge-graph && uv run -q --with pytest python -m pytest -q
```

## Documentación de las tecnologías

| Tecnología | Papel | Documentación |
|---|---|---|
| **GitHub Copilot** | La herramienta (Sesión 1) | <https://docs.github.com/en/copilot> · referencia de la CLI <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference> · hooks <https://docs.github.com/en/copilot/reference/hooks-reference> |
| **Agentes de VS Code** | Harnesses Copilot / Local | <https://code.visualstudio.com/docs/agents/concepts/agent-harnesses> |
| **MCP** | Estándar de conexión (§07) | <https://modelcontextprotocol.io> |
| **CodeGraph** | Grafo de código (§13) | <https://colbymchenry.github.io/codegraph/> |
| **Serena** | Navegación LSP (§13) | <https://github.com/oraios/serena> |
| **GSD** | Método empaquetado, solo Claude Code (§13) | <https://github.com/tomascortereal/claude-code-setup> |
| **Spec Kit** | Plantillas guiadas por especificación (solo fuentes de terceros) | <https://github.com/github/spec-kit> |
| **graphify** | Grafo de conocimiento de tickets (Sesión 2) | <https://graphify.net> |
| **Context7** | Documentación actualizada de librerías | <https://context7.com> |

## Fuentes

Documentación oficial <https://docs.github.com/en/copilot> y <https://code.visualstudio.com/docs>,
**verificada el 2026-10-17. Copilot cambia rápido; revísalo antes de reutilizarlo.** Citas por afirmación:
[`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md); lista de URLs
en [`GUIA_TECNICA.md` § Fuentes](./GUIA_TECNICA.md#fuentes).

> Los ejemplos derivados de un proyecto profesional real están **sanitizados** (sin nombres de clientes,
> IDs de tickets, IDs de cuentas, personas ni secretos). El material del grafo de conocimiento, los
> runbooks de sincronización, los ejemplos de la metodología y la captura del grafo vienen del volumen Pi,
> ya sanitizado, con el mismo mapeo de seudónimos (tickets `TKT-1xx` / `CHG-1xx`, clientes
> `ClientB`…`ClientV`), para que los volúmenes sean coherentes entre sí. El `confluence_pack/` del volumen
> Cursor (páginas de publicación en Confluence) **no se incluye a propósito** aquí.
