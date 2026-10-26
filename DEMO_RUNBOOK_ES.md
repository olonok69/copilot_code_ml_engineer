# DEMO_RUNBOOK — Presentación de GitHub Copilot (40 slides)

> English version: [`DEMO_RUNBOOK.md`](./DEMO_RUNBOOK.md).

Este es el runbook para el/la **presentador/a**. Guía de presentación: [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) ·
deck: [`presentation/Copilot_Presentation.pptx`](./presentation/Copilot_Presentation.pptx) ·
referencia: [`GUIA_TECNICA.md`](./GUIA_TECNICA.md).

> **Atención: qué se ha verificado y qué no.** Los comandos, flags, rutas de ficheros y ajustes de
> abajo salen de [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md)
> (la documentación a fecha de 2026-10-17). Mientras se construía este repo solo se ejecutaron las
> partes offline: los tests del hook, el `npm test` de los objetivos de demo y la generación del deck.
> **Haz un ensayo completo en tu máquina y con tu versión de Copilot antes de presentar.** Copilot
> cambia entre versiones.

---

## Qué está activo en *este* repo

Cuando ejecutas `copilot` desde la raíz del repo, o abres el repo en VS Code con el harness
**Copilot**, se cargan estas piezas:

| Pieza | Ruta | Cómo probarla |
|---|---|---|
| Memoria siempre cargada | [`AGENTS.md`](./AGENTS.md), [`.github/copilot-instructions.md`](./.github/copilot-instructions.md), [`.github/instructions/`](./.github/instructions/) | `/instructions` en la CLI lista las fuentes |
| Skills | [`.github/skills/`](./.github/skills/): `audit`, `audit-python`, `deploy-staging` | `/audit`, `/audit-python`, `/deploy-staging` |
| Agente personalizado | [`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md) | `copilot --agent refactor-scout`, o pídelo por su nombre |
| Hook | [`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) + `.sh` / `.ps1` | pide al agente que haga `git push` → **denegado** |
| MCP | [`.mcp.json`](./.mcp.json) (`mcpServers`, workspace) | `copilot mcp list` · `/mcp` |

Las copias didácticas de `examples/**` **no** se cargan hasta que las copias en `.github/`.
En la Sesión 1, señala también las skills personales reutilizables de la metodología en
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/).

---

## Comprobaciones previas (T-30 min)

```bash
# 1. Node 22+ y la CLI (una de estas opciones)
node --version                      # debe ser >= 22 para instalar con npm
npm install -g @github/copilot      # o: brew install --cask copilot-cli / winget install GitHub.Copilot
copilot --version
copilot update                      # la auto-actualización viene activada; fuérzala una vez antes de la charla

# 2. Autenticación
copilot login                       # --device-code en terminales remotos; o COPILOT_GITHUB_TOKEN

# 3. Primer arranque en el repo -> responde al aviso TRUST-FOLDER ("trust for future sessions")
cd copilot_code_ml_engineer
copilot
#   dentro de la sesión:
#   /instructions   -> aparecen AGENTS.md, copilot-instructions.md, instructions/*.instructions.md
#   /skills list    -> audit, audit-python, deploy-staging
#   /mcp            -> servidores del workspace + integrados (github, playwright, fetch, time)
#   /context        -> apunta el peso de "Custom Instructions" para el slide 14

# 4. Autotest del hook (offline, las dos versiones si tienes PowerShell)
bash .github/hooks/test-block-external-git.sh            # se espera "0 failures"
PS=1 bash .github/hooks/test-block-external-git.sh       # también la versión .ps1

# 5. Objetivos de demo
(cd ex_npm && npm install && npm test)
(cd ex_staging && npm test && npm run build)
(cd ex_app && python -m pip install pip-audit && python -m pip_audit -r requirements.txt)
```

**VS Code:** instala la extensión de Copilot, inicia sesión, abre esta carpeta y elige el harness
**Copilot** en el control Session Target. En el slide 5 cambiarás a **Local** para enseñar la
diferencia. Abre **Chat: Open Customizations** y comprueba que aparecen las tres skills del repo;
muestra el paquete de skills personales de la metodología como una configuración activa aparte. Si
falta una skill del repo, puede que su `name` no coincida con el nombre de su carpeta.

**Configuración de dos sesiones en WSL:** usa este repo del curso para la Sesión 1 y después abre el
workspace WSL `/mnt/d/repos3/ILS_2`, aprobado por el usuario, para la Sesión 2. Confirma la lista de
skills personales en Copilot Customizations e inspecciona la lista de MCP en la ventana activa; no
des por hecho que lo que se descubre en el repo del curso demuestra lo que se descubre en el repo de
destino. La comprobación del 2026-10-25 verificó un uso acotado de CodeGraph y pruebas de skills
offline o simuladas, pero dejó pendientes el preview real, la descarga remota de evidencia, las
lecturas autenticadas de Atlassian y las operaciones compartidas de `day` / `kg-refresh`. Mantén
cerradas esas puertas durante la charla.

**Plan B si no hay red o no puedes iniciar sesión:** haz todas las demos a partir de los textos de los
slides, más el test del hook (offline) y `copilot --help` / `copilot help permissions`.

---

## Comando por slide

| # | Slide | Demo (≤ 2 min salvo que se indique) |
|---|---|---|
| 1–3 | Título, agenda, separador | — |
| 4 | Cinco superficies | `copilot --version`. Explica que `gh copilot` es la extensión retirada, no esta herramienta. |
| 5 | Dos motores en VS Code | Cambia Session Target **Copilot ↔ Local**. En Local, enseña un prompt file que aparece como `/nombre`; en el harness Copilot no aparece. |
| 6 | Matriz de funcionalidades | Abre la tabla §2 de [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md). |
| 7 | Instalación / autenticación | `copilot login --help`; enseña el orden de los tokens en variables de entorno. |
| 8 | Headless + facturación | `copilot -p "Summarise AGENTS.md in 3 bullets" -s` · después `/usage` en una sesión interactiva. |
| 9 | Memoria de dos niveles | Abre [`AGENTS.md`](./AGENTS.md) (corto) y después uno de los ficheros a los que apunta. |
| 10 | Qué se carga y dónde | `/instructions` en la CLI. Menciona que la CLI también lee `CLAUDE.md` / `.claude/rules`, pero no `~/.claude/CLAUDE.md`. |
| 11 | Permisos | Demo de denegación en headless (abajo, **D1**). |
| 12 | Confianza / sandbox | `copilot help permissions` · `/sandbox` (si está disponible en tu versión). |
| 13 | Sesiones | Ejecuta un comando `-p`, copia el `copilot --resume=…` que imprime y reanúdalo; `/rewind` sobre una edición de prueba. |
| 14 | Ventana de contexto | `/context` y después `/compact "keep only the hook design"`. |
| 15 | Higiene | Solo el slide. |
| 16 | Caching | VS Code: Agent Debug Logs → Summary → **Cache Explorer** (solo si tu versión lo tiene). CLI: `/usage`. |
| 17 | Ficheros MCP | `copilot mcp list` · abre [`.mcp.json`](./.mcp.json): fíjate en `tools: ["*"]` y en que **no hay** entrada de Playwright. |
| 18 | Trampas de MCP | Pide: "use context7 to look up python-pptx `add_picture`". |
| 19 | Skills | Demos de skills **S1–S3** (abajo). |
| 20 | Agente personalizado | "Use the refactor-scout agent to find every caller of `health` in ex_npm": **no** debe editar ficheros. |
| 21 | Subagentes / fleet | `/subagents` · opcional `/fleet` sobre un plan de 2 tareas (gasta créditos). `/delegate` solo si quieres un PR en borrador en directo. |
| 22–23 | Hooks | Demo del hook **H1** (abajo). |
| 24 | Automatización | Enseña el workflow de [`examples/automation/`](./examples/automation/) (`--trust-folder`, allow/deny explícitos). **No** ejecutes en directo el script de tareas del cloud agent. |
| 25–33 | Sesión 2 · metodología | Slides + abre [`examples/methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md) y [`docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md). Demos sobre código real: **R1** (abajo). |
| 34–37 | Sesión 2 · caso del grafo | `bash docs/knowledge-graph/kg_query.sh find letter` y después `kg_query.sh TKT-104` contra el grafo real sanitizado (ver [`docs/knowledge-graph/`](./docs/knowledge-graph/)). |
| 38 | Sesión 2 · evidencia de paridad | Presenta el límite entre lo verificado y lo pendiente; no ejecutes preview real, descargas remotas, lecturas autenticadas ni operaciones compartidas. |
| 39–40 | Apéndice, cierre | — |

---

## Guiones de demo

### S1–S3 — skills sobre los objetivos de demo

| Skill | Objetivo | Qué hace |
|---|---|---|
| `/audit` | [`ex_npm/`](./ex_npm/) | `npm audit` → arreglo seguro → `npm test` |
| `/audit-python` | [`ex_app/`](./ex_app/) | `pip-audit -r requirements.txt` → smoke test |
| `/deploy-staging` | [`ex_staging/`](./ex_staging/) | `npm test` → `build` → **te pide el OK** → `deploy:staging` (servidor local) → `GET /health` |

```text
/audit ex_npm
/audit-python ex_app
/deploy-staging ex_staging
```

En `/deploy-staging` el agente **debe detenerse** antes de `npm run deploy:staging` y esperarte.
Aquí "staging" es un servidor local, sin nube. Limpia con `npm run staging:stop`.

### H1 — el hook dice que no

En modo interactivo, en la raíz del repo (la carpeta tiene que tener confianza; si no, el hook del
repo no se carga):

```text
> commit nothing, just run: git push origin main
```

Resultado esperado: la llamada a la herramienta se **deniega** con el motivo "Methodology handoff
gate". Después prueba `gh pr create --fill` y `gh pr merge 1 --auto`, que también deberían denegarse.
Por último `git status`, que debería ejecutarse con normalidad.

Prueba offline que no necesita Copilot: `bash .github/hooks/test-block-external-git.sh`. Primero
ejecuta un canario (una denegación conocida), así que si pasa, el resultado significa algo.

**Atención:** prueba también `/pr automerge` en un repo de pruebas. Si los comandos `/pr` propios de
la CLI pasan por `preToolUse` está **NO VERIFICADO**. Lo que observes es la respuesta para tu versión,
así que dilo en voz alta.

### D1 — allow/deny en headless (slide 11)

```bash
copilot -p "Show the last 3 commits, then push the branch" -s \
  --allow-tool='shell(git:*)' \
  --deny-tool='shell(git push)' --deny-tool='shell(gh pr)' \
  --no-ask-user --trust-folder
```

Resultado esperado: `git log` se ejecuta y el push se rechaza. Deny gana a allow, incluso con
`--allow-tool='shell(git:*)'`. Sin `--trust-folder`, el hook del repo se omite en modo `-p` (solo te
protege la capa `--deny-tool`). Ejecútalo una vez sin el flag para enseñarlo.

### R1 — CodeGraph / Serena / kg sobre código real

Este repo del curso no es un código de producto indexado. Para los slides 28–29 y 37, **abre tu propio
repo indexado** (uno con `.codegraph/`) que tenga los servidores de CodeGraph y Serena en su
`.mcp.json` (plantilla:
[`docs/ai-agents-code-methodology/copilot/mcp.json.example`](./docs/ai-agents-code-methodology/copilot/mcp.json.example)).
Después ejecuta:

```text
> use codegraph_explore to show who calls <a function you know>, then Serena find_referencing_symbols before we rename it
```

Arranca `copilot` **desde la raíz de ese repo**. Si `--path .` se resuelve respecto al directorio de
la sesión está NO VERIFICADO.

---

## Tiempos (franja de 90 minutos)

| Bloque | Slides | Minutos |
|---|---|---|
| Apertura + §00 superficies | 1–6 | 12 |
| §01–§03 instalación, memoria, permisos | 7–12 | 15 |
| §04–§06 sesiones, contexto, caching | 13–16 | 10 |
| §07–§09 MCP, skills, agentes | 17–21 | 15 |
| §10–§11 hooks, automatización | 22–24 | 10 |
| Sesión 2 · metodología + grafo | 25–38 | 25 |
| Apéndice + cierre | 39–40 | 3 |

Para 60 minutos, quita las demos en vivo de los slides 13, 16, 21 y 24 y enseña solo el slide.

---

## Fallos habituales

| Síntoma | Causa | Solución |
|---|---|---|
| El hook no salta en `copilot -p` / CI | `-p` omite los hooks del repo, el MCP del workspace y los plugins en una **carpeta sin confianza** | `--trust-folder` (o `GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`) |
| El hook no salta en modo interactivo | La carpeta no tiene confianza, o los hooks cambiaron después de arrancar la CLI (los hooks se cargan al inicio) | Da confianza a la carpeta; reinicia `copilot` |
| El hook "permitió" un push | El hook **agotó el timeout**. Los timeouts fallan **en abierto** en todos los eventos | Mantén el hook rápido (sin red); revisa `timeoutSec` |
| Se bloquean todas las llamadas a herramientas | El script del hook falla. Un código de salida distinto de cero falla en cerrado en `preToolUse` | Ejecuta el script de test; comprueba `bash`/`python3` en el PATH y el bit de ejecución del `.sh` |
| Falta una skill en VS Code | `name` ≠ nombre de la carpeta (minúsculas con guiones). VS Code la descarta en silencio | Renómbrala para que coincida |
| Falta una skill personal en la CLI | La CLI **no** lee `~/.claude/skills/` | Cópiala o enlázala en `~/.copilot/skills/`, o `copilot skill add <dir>` |
| Dos servidores Playwright / herramientas duplicadas | Playwright viene **integrado** en la CLI y además se configuró | Quítalo de `.mcp.json` (déjalo solo en `.vscode/mcp.json` para Local si hace falta) |
| Se ignora un servidor MCP | Falta `tools` (obligatorio en configuraciones de la CLI), o se usó `servers` en lugar de `mcpServers` en `.mcp.json` | Añade `"tools": ["*"]`; usa la clave raíz correcta |
| Un servidor de `.vscode/mcp.json` no aparece en el harness Copilot | Usa `${input:...}`, y esos no se reenvían | Muévelo a `.mcp.json` con variables de entorno |
| El prompt file `/nombre` no existe | Estás en el harness Copilot o en la CLI | Cambia a Local, o conviértelo en una skill |
| Se ignora un `AGENTS.md` anidado | La CLI solo lee la raíz + el directorio actual; VS Code Local necesita `chat.useNestedAgentsMdFiles` | Usa `.instructions.md` con `applyTo` |
| Sorpresa en el coste | `/fleet`, autopilot, el contexto de 1M y las tareas en la nube gastan AI Credits | `--max-ai-credits`, `/usage`, modelo `auto` |
