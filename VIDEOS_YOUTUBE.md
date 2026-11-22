# Vídeos de YouTube del curso

Títulos y descripciones para publicar las cuatro grabaciones del curso: las dos sesiones en castellano y
las mismas dos sesiones en inglés. Cada descripción está en un bloque de texto plano para copiarla tal cual
en YouTube, que no interpreta Markdown.

| Vídeo | Idioma | Sesión | Slides |
|---|---|---|---|
| 1 | Castellano | Sesión 1: la herramienta | 1 a 24 |
| 2 | Castellano | Sesión 2: la metodología y el grafo de conocimiento de tickets | 25 a 42 |
| 3 | Inglés | Session 1: the tool | 1 a 24 |
| 4 | Inglés | Session 2: the methodology and the ticket knowledge graph | 25 a 42 |

Antes de publicar, conviene añadir a cada descripción los capítulos con marcas de tiempo y, en cada vídeo,
el enlace a su pareja (la otra sesión del mismo idioma) una vez que tenga URL.

---

## Vídeo 1. Castellano, Sesión 1

Título:

```text
GitHub Copilot para desarrolladores - Parte 1: la herramienta
```

Descripción:

```text
Primera sesión del curso sobre GitHub Copilot como agente de programación, orientado a desarrolladores. No hablamos de autocompletado: hablamos de un agente que lee tu código, edita ficheros, ejecuta comandos y abre pull requests. El objetivo es entender qué piezas tiene Copilot, qué fichero lee cada una y cómo configurarlas bien.

La idea de partida: "Copilot" no es un solo producto. Es un agente de terminal, dos motores distintos dentro de VS Code, un plugin de JetBrains, un agente en la nube que abre pull requests y un revisor de pull requests. La mayoría de las afirmaciones erróneas sobre Copilot vienen de mezclar estas piezas.

Qué se cubre en este vídeo:

- Mapa de superficies: Copilot CLI (copilot, no el retirado gh copilot), VS Code con sus dos harnesses (Copilot y Local), JetBrains, Copilot cloud agent y Copilot code review.
- Instalación, autenticación y modo headless con copilot -p para scripts y CI. Modelos y facturación en GitHub AI Credits: cómo se relaciona un crédito con los tokens y cuánto cuesta un turno.
- Memoria e instrucciones: AGENTS.md, copilot-instructions.md y ficheros .instructions.md con applyTo, y qué carga cada superficie.
- Permisos, carpetas de confianza y sandbox: por qué deny siempre gana a allow y por qué una regla de equipo como "nunca hagas push" tiene que ser un hook.
- Sesiones, ventana de contexto y prompt caching: qué se puede controlar y qué no.
- MCP: un protocolo y cuatro ficheros de configuración distintos, y las trampas de cada superficie.
- Skills y plugins: un mismo SKILL.md para casi todas las superficies, y qué cambia al portar desde Claude Code.
- Agentes personalizados y subagentes: cuándo usar un subagente, /fleet o el cloud agent.
- Hooks: el veto determinista y una receta portable para bloquear push, pull request y merge.
- Automatización: copilot -p en GitHub Actions, tareas del cloud agent por API, Copilot SDK y revisión de código automática.

La documentación de Copilot se contrastó con las fuentes oficiales el 17 de octubre de 2026. Copilot cambia rápido: revisa las fuentes antes de reutilizar el material.

La segunda parte del curso, en otro vídeo, trata la metodología de trabajo con agentes y el grafo de conocimiento de tickets.

Material del curso (presentación, guías y ejemplos):
https://github.com/olonok69/copilot_code_ml_engineer

El mismo curso con otras herramientas:
Claude Code: https://github.com/olonok69/claude_code_ml_engineer
Cursor: https://github.com/olonok69/cursor_code_ml_engineer

Documentación oficial:
GitHub Copilot: https://docs.github.com/en/copilot
VS Code: https://code.visualstudio.com/docs
```

---

## Vídeo 2. Castellano, Sesión 2

Título:

```text
GitHub Copilot para desarrolladores - Parte 2: la metodología y el grafo de conocimiento de tickets
```

Descripción:

```text
Segunda sesión del curso sobre GitHub Copilot. Una herramienta potente sin método produce caos rápidamente, así que aquí vemos cómo se trabaja de verdad con un agente de programación en un proyecto en producción. La metodología no depende de la herramienta: nació en Claude Code, pasó a Cursor y en este vídeo la vemos funcionando en Copilot. Terminamos con un caso completo, un grafo de conocimiento construido a partir del historial de tickets del proyecto, y con una prueba de campo en una jornada real.

La idea central: el agente es un colaborador disciplinado, no un piloto automático. El agente se encarga de investigar, planificar, implementar, probar y documentar. La persona decide qué se hace y es la única que hace push, abre pull requests, hace merge o despliega. En Copilot, por primera vez, esa regla se puede imponer con un hook.

Qué se cubre en este vídeo:

La metodología
- El flujo de 11 etapas, desde orientarse hasta persistir lo aprendido, unidas por puertas que detienen el trabajo cuando falta evidencia.
- La puerta de salida son cinco comprobaciones, no "los tests pasan", y cinco casos reales en los que una comprobación en verde no demostraba nada.
- Las herramientas del método y el orden en que se usan, de lo barato y determinista a lo caro: grafo de conocimiento, CodeGraph, Serena, oráculos deterministas y Playwright. GSD solo existe en Claude Code; vemos sus sustitutos en Copilot.
- La transferencia de Claude Code a Copilot: las cinco reglas que viajan sin cambios, lo que cambia en la superficie y los agujeros nuevos que hay que cerrar (/pr automerge y las aprobaciones del code review).
- Operaciones: sincronizar máquinas y compartir el registro de ingeniería con un equipo usando S3.

El grafo de conocimiento de tickets
- El problema: responder "qué se rompió antes cerca de aquí" sin leer todo el historial.
- El pipeline construido con graphify y las skills kg y kg-refresh, que se portan a Copilot sin cambios de fondo.
- El resultado: 3.921 nodos, 8.508 enlaces y 178 comunidades, que se consultan sin llamar a ningún modelo.

La prueba de campo (28 de octubre de 2026)
- La metodología y todas sus skills ejecutadas con Copilot en VS Code durante una jornada real.
- Un ticket pasado repetido a través de las puertas: Copilot llega a la misma causa raíz, escribe 14 tests nuevos y valida el arreglo dentro de la imagen desplegada.
- Qué quedó verificado, qué sigue pendiente y por qué conviene decirlo en voz alta.

La primera parte del curso, en otro vídeo, explica la herramienta: superficies, instalación, memoria, permisos, contexto, MCP, skills, subagentes, hooks y automatización.

Material del curso (presentación, guías y ejemplos):
https://github.com/olonok69/copilot_code_ml_engineer

El mismo curso con otras herramientas:
Claude Code: https://github.com/olonok69/claude_code_ml_engineer
Cursor: https://github.com/olonok69/cursor_code_ml_engineer

Referencias:
Documentación de GitHub Copilot: https://docs.github.com/en/copilot
CodeGraph: https://colbymchenry.github.io/codegraph/
Serena: https://github.com/oraios/serena
GSD: https://github.com/tomascortereal/claude-code-setup
Spec Kit: https://github.com/github/spec-kit
graphify: https://graphify.net
```

---

## Vídeo 3. Inglés, Sesión 1

Título:

```text
GitHub Copilot for developers - Part 1: the tool
```

Descripción:

```text
First session of the course on GitHub Copilot as a coding agent, aimed at developers. This is not about autocomplete: it is about an agent that reads your code, edits files, runs commands and opens pull requests. The goal is to understand which pieces Copilot is made of, which file each one reads and how to configure them well.

The starting point: "Copilot" is not a single product. It is a terminal agent, two different engines inside VS Code, a JetBrains plugin, a cloud agent that opens pull requests and a pull request reviewer. Most wrong statements about Copilot come from mixing these pieces up.

What this video covers:

- Surfaces map: Copilot CLI (copilot, not the retired gh copilot), VS Code with its two harnesses (Copilot and Local), JetBrains, Copilot cloud agent and Copilot code review.
- Install, authentication and headless mode with copilot -p for scripts and CI. Models and billing in GitHub AI Credits: how a credit relates to tokens and what a turn costs.
- Memory and instructions: AGENTS.md, copilot-instructions.md and .instructions.md files with applyTo, and what each surface loads.
- Permissions, trusted folders and sandbox: why deny always wins over allow, and why a team rule such as "never push" has to be a hook.
- Sessions, the context window and prompt caching: what you can control and what you cannot.
- MCP: one protocol, four different configuration files, and the traps on each surface.
- Skills and plugins: the same SKILL.md on almost every surface, and what changes when porting from Claude Code.
- Custom agents and subagents: when to use a subagent, /fleet or the cloud agent.
- Hooks: the deterministic veto, and a portable recipe that blocks push, pull request and merge.
- Automation: copilot -p in GitHub Actions, cloud agent tasks over the API, the Copilot SDK and automatic code review.

The Copilot documentation was checked against the official sources on 17 October 2026. Copilot moves fast: check the sources again before reusing the material.

The second part of the course, in a separate video, covers the methodology for working with agents and the ticket knowledge graph.

Course material (slides, guides and examples):
https://github.com/olonok69/copilot_code_ml_engineer

The same course with other tools:
Claude Code: https://github.com/olonok69/claude_code_ml_engineer
Cursor: https://github.com/olonok69/cursor_code_ml_engineer

Official documentation:
GitHub Copilot: https://docs.github.com/en/copilot
VS Code: https://code.visualstudio.com/docs
```

---

## Vídeo 4. Inglés, Sesión 2

Título:

```text
GitHub Copilot for developers - Part 2: the methodology and the ticket knowledge graph
```

Descripción:

```text
Second session of the course on GitHub Copilot. A powerful tool without a method produces chaos quickly, so here we look at how to actually work with a coding agent on a project in production. The methodology does not depend on the tool: it started in Claude Code, moved to Cursor, and in this video we see it running in Copilot. We finish with a complete case, a knowledge graph built from the project's ticket history, and with a field test on a real working day.

The core idea: the agent is a disciplined collaborator, not an autopilot. The agent handles research, planning, implementation, tests and documentation. The person decides what gets done and is the only one who pushes, opens pull requests, merges or deploys. In Copilot, for the first time, that rule can be enforced with a hook.

What this video covers:

The methodology
- The 11-stage workflow, from orientation to persisting what was learned, linked by gates that stop the work when evidence is missing.
- The exit gate is five checks, not "the tests pass", and five real cases where a green check proved nothing.
- The tools of the method and the order to use them, from cheap and deterministic to expensive: knowledge graph, CodeGraph, Serena, deterministic oracles and Playwright. GSD only exists in Claude Code; we look at its substitutes in Copilot.
- The transfer from Claude Code to Copilot: the five rules that travel unchanged, what changes on the surface, and the new holes to close (/pr automerge and code review approvals).
- Operations: syncing machines and sharing the engineering record with a team using S3.

The ticket knowledge graph
- The problem: answering "what broke before near here" without reading the whole history.
- The pipeline built with graphify and the kg and kg-refresh skills, which port to Copilot without changes of substance.
- The result: 3,921 nodes, 8,508 links and 178 communities, queried without calling any model.

The field test (28 October 2026)
- The methodology and all its skills run with Copilot in VS Code on a real working day.
- A past ticket replayed through the gates: Copilot reaches the same root cause, writes 14 new tests and validates the fix inside the deployed image.
- What was verified, what is still pending, and why it is worth saying so out loud.

The first part of the course, in a separate video, explains the tool: surfaces, installation, memory, permissions, context, MCP, skills, subagents, hooks and automation.

Course material (slides, guides and examples):
https://github.com/olonok69/copilot_code_ml_engineer

The same course with other tools:
Claude Code: https://github.com/olonok69/claude_code_ml_engineer
Cursor: https://github.com/olonok69/cursor_code_ml_engineer

References:
GitHub Copilot documentation: https://docs.github.com/en/copilot
CodeGraph: https://colbymchenry.github.io/codegraph/
Serena: https://github.com/oraios/serena
GSD: https://github.com/tomascortereal/claude-code-setup
Spec Kit: https://github.com/github/spec-kit
graphify: https://graphify.net
```
