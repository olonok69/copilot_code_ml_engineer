# GitHub Copilot — Guía de presentación (curso en dos sesiones)

> English version: [`SPEAKER_GUIDE.md`](./SPEAKER_GUIDE.md).

> Deck: [`presentation/Copilot_Presentation.pptx`](./presentation/Copilot_Presentation.pptx)
> (se regenera con [`presentation/build_pptx_copilot.py`](./presentation/build_pptx_copilot.py)).
> Detalle copy-paste: [`GUIA_TECNICA.md`](./GUIA_TECNICA.md) · demos en vivo por slide:
> [`DEMO_RUNBOOK_ES.md`](./DEMO_RUNBOOK_ES.md) · material ejecutable: [`examples/`](./examples/).

> Esta es la guía para el/la **ponente**. Cada sección corresponde a un bloque de slides e incluye el
> hilo a contar, los puntos que importan y una **frase de cierre** que puedes decir tal cual. Audiencia:
> **técnica / desarrolladores**. Es el **volumen GitHub Copilot** del curso. Sus hermanos son el
> [volumen Claude Code](https://github.com/olonok69/claude_code_ml_engineer) y el
> [volumen Cursor](https://github.com/olonok69/cursor_code_ml_engineer) (el [volumen Pi](https://github.com/olonok69/pi_code_ml_engineer)
> se construyó en paralelo). La metodología y el grafo siguen siendo temas distintos, pero se enseñan
> juntos en la Sesión 2.
>
> El deck tiene **dos sesiones** más un apéndice:
> - **Sesión 1 — GitHub Copilot (§00–§11):** cinco superficies, dos motores en VS Code y el fichero que
>   lee cada superficie.
> - **Sesión 2 — La metodología y el grafo de tickets (§12–§16):** cómo se trabaja de verdad con un
>   agente en producción. No depende de la herramienta. Nació en Claude Code, pasó a Cursor y ahora
>   funciona en Copilot. El caso de estudio de graphify es el último tema de esta misma sesión.
>
> **Nota de verificación:** cada afirmación sobre Copilot de esta guía sale de
> [`docs/research/COPILOT_FINDINGS_2026-10-17.md`](./docs/research/COPILOT_FINDINGS_2026-10-17.md),
> que se contrastó con docs.github.com y code.visualstudio.com el **17 de octubre de 2026**. Cuando la
> documentación no dice nada, esta guía lo indica como **NO DOCUMENTADO / NO VERIFICADO**. Copilot
> cambia rápido, así que revisa los hallazgos antes de dar el curso.

---

## Índice de slides

| # | Slide | Sección |
|---|---|---|
| 1 | Título | — |
| 2 | Agenda | — |
| 3 | Separador de la Sesión 1 | — |
| 4 | "Copilot" son cinco superficies distintas | §00 |
| 5 | VS Code tiene dos motores de Copilot | §00 |
| 6 | Matriz funcionalidad × superficie | §00 |
| 7 | Instalar, iniciar sesión, arrancar | §01 |
| 8 | copilot -p, modelos y AI Credits | §01 |
| 9 | El patrón de dos niveles, con ficheros de Copilot | §02 |
| 10 | Qué se carga y dónde | §02 |
| 11 | Allow, deny, y deny gana | §03 |
| 12 | Carpetas de confianza, sandbox, límites en la nube | §03 |
| 13 | Sesiones: resume, fork, rewind, delegate | §04 |
| 14 | Ventana de contexto | §05 |
| 15 | Higiene de contexto | §05 |
| 16 | Caching: la respuesta honesta | §06 |
| 17 | Un protocolo, cuatro ficheros de configuración | §07 |
| 18 | Trampas de MCP por superficie | §07 |
| 19 | Skills: un SKILL.md, casi todas las superficies | §08 |
| 20 | Agentes personalizados | §09 |
| 21 | ¿Subagente, /fleet o cloud agent? | §09 |
| 22 | Hooks: el veto determinista | §10 |
| 23 | La receta portable: bloquear push, PR y merge | §10 |
| 24 | De copilot -p a agentes en la nube | §11 |
| 25 | Separador de la Sesión 2 | — |
| 26 | El flujo real de 11 etapas | §12 |
| 27 | La puerta de salida son CINCO comprobaciones | §12 |
| 28 | Qué herramienta usa el agente, y cuándo | §13 |
| 29 | CodeGraph + Serena en cada superficie de Copilot | §13 |
| 30 | GSD: solo Claude Code. Los sustitutos en Copilot | §13 |
| 31 | De Claude Code a Copilot | §14 |
| 32 | Agujeros nuevos, y cómo el merge sigue siendo humano | §14 |
| 33 | De transportar (tarball) a compartir (S3) | §15 |
| 34 | Continuación de la Sesión 2: caso del grafo de tickets | — |
| 35 | El problema y el pipeline | §16a |
| 36 | El grafo actual: 3.921 nodos, 178 comunidades | §16b |
| 37 | Usarlo desde Copilot | §16c |
| 38 | Comprobación de paridad en WSL (ILS_2): verificado vs pendiente | — |
| 39 | Claude Code → Cursor → Copilot | Apéndice |
| 40 | Cierre + fuentes | — |

---

## Slides 1–3 — Apertura

**Hilo:** Este es el tercer volumen del curso. La audiencia ya conoce (o va a conocer) el mismo método
en Claude Code y en Cursor. El mensaje de este volumen es sencillo: **"Copilot" no es un solo
producto.** Es un agente de terminal, dos motores distintos dentro de VS Code, un plugin de JetBrains,
un agente en la nube que abre PRs y un revisor de PRs. La mayoría de las afirmaciones erróneas sobre
Copilot vienen de mezclar estas piezas.

La agenda (slide 2) usa la numeración de secciones que recorre todos los documentos del repo: §00–§11
en la Sesión 1 y §12–§16 en la Sesión 2. Cuando alguien haga una pregunta, mándalo al mismo número §
de [`GUIA_TECNICA.md`](./GUIA_TECNICA.md).

**Frase de cierre:** *"Mismo método, tercer agente. Esta vez lo difícil no es el método. Es saber con qué Copilot estás hablando."*

---

# SESIÓN 1 — GitHub Copilot

Cada sección de abajo termina con las **demos** de sus slides: qué ejecutar, dónde está en [`DEMO_RUNBOOK_ES.md`](./DEMO_RUNBOOK_ES.md) y qué demuestra. Haz antes las [comprobaciones previas](./DEMO_RUNBOOK_ES.md#comprobaciones-previas-t-30-min). Sin red o sin poder iniciar sesión, usa el plan B del runbook (textos de los slides, test offline del hook, `copilot --help`).

## §00 Mapa de superficies (slides 4–6)

**Hilo (slide 4):** Nombra las cinco superficies antes de decir nada más:

- **Copilot CLI (`copilot`)**: el agente de terminal, paquete npm `@github/copilot`, GA desde el
  2026-02-25. **No** es la antigua extensión `gh copilot`, que está retirada. Los tutoriales antiguos
  que muestran `gh copilot suggest` describen otro producto.
- **Agente de VS Code**: tiene *harnesses* (motores), en concreto **Copilot**, **Local**, Claude y
  Codex, más un destino **Cloud**.
- **Modo agente de JetBrains**: el modo agente y MCP están soportados. Skills, agentes personalizados,
  instrucciones personalizadas y prompt files están en **Preview**.
- **Copilot cloud agent**: antes se llamaba "coding agent". Le das un issue, un prompt, una llamada a
  la API o una automatización. Trabaja en un sandbox efímero de GitHub Actions y abre un **PR en
  borrador**.
- **Copilot code review**: un revisor de PRs que los rulesets pueden solicitar automáticamente.
- Además: Copilot en github.com (chat, la página Agents, Spaces) y la app de escritorio de Copilot.

**Hilo (slide 5), el dato estructural más importante de la Sesión 1:** VS Code tiene **dos motores
de Copilot**.

- El **harness Copilot** ejecuta el mismo runtime que la CLI. Comparte con la CLI `~/.copilot`, el
  esquema de `.github/hooks`, `.mcp.json`, las skills y los agentes.
- El **harness Local** es el modo agente clásico. Tiene sus propios ajustes `chat.*`, su propio
  esquema de hooks (PascalCase, `hookSpecificOutput`) y `.vscode/mcp.json` con `servers`. Es el
  **único** sitio donde funcionan los prompt files y los `handoffs`.

Elige el harness en el control **Session Target** y después lee la documentación de ese harness.

**Hilo (slide 6):** Recorre la matriz fila a fila. Hay tres celdas que merecen una pausa:

- Los **prompt files** solo funcionan en VS Code Local (además de Visual Studio y JetBrains).
- Los **hooks** existen casi en todas partes, pero VS Code Local usa un **esquema distinto**.
- Los **hooks de code review** están **NO DOCUMENTADOS**.

La matriz completa, con una fuente para cada celda, está en el
[fichero de hallazgos](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

**Demos (slides 4–6), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):**
- Slide 4: `copilot --version`. Demuestra que la CLI es `copilot`, no la extensión retirada `gh copilot`.
- Slide 5: en VS Code, cambia Session Target entre **Copilot** y **Local**; un prompt file aparece como `/nombre` solo en Local. Demuestra que los dos motores leen ficheros distintos.
- Slide 6: abre la tabla §2 del [fichero de hallazgos](./docs/research/COPILOT_FINDINGS_2026-10-17.md). Demuestra que cada celda de la matriz tiene una fuente.

**Frase de cierre:** *"Antes de cualquier afirmación del tipo 'Copilot puede / no puede', haz dos preguntas: ¿qué superficie? y ¿qué harness?"*

---

## §01 Instalación, autenticación, headless, modelos, facturación (slides 7–8)

**Hilo (slide 7):** Instalar es una línea: npm (Node 22+), Homebrew, winget o el script de
instalación. Para autenticarse, la CLI toma los tokens en un orden fijo: `COPILOT_GITHUB_TOKEN` >
`GH_TOKEN` > `GITHUB_TOKEN`. Un PAT tiene que ser **fine-grained y propiedad del usuario**, con el
permiso "Copilot Requests". En Actions, el workflow necesita `permissions: copilot-requests: write` y
la política de la organización tiene que permitir la facturación de la CLI.

En el primer arranque dentro de un repo, la CLI pregunta si quieres **confiar en la carpeta**. Ese
aviso vuelve a salir en el slide 12, porque en CI nadie lo ve. `copilot init` escribe
`.github/copilot-instructions.md`.

**Hilo (slide 8):** `copilot -p` es la base de todas las automatizaciones de §11:

```bash
copilot -p "Explain ./complex.ts" -s
copilot -p '...' -s --allow-tool='shell(git:*)' --deny-tool='shell(git push)' --no-ask-user
copilot -p '...' --trust-folder          # carga hooks/MCP del repo para esta ejecución
copilot -p '...' --max-ai-credits=5      # límite blando por respuesta
```

**Modelos:** el modelo por defecto de la CLI es `claude-sonnet-5.5`. Puedes elegir otro con
`--model`, `COPILOT_MODEL` o `/model`. `auto` deja que Copilot elija, con un 10% de descuento en los
planes de pago.

**La facturación cambió el 2026-06-01** a **GitHub AI Credits**. Las "premium requests" y los
multiplicadores son legado. Solo aplican a los planes anuales Pro/Pro+ que se quedaron en el modelo
antiguo. Las completions de código y las sugerencias de next-edit no se facturan.

**Cómo se relaciona un crédito con un token.** No existe una equivalencia fija del tipo "un crédito =
N tokens". Cada modelo tiene un precio en dólares **por cada millón de tokens**, con cuatro tarifas
distintas: entrada, entrada cacheada, escritura en caché y salida. **1 AI credit = 0,01 $**, así que
una tarifa de 1 $ por millón de tokens cuesta 100 créditos por millón de tokens. Por eso el mismo
prompt cuesta un número distinto de créditos en cada modelo, y los tokens de salida cuestan mucho más
que los de entrada.

| Modelo (tramo por defecto) | Entrada | Entrada cacheada | Escritura en caché | Salida |
|---|---|---|---|---|
| Claude Haiku 5.5 (≤100K de entrada) | 0,10 $ = 10 créditos | 0,01 $ = 1 crédito | 0,125 $ = 12,5 créditos | 0,50 $ = 50 créditos |
| Claude Sonnet 5.5 (por defecto en la CLI) | 2,00 $ = 200 créditos | 0,10 $ = 10 créditos | 2,50 $ = 250 créditos | 10,00 $ = 1.000 créditos |
| Claude Opus 5.5 | 4,00 $ = 400 créditos | 0,20 $ = 20 créditos | 5,00 $ = 500 créditos | 20,00 $ = 2.000 créditos |

*Por cada millón de tokens. Fuente: docs.github.com, "Models and pricing", consultado el 2026-10-26.*

Ejemplo con Claude Sonnet 5.5: un turno que lee 50.000 tokens de entrada y escribe 5.000 de salida
cuesta 50.000 × 200 / 1M + 5.000 × 1.000 / 1M = 10 + 5 = **15 créditos (0,15 $)**. Si 40.000 de esos
tokens de entrada salen de la caché, la parte de entrada baja a 10.000 × 200 / 1M + 40.000 × 10 / 1M =
2,4 créditos, y el turno cuesta unos **7,4 créditos**. Por eso §06 insiste en mantener estable el
prefijo.

Asignación mensual: Pro (10 $) 1.500 créditos, Pro+ (39 $) 7.000, Max (100 $) 20.000. Los créditos que
no se usan no pasan al mes siguiente. Los 1.500 créditos de Pro dan para unos 100 turnos como el del
ejemplo. La selección automática de modelo (`auto`) tiene un 10% de descuento en los planes de pago.
Para vigilar el gasto: `/usage` en la CLI, `--max-ai-credits` por respuesta y el panel de uso de
github.com.

**Demos (slides 7–8), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):**
- Slide 7: `copilot login --help`. Demuestra las opciones de inicio de sesión y el orden en que se leen las variables de token.
- Slide 8: `copilot -p "Summarise AGENTS.md in 3 bullets" -s` y después `/usage` en una sesión interactiva. Demuestra una ejecución headless y cuánto costó en AI Credits.

**Frase de cierre:** *"La CLI es `copilot`, y se paga en AI Credits. Si un slide dice 'premium requests', es del año pasado."*

---

## §02 Memoria e instrucciones (slides 9–10)

**Hilo (slide 9):** Es el mismo patrón de dos niveles que en los otros volúmenes, construido con los
ficheros de Copilot:

- **Nivel 1 (siempre cargado, pequeño):** un `AGENTS.md` en la raíz, que leen todas las superficies,
  así que es la única voz compartida con Claude Code y Cursor. Añade, si quieres, un
  `.github/copilot-instructions.md` pequeño y ficheros acotados
  `.github/instructions/*.instructions.md` con globs `applyTo`.
- **Nivel 2 (bajo demanda):** `data/changes/STATUS.md`, `PLAYBOOK.md`, `SHARP_EDGES.md` y los
  ledgers por ticket.
- **Nivel 0 (local de la máquina):** `IDENTITY.md` (en el gitignore), o
  `~/.copilot/copilot-instructions.md` para instrucciones personales. **Atención:** la CLI **no** lee
  `~/.claude/CLAUDE.md`.

La CLI también admite imports `@path` inmediatos en `AGENTS.md`, `CLAUDE.md` y
`copilot-instructions.md`. Úsalos solo para lo que tenga que cargarse desde el principio. Si VS Code
expande `@path` o no está NO DOCUMENTADO.

**Hilo (slide 10):** cinco trampas sobre qué se carga y dónde:

1. **La CLI lo mezcla todo:** `CLAUDE.md`, `GEMINI.md`, `AGENTS.md`, `.instructions.md`,
   `.claude/rules`, `copilot-instructions.md`, leídos en la raíz de git **y** en el directorio actual.
   Tus reglas de Claude Code vienen incluidas sin coste.
2. **Un `AGENTS.md` anidado se comporta distinto en cada superficie.** La CLI lee solo la raíz + el
   directorio actual. El cloud agent usa "gana el más cercano". VS Code Local necesita
   `chat.useNestedAgentsMdFiles`, que viene desactivado.
3. **El patrón seguro para reglas por carpeta:** `.instructions.md` con `applyTo: "subdir/**"`. Añade
   `excludeAgent: "code-review"` (o `"cloud-agent"`) cuando una regla no tenga sentido para ese agente.
4. **Los prompt files son solo de Local.** El equivalente en la CLI es una skill.
5. **Copilot Memory no es tu ledger.** Vive en la nube, está en preview y los recuerdos caducan a los
   28 días. La herramienta `/memories` de VS Code y `/chronicle` de la CLI son, a su vez, sistemas
   distintos.

Material: [`examples/agents-md/`](./examples/agents-md/).

**Demos (slides 9–10), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):**
- Slide 9: abre [`AGENTS.md`](./AGENTS.md) y después uno de los ficheros a los que apunta. Demuestra el patrón de dos niveles: un fichero corto, siempre cargado, con punteros.
- Slide 10: `/instructions` en la CLI. Demuestra qué ficheros de instrucciones se cargaron de verdad (la CLI también lee `CLAUDE.md` y `.claude/rules`).

**Frase de cierre:** *"`AGENTS.md` es el único fichero que leen todas las superficies. Que sea un onboarding de 30 segundos: punteros, no copias."*

---

## §03 Permisos, confianza, sandbox (slides 11–12)

El mensaje de los dos slides: Copilot tiene **varias capas independientes**, y cada una frena una cosa
distinta. El slide 11 trata de *qué herramientas pueden ejecutarse*; el slide 12, de *qué llega a
cargarse* y *a qué puede acceder el proceso*.

**Hilo (slide 11): allow, deny, y deny gana.**

1. **Cómo se escribe una regla.** Los permisos de la CLI siguen el patrón `Tipo(argumento)`:

   | Tipo | Ejemplo | Qué cubre |
   |---|---|---|
   | `shell` | `shell(git:*)` | `git` con cualquier subcomando (`:*` = la raíz del comando más un espacio) |
   | `shell` | `shell(git push)`, `shell(gh pr)` | en `git` y `gh`, el subcomando de primer nivel |
   | `write` / `read` | `write(src/*.ts)`, `read(.env)` | edición / lectura de ficheros |
   | `url` | `url(github.com)` | peticiones web a ese host |
   | MCP | `MyMCP(tool)`, `MyMCP` | una herramienta de un servidor, o el servidor entero |

2. **Cómo se decide.** Si una llamada coincide con una regla deny, se rechaza. Si coincide con una
   regla allow y con ninguna deny, se ejecuta sin preguntar. Todo lo demás te pregunta (`y`, `n`, `!`
   para permitir llamadas parecidas durante la sesión, `#` para denegarlas). **Deny siempre gana a
   allow**, incluso con `--allow-all` / `--yolo` o con una aprobación guardada.
3. **Dónde viven las reglas.** Los flags (`--allow-tool`, `--deny-tool`) duran una ejecución y nunca se
   guardan. Las aprobaciones que guardas en el aviso van a `~/.copilot/permissions-config.json`, por
   usuario y por máquina. Las reglas `permissions.deny/allow` para toda la organización existen
   **solo** como ajustes gestionados por la empresa o por MDM.
4. **El dato clave: el repo no puede contener una lista allow/deny.** `.github/copilot/settings.json`
   acepta una lista corta de claves e ignora el resto en silencio. Así que una regla de equipo como
   "nunca hagas push" que quieras subir al repo tiene que ser un **hook** (§10).
   `permissions.disableBypassPermissionsMode` (usuario, gestionado o MDM) puede desactivar `--yolo`.
5. **En VS Code es lo mismo con otros nombres.** `chat.permissions.default` vale Manual, Assisted o
   Allow all, y `chat.tools.terminal.autoApprove` lista comandos como `true` / `false`. Una regla en
   `false` solo *pide* aprobación; no bloquea. Para bloquear, la documentación remite a un hook de
   denegación `PreToolUse`.

**Hilo (slide 12): tres capas más.**

- **Carpetas de confianza: qué se carga.** En el primer arranque dentro de una carpeta, la CLI pregunta
  si confías en ella (para esta sesión o para las siguientes; la lista es `trustedFolders` en
  `~/.copilot/config.json`). La confianza controla **los hooks del repo, el MCP del workspace
  (`.mcp.json`), los plugins del repo y el modelo del repo**. En modo `-p`, una carpeta sin confianza
  **los omite en silencio** salvo que pases `--trust-folder` (o definas las variables
  `GITHUB_COPILOT_PROMPT_MODE_*`). Así es como una puerta de CI basada en un hook del repo acaba sin
  hacer nada.
- **Sandbox local: a qué puede acceder el proceso.** GA desde el 2026-10-07: `/sandbox enable`,
  `--sandbox`, o `sandbox.enabled` en `~/.copilot/settings.json`. Limita los hosts de red
  (`sandbox.userPolicy.network.allowedHosts|blockedHosts`), deniega rutas
  (`sandbox.userPolicy.filesystem.deniedPaths`) y enmascara credenciales: el proceso ve un marcador y
  el proxy inyecta el secreto real solo hacia los hosts que indiques. Vive en los ajustes del usuario,
  así que un repo no puede sobrescribirlo.
- **Cloud agent: límites estructurales.** Todas las herramientas están preaprobadas, y un hook que
  responde `"ask"` cuenta como `"deny"`. El agente solo hace push a su rama `copilot/`. No puede marcar
  un PR como listo, ni aprobarlo, ni hacer merge. Las ejecuciones de workflows las aprueban personas. La
  red la limita el firewall de "Internet access" en los ajustes del repo.

**Ejemplos en este repo, y lo que falta:**

| Tema | Ejemplo | Estado |
|---|---|---|
| Flags allow/deny de la CLI | [`examples/permissions/copilot-cli-flags.sh`](./examples/permissions/copilot-cli-flags.sh) | Script ilustrativo, contrastado con la referencia de la CLI; no se ha ejecutado contra una CLI real. |
| Demo de allow/deny en headless | [`DEMO_RUNBOOK_ES.md` D1](./DEMO_RUNBOOK_ES.md#d1--allowdeny-en-headless-slide-11) | Demo para hacer en directo. |
| `--trust-folder` en CI | [`examples/automation/copilot-cli-action.yml`](./examples/automation/copilot-cli-action.yml) | Ejemplo de workflow; no se ha ejecutado en este repo. |
| Veto por contenido (hook) | [`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json), [`examples/hooks/deny-env-read.json`](./examples/hooks/deny-env-read.json) | Hook activo; probado offline con `bash .github/hooks/test-block-external-git.sh`. |
| Auto-aprobación y sandbox en VS Code | [`examples/permissions/.vscode/settings.json.example`](./examples/permissions/.vscode/settings.json.example) | Ajustes de ejemplo. |
| Referencia completa | [`examples/permissions/README.md`](./examples/permissions/README.md) | Texto (en inglés). |
| Aprobaciones guardadas (`permissions-config.json`) | **No hay ejemplo en el repo.** | Lo crea la CLI cuando guardas una aprobación. |
| Carpetas de confianza (`trustedFolders`) | **No hay ejemplo en el repo.** | Se enseña en directo con el aviso del primer arranque. |
| Sandbox de la CLI (ajustes `sandbox.*`) | **No hay ejemplo de CLI en el repo.** | Solo existe como ejemplo el ajuste de VS Code. |
| `permissions.deny` gestionado / `disableBypassPermissionsMode` | **No hay ejemplo en el repo.** | Solo empresa / MDM; se menciona en [`COPILOT_WORKING_AGREEMENT_TEMPLATE.md`](./docs/ai-agents-code-methodology/templates/COPILOT_WORKING_AGREEMENT_TEMPLATE.md). |
| Firewall del cloud agent | **No hay ejemplo en el repo.** | Se configura en la interfaz de ajustes del repo. |

**Demos (slides 11–12):**
- Slide 11: [D1, allow/deny en headless](./DEMO_RUNBOOK_ES.md#d1--allowdeny-en-headless-slide-11). Demuestra que deny gana a allow aunque `shell(git:*)` esté permitido, y que sin `--trust-folder` el hook del repo se omite en modo `-p`.
- Slide 12: `copilot help permissions` y, si tu versión lo tiene, `/sandbox` ([tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide)). Demuestra los temas de permisos y los controles del sandbox; no hay ejemplo de sandbox de la CLI en el repo.

**Frase de cierre:** *"Las allowlists deciden qué se ejecuta sin preguntar. Solo un hook puede vetar por contenido, y en CI el hook solo se carga si confiaste en la carpeta."*

---

## §04 Sesiones (slide 13)

**Hilo:** Estos son los controles de sesión que de verdad vas a usar:

- `--continue` / `--resume` (cada ejecución `-p` imprime su ID de sesión)
- `/fork`, que funciona mientras el agente está trabajando
- `/rewind`: solo la conversación, o la conversación **y** los ficheros, sin necesidad de git
- `/share`, `/remote` (dirigir la sesión desde la web, el móvil o VS Code)
- `/delegate`, o un `&` al principio, que pasa la sesión al cloud agent como rama y PR en borrador

**Atención:** los "checkpoints" que lista `/session checkpoints` son **resúmenes de compactación**, no
instantáneas de ficheros. En VS Code, el control Session Target mueve una sesión entre harnesses o a
Cloud, y el historial viaja con ella.

**Demo (slide 13), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):** ejecuta un comando `-p`, copia la línea `copilot --resume=…` que imprime y reanúdalo; después haz `/rewind` de una edición de prueba. Demuestra que cualquier ejecución headless se puede reanudar, y que `/rewind` con ficheros devuelve el árbol a su estado anterior.

**Frase de cierre:** *"Un checkpoint de compactación es un resumen. Solo `/rewind` con ficheros devuelve tu árbol a su estado anterior."*

---

## §05 Ventana de contexto (slides 14–15)

**Hilo (slide 14):** `/context` muestra a dónde van los tokens: system prompt, instrucciones
personalizadas, herramientas del sistema, herramientas MCP, mensajes y espacio libre. La
auto-compactación empieza en torno al **80%** y se detiene en torno al 95%. `/compact [foco]` la lanza
a mano, y **una compactación no se puede deshacer**. La salida de una herramienta de más de **20 KiB**
va a un fichero temporal, y el modelo recibe la ruta más un avance
(`COPILOT_LARGE_OUTPUT_THRESHOLD_BYTES` cambia el límite). En VS Code, el control del cuadro de chat
muestra el mismo desglose más los AI credits. Ojo: `#codebase` lanza una búsqueda; no pega el repo en
el contexto. La ventana por defecto exacta de cada modelo está NO DOCUMENTADA en una tabla única.

**Hilo (slide 15):** seis hábitos, los mismos que en los volúmenes hermanos:

1. Instrucciones pequeñas y estables.
2. El material que se usa poco va en skills, que se cargan bajo demanda.
3. Menos servidores MCP; usa `deferTools: "auto"` para conjuntos grandes de herramientas.
4. Manda la investigación a subagentes: tienen su propia ventana de contexto.
5. `/plan` antes de implementar.
6. Una sesión nueva por tarea.

Material: [`examples/context/`](./examples/context/).

**Demo (slide 14), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):** `/context` y después `/compact "keep only the hook design"`. Demuestra a dónde van los tokens y una compactación con foco. El slide 15 no tiene demo.

**Frase de cierre:** *"Compacta a propósito, con un foco. El orden de herramientas de la Sesión 2 es, en realidad, una política de contexto."*

---

## §06 Prompt caching (slide 16)

**Hilo, sé honesto con la sala:** Copilot **no tiene ningún control de caché para el usuario**. No hay
`cache_control`, ni ajuste de TTL, ni variable de entorno en la CLI, en VS Code ni en el cloud agent.
Pero el caching **sí** ocurre y **se factura**: las tablas de precios cobran los tokens de entrada
cacheada y de escritura en caché.

Lo que sí puedes hacer:

- **Diagnosticar en VS Code** con el **Cache Explorer** (Agent Debug Logs → Summary). Muestra el % de
  aciertos por turno, los tokens reutilizados y la *primera divergencia* en el prompt. Diagnostica; no
  controla nada.
- **Mantener estable el prefijo:** elige el modelo, el esfuerzo y las herramientas antes de la primera
  petición, y no edites ficheros de instrucciones ni de agentes a mitad de sesión.
- **Hacer fork en lugar de reiniciar.** El fork conserva la caché.

La CLI no tiene vista de caché: `/usage` solo muestra tokens y créditos. Si la exportación a
OpenTelemetry lleva atributos de caché está NO VERIFICADO. La demo del mecanismo usa la API de
Anthropic, no Copilot: [`examples/prompt-caching/`](./examples/prompt-caching/).

**Demo (slide 16), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):** en VS Code, Agent Debug Logs → Summary → Cache Explorer (solo si tu versión lo tiene); en la CLI, `/usage`. Demuestra que el caching ocurre y se factura, pero solo se puede diagnosticar, no configurar.

**Frase de cierre:** *"No puedes configurar la caché. Puedes dejar de romperla."*

---

## §07 MCP (slides 17–18)

**Hilo (slide 17):** hay un solo protocolo pero **cuatro sitios de configuración**:

| Superficie | Fichero | Clave raíz |
|---|---|---|
| CLI (usuario) | `~/.copilot/mcp-config.json` | `mcpServers` |
| CLI + harness Copilot de VS Code (repo) | `.mcp.json` o `.github/mcp.json` (requiere confianza en la carpeta) | `mcpServers` |
| VS Code Local | `.vscode/mcp.json` | **`servers`** |
| Cloud agent | Settings del repo → Copilot → MCP servers (JSON en la interfaz) | `mcpServers` |

En las configuraciones de la CLI y de la nube, **`tools` es obligatorio** (por ejemplo `["*"]`).
`mcpServers` frente a `servers` es el error de copy-paste más frecuente.

**Hilo (slide 18):** seis trampas:

1. La CLI trae servidores **integrados**: GitHub (sobre todo lectura), **Playwright**, fetch y time.
   **No configures Playwright dos veces.**
2. El cloud agent usa solo herramientas (ni resources ni prompts) y no admite servidores remotos con
   OAuth. Los secretos necesitan el prefijo `COPILOT_MCP_`. Ejecuta las herramientas **sin
   aprobación**, así que pon en la allowlist solo las de lectura.
3. Los binarios para el cloud agent se instalan con `.github/workflows/copilot-setup-steps.yml`: un
   único job llamado `copilot-setup-steps`, en la rama por defecto.
4. Code review solo usa una herramienta MCP si la herramienta tiene `readOnlyHint: true` y el
   interruptor está activado.
5. Migra desde VS Code con `jq '{mcpServers: .servers}'`. Los servidores que usan `${input:...}` no se
   reenvían al harness Copilot.
6. La allowlist de empresa compara por huella (fingerprint) y falla en cerrado.

Material: [`examples/mcp/`](./examples/mcp/) · el conjunto del método (CodeGraph, Serena, Context7) en
[`docs/ai-agents-code-methodology/copilot/`](./docs/ai-agents-code-methodology/copilot/).

**Demos (slides 17–18), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):**
- Slide 17: `copilot mcp list` y después abre [`.mcp.json`](./.mcp.json). Demuestra el `tools: ["*"]` obligatorio y que Playwright no está configurado porque viene integrado.
- Slide 18: pide "use context7 to look up python-pptx `add_picture`". Demuestra un servidor MCP en uso durante una tarea.

**Frase de cierre:** *"La configuración le da la herramienta al agente. Un mapa de disparadores en tus instrucciones hace que la use."*

---

## §08 Skills y plugins (slide 19)

**Hilo:** Una skill es un `SKILL.md` en `.github/skills/<nombre>/`. Todas las superficies leen esa
ubicación, y también `.claude/skills/` y `.agents/skills/`. Para skills personales, usa
`~/.copilot/skills/`.

Tres reglas de portado que cuestan horas de verdad:

- **Atención: la CLI no lee `~/.claude/skills/`.** VS Code sí. Copia las skills o crea un enlace
  simbólico, o regístralas con `copilot skill add`.
- **Atención: VS Code descarta en silencio una skill cuyo `name` no coincide con el nombre de su
  carpeta** en formato minúsculas-con-guiones.
- **Quita `trigger:`.** No es una clave de Copilot. Copilot ya expone cada skill como `/nombre` y elige
  las skills automáticamente por su `description` (≤1024 caracteres).

Plugins: `copilot plugin install NOMBRE@MARKETPLACE`. `awesome-copilot` viene integrado, y los paquetes
en formato Claude `.claude-plugin/` se pueden leer.

La razón más fuerte para una skill sigue siendo **hacer cumplir una práctica**: "pull al empezar, push
al terminar" estuvo meses en un runbook y nadie lo hacía, hasta que se convirtió en la skill `day`.
Material: [`examples/skills-plugins/`](./examples/skills-plugins/), skills activas en
[`.github/skills/`](./.github/skills/).

El paquete reutilizable de la metodología está en
[`docs/ai-agents-code-methodology/copilot/skills/`](./docs/ai-agents-code-methodology/copilot/skills/).
En la sesión en vivo de Copilot en WSL, el usuario confirmó que estas ocho skills personales aparecen
en Copilot Customizations: `day`, `evidence`, `preview`, `atlassian`, `kg`, `kg-refresh`,
`methodology-plan` y `sanitise-diff`. Tómalo como una comprobación de descubrimiento, no como prueba de
que todo comportamiento remoto o de producción sea seguro de ejecutar; la Sesión 2 dice qué se probó y
qué no.

**Demo (slide 19):** [S1–S3, skills sobre los objetivos de demo](./DEMO_RUNBOOK_ES.md#s1s3--skills-sobre-los-objetivos-de-demo): `/audit ex_npm`, `/audit-python ex_app`, `/deploy-staging ex_staging`. Demuestra skills invocadas como `/nombre`, y una skill que se detiene a pedir tu OK antes de desplegar.

**Frase de cierre:** *"Un SKILL.md funciona en casi todas las superficies. Ponle el nombre de su carpeta, y déjalo donde la CLI pueda verlo."*

---

## §09 Agentes personalizados y subagentes (slides 20–21)

**Hilo (slide 20):** un agente personalizado es `.github/agents/<nombre>.agent.md`. El ejemplo es
`refactor-scout` con `tools: ["read", "search"]`. **Esa lista de herramientas es lo que impone el
límite; el texto no.** Dos trampas:

- Cuando la CLI ejecuta un agente personalizado como subagente, este **no recibe las instrucciones del
  repo** salvo que se defina `include-custom-instructions: true`.
- Los `handoffs[]` solo funcionan en VS Code Local.

Los agentes integrados de la CLI son explore, task, general-purpose, research, rubber-duck,
security-review y code-review. **Atención:** sus modelos por defecto documentados (por ejemplo
`claude-sonnet-4.6`, `gpt-5.4-mini`) **no coinciden** con la tabla de modelos por defecto de la CLI. Es
una incoherencia de la documentación, así que verifícalo en tu versión. Agente activo:
[`.github/agents/refactor-scout.agent.md`](./.github/agents/refactor-scout.agent.md).

**Hilo (slide 21):** tres formas de ejecutar trabajo en paralelo:

| | Subagente (`task`) | `/fleet` | Cloud agent (`/delegate`, `&`) |
|---|---|---|---|
| Contexto | Ventana propia, devuelve un resumen | Subagentes en paralelo sobre un plan | Sesión asíncrona completa |
| Resultado | En tu sesión | En tu sesión | Rama + PR en borrador |
| Para qué | Investigación ruidosa | Ejecutar un plan por oleadas en paralelo | Trabajo largo y asíncrono |

Los límites de concurrencia dependen del plan (Free 2 · Pro 4 · Max 8 · Business 16 · Enterprise 32).
**La profundidad máxima es contradictoria en la documentación:** la tabla de referencia dice 6 y la
tabla de variables de entorno dice 4. Dilo en voz alta. Material:
[`examples/subagents/`](./examples/subagents/).

**Demos (slides 20–21), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):**
- Slide 20: "Use the refactor-scout agent to find every caller of `health` in ex_npm". Demuestra que la lista `tools` del agente lo mantiene en solo lectura: no debe editar ficheros.
- Slide 21: `/subagents` y, opcionalmente, `/fleet` sobre un plan de dos tareas (gasta créditos). Demuestra las formas de ejecutar trabajo en paralelo.

**Frase de cierre:** *"Usa un subagente cuando quieras que el ruido se quede fuera de tu sesión. Usa el cloud agent cuando el trabajo sea largo. El coste no es el mismo."*

---

## §10 Hooks (slides 22–23)

**Hilo (slide 22):** los hooks de la CLI y del cloud agent viven en `.github/hooks/*.json`, con la
forma `{"version": 1, "hooks": {"preToolUse": [...]}}`. La CLI también lee hooks de
`.claude/settings.json`. El contrato:

- stdin trae `{toolName, toolArgs}`. **Atención:** `toolArgs` puede llegar como **cadena JSON**; el
  propio ejemplo de depuración de la documentación pasa una.
- Para denegar, devuelve `permissionDecision: "deny"` con un motivo, **o sal con código 2**.
- Un fallo o cualquier otro código de salida distinto de cero **falla en cerrado** en `preToolUse`.
- Un **timeout falla en abierto en todos los eventos**, incluidos los hooks de política. Mantén
  rápidos los hooks que bloquean.

El harness Local de VS Code usa un esquema distinto: eventos en PascalCase, `{tool_name, tool_input}`,
`hookSpecificOutput`. Los hooks de code review están NO DOCUMENTADOS.

**Hilo (slide 23):** la receta portable que va activa en este repo
([`.github/hooks/block-external-git.json`](./.github/hooks/block-external-git.json) + `.sh` +
`.ps1`):

1. Un único script lee las dos formas de payload y además filtra por nombre de herramienta.
2. Detecta `git push`, `gh pr create|merge|ready`, los endpoints de merge de `gh api`, releases y
   despliegues.
3. Responde en los dos formatos y **sale con código 2**, la única señal que documentan ambos esquemas.
4. Nunca responde "allow". Un allow podría auto-aprobar la herramienta y saltarse el aviso normal.
5. En la CLI, añade `--deny-tool='shell(git push)' --deny-tool='shell(gh pr)'` como segunda capa.
6. Se prueba con un **canario primero**: `bash .github/hooks/test-block-external-git.sh`.

**Atención:** `/pr create|auto|automerge` son comandos slash propios de la CLI que pueden crear PRs y
**hacer merge**. Si pasan por `preToolUse` está NO VERIFICADO. Declara en las instrucciones que son
solo para personas, y prueba el hook contra ellos en tu versión.

Material: [`examples/hooks/`](./examples/hooks/).

**Demo (slides 22–23):** [H1, el hook dice que no](./DEMO_RUNBOOK_ES.md#h1--el-hook-dice-que-no). Pide al agente `git push`, `gh pr create` y `gh pr merge`: se deniegan todos, mientras que `git status` se ejecuta. Demuestra un veto determinista que las instrucciones solas no dan. Plan B offline: `bash .github/hooks/test-block-external-git.sh`.

**Frase de cierre:** *"Las instrucciones piden. Un hook garantiza, siempre que responda antes del timeout."*

---

## §11 Automatización (slide 24)

**Hilo:** cuatro formas de automatizar, de la más simple a la más gestionada:

- **`copilot -p` en GitHub Actions:** instala con npm, define `copilot-requests: write` (o usa
  `COPILOT_GITHUB_TOKEN`), pasa `--trust-folder` para que se carguen los hooks del repo, y deja
  `--allow-tool` al mínimo con `--deny-tool` explícitos.
- **GitHub Agentic Workflows (`github/gh-aw`):** GitHub los recomienda frente a pasos `copilot` en
  crudo por sus salvaguardas.
- **API de tareas del cloud agent** (`POST /agents/repos/{owner}/{repo}/tasks`, preview pública, solo
  tokens user-to-server) y **Automations** (disparadores por calendario o por evento).
- **Code review mediante rulesets:** "Automatically request Copilot code review". **Atención:** el
  revisor lee sus instrucciones desde la rama **head**, así que un PR puede cambiar las instrucciones de
  su propio revisor.

El Copilot SDK (npm, pip, Go, .NET, Java) sigue el flujo `CopilotClient` → `createSession` →
`sendAndWait`, y tiene hooks programáticos. Material: [`examples/automation/`](./examples/automation/).

**Demo (slide 24), en la [tabla de comando por slide](./DEMO_RUNBOOK_ES.md#comando-por-slide):** enseña el workflow de [`examples/automation/`](./examples/automation/) sin ejecutarlo, y no ejecutes en directo el script de tareas del cloud agent. Demuestra cómo en CI la allowlist se escribe en la línea de comandos (`--trust-folder`, allow/deny explícitos).

**Frase de cierre:** *"En CI no hay nadie para responder al aviso de confianza, así que escribe la allowlist en la línea de comandos."*

---

# SESIÓN 2 — La metodología y el grafo de tickets

## Slide 25 — Separador

**Hilo:** Todo lo que viene a partir de aquí funciona igual con cualquier agente. Nació en Claude
Code y se portó a Cursor. Este volumen lo muestra funcionando en Copilot, y §14 cuenta qué hubo que
cambiar. No fue mucho.

---

## §12 El flujo y la puerta de salida (slides 26–27)

**Hilo (slide 26):** **El agente es un colaborador disciplinado, y se gana la autonomía decisión a
decisión.** Hay 11 etapas, y las de color coral son puertas:

1. Orientarse (skill `kg` + historial + estado)
2. **Triaje de entrada contra el contrato de salida**
3. **Regresión frente a problema preexistente**
4. Investigar con un oráculo determinista
5. **`/plan` → acuerdo humano explícito**
6. TDD RED → GREEN
7. **Verificar (la puerta de salida)**
8. Documentar una sola vez
9. Sanitizar las líneas añadidas
10. Handoff: la persona hace el push. En Copilot, **el hook lo impone**.
11. **Revisión del bot + persistir lo aprendido**

Diagrama: [`examples/methodology/flow.png`](./examples/methodology/flow.png). Recorrido completo:
[`examples/methodology/WORKFLOW.md`](./examples/methodology/WORKFLOW.md) y el caso de principio a fin
en [`examples/methodology/REAL_EXAMPLE.md`](./examples/methodology/REAL_EXAMPLE.md).

**Hilo (slide 27):** La puerta de salida son **cinco comprobaciones**, no "los tests pasan":

- **(0) Validar el instrumento** contra un caso de respuesta conocida.
- **(1) Reproducir en la etapa de salida real**, a través del wrapper que construye el contrato.
- **(2) Comprobar la lista de miembros, nunca un total.**
- **(3) Verificar dentro de la imagen desplegada.**
- **(4) Mirar la salida.**

Después cuenta las cinco formas en que una puerta en verde no demuestra nada. Todas han pasado:

- un instrumento roto que devuelve un "no" uniforme y convincente;
- un total que cuadra porque dos errores se compensan;
- una puerta que no podía fallar (cero casos positivos en el corpus);
- un canario que nunca aplicó la perturbación que aplica producción;
- una comprobación estructural leída como si fuera semántica.

**Frase de cierre:** *"Los tests en verde no prueban lo que se entrega. La puerta tiene cinco comprobaciones porque cada una nos ha fallado alguna vez."*

---

## §13 Las herramientas del método (slides 28–30)

**Hilo (slide 28):** las instrucciones dicen *qué herramienta y en qué orden*: de barata a cara, de
determinista a probabilística.

| Etapa | Herramienta |
|---|---|
| Orientarse | skill `kg` |
| Navegar | CodeGraph `codegraph_explore` (una llamada; trata su salida como ya leída) |
| Comprobar refactor | Serena `find_referencing_symbols` (**obligatorio** antes de renombrar) |
| Diagnosticar | oráculo determinista |
| Entorno | CLI de la nube, solo lectura |
| Contrato | Playwright, que viene **integrado** en la CLI |
| Al final | el turno del agente, para verificar |

Se distribuye como
[`01-tool-prevalence.instructions.md`](./docs/ai-agents-code-methodology/copilot/instructions/).

**Hilo (slide 29):** dónde se configura cada servidor en cada superficie. CodeGraph: `.mcp.json` stdio
con `--path .` (CLI y harness Copilot), `.vscode/mcp.json` con `${workspaceFolder}` (Local), ajustes MCP
del repo más `copilot-setup-steps.yml` (nube). Si `--path .` se resuelve respecto al directorio de la
sesión está NO VERIFICADO, así que arranca desde la raíz del repo o fija una ruta absoluta. Material:
[`examples/codegraph/`](./examples/codegraph/), [`examples/serena/`](./examples/serena/).

**Hilo (slide 30):** **GSD solo funciona en Claude Code.** Copilot no tiene un equivalente propio de su
máquina de estados de fases y roadmap. Las piezas más cercanas:

- el modo plan (`/plan`, `--plan`, impuesto en la capa de herramientas) y `--plan --mode autopilot`;
- `/fleet` para las oleadas;
- agentes personalizados por rol;
- un hook `agentStop` con `decision: block` como puerta de "verificar antes de parar";
- **Spec Kit** (`github/spec-kit`). Solo lo confirman fuentes de terceros, y la versión actual está NO
  VERIFICADA.

El estado sigue en `data/changes/`. Material: [`examples/gsd/`](./examples/gsd/).

**Frase de cierre:** *"El orden es la política: los oráculos diagnostican y el modelo verifica."*

---

## §14 Transferencia: de Claude Code a Copilot (slides 31–32)

**Hilo (slide 31):** Las **cinco reglas viajan sin cambios**:

1. planificar → acordar → implementar;
2. verificar sobre el contrato del consumidor;
3. arreglar la clase general, no una entrada concreta;
4. dejar un rastro duradero;
5. la persona es dueña de todo lo externo.

Solo cambia la superficie:

| Claude Code | Copilot |
|---|---|
| `CLAUDE.md` | `AGENTS.md` + `.instructions.md` (la CLI también lee `CLAUDE.md`) |
| `~/.claude/skills` | `.github/skills` (ojo con el hueco de la CLI) |
| allow/deny en settings | flags + hooks |
| PreToolUse | `preToolUse` en `.github/hooks` |
| Agent Teams | `/fleet` + cloud agent |
| `claude -p` | `copilot -p --trust-folder` |

El kit de arranque es [`COPILOT_ADAPTATION.md`](./docs/ai-agents-code-methodology/COPILOT_ADAPTATION.md)
más la superficie lista para copiar en
[`docs/ai-agents-code-methodology/copilot/`](./docs/ai-agents-code-methodology/copilot/).

**Hilo (slide 32):** este es el slide que más importa para la gobernanza. Hay **agujeros nuevos**:

- `/pr create|auto|automerge` de la CLI, que pueden hacer merge (cobertura del hook NO VERIFICADA);
- **Copilot code review puede aprobar PRs** (preview, desactivado por defecto; déjalo desactivado);
- el revisor lee sus instrucciones desde la rama head, así que pon CODEOWNERS en `.github/**`,
  `AGENTS.md` y `.mcp.json`.

Y, como novedad de este volumen, **"la persona es dueña del merge" ya se puede imponer**: el hook de
denegación `preToolUse` más `--deny-tool` (deny gana a `--yolo`), los límites estructurales del cloud
agent (no puede aprobar ni hacer merge, y solo hace push a `copilot/`) y
`disableBypassPermissionsMode`.

**Frase de cierre:** *"En 2025, 'el agente no hace merge' era una política. En 2026 es un hook, un flag y una regla de rama, y aun así tienes que cerrar dos puertas nuevas."*

---

## §15 Operaciones: sincronización de máquinas y registro compartido (slide 33)

**Hilo:** dos mecanismos que no compiten entre sí:

- **(A) tarball + USB** para levantar una máquina entera. La salida es una copia completa; la entrada
  es solo el delta de `data/`. Lleva `~/.copilot` a propósito (skills, agentes, `mcp-config.json`) y
  vuelve a fijar el `--path` de CodeGraph en la máquina de destino.
- **(B) un registro compartido sobre S3** para el trabajo diario. El alcance crece por fases revisadas.
  Se escribe mediante sync y se lee mediante un montaje de solo lectura. Dry-run por defecto. Se
  protegen **las dos** direcciones. Un único publicador. "Derivado" es una propiedad de cada fichero, no
  de la carpeta.

La parte específica del agente: la máquina tiene un rol. `IDENTITY.md` dice si es publicadora o
contribuidora, y `AGENTS.md` apunta a ese fichero. En Copilot, la skill `day` se puede imponer con un
hook de prompt `sessionStart` que ejecuta `/day start` (CLI, solo en sesiones interactivas nuevas). El
volumen de Cursor no podía hacerlo.

Runbooks: [`docs/synchro/`](./docs/synchro/) · scripts:
[`examples/methodology/s3-sync/`](./examples/methodology/s3-sync/).

**Frase de cierre:** *"Una regla en un runbook se degrada en silencio. Una rutina que invocas deja rastro."*

---

# CONTINUACIÓN DE LA SESIÓN 2 — El grafo de conocimiento de tickets

## §16 (slides 34–37)

**Hilo (slide 35):** Un bug "nuevo" casi siempre tiene contexto previo que limita el arreglo.
**graphify** (no CodeGraph; CodeGraph es solo la analogía) construye un grafo sobre la *memoria* del
proyecto: informes de tickets, sharp edges, runbooks. `kg_refresh.sh prepare` prepara el corpus fuera
del repo, porque graphify respeta `.gitignore` y `data/` está ignorado. Después el agente hace la
extracción semántica, y `finalize` copia los artefactos de vuelta y comprueba que no haya fugas. Los
extremos del pipeline son deterministas y están probados.

**Hilo (slide 36):** la instantánea actual del grafo tiene **3.921 nodos · 8.508 enlaces · 178
comunidades · 73 hiperaristas**. Procedencia de los enlaces: 94,3% `EXTRACTED`, 5,6% `INFERRED` y menos
del 0,1% `AMBIGUOUS`. La imagen del deck es una representación solo de la topología a partir de la
instantánea actual de ILS_2; se omiten etiquetas y metadatos porque el grafo original contiene
identificadores internos. El grafo interactivo incluido en
[`docs/knowledge-graph/`](./docs/knowledge-graph/) sigue siendo una instantánea distinta, más antigua y
sanitizada. Consulta [`docs/KNOWLEDGE_GRAPH.md`](./docs/KNOWLEDGE_GRAPH.md).

**Hilo (slide 37):** las consultas usan **cero LLM** (`kg_query.sh explain|path|find` lee
`graph.json`) y se enganchan en la etapa 1 (Orientarse): ejecuta `kg` *antes* de grep. Con Copilot:

- Pon las skills en `.github/skills/` o en `~/.copilot/skills/`. La CLI no las encontrará en
  `~/.claude/skills`.
- El paso semántico de `kg-refresh` puede ejecutarse con subagentes de la CLI (`task`, `/fleet`), o
  seguir ejecutándose desde Claude Code.
- La protección de "solo el publicador" se queda en el script.
- No es tarea para el cloud agent: el corpus no está en su sandbox.

**Frase de cierre:** *"Pagas un paso semántico al construir y cero LLM al consultar. El grafo es el mapa; el agente es el guía."*

---

## Comprobación de paridad en WSL (slide 38)

La comprobación de paridad en WSL solo recoge evidencia que el otro agente obtuvo de verdad. El
usuario confirmó las ocho skills personales en la vista activa de Copilot Customizations; la CLI de
CodeGraph y una consulta MCP acotada funcionaron en el repo de destino; las suites de tests de
evidence y Atlassian se ejecutaron contra fixtures offline o simulados. Por separado, se confirmó que
la vista MCP de Copilot en el repo del curso muestra CodeGraph y Context7. No juntes todo esto en una
sola afirmación sobre todas las superficies del repo de destino.

La comprobación **no** ejecutó, a propósito, trabajo real de preview (no había fixture aprobado),
descargas de evidencia, lecturas autenticadas de Atlassian ni operaciones compartidas de `day` /
`kg-refresh`. Serena no estaba disponible; Pylance aportó navegación local de Python, que no sustituye
a Serena. El slide hace visible este límite en lugar de presumir de paridad completa.

**Frase de cierre:** *"Verificado significa exactamente lo que ejecutamos; pendiente significa que aún no está demostrado."*

---

## Apéndice y cierre (slides 39–40)

**Slide 39:** la tabla de equivalencias Claude Code → Cursor → Copilot. Es el slide para hacerle una
foto. La versión larga está en [`GUIA_TECNICA.md`](./GUIA_TECNICA.md).

**Slide 40:** ocho ideas para llevarse y después las fuentes. Lee la fecha en voz alta: **verificado
el 2026-10-17; Copilot cambia rápido, así que revísalo antes de reutilizarlo.** Fuentes:
docs.github.com/en/copilot, code.visualstudio.com/docs, github.blog/changelog y el
[fichero de hallazgos](./docs/research/COPILOT_FINDINGS_2026-10-17.md).

**Frase de cierre:** *"De asistente a sistema: la herramienta cambia y la disciplina no. En Copilot, por fin, parte de esa disciplina se puede imponer."*
