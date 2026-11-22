# GitHub Copilot para desarrolladores: un curso en dos sesiones

English version: [README.md](./README.md).

Este repositorio contiene el material de un curso sobre GitHub Copilot usado como agente de programación,
no como autocompletado. Es el volumen Copilot de una serie que enseña el mismo método con distintas
herramientas: [Claude Code](https://github.com/olonok69/claude_code_ml_engineer),
[Cursor](https://github.com/olonok69/cursor_code_ml_engineer),
GitHub Copilot (este repositorio) y [Pi](https://github.com/olonok69/pi_code_ml_engineer).

El curso se impartió en dos sesiones, grabadas en inglés y en castellano. Está dirigido a desarrolladores.
Cada afirmación sobre Copilot se contrastó con docs.github.com y code.visualstudio.com el 17 de octubre de
2026, y la metodología se probó en una jornada real con Copilot en VS Code el 28 de octubre de 2026. Cuando
la documentación oficial no dice nada o se contradice, el material lo indica. Copilot cambia rápido:
conviene revisar las fuentes antes de reutilizar el material.

## Las dos sesiones

### Sesión 1: GitHub Copilot, la herramienta (secciones 00 a 11, slides 1 a 24)

La sesión parte de un hecho estructural: "Copilot" no es un solo producto. Es un agente de terminal, dos
motores distintos dentro de VS Code, un plugin de JetBrains, un agente en la nube que abre pull requests y
un revisor de pull requests. La mayoría de las afirmaciones erróneas sobre Copilot vienen de mezclar estas
piezas.

| Sección | Tema | Puntos clave |
|---|---|---|
| 00 | Mapa de superficies | Copilot CLI (`copilot`, no el retirado `gh copilot`), VS Code con los harnesses Copilot y Local, JetBrains, Copilot cloud agent, Copilot code review; matriz de funcionalidad por superficie |
| 01 | Instalación, autenticación, headless, modelos, facturación | Orden de los tokens, PAT fine-grained, `copilot -p`, modelo por defecto, facturación en GitHub AI Credits desde el 2026-06-01 y relación entre créditos y tokens |
| 02 | Memoria e instrucciones | Patrón de dos niveles con `AGENTS.md`, `.github/copilot-instructions.md` y `.instructions.md` con `applyTo`; qué carga cada superficie |
| 03 | Permisos, confianza, sandbox | Reglas allow y deny (deny gana), carpetas de confianza, sandbox local, límites estructurales del cloud agent; un repositorio no puede incluir una lista allow/deny, así que las reglas de equipo se convierten en hooks |
| 04 | Sesiones | Reanudar, bifurcar, rebobinar, compartir y delegar en el cloud agent |
| 05 | Ventana de contexto | `/context`, compactación, salidas grandes de herramientas, seis hábitos de higiene de contexto |
| 06 | Prompt caching | No hay control para el usuario; la caché existe y se factura; cómo dejar de romperla |
| 07 | MCP | Un protocolo y cuatro ficheros de configuración (`mcpServers` frente a `servers`), servidores integrados, reglas del cloud agent |
| 08 | Skills y plugins | Un `SKILL.md` para casi todas las superficies; trampas al portar desde Claude Code; plugins y marketplaces |
| 09 | Agentes personalizados y subagentes | `.agent.md` con una lista de herramientas que impone el límite; subagente frente a `/fleet` frente a cloud agent |
| 10 | Hooks | El veto determinista; una receta portable que bloquea push, pull request y merge |
| 11 | Automatización | `copilot -p` en GitHub Actions, tareas del cloud agent por REST, Copilot SDK, revisión de código automática |

### Sesión 2: la metodología y el grafo de conocimiento de tickets (secciones 12 a 16, slides 25 a 42)

Un agente potente sin método produce caos rápidamente. Esta sesión muestra cómo trabajar con un agente de
programación en un proyecto en producción. El método no depende de la herramienta: nació en Claude Code,
pasó a Cursor y ahora funciona en Copilot. El agente es un colaborador disciplinado; la persona decide qué
se hace y es dueña del push, de las pull requests, del merge y del despliegue.

| Sección | Tema | Puntos clave |
|---|---|---|
| 12 | Flujo y puerta de salida | Once etapas unidas por puertas; la puerta de salida son cinco comprobaciones, y cinco casos reales en los que una comprobación en verde no demostraba nada |
| 13 | Las herramientas del método | Orden de barato y determinista a caro: grafo de conocimiento, CodeGraph, Serena, oráculos deterministas, Playwright; GSD solo en Claude Code y sus sustitutos en Copilot |
| 14 | Transferencia de Claude Code a Copilot | Cinco reglas que viajan sin cambios, la superficie que cambia, agujeros nuevos (`/pr automerge`, aprobaciones del code review) y cómo "la persona es dueña del merge" se puede imponer con un hook `preToolUse` |
| 15 | Operaciones | Sincronización de máquinas con un tarball y registro de ingeniería compartido sobre S3, con un único publicador y simulación por defecto |
| 16 | Grafo de conocimiento de tickets | graphify sobre la memoria del proyecto; skills `kg` y `kg-refresh`; consultas sin llamar a un modelo |
| Prueba de campo | 2026-10-28 | Una jornada real con Copilot en VS Code y un ticket pasado repetido a través de las puertas; qué se verificó y qué queda pendiente |

## Documentación

| Fichero | Idioma | Contenido |
|---|---|---|
| [GUIA_PRESENTACION.md](./GUIA_PRESENTACION.md) | Castellano | Guía para el ponente, slide a slide: el hilo que contar, los puntos clave, las demos y una frase de cierre por sección |
| [GUIA_TECNICA.md](./GUIA_TECNICA.md) | Castellano | Guía técnica de implementación con comandos y configuración de cada sección, la tabla de equivalencias entre Claude Code, Cursor y Copilot, y las fuentes |
| [TECHNICAL_GUIDE.md](./TECHNICAL_GUIDE.md) | Inglés | Versión en inglés de la guía técnica |
| [VIDEOS_YOUTUBE.md](./VIDEOS_YOUTUBE.md) | Inglés y castellano | Títulos y descripciones de las cuatro sesiones grabadas |
| [docs/KNOWLEDGE_GRAPH.md](./docs/KNOWLEDGE_GRAPH.md) | Inglés | El caso de estudio del grafo de conocimiento de tickets |
| [docs/research/COPILOT_FINDINGS_2026-10-17.md](./docs/research/COPILOT_FINDINGS_2026-10-17.md) | Inglés | Notas de investigación fechadas, con una fuente para cada afirmación |
| [docs/ai-agents-code-methodology/field-reports/](./docs/ai-agents-code-methodology/field-reports/) | Inglés | Informes de la prueba de campo del 2026-10-28 |

La numeración de secciones (00 a 17, más los apéndices A y B) coincide en la guía de presentación, las
guías técnicas, el deck y los volúmenes hermanos.

## Estructura del repositorio

| Ruta | Contenido |
|---|---|
| [presentation/](./presentation/) | El deck (`Copilot_Presentation.pptx`) y su generador `build_pptx_copilot.py` |
| [examples/](./examples/) | Material ejecutable por sección del curso |
| [docs/ai-agents-code-methodology/](./docs/ai-agents-code-methodology/) | Kit de arranque de la metodología, la guía de adaptación `COPILOT_ADAPTATION.md` y una superficie `copilot/` lista para copiar con instrucciones, skills, agentes y hooks |
| [docs/knowledge-graph/](./docs/knowledge-graph/) | Pipeline del grafo de conocimiento, scripts, tests y una instantánea sanitizada del grafo |
| [docs/synchro/](./docs/synchro/) | Runbooks de sincronización de máquinas y de S3 |
| [ex_npm/](./ex_npm/), [ex_app/](./ex_app/), [ex_staging/](./ex_staging/) | Pequeños objetivos de demo para las skills `/audit`, `/audit-python` y `/deploy-staging` |
| [AGENTS.md](./AGENTS.md), [.github/](./.github/), [.mcp.json](./.mcp.json) | La superficie de Copilot activa en este repositorio |

El deck y los ejemplos están en inglés.

### Ejemplos por sección

Sesión 1: [agents-md](./examples/agents-md/) (02), [permissions](./examples/permissions/) (03),
[context](./examples/context/) (05), [prompt-caching](./examples/prompt-caching/) (06),
[mcp](./examples/mcp/) (07), [skills-plugins](./examples/skills-plugins/) (08),
[subagents](./examples/subagents/) (09), [hooks](./examples/hooks/) (10),
[automation](./examples/automation/) (11).

Sesión 2: [methodology](./examples/methodology/) (flujo, ejemplo real, herramientas, sincronización de
máquinas y scripts de S3), [codegraph](./examples/codegraph/), [serena](./examples/serena/),
[gsd](./examples/gsd/) (13), el kit de la metodología en
[docs/ai-agents-code-methodology/](./docs/ai-agents-code-methodology/) (14) y el grafo en
[docs/knowledge-graph/](./docs/knowledge-graph/) (16).

## Probar la superficie activa

Ejecuta `copilot` desde la raíz del repositorio y confía en la carpeta cuando lo pregunte, o abre el
repositorio en VS Code con el harness Copilot.

| Pieza | Ruta | Cómo probarla |
|---|---|---|
| Instrucciones siempre cargadas | `AGENTS.md`, `.github/copilot-instructions.md`, `.github/instructions/` | `/instructions` en la CLI |
| Skills | `.github/skills/audit`, `audit-python`, `deploy-staging` | `/audit ex_npm`, `/audit-python ex_app`, `/deploy-staging ex_staging` |
| Agente de solo lectura | `.github/agents/refactor-scout.agent.md` | `copilot --agent refactor-scout` |
| Hook que bloquea git externo | `.github/hooks/block-external-git.json` | Pide al agente un `git push`: se deniega |
| MCP | `.mcp.json` (Context7 y CodeGraph) | `copilot mcp list`; Playwright viene integrado en la CLI y no se configura aquí |

## Regenerar y probar

```bash
uv run --with python-pptx --with pillow python presentation/build_pptx_copilot.py   # deck
python examples/methodology/render_flow.py      # diagrama del flujo de 11 etapas
python examples/subagents/render_agents.py      # diagrama de subagente, /fleet y cloud agent

bash .github/hooks/test-block-external-git.sh   # hook de bloqueo de git (PS=1 prueba también PowerShell)
cd examples/methodology/tools && uv run -q --with pytest --with boto3 python -m pytest -q
cd docs/knowledge-graph && uv run -q --with pytest python -m pytest -q
```

Todo esto funciona sin conexión.

## Referencias de las tecnologías

| Tecnología | Papel | Documentación |
|---|---|---|
| GitHub Copilot | La herramienta (Sesión 1) | https://docs.github.com/en/copilot |
| Agentes de VS Code | Harnesses Copilot y Local | https://code.visualstudio.com/docs/agents/concepts/agent-harnesses |
| MCP | Estándar de conexión de herramientas (07) | https://modelcontextprotocol.io |
| CodeGraph | Grafo del código (13) | https://colbymchenry.github.io/codegraph/ |
| Serena | Navegación por símbolos sobre LSP (13) | https://github.com/oraios/serena |
| GSD | Método empaquetado, solo Claude Code (13) | https://github.com/tomascortereal/claude-code-setup |
| Spec Kit | Plantillas guiadas por especificación (13) | https://github.com/github/spec-kit |
| graphify | Grafo de conocimiento de tickets (16) | https://graphify.net |
| Context7 | Documentación actualizada de librerías | https://context7.com |

La lista completa de fuentes está en [GUIA_TECNICA.md](./GUIA_TECNICA.md#fuentes).

## Nota sobre los datos

El material que procede de un proyecto profesional real está sanitizado: sin nombres de clientes,
identificadores de tickets, identificadores de cuentas, personas ni secretos. El material del grafo de
conocimiento, los runbooks de sincronización y los ejemplos de la metodología usan los mismos seudónimos que
el volumen Pi (tickets `TKT-1xx` y `CHG-1xx`, clientes `ClientB` a `ClientV`), para que los volúmenes sean
coherentes entre sí. El registro de ingeniería real vive en `data/`, que git ignora.
