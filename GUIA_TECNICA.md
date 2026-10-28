# GitHub Copilot — Guía técnica de implementación (curso en dos sesiones)

> English version: [`TECHNICAL_GUIDE.md`](./TECHNICAL_GUIDE.md).

> Referencia copy-paste para construir cada pieza. Complementa a
> [`GUIA_PRESENTACION.md`](./GUIA_PRESENTACION.md) (el hilo narrativo) con el **cómo**.
> Los artefactos ejecutables están en [`examples/`](./examples/); [`docs/`](./docs/) es el paquete de la
> metodología y material de referencia. Volúmenes hermanos, misma estructura y numeración de secciones:
> [Claude Code](https://github.com/olonok69/claude_code_ml_engineer) ·
> [Cursor](https://github.com/olonok69/cursor_code_ml_engineer) ·
> [Pi](https://github.com/olonok69/pi_code_ml_engineer).
>
> **Nota de verificación:** cada afirmación sobre Copilot sale de
> [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md), que
> cita una página de docs.github.com o code.visualstudio.com para cada dato, todas consultadas el **17 de
> octubre de 2026**. Donde la documentación no dice nada, la guía lo indica como **NO VERIFICADO** o
> **NO DOCUMENTADO**. Donde la documentación se contradice, la guía también lo dice. Copilot cambia
> rápido: revísalo antes de reutilizarlo.
>
> Los nombres de comandos, flags, claves de configuración y textos de la interfaz se dejan en inglés,
> tal como aparecen en el producto.

## Índice

**Sesión 1 — GitHub Copilot**

0. [Mapa de superficies (leer primero)](#0-mapa-de-superficies)
1. [Instalación, autenticación, headless, modelos, facturación](#1-instalación-autenticación-headless-modelos-facturación)
2. [Memoria e instrucciones](#2-memoria-e-instrucciones)
3. [Permisos, confianza, sandbox](#3-permisos-confianza-sandbox)
4. [Sesiones](#4-sesiones)
5. [Ventana de contexto](#5-ventana-de-contexto)
6. [Prompt caching](#6-prompt-caching)
7. [MCP](#7-mcp)
8. [Skills y plugins](#8-skills-y-plugins)
9. [Agentes personalizados y subagentes](#9-agentes-personalizados-y-subagentes)
10. [Hooks](#10-hooks)
11. [Automatización](#11-automatización)

**Sesión 2 — La metodología + el grafo de tickets**

12. [El flujo de trabajo y el ejemplo real](#12-metodología)
13. [Las herramientas: CodeGraph, Serena, GSD](#13-las-herramientas-del-método)
14. [Transferir la metodología: de Claude Code a Copilot](#14-transferir-la-metodología)
15. [Sincronización de máquinas (tarball + S3)](#15-sincronización-de-máquinas)
16. [Grafo de conocimiento de tickets](#16-grafo-de-conocimiento-de-tickets)
17. [Prueba de campo 2026-10-28: la metodología en Copilot, medida](#17-prueba-de-campo-2026-10-28)

**Apéndices**

- [A. Tabla de equivalencias: Claude Code → Cursor → Copilot](#a-tabla-de-equivalencias-claude-code--cursor--copilot)
- [B. Trampas que cambiaron en 2025–2026](#b-trampas-que-cambiaron-en-20252026)
- [Fuentes](#fuentes)

---

# SESIÓN 1 — GitHub Copilot

## 0. Mapa de superficies

"Copilot" no es un solo producto. Antes de configurar nada, decide **qué superficie** lee el fichero
que vas a escribir.

| Superficie | Qué es | Nota |
|---|---|---|
| **Copilot CLI** (`copilot`) | Agente de terminal, paquete npm `@github/copilot`. GA desde el 2026-02-25 (preview pública desde septiembre de 2025). | **Atención:** **no** es la extensión retirada `gh copilot` (una extensión de GitHub CLI de 2024). |
| **VS Code — harness Copilot** | El mismo runtime que la CLI (Copilot SDK, se ejecuta en el "Agent Host"). | Comparte con la CLI `~/.copilot/*`, `.github/hooks` (esquema de la CLI), `.mcp.json`, skills y agentes. |
| **VS Code — harness Local** | El modo agente clásico de VS Code, en el extension host. | Ajustes `chat.*` propios, **esquema de hooks propio**, `.vscode/mcp.json`. **Los prompt files y los `handoffs` solo funcionan aquí.** |
| VS Code — harnesses Claude / Codex, destino Cloud | Otros motores que se eligen en el control Session Target. | Fuera de alcance, salvo "Cloud" = delegar en el cloud agent. |
| **Modo agente de JetBrains** | Modo agente + MCP soportados. | Skills, agentes personalizados, instrucciones personalizadas y prompt files están en **Preview**. |
| **Copilot cloud agent** | **Antes "coding agent".** Recibe un issue / prompt / llamada a la API / automatización, trabaja en un sandbox Linux efímero de GitHub Actions y abre un **PR en borrador**. | Todas las herramientas preaprobadas; por diseño no puede aprobar ni hacer merge. |
| **Copilot code review** | Revisor de PRs en github.com y en los IDE; puede ser automático mediante rulesets. | Lee instrucciones y skills **desde la rama head del PR**. |
| Copilot en github.com, app de Copilot | Chat, página Agents, Spaces; app de escritorio (`copilot app` / `/app`). | Se menciona por completitud. |

### Matriz funcionalidad × superficie

| Funcionalidad | CLI | VS Code harness Copilot | VS Code harness Local | JetBrains | Cloud agent | Code review |
|---|---|---|---|---|---|---|
| `.github/copilot-instructions.md` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `.github/instructions/*.instructions.md` (`applyTo`) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` | ✓ solo raíz + directorio actual | ✓ | ✓ (anidados: `chat.useNestedAgentsMdFiles`, desactivado) | ✗ en Chat | ✓ gana el más cercano | ✓ |
| `CLAUDE.md` / `GEMINI.md` | ✓ | — | `chat.useClaudeMdFile` | — | ✓ | ✓ (+ `REVIEW.md`) |
| Prompt files `.github/prompts/*.prompt.md` | ✗ | ✗ | ✓ | ✓ (preview) | ✗ | ✗ |
| Skills | ✓ | ✓ | ✓ | Preview | ✓ | ✓ |
| Agentes personalizados `.github/agents/*.agent.md` | ✓ | ✓ | ✓ (+ `handoffs`) | Preview | ✓ | — |
| Hooks | ✓ `.github/hooks` | ✓ esquema de la CLI | ✓ **esquema distinto** | — | ✓ solo `.github/hooks`, Linux | **NO DOCUMENTADO** |
| Configuración MCP | `.mcp.json`, `.github/mcp.json`, `~/.copilot/mcp-config.json` (`mcpServers`) | `.mcp.json` + fichero de usuario (+ `.vscode/mcp.json` reenviado) | `.vscode/mcp.json` (`servers`) | `mcp.json` desde la interfaz (ruta NO DOCUMENTADA) | JSON en Settings del repo | solo herramientas con `readOnlyHint: true` |
| Modo plan | `/plan`, `--plan`, Shift+Tab | agente Plan | agente Plan | — | — | — |

Fuentes: GH:reference/custom-instructions-support, GH:reference/copilot-feature-matrix,
VSC:agents/concepts/agent-harnesses, VSC:agent-customization/hooks, VSC:agent-customization/prompt-files.
(**Atención:** la página de la matriz de funcionalidades todavía lista VS Code solo hasta la 1.108;
verifícalo en tu versión.)

> **El dato estructural más importante:** VS Code tiene **dos motores de Copilot**. Un hook, un prompt
> file o un servidor MCP que funciona en uno puede, en silencio, no existir en el otro. Indica siempre
> el harness.

---

## 1. Instalación, autenticación, headless, modelos, facturación

```bash
npm install -g @github/copilot                  # Node.js 22+; prerelease: @github/copilot@prerelease
brew install --cask copilot-cli                 # macOS/Linux
winget install GitHub.Copilot                   # Windows (requiere PowerShell 6+)
curl -fsSL https://gh.io/copilot-install | bash # script para macOS/Linux (PREFIX=, VERSION=)
copilot update                                  # o /update; auto-actualización activada por defecto (COPILOT_AUTO_UPDATE=false)
```

**Autenticación.** `copilot login` (o `/login`) con `--host`, `--web-flow`, `--device-code` (por defecto
en terminales remotos y en CI), `--with-token` (stdin). Tokens en variables de entorno, por orden de
precedencia: `COPILOT_GITHUB_TOKEN` > `GH_TOKEN` > `GITHUB_TOKEN`. Un PAT tiene que ser un PAT
**fine-grained y propiedad del usuario** con el permiso de cuenta **"Copilot Requests"**. En Actions con
`GITHUB_TOKEN`: permiso de workflow `copilot-requests: write` y la política de organización "Allow use of
Copilot CLI billed to the organization" activada.

**Headless.**
```bash
copilot -p "Explain ./complex.ts" -s                 # -p termina al acabar; -s = solo la respuesta
echo "Explain ./complex.ts" | copilot                # stdin por tubería funciona (se ignora si se pasa -p)
copilot -p '...' -s --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --no-ask-user --model=claude-sonnet-5.5
copilot -p '...' --output-format=json                # eventos JSONL
copilot -p '...' --share=./report.md                 # exporta la transcripción
copilot -p "..." --trust-folder                      # confía en hooks/MCP/plugins del repo solo para esta ejecución -p
copilot -p "..." --max-ai-credits=5                  # límite blando de gasto por respuesta
copilot --plan --mode autopilot -p "..."             # planificar y después autopilot
copilot -p "..." --fleet                             # orquestación de subagentes en paralelo
```

Subcomandos: `copilot init` (escribe `.github/copilot-instructions.md`), `copilot mcp list|get|add|enable|disable|remove`,
`copilot skill list|add [--project]|remove|enable|disable`, `copilot plugin …`, `copilot config [--repo|--local] KEY VALUE`,
`copilot instruction list`, `copilot help permissions|sandbox|config`.

Comandos slash que conviene conocer: `/model`, `/context`, `/compact [focus]`, `/usage`, `/limits` · `/agent`,
`/subagents`, `/plan`, `/autopilot`, `/fleet`, `/delegate` (prefijo `&`) · `/review`, `/security-review`,
`/rubber-duck` · `/skills`, `/mcp`, `/plugin`, `/instructions` · `/permissions`, `/sandbox` · `/resume`,
`/session`, `/rewind`, `/fork`, `/share`, `/chronicle` · `/remote`, `/pr [view|create|fix|auto|automerge]` ·
`/research`. **Atención: `/pr auto` y `/pr automerge` pueden hacer merge de PRs**; ver §10 y §14.

**Modelos (tabla de la CLI, 2026-10-17).** Por defecto `claude-sonnet-5.5`; también `gpt-5.4`, `claude-opus-5.5`,
`claude-haiku-5.5`, `claude-haiku-4.5`, `gpt-5.3-codex`, `gemini-3.7-flash`, `gemini-3.8-flash`, opcionales
`gpt-6.1-sol` / `gpt-6-astra` / `gpt-6-luna`, y `auto`. Se eligen con `--model=`, `COPILOT_MODEL`,
`/model [--session|--global|--repo|--local]`, `"model"` en `settings.json`, o `"model"` en
`.github/copilot/settings.json` del repo (solo carpetas de confianza); allowlist con `.github/allowed_models.txt`.
Esfuerzo: `--effort=low|medium|high|xhigh|max`. Contexto de 1M tokens: solo VS Code y CLI, en los modelos
que lo soportan y con más créditos (`--context long_context`). BYOK: `providers.json` / `COPILOT_PROVIDERS_CONFIG`.

**Facturación.** Desde el **2026-06-01**: GitHub **AI Credits** (1 crédito = 0,01 $), con precio por token
para entrada, salida, entrada cacheada y escritura en caché. Pro 10 $ → 1.500 créditos; Pro+ 39 $ → 7.000;
Max 100 $ → 20.000. Free/Student: solo el modelo Auto. Business/Enterprise: créditos compartidos. Las
completions y las sugerencias de next-edit no se facturan. Selección automática de modelo: 10% de
descuento en los planes de pago. **Atención: las "premium requests" y los multiplicadores son legado**;
solo aplican a los planes anuales Pro/Pro+ que se quedaron en el modelo antiguo. Cualquier slide de un
curso que diga "300 premium requests" está desactualizado.

**Créditos por token (consultado el 2026-10-26, "Models and pricing").** Los precios están en dólares por
millón de tokens, así que 1 $ por millón de tokens = 100 créditos por millón de tokens. No hay una relación
fija de créditos por token: depende del modelo y del tipo de token.

| Modelo (tramo por defecto), por millón de tokens | Entrada | Entrada cacheada | Escritura en caché | Salida |
|---|---|---|---|---|
| Claude Haiku 5.5 (≤100K de entrada) | 0,10 $ = 10 cr | 0,01 $ = 1 cr | 0,125 $ = 12,5 cr | 0,50 $ = 50 cr |
| Claude Sonnet 5.5 (por defecto en la CLI) | 2,00 $ = 200 cr | 0,10 $ = 10 cr | 2,50 $ = 250 cr | 10,00 $ = 1.000 cr |
| Claude Opus 5.5 | 4,00 $ = 400 cr | 0,20 $ = 20 cr | 5,00 $ = 500 cr | 20,00 $ = 2.000 cr |

Ejemplo (Sonnet 5.5): 50.000 tokens de entrada + 5.000 de salida = 10 + 5 = 15 créditos (0,15 $); si
40.000 de los tokens de entrada salen de la caché, unos 7,4 créditos. Los créditos mensuales que no se
usan no pasan al mes siguiente.

---

## 2. Memoria e instrucciones

### Qué se carga y dónde

| Fichero | CLI | VS Code | Cloud agent | Code review |
|---|---|---|---|---|
| `.github/copilot-instructions.md` | ✓ | ✓ | ✓ | ✓ (el **único** fichero que lee el code review de VS Code / Visual Studio / Eclipse) |
| `.github/instructions/**/*.instructions.md` | ✓ | ✓ | ✓ | ✓ |
| `AGENTS.md` | raíz + directorio actual | ✓ | gana el más cercano | ✓ |
| `CLAUDE.md`, `GEMINI.md`, `.claude/rules/**/*.md` | ✓ | Local: `chat.useClaudeMdFile` | ✓ (`CLAUDE.md`) | ✓ + `REVIEW.md` |
| Personal | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/**` | `~/.copilot/instructions` (harness Copilot) / perfil (Local) | — | — |

**Reglas de carga de la CLI.** Todas las fuentes se cargan **a la vez y se combinan**, y cada una se lee
en la raíz de git **y** en el directorio actual. **Atención:** un `<subdir>/AGENTS.md` anidado solo se
recoge **si arrancas `copilot` desde ese subdirectorio**, no "el más cercano en el árbol" (esa es la regla
del cloud agent). **Atención:** la CLI **no** lee `~/.claude/CLAUDE.md`; las instrucciones personales van en
`~/.copilot/copilot-instructions.md`. Para desactivarlas, `--no-custom-instructions`; para activar o
desactivar ficheros, `/instructions`.

**Imports `@path`** (inmediatos, recursivos, con protección frente a ciclos y tamaño) funcionan en
`AGENTS.md`, `CLAUDE.md` y `.github/copilot-instructions.md` **en la CLI**. La documentación de VS Code dice
"use Markdown links"; si VS Code expande `@path` está **NO DOCUMENTADO**, así que mejor usa punteros.

**Instrucciones por ruta:**
```markdown
---
applyTo: "app/models/**/*.rb"     # se admiten globs separados por comas: "**/*.ts,**/*.tsx"
excludeAgent: "code-review"       # o "cloud-agent" (opcional)
---
Aquí van las reglas para los modelos.
```
VS Code acepta además `name` y `description` opcionales (la descripción permite la carga bajo demanda). La
CLI también lee `.claude/rules/*.md` con `paths:` (o `applyTo:`): las reglas de Claude Code se reutilizan
tal cual.

**Ajustes de VS Code (harness Local):** `chat.useAgentsMdFile`, `chat.useNestedAgentsMdFiles` (desactivado
por defecto), `chat.useClaudeMdFile`, `github.copilot.chat.codeGeneration.useInstructionFiles`,
`chat.useCustomizationsInParentRepositories`.

**Prompt files** (`.github/prompts/*.prompt.md`, frontmatter `description`, `name`, `argument-hint`,
`agent`, `model`, `tools`; se invocan con `/nombre`) funcionan **solo en el harness Local de VS Code**
(además de Visual Studio y JetBrains según la documentación de GitHub). La CLI no los carga: usa skills, o
`.claude/commands/*.md`.

### Patrón de dos niveles (ver [`examples/agents-md/`](./examples/agents-md/))
- **Nivel 1** = `AGENTS.md` en la raíz (una voz compartida con Cursor y Claude Code) + un
  `.github/copilot-instructions.md` pequeño + puertas acotadas en
  `.github/instructions/<tema>.instructions.md`. Pequeños, con punteros de una línea.
- **Nivel 2** = ledgers en `data/changes/` (`STATUS.md`, `PLAYBOOK.md`, `SHARP_EDGES.md`, `TEST_MAP.md`,
  `FOLLOWUPS.md`, `<ticket>/<ticket>.md`) que se leen bajo demanda. Usa `@path` solo para lo que tenga que
  cargarse desde el principio.
- **Regla de escribir una sola vez:** cada dato vive en un único ledger; el fichero siempre cargado lleva
  el puntero.
- **Nivel 0:** `IDENTITY.md` local de la máquina (en el gitignore). Se carga mediante
  `~/.copilot/copilot-instructions.md` o un hook `sessionStart` que devuelve `additionalContext`
  (CLI/nube).
- **Reglas por carpeta:** como un `AGENTS.md` anidado se comporta distinto en cada superficie, el patrón
  portable es `.instructions.md` con `applyTo: "subdir/**"`.

> **El índice también se queda obsoleto.** Mover contenido del fichero siempre cargado a uno bajo demanda
> no lo actualiza. Caso real: una lista de 28 entradas ticket→test se movió a `TEST_MAP.md` y la
> comprobación verificaba "28 entradas". Tenía 28, y 28 era incorrecto: `tests/` tenía 80 ficheros.
> Verifica una lista movida contra lo que describe, nunca contra su versión anterior.

### Sistemas de memoria: tres distintos, ninguno canónico
- **Copilot Memory** (nube, preview pública): datos del repo con citas al código (validadas contra la
  rama) + preferencias del usuario; la usan el cloud agent, el code review y la CLI; **los recuerdos que no
  se usan caducan a los 28 días**. En la CLI, `--enable-memory` la activa en modo `-p`.
- **Herramienta de memoria de VS Code** (local): `/memories/`, `/memories/repo/`, `/memories/session/`.
- **Almacén de sesiones de la CLI + `/chronicle`** (`standup`; `improve` sugiere cambios en
  `copilot-instructions.md`; `skills create` redacta skills a partir del uso).

Trata los tres como las Memories de Cursor: un **complemento**, nunca la fuente de verdad. La memoria
canónica se queda en ledgers versionados.

---

## 3. Permisos, confianza, sandbox

Qué partes tienen un ejemplo en el repo y cuáles no (aprobaciones guardadas, carpetas de confianza, ajustes
de sandbox de la CLI, ajustes gestionados, firewall del cloud agent): ver la tabla de
[`GUIA_PRESENTACION.md` §03](./GUIA_PRESENTACION.md#03-permisos-confianza-sandbox-slides-1112).

### Patrones de la CLI: `Tipo(argumento)`

| Tipo | Ejemplos |
|---|---|
| `shell` | `shell(git:*)` (`:*` = raíz del comando + espacio), `shell(git push)`, `shell(gh pr)` (git/gh comparan el subcomando de primer nivel) |
| `write` / `read` | `write(src/*.ts)`, `read(.env)` |
| `url` | `url(github.com)` |
| `memory` | `memory` |
| Servidor MCP | `MyMCP(tool)`, `MyMCP` |

```bash
copilot --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --deny-tool='shell(gh pr)'
```
- **Deny siempre gana a allow**, incluso con `--allow-all`/`--yolo` o con aprobaciones guardadas.
- `--deny-tool='write(PATH)'` compara de forma exacta o por segmento final ("no glob support yet").
- Además: `--available-tools` / `--excluded-tools` (ocultar herramientas), `--allow-url` / `--deny-url`,
  `--allow-all-paths`, `--allow-all-tools` (`COPILOT_ALLOW_ALL`), `/permissions assisted` (un juez LLM
  recomienda).
- Teclas del aviso: `y`, `n`, `!` (permitir similares en la sesión), `#` (denegar similares). Aprobaciones
  guardadas: `~/.copilot/permissions-config.json`; URLs: `allowedUrls` en `~/.copilot/settings.json`.
  **Los flags nunca se guardan.**

**Atención: no hay listas allow/deny a nivel de repo.** `.github/copilot/settings.json` solo acepta una
allowlist de claves (`companyAnnouncements`, `contextTier`, `deniedUrls`, `disableAllHooks`,
`disabledMcpServers`, `disabledSkills`, `effortLevel`, `enabledPlugins`, `extraKnownMarketplaces`, `hooks`,
`includeCoAuthoredBy`, `mergeStrategy`, `model`, `respectGitignore`); todo lo demás se **ignora en
silencio**. Las reglas `permissions.deny/ask/allow` existen solo como ajustes **gestionados por la empresa
/ MDM**. **Consecuencia: una regla de equipo "nunca hagas push" que se suba al repo tiene que ser un hook
(§10).** `permissions.disableBypassPermissionsMode: "disable" | "allow-auto-only"` (usuario, gestionado o
MDM) bloquea `--yolo` y los demás flags de permitir todo.

**Carpetas de confianza.** En el primer arranque se pregunta; la lista vive en `trustedFolders` dentro de
`~/.copilot/config.json` (estado gestionado automáticamente; los ajustes de usuario están en
`settings.json`). La confianza controla **los hooks del repo, el MCP del workspace (`.mcp.json`,
`.github/mcp.json`), los ajustes de plugins del repo y `model`/`effortLevel` del repo**. **Atención: en
modo `-p` todo esto se omite en carpetas sin confianza** salvo que uses `--trust-folder`,
`GITHUB_COPILOT_PROMPT_MODE_REPO_HOOKS=true`, `GITHUB_COPILOT_PROMPT_MODE_WORKSPACE_MCP=true`,
`GITHUB_COPILOT_PROMPT_MODE_EXTENSIONS=true` o `COPILOT_ALLOW_ALL=true`. **Una puerta de CI basada en un
hook del repo no hace nada sin una de estas opciones.**

**Sandbox** (GA desde el 2026-10-07: CLI, app de Copilot, Agent Host de VS Code). Motor MXC (Seatbelt /
Bubblewrap / ProcessContainer). `/sandbox enable`, `--sandbox`, o `sandbox.enabled` en
`~/.copilot/settings.json`. Claves de política:
`sandbox.userPolicy.network.allowedHosts|blockedHosts|allowLocalNetwork|proxy`,
`sandbox.userPolicy.filesystem.deniedPaths`, `sandbox.credentials.envVars{…injectHosts}` (enmascarado de
secretos), `sandbox.auth.git`, `sandbox.auth.gh`. **El repo no puede sobrescribirlo.** El modo plan bloquea
las ediciones del proyecto en la capa de herramientas ("safety net, not a guarantee").

### VS Code
`chat.permissions.default`: **Manual** (por defecto), **Assisted**, **Allow all**. Ajustes:
`chat.tools.eligibleForAutoApproval`, `chat.tools.urls.autoApprove`, `chat.tools.terminal.autoApprove`
(`false` gana), `chat.tools.global.autoApprove`, `chat.agent.sandbox.enabled` (red permitida por defecto;
en Linux/WSL2 necesita `bubblewrap` + `socat`). **Atención:** una regla de terminal en `false` **solo exige
aprobación; no bloquea**. Para bloquear, la documentación indica un hook `PreToolUse` que devuelva
`permissionDecision: "deny"`.

### Cloud agent
Todas las herramientas preaprobadas, sin avisos; un `"ask"` de un hook se trata como `"deny"`. Firewall en
los ajustes **"Internet access"** del repositorio (cubre cloud agent + code review; no es compatible con
runners self-hosted). Salvaguardas: solo lo pueden lanzar usuarios con permiso de escritura; hace push
**solo a su propia rama `copilot/`** (o a la rama del PR cuando mencionas a `@copilot` en un PR existente);
**no puede marcar como listo, aprobar ni hacer merge**; los workflows esperan a que una persona pulse
"Approve and run workflows"; quien lo solicita no puede aprobar el PR. Protege la configuración de Copilot
y de MCP con `CODEOWNERS` + "Require review from Code Owners". Ejemplos:
[`examples/permissions/`](./examples/permissions/).

### Las capas, comparadas con Claude Code y Cursor
1. **Flags / aprobaciones guardadas** (CLI) o `chat.tools.*` (VS Code): por usuario y por máquina.
2. **Ajustes gestionados**: el único sitio para un `permissions.deny` de toda la organización.
3. **Instrucciones** (`AGENTS.md`, `.instructions.md`): criterio, no veto.
4. **Hooks**: denegación `preToolUse` por *contenido*; el único veto que se puede subir al repo.
5. **Límites estructurales**: el cloud agent no puede hacer merge; `CODEOWNERS` sobre la configuración.

> Claude Code mantiene `permissions.allow/deny` en un `settings.json` versionado; Cursor usa
> `permissions.json`; **Copilot no tiene allow/deny versionado**: la misma *política* (la persona es dueña
> de todo lo externo) se reimplementa con un hook + flags + límites estructurales.

---

## 4. Sesiones

| Necesidad | CLI | VS Code |
|---|---|---|
| Reanudar | `copilot --continue`, `--resume[=ID|nombre]`, `/resume`; cada ejecución `-p` imprime una pista `--resume` | vista Sessions |
| Nombrar | `-n NOMBRE`, `/rename` | — |
| En paralelo | `/fork` (funciona mientras trabaja), `/new worktree`, `-w`, barra lateral Sessions | varios chats, `/fork`, fork desde un checkpoint |
| Checkpoints | en **cada compactación**: `/session checkpoints` (un *resumen*, no una instantánea de ficheros) | checkpoints |
| Volver atrás | `/rewind` (alias `/undo`): solo conversación, o conversación + ficheros; no requiere git | restaurar checkpoint |
| Compartir | `/share`, `--share`, `--share-gist` (sin gists para EMU/residencia de datos) | — |
| Remoto | `/remote on`, `--remote` (GA desde el 2026-05-18: dirigir desde github.com, Mobile, VS Code) | — |
| Pasar a la nube | `/delegate` o prefijo `&` → rama + PR en borrador | Session Target → Cloud |

A diferencia de Cursor (puntos de entrada independientes), Copilot **sí** pasa sesiones entre superficies:
CLI → nube con `/delegate`, Session Target de VS Code con historial, y control remoto de una sesión de CLI
en marcha.

---

## 5. Ventana de contexto

Referencia completa: [`examples/context/`](./examples/context/).

```text
/context              # uso por System Prompt, Custom Instructions, System Tools, MCP Tools, Messages, Free Space, Buffer
/compact [focus]      # compactación manual; Esc cancela; las compactaciones no se pueden deshacer
```
- La **auto-compactación** empieza en segundo plano en torno al **80%** y se detiene en torno al 95%.
  VS Code: se desactiva con `github.copilot.chat.summarizeAgentConversationHistory.enabled`; el control de
  ventana de contexto del cuadro de chat muestra el desglose y los AI credits.
- La salida de una herramienta **> 20 KiB** se escribe en un fichero temporal; el modelo recibe la ruta +
  un avance (`COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES`).
- **Carga diferida de herramientas:** ajuste `toolSearch`; por servidor MCP, `deferTools: "auto"|"never"`.
- Instrucciones de servidores MCP: solo se cargan al principio las de los servidores en la allowlist
  (`--allow-all-mcp-server-instructions` carga todas).
- Los subagentes se ejecutan en ventanas separadas. **Atención:** los agentes personalizados lanzados como
  subagentes **no reciben las instrucciones del repo** salvo que se defina `include-custom-instructions: true`.
- Referencias en VS Code: `#codebase` lanza una búsqueda (no vuelca el código), `#file:`, `#fetch`, `#tool:<name>`.
- Ventana por defecto exacta de cada modelo: **NO DOCUMENTADA** en una tabla única.

**Palancas para un contexto ligero:** instrucciones pequeñas y estables; el material que se usa poco, en
skills (carga bajo demanda); menos servidores MCP (`disabledMcpServers`); subagentes para la investigación
ruidosa; sesión nueva entre tareas que no tienen relación. *Si puedes borrar una línea de `AGENTS.md` sin
que el agente se equivoque, bórrala.*

---

## 6. Prompt caching

**La respuesta honesta: Copilot no tiene ningún control de caché para el usuario.** Ni `cache_control`, ni
TTL, ni variable de entorno, en la CLI, VS Code o el cloud agent (NO DOCUMENTADO en ningún sitio).
Controles a nivel de SDK: NO DOCUMENTADOS.

Pero el caching ocurre y **lo pagas**: las tablas de precios facturan la **entrada cacheada** y la
**escritura en caché** por modelo (las familias de Anthropic y GPT-5.6+/GPT-6 listan costes de escritura en
caché).

Lo que *sí* puedes hacer:
- **Diagnosticar en VS Code con el Cache Explorer** (Agent Debug Logs → Summary → Cache Explorer): % de
  aciertos por turno, tokens reutilizados y la **primera divergencia** en la firma del prompt (system /
  tools / messages). Solo diagnóstico, no control.
- **Mantener estable el prefijo**: elige modelo, esfuerzo, tamaño de contexto y herramientas *antes* de la
  primera petición; no edites ficheros de instrucciones o de agentes a mitad de sesión; adjunta solo el
  contexto relevante; subagentes para la investigación lateral; `/compact` o sesión nueva a propósito.
  **El fork conserva la caché del prompt.**
- La CLI no tiene vista de caché; `/usage` muestra tokens y créditos por modelo. Existe exportación a
  OpenTelemetry; si lleva atributos de tokens de caché está NO VERIFICADO.

El mecanismo en sí (caché por prefijo, breakpoints, multiplicadores de escritura y lectura) se muestra con
la API de Anthropic en [`examples/prompt-caching/`](./examples/prompt-caching/), para entender *por qué*
funciona el consejo del prefijo estable, no porque Copilot lo exponga.

---

## 7. MCP

| Superficie | Fichero | Clave raíz |
|---|---|---|
| CLI usuario | `~/.copilot/mcp-config.json` | `mcpServers` |
| CLI workspace | `.mcp.json` (cualquier directorio del directorio actual → raíz de git), `.github/mcp.json`; **requiere confianza en la carpeta** | `mcpServers` |
| CLI por sesión | `--additional-mcp-config='{json}'` o `@file` | — |
| VS Code harness Copilot | `.mcp.json` + `~/.copilot/mcp-config.json`; reenvía los servidores elegibles de `.vscode/mcp.json` **salvo los que usan `${input:...}`** | `mcpServers` |
| VS Code harness Local | `.vscode/mcp.json` o `mcp.json` del perfil | **`servers`** (+ `inputs[]`, `sandbox{}`) |
| JetBrains | `mcp.json` desde Chat → icono de herramientas → "Add MCP Tools" (ruta en disco NO DOCUMENTADA) | `servers` |
| Cloud agent + code review | **Settings → Copilot → MCP servers** del repo (JSON en la interfaz) o `mcp-servers:` en el YAML del agente | `mcpServers` |

```jsonc
// .mcp.json (CLI + harness Copilot de VS Code). El JSON real no admite comentarios; ver examples/mcp/.
{ "mcpServers": {
    "codegraph": { "command": "codegraph", "args": ["serve", "--path", ".", "--mcp"], "tools": ["*"] },
    "serena":    { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"], "tools": ["*"] },
    "context7":  { "type": "http", "url": "https://mcp.context7.com/mcp", "tools": ["*"] }
} }
```
- **`tools` es obligatorio** en las configuraciones de la CLI y de la nube. Otros campos: `env` (`$VAR`,
  `${VAR:-default}`), `cwd`, `timeout`, `deferTools`; remotos: `headers`, `oauthClientId`, `oauthScopes`,
  `oauthGrantType: client_credentials`.
- Los nombres de herramientas llegan al modelo como `serverName-toolName`.
- **Integrados en la CLI:** `github-mcp-server` (subconjunto por defecto, sobre todo lectura),
  **`playwright`**, `fetch`, `time`. **Atención: no vuelvas a configurar Playwright.** Se desactivan con
  `--disable-builtin-mcps` / `--disable-mcp-server NAME`.
- **Atención:** `${workspaceFolder}` es solo de VS Code. Si `--path .` se resuelve respecto al directorio de
  la sesión en los servidores del workspace está NO VERIFICADO: arranca desde la raíz del repo, o usa una
  ruta absoluta en `~/.copilot/mcp-config.json`.
- **Cloud agent:** servidores por defecto GitHub (solo lectura) + Playwright (localhost). Solo
  herramientas: ni resources, ni prompts, ni servidores remotos con OAuth. Secretos: secrets/variables de
  Agents con el prefijo **`COPILOT_MCP_`**. Las herramientas se ejecutan sin aprobación → pon en la
  allowlist solo las de lectura. Instala los binarios en `.github/workflows/copilot-setup-steps.yml` (un
  único job llamado `copilot-setup-steps`, en la rama por defecto). Context7 necesita una regla de allow
  en el firewall.
- **Code review solo usa una herramienta MCP si tiene `annotations.readOnlyHint: true`.**
- Migración: `jq '{mcpServers: .servers}' .vscode/mcp.json > .mcp.json`.

Ejemplos: [`examples/mcp/`](./examples/mcp/) · activo: [`.mcp.json`](./.mcp.json).

> **La configuración da capacidad; las instrucciones dan criterio.** Instalar Serena hace que la
> herramienta exista; conseguir que el agente la use sin que se lo pidas requiere una instrucción con un
> mapa de disparadores ("CodeGraph ANTES de leer ficheros enteros; `find_referencing_symbols` SIEMPRE antes
> de renombrar"):
> [`examples/methodology/tools.md`](./examples/methodology/tools.md).

---

## 8. Skills y plugins

| Superficie | Proyecto | Personal |
|---|---|---|
| CLI | `.github/skills/`, `.agents/skills/`, `.claude/skills/` | `~/.copilot/skills/`, `~/.agents/skills/` |
| VS Code | `.github/skills/`, `.claude/skills/`, `.agents/skills/` | `~/.copilot/skills/`, **`~/.claude/skills/`**, `~/.agents/skills/` |
| Cloud agent, code review | `.github/skills`, `.claude/skills`, `.agents/skills` | — |

**Atención: la CLI no lee `~/.claude/skills/`** (VS Code sí). Copia las skills personales o crea un enlace
simbólico en `~/.copilot/skills/`, o usa `copilot skill add <dir>` / `COPILOT_SKILLS_DIRS`.

**Frontmatter.** `name` (obligatorio) + `description` (obligatorio, ≤1024 caracteres); opcionales
`argument-hint`, `allowed-tools` (CLI/nube), `user-invocable`, `disable-model-invocation`; `context: fork`
(VS Code, tras feature flag); `license` (nube). **Atención: VS Code exige que `name` esté en
minúsculas-con-guiones y sea igual al nombre de la carpeta; si no, la skill "silently fails to load"**. La
regla portable es: nombre de carpeta = `name`. **Atención:** quita las claves `trigger:` al estilo Claude
(no es una clave de Copilot; si las claves desconocidas se ignoran está NO VERIFICADO). La gramática exacta
de las entradas de `allowed-tools` está NO VERIFICADA más allá de `shell`.

**Invocación:** `/nombre-de-skill`, o automáticamente por `description`. Se gestionan con
`/skills list|info|add|remove|reload`, `copilot skill …`, "Chat: Open Customizations" en VS Code y
`gh skill` (GitHub CLI ≥ 2.90, preview).

```text
.github/skills/audit/SKILL.md            # activa en este repo → /audit sobre ex_npm
.github/skills/audit-python/SKILL.md     # → /audit-python sobre ex_app
.github/skills/deploy-staging/SKILL.md   # → /deploy-staging sobre ex_staging
```
Skills de la metodología (`day`, `atlassian`, `evidence`, `preview`, `kg`, `kg-refresh`, `methodology-plan`,
`sanitise-diff`): [`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/);
ejemplos resueltos con sus herramientas: [`examples/skills-plugins/`](./examples/skills-plugins/) +
[`examples/methodology/tools/`](./examples/methodology/tools/). `day`, `atlassian`, `evidence` y `preview`
usan credenciales locales (`preview` además Docker): **solo superficies locales, no el cloud agent**.

**Atención: la razón más fuerte para una skill es hacer cumplir una práctica, no la comodidad.** "Pull al
empezar, push al terminar" estuvo meses en un documento de operaciones sin que nadie lo siguiera;
empaquetado como `day start` / `day end`, se ejecuta y además deja el registro que hace visible un olvido.
Aquí Copilot aporta una mejora real frente a Cursor: un **hook de prompt** `sessionStart` de la CLI
`{"type":"prompt","prompt":"/day start"}` (solo en sesiones interactivas nuevas) puede *ejecutar* la rutina
en lugar de recordártela.

**Plugins.** Agent Plugins 1.0 (`plugin.json` con el esquema de agent-plugins.org) o el `plugin.json`
antiguo de Copilot; el cargador antiguo también acepta `.claude-plugin/plugin.json`, y los marketplaces de
Claude Code se pueden leer. `copilot plugin install NAME@MARKETPLACE | OWNER/REPO | URL | PATH`,
`copilot plugin marketplace add OWNER/REPO`; marketplace integrado **`awesome-copilot`**. Declarados en el
repo: `enabledPlugins` / `extraKnownMarketplaces` en `.github/copilot/settings.json`.

---

## 9. Agentes personalizados y subagentes

Referencia completa + diagrama: [`examples/subagents/`](./examples/subagents/). Activo:
[`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md).

**Ubicaciones (CLI, por orden de prioridad):** `~/.copilot/agents/` → `.github/agents/` (directorio actual
→ raíz de git; gana el más profundo) → `.claude/agents/` → raíces de `--add-dir` → plugins →
organización/empresa (`/agents` en el repo `.github` o `.github-private` de la organización). Extensión
`*.agent.md`. VS Code: `.github/agents/*.agent.md`, carpeta de usuario, `.claude/agents/*.md`.

```yaml
---
name: refactor-scout
description: Read-only blast-radius research before a rename or delete; returns a summary
tools: ["read", "search"]      # la lista de herramientas de solo lectura ES lo que impone el límite; el texto no
user-invocable: true
---
```
Frontmatter: `description` (obligatorio en CLI/nube), `name`, `tools` (alias `execute/shell/Bash`, `read`,
`edit`, `search`, `agent`, `web`, `todo`, `server/*`, `server/tool`; `[]` = ninguna), `model`,
`target: vscode|github-copilot`, `disable-model-invocation`, `user-invocable`, `mcp-servers` (nube + CLI),
solo en la CLI `include-custom-instructions`, `hooks`, `sidekick:`; **solo en VS Code Local:**
`handoffs[]`, `agents[]`, `argument-hint`. Cuerpo de 30.000 caracteres como máximo (nube).

**Subagentes integrados de la CLI:** `code-review`, `explore`, `general-purpose`, `research`,
`rubber-duck`, `security-review`, `task`. Se lanzan mediante la herramienta `task`; a los agentes en
segundo plano se les pueden mandar mensajes (`write_agent`). **Atención:** la documentación lista modelos
por defecto para los integrados (`claude-sonnet-4.6`, `gpt-5.4-mini`) que **difieren** de la tabla de
modelos por defecto de la CLI (`claude-sonnet-5.5`): una incoherencia de la documentación.

**Límites:** concurrencia según el plan (Free 2, Pro 4, Max 8, Business 16, Enterprise 32). **Atención:**
la profundidad máxima es **6** en la tabla de referencia pero **4** en la tabla de variables de entorno
(`COPILOT_SUBAGENT_MAX_DEPTH`); la documentación se contradice, verifícalo en tu versión.

**Paralelismo y equipos.** `/fleet` / `--fleet` ejecuta un plan con subagentes en paralelo; los
**sidekick agents** trabajan en segundo plano y publican en la bandeja de la sesión; `/tasks`;
`/delegate` pasa el trabajo al cloud agent. Copilot está más cerca de los Agent Teams de Claude Code que
Cursor (mensajería con `write_agent`), pero sigue sin ser el mismo modelo de líder / compañeros / bandeja
compartida.

| | Subagente (`task`) | `/fleet` | Cloud agent (`/delegate`) |
|---|---|---|---|
| Contexto | Aislado; devuelve un resumen | N subagentes aislados sobre un plan | Sesión completa en el sandbox de Actions |
| Comunicación | Resultado → padre (`write_agent` para los de segundo plano) | Orquestado por el padre | PR en borrador + comentarios |
| Coste | Bajo | Medio | Alto |
| Salida | Texto | Ediciones en tu sesión | Rama `copilot/…` + PR en borrador |

---

## 10. Hooks

Todo en [`examples/hooks/`](./examples/hooks/); activo en
[`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json).

**Soporte:** CLI y cloud agent (un esquema), VS Code (Preview, **dos implementaciones**), code review:
NO DOCUMENTADO.

**Ubicaciones (CLI, se combinan todas):** `/etc/github-copilot/policy.d/*.json` (propiedad de root) →
**`.github/hooks/*.json`** → `~/.copilot/hooks/*.json` → `hooks` en línea en `.github/copilot/settings.json`,
`.github/copilot/settings.local.json`, **`.claude/settings.json`**, `.claude/settings.local.json` →
`~/.copilot/settings.json` → `hooks.json` de plugins → `hooks:` en el frontmatter de agentes. El cloud agent
solo lee `.github/hooks/*.json` (Linux; las entradas `powershell` se ignoran; CWD `/workspace`). Los cambios
se cargan al arrancar la CLI.

```json
{ "version": 1,
  "hooks": {
    "preToolUse": [
      { "type": "command", "matcher": "bash|powershell",
        "bash": "./.github/hooks/block-external-git.sh",
        "powershell": "./.github/hooks/block-external-git.ps1",
        "cwd": ".", "timeoutSec": 10 }
    ] } }
```

**Eventos:** `sessionStart`, `sessionEnd`, `userPromptSubmitted`, `userPromptTransformed`, **`preToolUse`**,
`postToolUse`, `postToolUseFailure`, `permissionRequest` (CLI), `agentStop`, `subagentStart`,
`subagentStop`, `preCompact`, `errorOccurred`, `notification` (CLI). Tipos: `command`, `http` (https para
`preToolUse`/`permissionRequest`), `prompt` (solo `sessionStart`).

**Contrato de `preToolUse`:**
- Entrada `{sessionId, timestamp, cwd, toolName, toolArgs}`. **Atención:** `toolArgs` está tipado como
  `unknown`, pero el ejemplo de depuración de la documentación pasa una **cadena JSON**; contempla los dos
  casos.
- Salida: un objeto JSON `{"permissionDecision":"allow"|"deny"|"ask","permissionDecisionReason":"…"}`
  (motivo obligatorio para deny; `modifiedArgs` opcional).
- Códigos de salida: `0` se interpreta stdout · **`2` = deny** · cualquier otro distinto de cero = **deny
  que falla en cerrado** para `preToolUse`.
- **Atención: los timeouts fallan EN ABIERTO, en todos los eventos, incluidos los hooks de política** (por
  defecto 30 s). Mantén rápidos los hooks que bloquean.
- `agentStop` / `subagentStop`: `{"decision":"block","reason":"…"}` fuerza otro turno (protección tras 8):
  una puerta de "verificar antes de parar".
- Interruptor general: `disableAllHooks: true`.
- Los alias en PascalCase (`PreToolUse`) cambian el payload a snake_case al estilo VS Code y a la semántica
  de matcher de Claude (`bash`/`powershell` → `Bash`, `view` → `Read`, `task` → `Agent`).

**Harness Local de VS Code: esquema distinto.** Ficheros: `.github/hooks/*.json`, `~/.copilot/hooks/*.json`,
`.claude/settings*.json` (solo con `chat.useClaudeHooks`, desactivado por defecto), frontmatter de agentes,
plugins. Eventos en PascalCase; entrada `{tool_name, tool_input, tool_use_id}`; salida
`{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"…"}}`;
salida 2 = error bloqueante. Los ficheros en formato Copilot se interpretan allí, pero los payloads en
ejecución usan el esquema Local.

**La receta portable de bloqueo (el hook de este repo):** un único script lee las dos formas de payload
(`toolArgs.command` como cadena u objeto, o `tool_input.command`), filtra las herramientas de shell dentro
del propio script (Local puede ignorar el matcher; NO VERIFICADO), deniega `git push`,
`gh pr create|merge|ready`, `gh api …/merge`, `gh release create`, `terraform apply`, `kubectl apply`,
`helm upgrade|install`, `aws … deploy`, imprime las dos formas de salida y **sale con código 2**, la única
señal de bloqueo documentada en los dos esquemas. Si no hay coincidencia imprime `{}` y sale con 0; a
propósito **no** responde `"allow"`, que podría auto-aprobar la herramienta.

```bash
bash .github/hooks/test-block-external-git.sh          # 16 casos offline, incluido un canario de respuesta conocida
PS=1 bash .github/hooks/test-block-external-git.sh     # también la versión PowerShell
```

**Atención:** dos huecos que se cierran por política, no con este hook: **`/pr create|auto|automerge`** son
comandos propios de la CLI; si pasan por `preToolUse` está **NO VERIFICADO** → decláralos solo para
personas en las instrucciones y prueba el hook contra ellos en tu versión. Y **en `-p`/CI, los hooks del
repo no se cargan en una carpeta sin confianza** → `--trust-folder`. Cinturón y tirantes:
`--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'`.

---

## 11. Automatización

Ver [`examples/automation/`](./examples/automation/).

**`copilot -p` en GitHub Actions:**
```yaml
permissions:
  contents: read
  copilot-requests: write          # vía GITHUB_TOKEN; o COPILOT_GITHUB_TOKEN = PAT fine-grained
steps:
  - uses: actions/checkout@v4
  - run: npm install -g @github/copilot
  - run: |
      copilot -p "Review the diff against main and list risky changes" -s --no-ask-user \
        --trust-folder \
        --allow-tool='shell(git:*)' \
        --deny-tool='shell(git push)' --deny-tool='shell(gh pr)'
    env:
      GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
`COPILOT_TASK_WAIT_TIMEOUT_SECONDS` (por defecto 600) limita la espera de las tareas en segundo plano.

**GitHub recomienda GitHub Agentic Workflows** (`github/gh-aw`) frente a pasos `copilot` en crudo
(salvaguardas, `GITHUB_TOKEN` por defecto).

**Cloud agent vía REST (preview pública, solo tokens user-to-server):**
```bash
curl -X POST https://api.github.com/agents/repos/OWNER/REPO/tasks \
  -H "Authorization: Bearer $USER_TOKEN" \
  -d '{"prompt":"Fix the flaky health test","base_ref":"main","create_pull_request":true}'
# listar: GET /agents/repos/OWNER/REPO/tasks · GET /agents/tasks
```
Además: asignar un issue a Copilot (REST/GraphQL); **Automations** (panel Agents → Automations del repo;
disparadas por calendario o por eventos; por defecto se ignoran los eventos de usuarios sin permiso de
escritura); integraciones (Slack, Teams, Jira, Linear, Azure Boards, Raycast); `/every` y `/after` en la CLI
(experimentales).

**Copilot SDK:** `@github/copilot-sdk` (npm), `github-copilot-sdk` (pip, `from copilot import CopilotClient`),
Go, .NET, Java. Flujo: `new CopilotClient()` → `createSession({model:"auto"})` → `sendAndWait({prompt})`;
los hooks programáticos (`onPreToolUse`) devuelven `permissionDecision`. Controles de caché del SDK: NO
DOCUMENTADOS.

**Automatización del code review:** regla de ruleset **"Automatically request Copilot code review"**
("Review new pushes", "Review draft pull requests"); esfuerzo Lite o Balanced; lee
`copilot-instructions.md`, las instrucciones por ruta, `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `REVIEW.md` y
`.github/skills` **desde la rama head**, así que un PR puede cambiar las instrucciones de su propio revisor:
protégelas con CODEOWNERS. **Atención: las aprobaciones de Copilot** (preview, desactivadas por defecto)
pueden contar como aprobaciones obligatorias; **déjalas desactivadas** si la persona es dueña del merge.

**Servidor ACP:** `copilot --acp`.

---

# SESIÓN 2 — La metodología

## 12. Metodología

El material de fondo (flujo de 11 etapas, ejemplo real de principio a fin, prevalencia de herramientas)
está en [`examples/methodology/`](./examples/methodology/). Resumen:

### El flujo real ([`WORKFLOW.md`](./examples/methodology/WORKFLOW.md))
Agente = colaborador disciplinado; la autonomía se gana decisión a decisión. 11 etapas encadenadas por
**puertas deterministas**: orientarse (skill `kg` + historial + estado) → triaje de entrada contra el
**contrato de salida** → regresión frente a problema preexistente → investigar con un **oráculo
determinista** (antes de la llamada de pago al LLM) → **modo plan** (`/plan`, impuesto en la capa de
herramientas) + acuerdo humano → implementar: TDD RED→GREEN → verificar (unitarios + acotados + regresión +
contrato a través del *wrapper* Y dentro de la imagen desplegada) → documentar → **sanitizar** (skill
`sanitise-diff` sobre las líneas añadidas) → handoff (el agente **no** hace push/PR/merge/deploy: hook
`preToolUse` + instrucciones; lo hace la persona) → revisión (Copilot code review, **aprobaciones
desactivadas**) + persistir (`kg-refresh` si aplica). Diagrama: [`flow.png`](./examples/methodology/flow.png).
Caso de estudio: [`REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

> **La puerta de salida son CINCO comprobaciones** (no "los tests pasan"):
> **(0) validar el instrumento de medida**: cualquier diagnóstico que informe una decisión de entrega se
> ejecuta primero contra un **caso de respuesta conocida**, registrado junto al hallazgo; nunca envuelvas
> la medición en tu propio `try/except → return False`;
> **(1) reproducir en la etapa de salida real**: el *wrapper* que reconstruye el contrato, no una función
> interna; **(2) la salida cumple el contrato en la LISTA de miembros, nunca en un total**; **(3) verificar
> dentro de la imagen desplegada**; **(4) mirar la salida** renderizada, a ojo, antes del PR. Los tests en
> verde no prueban lo que se entrega. Mismo papel que las puertas de Claude Code y Cursor: solo cambia qué
> agente la ejecuta.
>
> **Cinco formas en que una puerta en verde no demuestra nada** (nos han pasado las cinco): un
> **instrumento roto** (una sonda que se traga su propio error y devuelve un "no" uniforme y plausible);
> **un total que cuadra** (un elemento añadido por error y otro eliminado por error se compensan; compara
> ids, mide deltas); **una puerta que no podía fallar** (un detector que salta en 0 de 190 documentos del
> corpus se lee igual tanto si funciona como si está roto; dilo); **un canario que nunca aplicó la
> perturbación real** (el test sintético recuperó el 100%, el cambio real recuperó menos del 1% porque
> tocaba lo que el test nunca tocó); **una puerta estructural leída como semántica** (todos los grupos
> casaban, cero huérfanos, y el 56% de los nombres arrastrados eran incorrectos; programa la lectura
> humana).
>
> **El contrato de salida es un documento vivo.** Cuando un cambio altera lo que se emite: **cumple**,
> **revisa** la regla en el mismo cambio, o **registra** por qué queda fuera de alcance. El silencio no es
> una opción. Cita las reglas por un identificador estable, nunca por una ruta local.
>
> **¿De dónde sale el número esperado?** "El otro entorno devuelve X" es evidencia sobre ese entorno,
> nunca una especificación.

### Prevalencia de herramientas ([`tools.md`](./examples/methodology/tools.md))
`AGENTS.md` y `.github/instructions/01-tool-prevalence.instructions.md` dicen **qué herramienta y en qué
orden** (de barata a cara, de determinista a probabilística):
```
Orient       -> kg skill (ticket graph) · STATUS.md/ledgers · git · gh (read-only)   (no inference)
Navigate     -> CodeGraph codegraph_explore (MCP) — source + paths + blast radius, treat as ALREADY read
Refactor-chk -> Serena find_referencing_symbols (MCP) — MANDATORY before rename/delete
Diagnose     -> deterministic oracle (parser/validator/_diag_*.py)
Environment  -> cloud CLI, read-only
Contract     -> Playwright (built into the Copilot CLI) / browser dev tools against the output endpoint
Deployed     -> Docker: repro inside the runtime image
Only at the end -> the agent turn, to VERIFY the fix (not to diagnose)
```
(Se deja en inglés porque es el texto literal de la instrucción que se distribuye.)

### Permisos del método (misma política, tercer mecanismo)
Claude Code: allowlist versionada. Cursor: `permissions.json` + rules + hooks. **Copilot: sin allow/deny
versionado** → (1) instrucciones para la prevalencia y el "no push", (2) flags de CLI por usuario o
`chat.tools.*` de VS Code, (3) **el hook `preToolUse`** como veto que se sube al repo, (4) límites
estructurales del cloud agent, (5) `permissions.deny` gestionado para la política de la organización.

---

## 13. Las herramientas del método

Instalación + smoke tests: [`AGENT_SETUP_TOOLS.md`](./docs/ai-agents-code-methodology/AGENT_SETUP_TOOLS.md).

### CodeGraph ([`examples/codegraph/`](./examples/codegraph/))
Índice con Tree-sitter → SQLite en `.codegraph/` (sin API keys). Símbolos + rutas de llamada + radio de
impacto + indicadores de cobertura de tests, en un solo viaje.
```bash
codegraph init ; codegraph sync ; codegraph explore "<symbol|question>"
```
Se registra en `.mcp.json` con `"tools": ["*"]` (§7); para el cloud agent, instálalo en
`copilot-setup-steps.yml` y pega el JSON del servidor en los ajustes del repo. Es la **primera** herramienta
de navegación; trata su salida como ya leída. En WSL2 sobre `/mnt`, el watcher puede perder cambios →
`codegraph sync`.

### Serena ([`examples/serena/`](./examples/serena/))
Navegación semántica basada en LSP. `find_referencing_symbols` es la comprobación precisa antes de
renombrar o borrar (distingue métodos con el mismo nombre por su clase). Complementa a CodeGraph. El agente
de solo lectura [`refactor-scout`](./.github/agents/refactor-scout.agent.md) empaqueta CodeGraph → Serena →
grep.

**Copilot no hereda Serena de otros agentes.** En la prueba de campo del 2026-10-28 faltaba solo porque
nunca se había registrado para Copilot. Añadirlo a la configuración personal lo arregló:
```jsonc
// ~/.copilot/mcp-config.json (haz antes una copia)
{ "mcpServers": {
    "serena": { "command": "uvx", "args": ["--from", "git+https://github.com/oraios/serena", "serena", "start-mcp-server"], "tools": ["*"] }
} }
```
Medido tras reiniciar, en Copilot de VS Code: funcionaron `initial_instructions`, `find_symbol` y
`find_referencing_symbols`; `safe_delete_symbol` se negó a borrar un método referenciado y listó sus 5
referencias; `rename_symbol` informó de 7 cambios entre la definición, un llamador y tests en 3 ficheros
(revertido con git). No se probaron `replace_symbol_body` ni las herramientas de inserción.
- **Atención:** la primera llamada de cada sesión puede agotar el tiempo mientras arranca el servidor de
  lenguaje de Python (~1 min). Reintenta.
- **Atención:** las ediciones llegan al disco un poco después de que la herramienta responde: un `git diff`
  inmediato puede salir vacío.
- Serena guarda su caché en `.serena/` (ignorado) y puede listar referencias dentro de copias en `data/`
  (también ignorado).
- Orden de respaldo cuando Serena no está: CodeGraph → usos de Pylance → grep.

### GSD ([`examples/gsd/`](./examples/gsd/)): solo Claude Code
Ciclo por fases con estado versionado en `.planning/` y subagentes especializados. **No hay port a
Copilot.** Las piezas más cercanas en Copilot:
```
/plan, --plan, Shift+Tab           -> puerta de discusión -> plan (impuesto en la capa de herramientas)
--plan --mode autopilot            -> planificar y ejecutar, limitado por --max-autopilot-continues / --max-ai-credits
/fleet                             -> ejecución del plan por oleadas en paralelo
.github/agents/{planner,executor,verifier}.agent.md -> los roles gsd-*
agentStop hook decision: block     -> puerta de "verificar antes de parar"
VS Code handoffs (solo Local)      -> botones plan -> implementar
Spec Kit (github/spec-kit)         -> plantillas guiadas por especificación; solo fuentes de terceros, versión NO VERIFICADA
data/changes/                      -> el almacén de estado (no .planning/)
```
> **Honestidad:** este proyecto no usa GSD; usa el flujo de 11 etapas + `data/changes/`. GSD tiene más
> sentido en un proyecto nuevo con varios componentes.

---

## 14. Transferir la metodología

Material: [`docs/ai-agents-code-methodology/`](./docs/ai-agents-code-methodology/):
[`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md) (reescrito para las
superficies de 2026) + la superficie lista para copiar [`copilot/`](./docs/ai-agents-code-methodology/copilot/) +
[`templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md`](./docs/ai-agents-code-methodology/templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md).

**Lo que viaja sin cambios:** plan → acuerdo → implementar · verificar contra el contrato del consumidor ·
resolver la clase general · rastro duradero · la persona es dueña de todo lo externo.

**Lo que cambia, la superficie:**
```
CLAUDE.md (+ jerarquía)          -> AGENTS.md + .github/copilot-instructions.md + .github/instructions/*.instructions.md
                                    (la CLI también lee CLAUDE.md y .claude/rules, pero NO ~/.claude/CLAUDE.md)
~/.claude/skills/                -> .github/skills/ o ~/.copilot/skills/ (la CLI NO lee ~/.claude/skills)
permisos en settings.json        -> sin allow/deny versionado: hook + --deny-tool + ajustes gestionados
Hooks (PreToolUse, exit 2)       -> .github/hooks/*.json preToolUse; exit 2 / permissionDecision deny
Modo plan                        -> /plan, --plan (impuesto)
Subagentes + Agent Teams         -> .github/agents/*.agent.md + integrados + /fleet + sidekicks
claude -p                        -> copilot -p (+ --trust-folder en CI)
Auto-memory / claude-mem         -> Copilot Memory (nube, caduca a los 28 días) / /memories de VS Code / /chronicle; solo complementos
.mcp.json                        -> .mcp.json con "tools" obligatorio (+ .vscode/mcp.json "servers" para Local)
Agent SDK                        -> @github/copilot-sdk / github-copilot-sdk
```

**La regla que pasó a poder imponerse, y los dos agujeros nuevos.** "El agente no hace merge ni deploy
directo" antes era solo una política. Ahora: un hook de denegación `preToolUse` versionado (funciona en la
CLI, el cloud agent y el harness Copilot de VS Code), flags `--deny-tool` (deny gana a `--yolo`),
`permissions.disableBypassPermissionsMode`, los límites estructurales del cloud agent (su propia rama
`copilot/`, no puede aprobar ni hacer merge) y CODEOWNERS sobre `.github/hooks/**`, `.github/agents/**`,
`.github/skills/**`, `.mcp.json`, `AGENTS.md`. Agujeros nuevos que hay que cerrar: **`/pr auto` y
`/pr automerge` de la CLI** (cobertura del hook NO VERIFICADA → solo para personas en las instrucciones,
pruébalo en tu versión), y las **aprobaciones de Copilot code review** (preview, desactivadas por defecto)
→ **déjalas desactivadas**.

**Arranque en un repo de destino:** ver
[`TRANSFER_AND_BOOTSTRAP.md`](./docs/ai-agents-code-methodology/TRANSFER_AND_BOOTSTRAP.md) y
`scripts/bootstrap-new-repo.ps1.txt` + `scripts/bootstrap-copilot-repo.ps1.txt` (se distribuyen como
`.ps1.txt` para esquivar el bloqueo de contenido activo en el correo).

**Alternativa sin grafo de conocimiento de tickets** (el 80% del valor): `STATUS.md` con lo más reciente
primero + carpetas por ticket · búsqueda léxica por síntoma/símbolo/campo del contrato · historial de
commits (solapamiento de ficheros) · una sección corta de "zonas peligrosas". Copilot Memory y
`/chronicle` pueden ayudar a recordar, nunca como registro.

**Checklist del primer día:** `STATUS.md` · 3–5 invariantes en `SHARP_EDGES.md` · el contrato de salida ·
comandos de test acotados · instalar el hook y ejecutar su test · un issue completo RED→GREEN con
verificación del contrato.

---

## 15. Sincronización de máquinas

Dos mecanismos que no compiten entre sí: **(A)** tarball + USB para levantar una máquina completa; **(B)**
almacenamiento de objetos compartido (S3) para el registro de ingeniería del día a día.

### A. Puesta en marcha completa: tarball + USB (asimétrico)
Recorrido sanitizado: [`examples/methodology/machine-sync.md`](./examples/methodology/machine-sync.md);
runbooks en [`docs/synchro/`](./docs/synchro/). Adaptación:
```
Claude Code                             Copilot
Puntero en CLAUDE.md                    Puntero en AGENTS.md / en un .instructions.md
Empaquetar ~/.claude (skills, memoria)  Empaquetar ~/.copilot (skills, agentes, hooks, mcp-config.json, settings.json);
                                        Copilot Memory vive en la nube y no es un fichero: decide explícitamente qué viaja
MCP codegraph en ~/.claude.json         Volver a fijar --path en ~/.copilot/mcp-config.json (ruta absoluta en el portátil)
Skill /kg-refresh de Claude             Skill kg-refresh en ~/.copilot/skills + el mismo kg_refresh.sh
```
**Atención:** no metas `~/.copilot/config.json` en el tar a ciegas: contiene el estado de autenticación y
de `trustedFolders` de *esa* máquina; vuelve a iniciar sesión y a dar confianza en el destino. **Salida =
copia completa; entrada = solo el delta** (`git fetch` + un tarball pequeño del `data/` ignorado por git,
que aplica un agente siguiendo un `INSTRUCTIONS.md` escrito para él, con copias de seguridad primero y
STOP ante la duda). El agente nunca hace push, merge ni abre PRs durante la aplicación: el hook lo impone.

### B. El registro compartido: `data/` sobre S3
Runbook completo: [`docs/synchro/s3-sync/README.md`](./docs/synchro/s3-sync/README.md); scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).
```bash
./data-pull.sh            # vista previa  ->  ./data-pull.sh --go
./data-push.sh            # vista previa  ->  ./data-push.sh --go
./mount-data.sh           # vista compartida en vivo, SOLO LECTURA
./validate.sh             # una máquina no está lista hasta que esto imprime MACHINE READY
```

| Regla | Por qué |
|---|---|
| El alcance crece por fases revisadas | Cada ampliación es un evento de seguridad: primero escanea, prueba el escáner con un canario y después reconcilia. |
| Escribir mediante sync, leer mediante montaje de solo lectura | El almacenamiento de objetos no tiene bloqueos ni renombrado atómico. |
| Dry-run por defecto; `--delete` aparte | Un espejo exacto desde una vista obsoleta borra el push de un compañero. |
| Borrar a propósito = una herramienta con lápida | `delete.sh` (solo el publicador) + `_deletions.jsonl`; un push que no puede leer la lista se niega. |
| Docs = fuente; el grafo es derivado, **por fichero, no por carpeta** | Una capa de nombres escrita a mano vive dentro del árbol generado; trátala como fuente. |
| Los pares se mueven juntos | Marca la capa con una huella de su grafo; falla de forma visible si no coinciden. |
| Coordinar sin bloqueos | Un fichero de petición por contribuidor en una cola. |
| **Atención:** la recuperación caduca (30 días) | Haz pull antes de editar, push de lo que cambiaste, e informa de las pérdidas dentro del mes. |
| Los ledgers compartidos son solo de añadir | Reescribir uno borra en silencio la línea de otra persona. |
| **Atención:** protege AMBAS direcciones | Un pull te pisa a ti; un push pisa a tu compañero: niégate (exit 4), no te limites a avisar. |
| Un solo escritor por fichero de cada máquina | Si no, el primer síntoma es una conclusión equivocada sobre una persona. |
| Una protección que da falsas alarmas enseña a saltársela | La tasa de falsos positivos es una propiedad de seguridad. |

**La máquina tiene un rol.** `MACHINE_NAME` / `MACHINE_ROLE` en `config.env`, `identity.sh --write`
genera un `IDENTITY.md` local de la máquina, y las instrucciones siempre cargadas apuntan a él. Con Copilot,
cárgalo mediante `~/.copilot/copilot-instructions.md` (personal, local de la máquina) o un hook
`sessionStart`.

**Y el hábito necesita un mecanismo.** `day start` / `day end` empaquetados como una skill que conoce el
rol de la máquina ([`examples/skills-plugins/`](./examples/skills-plugins/)) y, con la CLI de Copilot,
opcionalmente *forzados* por un hook de prompt `sessionStart`. Cada paso peligroso está detrás de una
pregunta que responde primero; si la respuesta es ambigua, se detiene y pregunta.

> **Atención: una protección de seguridad puede desactivar en silencio el instrumento que demuestra el
> hábito.** Una instantánea previa al pull instalaba su propio `trap … EXIT`; bash solo guarda un trap
> EXIT, así que sustituyó al que escribía el registro de actividad: los dry-runs seguían registrándose y
> ningún pull real quedó registrado durante dos días. Pregúntate qué más reclama el mismo recurso de una
> sola plaza; el camino real y el del ensayo son caminos de código distintos.

> **Atención: mide una optimización antes de citarla.** Se predijo "de minutos a segundos"; se midió
> 212 s → 123 s.

> **Prueba de campo 2026-10-28 (Copilot, jornada real).** `day start` detectó que `LOCAL_DATA` en
> `config.env` apuntaba a otro checkout **antes** de cualquier pull; tras un arreglo solo local, se regeneró
> `IDENTITY.md`, la simulación de `changes` no encontró nada que subir y el pull se ejecutó con snapshot
> previo, apartó los ficheros borrados aguas arriba y no usó `--delete`. `day end` solo se ejecutó como vista
> previa simulada de la publicación más el registro de actividad en solo lectura. Esa vista previa mostró dos
> ficheros de `knowledge-graph/_corpus` que se habrían subido pese a la regla de contribuidor: una
> publicación real debe excluirlos, escribir antes la fila de STATUS y no usar nunca `--delete`. Un
> `canary_leadin_diff.json` local sobrescrito por una re-ejecución se restauró desde el bucket con un
> `s3 cp` de solo lectura. Ver [§17](#17-prueba-de-campo-2026-10-28).

---

# CONTINUACIÓN DE LA SESIÓN 2 — El grafo de conocimiento de tickets (graphify)

## 16. Grafo de conocimiento de tickets

**Tecnología: `graphify`, no CodeGraph.** CodeGraph indexa el *código*; este grafo indexa la **memoria del
proyecto**: informes por ticket, sharp edges, runbooks, notas de memoria. Pipeline:
[`docs/knowledge-graph/`](./docs/knowledge-graph/); narrativa: [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

| Pieza | Qué es |
|---|---|
| skill `kg` | `explain` / `path` / `find`: determinista, **sin LLM** |
| skill `kg-refresh` | `prepare` → extracción semántica (paso del agente) → `finalize` |
| [`kg_query.sh`](./docs/knowledge-graph/kg_query.sh) | Wrapper sobre `graphify explain`/`path` en `output/graph.json` + `find` |
| [`kg_refresh.sh`](./docs/knowledge-graph/kg_refresh.sh) | Extremos deterministas: `prepare` / `finalize` / `bootstrap` / `snapshot-memory` / `restore-memory` |
| `build_manifest.py` / `stage_corpus.py` | Enumeran y preparan el corpus con nombres que conservan la procedencia |
| `test_kg_*.py` | Los extremos están probados: es infraestructura, no algo de un solo uso |

> **Nota de sanitización.** El grafo interactivo incluido en `docs/knowledge-graph/output/` es una
> instantánea más antigua y sanitizada (507 nodos · 672 aristas · 35 comunidades). La captura del deck
> [`presentation/kg_graph.png`](./presentation/kg_graph.png) se ha actualizado a partir de la instantánea
> del grafo de ILS_2: 3.921 nodos · 8.508 enlaces · 178 comunidades · 73 hiperaristas (94,3% de enlaces
> `EXTRACTED`). Muestra solo la topología; se omiten etiquetas y metadatos porque el grafo original contiene
> identificadores internos. No copies la salida del grafo original en este repositorio del curso.

```bash
kg_refresh.sh prepare        # manifiesto -> preparar _corpus/ -> scratch FUERA del repo
                              # extracción semántica (agente, subagentes en paralelo) -> HTML/JSON/informe
kg_refresh.sh finalize       # copiar artefactos a output/ + comprobación de fugas
kg explain <ticket|topic>    # vecinos: el uso más habitual
kg path <A> <B>              # camino más corto
kg find <substr>             # descubrir el nombre exacto de un nodo
```

**Con Copilot.** `kg` es shell determinista, un port directo: `.github/skills/kg/SKILL.md` (o
`~/.copilot/skills/kg/`, porque la CLI no lee `~/.claude/skills`). `kg-refresh` envuelve el paso semántico
de graphify, que en Claude Code se reparte entre subagentes en paralelo. Con la CLI de Copilot ese mismo
reparto corresponde a subagentes integrados mediante la herramienta `task` o `/fleet` (concurrencia según
el plan: Pro 4, Max 8, Business 16); VS Code Local usa `runSubagent`. O sigue ejecutando el paso semántico
desde Claude Code: a los extremos les da igual qué agente trabajó en medio. La **protección de "solo el
publicador" se queda en el script**, no en el prompt. No es tarea para el cloud agent: el corpus vive en el
`data/` ignorado por git, que el cloud agent nunca ve.

**La trampa que sostiene el pipeline:** graphify respeta `.gitignore` y todo `data/` está ignorado → el
corpus se prepara en un scratch fuera del repo y los artefactos se copian de vuelta. Por eso `kg-refresh`
es una skill y no un script.

**Punto de enganche:** la etapa 1 (Orientarse) de `00-methodology-core.instructions.md`: ejecuta
`kg explain <ticket|topic>` antes de hacer grep en `data/changes/`. `EXTRACTED` = fiable; `INFERRED` = una
pista que hay que verificar. La ganancia real es la capacidad de recordar en las zonas densas.

> **Atención: nota de campo (2026-10-28).** `/kg count edges` en Copilot devolvió metadatos de tamaño del
> grafo (3.921 nodos / 8.508 aristas), pero `kg_query.sh` solo admite `explain`, `path` y `find`. Llamar al
> script con `count edges` no es una prueba de recuento válida; no la presentes como tal.
> `kg_query.sh find <substr>` funcionó (22 coincidencias). No regeneres el grafo desde una máquina
> contribuidora.

> **Atención: "derivado" es una propiedad del fichero, no de la carpeta.** Dentro del árbol generado vive
> un fichero escrito a mano (los nombres curados de las comunidades) que nada regenera; en una
> reconstrucción real sobrevivió **menos del 1%**. Clasifica por fichero: fuente / derivado / escrito a mano
> dentro de lo derivado (trátalo como fuente). Marca la capa con una huella de su grafo; una sincronización
> por fichero no puede expresar atomicidad.

> **Coste, con honestidad.** "Sin LLM al consultar" no significa "gratis": el razonamiento se paga una vez,
> al construir; cada consulta `kg` es una búsqueda determinista cuyo único coste es que el agente lea una
> salida corta. Se paga una vez y se cobra en cada uso, desde cualquiera de los cuatro agentes.

---

## 17. Prueba de campo 2026-10-28

La metodología y todas sus skills se ejecutaron con el **agente de GitHub Copilot en VS Code** en una
jornada real que no era de producción, con algunas restricciones deliberadas. Informes completos:
[`COPILOT_METHODOLOGY_LIVE_VALIDATION_2026-10-28.md`](./docs/ai-agents-code-methodology/field-reports/COPILOT_METHODOLOGY_LIVE_VALIDATION_2026-10-28.md)
(skill a skill) y
[`COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md`](./docs/ai-agents-code-methodology/field-reports/COPILOT_SST-6880_METHOD_REPLAY_2026-10-28.md)
(un ticket repetido a través de los gates). Son resultados **medidos** que sustituyen la afirmación
anterior de que "se espera paridad". No significan que se haya publicado, fusionado o subido nada.

### Skill a skill

| Skill / herramienta | Resultado | Qué se ejecutó de verdad | Límites |
|---|---|---|---|
| `day` start | PASA, acotado | Identidad + AWS no productivo comprobados; destino de sincronización obsoleto corregido (solo local, autorizado por el usuario); simulación limpia; pull protegido con snapshot, sin `--delete` | `git fetch` bloqueado (sin credenciales de GitHub no interactivas) |
| `day` end | MÍNIMO | Vista previa simulada de la publicación + registro de actividad en solo lectura | Sin subida; la vista previa marcó 2 ficheros de `_corpus` que hay que excluir |
| `evidence` | PASA, en vivo y solo lectura | 2 ejecuciones de desarrollo: fuente, DOCX resaltado, resultado bruto de la Lambda, log saneado; los hashes de la fuente coinciden | No es el contrato de consumo `get-sl-upload-status` (necesita una sesión de la aplicación) |
| `preview` / visor | PASA, resultados capturados | Frontend local + APIs simuladas mostraron los resultados capturados; contenedores eliminados después | A propósito no es el comando normal de preview, que re-extrae y puede gastar llamadas al modelo |
| `atlassian` | PASA | Suite simulada de 62 tests; 3 GET de solo lectura aprobados (2 Jira, 1 metadatos de Confluence) | Sin cuerpos de página, comentarios, exportaciones ni escrituras |
| `kg` | PASA, acotado | `find` con 22 coincidencias; `/kg count edges` solo devolvió metadatos | Ver la nota de §16 sobre `count` |
| `kg-refresh` | FUERA DE ALCANCE | — | Excluido por el usuario |
| `methodology-plan` | PARCIAL | Plan sintético de seis partes; gates 1–5 repetidos sobre el ticket real | No se hizo el acuerdo completo con la plantilla |
| `sanitise-diff` | PASA | Fixture desechable y después el diff real del arreglo (134 líneas añadidas) en un repo desechable | 1 id de ticket interno en un docstring de test (convención del repo) |
| CodeGraph | PASA, acotado | Consulta de un símbolo: un fichero con sus llamadores y dependencias | Navegación, no cobertura de tests |
| Serena | PASA, en vivo | Ver [§13](#13-las-herramientas-del-método) | Primera llamada lenta; las ediciones llegan tarde |
| Context7 | NO PROBADO | Conectado según el usuario | La sesión no expuso ninguna herramienta |

### Un ticket, repetido

En un clon de respaldo, rama `replay/…-pre-fix` creada desde el commit anterior al arreglo original:

| Gate | Resultado |
|---|---|
| Causa raíz | La misma que con los agentes anteriores: `is_potential_title` rechaza un título de 13 palabras (`TITLE_LEN_MAX` = 13) y `_underlined_lead_in_titles` se detiene en un número tecleado sin subrayar (`59.`), así que `_is_acceptable_title` nunca lo rescata. **No fue a ciegas**: el plan del arreglo se había leído antes. |
| RED | 14 tests nuevos: 5 fallan en el comportamiento buscado (aserciones, no errores de importación), 9 guardas pasan |
| GREEN | Una función, ~18 líneas añadidas + 2 regex, sin cambiar umbrales, prompts ni configuración; 14/14 nuevos + 17/17 existentes = 31 pasan |
| Radio de impacto | Diff de entradillas sin LLM sobre el corpus local, primero el canario: 8 ficheros ganan entradillas, exactamente 1 entrada cambia un resultado; las cifras coinciden con el barrido registrado en el ticket |
| Imagen desplegada | Re-extracción real con LLM en la imagen desplegada (rama montada en solo lectura, sobre una copia): 94 cláusulas, pasan las 6 comprobaciones |
| Regresión | Subconjunto relacionado: 235 pasan, 1 omitido, 0 fallan. Suite completa: 1552 → 1566 pasan (+14), los mismos 3 fallos y los mismos 5 errores de recogida (broker 0.1.3 frente a v0.1.5 en el venv del host; esos ficheros no se ejecutaron) |
| Saneado | 0 nombres (lista de 11 entradas), secretos, ids de cuenta, correos o atribución; 1 id de ticket interno |
| Cierre | Arreglo y tests revertidos y archivados (`fix.diff`, el test como `.txt`); rama de repetición borrada; nada confirmado ni subido |

Pendiente en el flujo real: la comprobación de re-subida en la función desplegada tras un merge, y una
ejecución a ciegas sobre un ticket no visto.

### Hallazgos prácticos

- Las importaciones en frío del extractor desde `/mnt/d` tardan ~5 min (limitadas por E/S; ~1,5–2 min con
  caché). Un tiempo de espera corto ahí es un límite de la herramienta, no un defecto.
- Las ejecuciones locales necesitan valores ficticios de `SQS_LAMBDACLIENTSL` / `SQS_MATTERRPCSERVICE`; no se
  usa la red.
- El extractor reescribe el DOCX que abre: ejecuta siempre sobre una copia y comprueba después el mtime del
  original.
- Si al venv del host le falta una versión de una dependencia, ejecuta dentro de la imagen desplegada con la
  rama montada en solo lectura, como hizo la segunda ejecución del propio ticket.
- Repetir un diff del corpus sobrescribe el fichero de salida registrado: guarda antes una copia exacta.
- Las carpetas de evidencia contienen documentos de clientes. Se quedan en local e ignoradas; no las copies
  nunca a slides ni a commits.

---

## A. Tabla de equivalencias: Claude Code → Cursor → Copilot

| Concepto | Claude Code | Cursor | GitHub Copilot (oct. 2026) |
|---|---|---|---|
| CLI / headless | `claude -p` | `agent -p --trust [--force]` | `copilot -p "…" -s [--allow-tool …] [--trust-folder]`; stdin por tubería OK |
| Agente asíncrono en la nube | (web / remoto) | Background/Cloud Agents | **Copilot cloud agent** (asignar issue, `/delegate`, `&`, `POST /agents/repos/{o}/{r}/tasks`) |
| Memoria siempre cargada | `CLAUDE.md` | `AGENTS.md` + `.cursor/rules` `alwaysApply` | `AGENTS.md` y/o `.github/copilot-instructions.md` (la CLI también `CLAUDE.md`/`GEMINI.md`) |
| Reglas acotadas | `.claude/rules` `paths:` | `.mdc` `globs` | `.github/instructions/*.instructions.md` `applyTo` (+ `excludeAgent`); la CLI también `.claude/rules` |
| Import inmediato | `@path` | `@file` en `.mdc` | `@path` en AGENTS.md/CLAUDE.md/copilot-instructions.md (CLI) |
| Memoria personal | `~/.claude/CLAUDE.md` | user rules | `~/.copilot/copilot-instructions.md`, `~/.copilot/instructions/` |
| Memoria automática | `MEMORY.md` / claude-mem | Cursor Memories | Copilot Memory (nube, preview) / `/memories` de VS Code / `/chronicle` |
| Prompts reutilizables | comandos slash / skills | skills | skills (todas las superficies); prompt files (VS Code Local, VS, JetBrains) |
| Permisos | `settings.json` `permissions.allow/deny` | `permissions.json` | `--allow-tool/--deny-tool`; `permissions-config.json` guardado; a nivel de repo solo mediante ajustes **gestionados**; `chat.tools.*` en VS Code |
| Modo bypass | `--dangerously-skip-permissions` | `--yolo`/`--force` | `--yolo`/`--allow-all`; se puede bloquear con `permissions.disableBypassPermissionsMode` |
| Sandbox | ajustes de sandbox | — | `/sandbox`, `--sandbox`, `sandbox.*` (GA 2026-10-07); `chat.agent.sandbox.enabled` en VS Code |
| Confianza | workspace trust | Workspace Trust / `--trust` | `trustedFolders`, `--trust-folder`, `--add-dir` |
| Sesiones | `--resume`/`--continue` | chats, sesiones de CLI | `--resume`/`--continue`, `/fork`, `/rewind`, `/share`, `/remote`, `/delegate` |
| Vista de contexto / compactación | `/context`, `/compact` | anillo de contexto, `/summarize` | `/context`, `/compact [focus]`, automática en torno al 80% |
| Control de prompt caching | solo `cache_control` en la API | ninguno | ninguno; se factura entrada cacheada / escritura en caché; Cache Explorer de VS Code (diagnóstico) |
| Configuración MCP | `.mcp.json` | `.cursor/mcp.json` | `.mcp.json`/`.github/mcp.json` + `~/.copilot/mcp-config.json` (`tools` obligatorio); `.vscode/mcp.json` (`servers`); nube: ajustes del repo |
| Skills | `.claude/skills`, `~/.claude/skills` | `.cursor/skills` (+ `.claude/skills`) | `.github/skills`, `.claude/skills`, `.agents/skills`; `~/.copilot/skills` (VS Code también `~/.claude/skills`) |
| Plugins | `/plugin` | Marketplace (interfaz) | `copilot plugin install`; `awesome-copilot`; lee `.claude-plugin/` |
| Subagentes | `.claude/agents/*.md` | `.cursor/agents/*.md` | `.github/agents/*.agent.md`, `~/.copilot/agents/` (la CLI también `.claude/agents/`) + 7 integrados |
| Paralelo / equipos | Agent Teams | Cloud Agents (sin mensajería) | `/fleet`, subagentes en segundo plano + `write_agent`, sidekicks, `/delegate` |
| Hooks | hooks en `settings.json` | `.cursor/hooks.json` | `.github/hooks/*.json` `{version:1}` camelCase; también `.claude/settings.json`; el esquema de VS Code Local es distinto |
| Bloquear un comando | PreToolUse exit 2 / deny | `permission:"deny"` / exit 2 | `preToolUse` `permissionDecision:"deny"` / **exit 2** (fallo = cerrado; timeout = abierto) |
| CI | `claude -p` en Actions | Cursor SDK / Bugbot | `copilot -p` (`copilot-requests: write`), Agentic Workflows, Automations |
| SDK | Agent SDK | `@cursor/sdk` | `@github/copilot-sdk` (+ Python/Go/.NET/Java) |
| Bot de revisión de PRs | — | Bugbot | Copilot code review (rulesets; `REVIEW.md`; aprobaciones en preview, déjalas desactivadas) |
| Modo plan | plan mode | Plan mode | `/plan`, `--plan`, Shift+Tab (impuesto) |
| GSD | plugin GSD | n/a | n/a: modo plan + `/fleet` + agentes personalizados (+ Spec Kit) |

## B. Trampas que cambiaron en 2025–2026

1. **Coding agent → cloud agent** (las URLs de la documentación ahora son `/cloud-agent/`).
2. **Premium requests → AI Credits** (2026-06-01).
3. **Copilot CLI GA el 2026-02-25**; no es el retirado `gh copilot`.
4. Los ajustes de usuario de la CLI se movieron a `~/.copilot/settings.json`; `config.json` es estado
   interno; ya no se leen hooks desde ahí.
5. División de harnesses en VS Code; `chat.agentSkillsLocations` / `chat.instructionsFilesLocations` están
   obsoletos y el harness Copilot no los lee.
6. VS Code descarta las skills cuyo `name` ≠ carpeta; la CLI ignora `~/.claude/skills`.
7. El anidamiento de `AGENTS.md` es distinto en cada superficie.
8. No hay allow/deny versionado en la CLI → hooks.
9. `-p` omite los hooks del repo / el MCP del workspace en carpetas sin confianza.
10. `tools` obligatorio en MCP; `.vscode/mcp.json` usa `servers`; `${input:}` no se reenvía; cloud agent:
    sin servidores remotos con OAuth, sin resources ni prompts.
11. Playwright, GitHub, fetch y time vienen integrados en la CLI.
12. Los timeouts de los hooks fallan en abierto.
13. Existen `/pr auto` / `/pr automerge`; code review puede aprobar (preview).
14. Code review lee la configuración desde la rama head del PR.
15. Contradicciones en la documentación: profundidad de subagentes 6 frente a 4; modelos por defecto de los
    integrados frente a la tabla de modelos por defecto.
16. El sandbox en Linux/WSL2 necesita `bubblewrap` + `socat`; el sandbox de VS Code permite red por defecto.
17. Copilot Memory caduca las entradas que no se usan a los 28 días.
18. Las exclusiones de contenido aplican en la CLI y en la app de Copilot (GA 2026-09-02,
    Business/Enterprise).

---

## Fuentes

**Verificado el 2026-10-17. Copilot cambia rápido: revísalo antes de reutilizarlo.** Citas completas por
afirmación: [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

- Referencia de comandos de Copilot CLI: <https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference>
- Instalar / autenticar / configurar la CLI: <https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/install-copilot-cli>
- Permitir herramientas: <https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools>
- Soporte de instrucciones personalizadas: <https://docs.github.com/en/copilot/reference/custom-instructions-support>
- Instrucciones de repositorio: <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions>
- Referencia de hooks: <https://docs.github.com/en/copilot/reference/hooks-reference>
- Configuración de agentes personalizados: <https://docs.github.com/en/copilot/reference/custom-agents-configuration>
- Sobre las agent skills: <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>
- Gestión de contexto (CLI): <https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management>
- Riesgos y mitigaciones del cloud agent: <https://docs.github.com/en/copilot/concepts/agents/cloud-agent/risks-and-mitigations>
- Entorno del cloud agent (`copilot-setup-steps.yml`): <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/customize-the-agent-environment>
- Cloud agent mediante la API: <https://docs.github.com/en/copilot/how-tos/use-copilot-agents/cloud-agent/use-cloud-agent-via-the-api>
- MCP para el cloud agent: <https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/configure-mcp-servers>
- Configuración del code review: <https://docs.github.com/en/copilot/how-tos/copilot-on-github/set-up-copilot/configure-code-review>
- Copilot CLI en Actions: <https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/automate-with-actions>
- Facturación (AI Credits): <https://docs.github.com/en/copilot/concepts/billing-and-usage/individuals/billing> · modelos y precios <https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing>
- Copilot Memory: <https://docs.github.com/en/copilot/concepts/agents/copilot-memory>
- Harnesses de agentes en VS Code: <https://code.visualstudio.com/docs/agents/concepts/agent-harnesses>
- Hooks de VS Code: <https://code.visualstudio.com/docs/agent-customization/hooks> · referencia <https://code.visualstudio.com/docs/agents/reference/hooks-reference>
- Configuración MCP de VS Code: <https://code.visualstudio.com/docs/agents/reference/mcp-configuration>
- Agent skills de VS Code: <https://code.visualstudio.com/docs/agent-customization/agent-skills>
- Cache Explorer de VS Code: <https://code.visualstudio.com/docs/agents/agent-troubleshooting/cache-explorer>
- Changelog: CLI GA <https://github.blog/changelog/2026-02-25-github-copilot-cli-is-now-generally-available/> · sandbox GA <https://github.blog/changelog/2026-10-07-local-sandboxing-for-github-copilot-now-generally-available/> · agent skills <https://github.blog/changelog/2025-12-18-github-copilot-now-supports-agent-skills/>
- Herramientas: CodeGraph <https://colbymchenry.github.io/codegraph/> · Serena <https://github.com/oraios/serena> · graphify <https://graphify.net> · Context7 <https://context7.com> · MCP <https://modelcontextprotocol.io> · GSD <https://github.com/tomascortereal/claude-code-setup> · Spec Kit <https://github.com/github/spec-kit> (solo fuentes de terceros)
