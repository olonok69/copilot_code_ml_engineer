# Trabajar con agentes de código de IA: el manual técnico

> English version: [`TECHNICAL.md`](TECHNICAL.md).

> **Público:** ingenieros que van a ejecutar, supervisar o ampliar un ciclo de
> desarrollo con agentes de IA. Es el complemento de implementación de
> [`README.md`](README.md) (que es la visión general en lenguaje llano). Es la
> misma metodología; aquí describimos la *mecánica* (los gates, los arneses, las
> pruebas) con detalle suficiente para construirla.
>
> **Deliberadamente agnóstico de la tecnología.** No se nombra ninguna
> herramienta, librería, lenguaje, proveedor de modelos ni producto. Todo lo que
> sigue es un *rol* o una *técnica*; rellena los roles con lo que ofrezca tu
> stack. Cuando decimos "el modelo" nos referimos a cualquier componente
> probabilístico/LLM; "el oráculo" es cualquier componente determinista que puede
> responder gratis a una pregunta estructural; "el agente" es el asistente de
> código de IA; "el bot de revisión" es cualquier revisor automático.
>
> **Esta revisión** añade las lecciones de una serie de cambios en los que los
> propios *gates* resultaron ser el punto débil: validar un diagnóstico contra un
> caso de respuesta conocida antes de fiarse de él (§2, incluida la arista
> peligrosa del atajo de la sonda barata que este documento recomendaba sin
> protección); afirmar sobre la composición y no sobre los totales, y decir en voz
> alta lo que un gate *no puede* mostrar (§4); verificar dentro del artefacto que
> realmente se entrega, no solo en local (§4); encontrar al verdadero último
> escritor de un campo del contrato y comprobar de dónde salió un valor
> "esperado" (§1); tratar el contrato como un documento vivo con tres resultados
> legítimos (§1); y un §7 nuevo sobre **compartir el rastro duradero entre
> máquinas y personas** mediante almacenamiento de objetos, incluido el problema
> de la identidad de la máquina, que solo aparece cuando un agente puede actuar en
> más de un rol.
>
> **Esta revisión** se ocupa de los puntos ciegos que les quedaban a los gates y de
> la dimensión *temporal* del registro. Un gate puede ser correcto, ejecutarse
> limpio y aun así no distinguir el arreglo que entregaste de uno más débil (§4);
> una comprobación dentro del artefacto no demuestra nada hasta que se ha visto
> fallar sobre el código sin arreglar (§4). Un hecho que alguien afirma sobre el
> entorno es una hipótesis, no evidencia, y los manejadores de excepciones que hay
> entre tú y un síntoma son lo primero de lo que sospechar al diagnosticar (§2). El
> §6 gana las dos dimensiones que le faltaban: el **tiempo**, cómo sobrevive el
> estado en curso a un límite de sesión, y la **densidad**, el parámetro del índice
> que ningún gate estructural puede ver. El §7 gana el **mínimo privilegio**: el
> permiso obvio sobre un registro compartido amplía el acceso en lugar de
> restringirlo. También añade la lección más afilada del conjunto (§4): una suite
> de tests depende de tu especificación y no puede decirte que la especificación
> está mal.
>
> **Esta revisión** recoge la primera ejecución **medida** del ciclo completo con
> un agente nuevo (GitHub Copilot en VS Code, 2026-10-28: una jornada real más un
> ticket pasado repetido desde su commit anterior al arreglo). Sustituye el "se
> espera paridad" por lo que se ejecutó de verdad, y añade lo que enseñó esa
> ejecución: un §10 nuevo sobre **validar la metodología en un agente nuevo**
> (validación acotada, la repetición histórica y la salvedad de si fue a ciegas);
> una capacidad configurada para un agente no está configurada para el siguiente
> (§6); un instrumento puede escribir en su propia entrada, y un tiempo de espera
> corto no es un defecto (§2); guarda una copia exacta de una medición registrada
> antes de repetirla, y nombra los ficheros de tests que no se ejecutaron (§4); la
> vista previa de la publicación es donde se hace visible una violación de alcance
> (§7); y las ediciones de una herramienta de refactorización pueden llegar después
> de que responda (§8). Informes de campo: [`field-reports/`](field-reports/).

---

## 0. La versión en una frase

Envuelve un generador rápido, con mucha amplitud y a veces demasiado seguro de sí
mismo en un conjunto de **gates deterministas** (reproducción del contrato, un
oráculo gratuito, una batería de tests por capas, una prueba de generalidad y un
escaneo de saneado) para que nada llegue al registro permanente sin evidencia, y
la persona conserve las decisiones y las acciones hacia fuera.

---

## 1. Primero el contrato: define la caja negra antes de tocar el interior

Elige el **contrato de salida**, la interfaz exacta que observa un consumidor
posterior, y conviértelo en la unidad de verdad. No el valor que devuelve una
función interna; lo que el siguiente sistema lee de verdad. Dos consecuencias:

- **Gate de entrada.** Antes de escribir código, reproduce el síntoma reportado
  *en el contrato*. Si no consigues que aparezca ahí, el defecto no está en tu
  componente, está aguas abajo, y la respuesta correcta es devolverlo con la
  muestra del contrato adjunta, no un parche. Este único gate elimina la clase de
  trabajo perdido más cara: arreglar el sistema equivocado.
- **Gate de salida.** Antes de entregar, reproduce el contrato *arreglado* en
  local y demuestra que el síntoma ha desaparecido. Que los tests unitarios
  internos estén en verde es necesario, no suficiente: el consumidor ve el
  contrato, así que lo que demuestras es el contrato. "Sin reproducción local del
  contrato = no está terminado."

Construye un pequeño arnés que ejecute el componente de extremo a extremo y emita
la forma del contrato (la misma estructura, profundidad y conjunto de campos que
analiza el consumidor). Reproduce los bugs **a través de esa forma completa**,
nunca a través de una primitiva aislada: una primitiva puede parecer correcta
mientras el contrato ensamblado está mal.

**Encuentra la verdadera etapa final.** El contrato lo produce lo que se ejecuta
*al final*, que a menudo es un envoltorio o un paso de ensamblado que reconstruye
un campo que el componente interno ya había rellenado. Si reproduces contra el
componente interno, estás leyendo una etapa previa a la final: un arreglo ahí
puede descartarse en silencio en la reconstrucción, y tu arnés mostrará que
funciona mientras la salida entregada está mal. Identifica al último escritor de
cada campo que te importa y reproduce a través de él. Equivocarse aquí cuesta
sesiones de depuración enteras que acaban en un falso "no reproducible".

**Establece la procedencia del valor esperado.** Cuando un ticket indica un número
o una salida esperada, pregunta de dónde salió. "El otro entorno devuelve X" es
evidencia *sobre ese entorno*, nunca una especificación; y si ese entorno ejecuta
el mismo camino de código que estás arreglando, igualarlo fielmente reproduce el
bug. Deriva el objetivo de la propia estructura de la entrada y del contrato
escrito, y dilo con claridad cuando la expectativa indicada está mal. Que una
expectativa reportada se equivoque por uno es frecuente y es en sí un hallazgo.

**Trata el contrato como un documento vivo, no como un oráculo fijo.** Cuando un
cambio altera lo que emite el componente, consulta la regla que lo gobierna
*antes* de diseñar el arreglo y haz exactamente una de tres cosas: **cumplir** la
regla, **revisar** la regla como parte del mismo cambio, o **registrar** por qué
el cambio queda fuera del alcance de la regla. Los tres son resultados legítimos;
**el silencio no lo es.** Revisar es normal y esperable: que un arreglo entregado
revele que una regla acordada estaba mal es como mejora el contrato, y una regla
mal escrita el primer día sobrevivirá, si no, a todos los que recuerdan por qué.
Dos notas prácticas: cita la regla por un **identificador estable** en todo lo
que vaya hacia fuera (texto de revisión, tickets, criterios de aceptación), nunca
por una ruta de fichero, porque las rutas locales no se resuelven para quien lo
lee; y resiste la tentación de imponerlo con una comprobación al hacer merge: la
decisión tiene tres valores, y un gate binario bloquearía el resultado *correcto*
de "revisar la regla".

## 2. Causa raíz determinista antes de cualquier ejecución de pago

El generador es probabilístico y a menudo se paga por uso. No lo uses para
*diagnosticar*. En su lugar:

- **Encuentra un oráculo gratuito y determinista.** La mayoría de los sistemas
  contienen un componente que puede responder a la pregunta estructural de forma
  determinista y sin coste marginal (un parser, un motor de maquetación, un
  analizador estático, un validador de esquemas o un **grafo/índice precalculado
  sobre el código o sobre el registro de decisiones previas**). Úsalo para
  confirmar la hipótesis: ejecútalo, obtén la misma respuesta cada vez y tendrás
  una causa raíz que puedes defender. Gasta la ejecución de pago/probabilística
  *solo* al final, para verificar el arreglo terminado contra el contrato en vivo.
- **Prueba los predicados de forma barata, pero pon un canario a la sonda.** Para
  probar una función de decisión aislada, instancia solo lo necesario del objeto
  para ejercitarla: sáltate el constructor pesado creando una instancia vacía y
  fijando solo los campos que lee el predicado. Obtienes un test determinista de
  milisegundos sobre la rama exacta, sin inicialización cara ni llamadas a red o
  al modelo. **Este atajo tiene una arista peligrosa, y ya ha hecho sangre.**
  Saltarse el constructor deja sin fijar todos los atributos en los que no
  pensaste; si el método bajo prueba lee uno de ellos *y* tiene su propio
  `try/except`, el error de atributo se traga y se devuelve como un negativo
  plausible. La sonda informa entonces de un "no" seguro y uniforme para todas las
  entradas, y un estudio basado en ella dio el titular correcto por una razón
  completamente equivocada, con los varios cientos de entradas leyéndose como
  negativas. Tres reglas hacen seguro el atajo:
  1. **Pon siempre un canario contra un caso de respuesta conocida.** Antes de
     fiarte de una sonda sobre entradas desconocidas, ejecútala sobre una entrada
     cuya respuesta ya conoces y registra ese resultado junto al hallazgo. Una
     sonda que no puede producir el positivo conocido no está midiendo nada.
  2. **Nunca envuelvas la medición en tu propio `try/except → return False`.**
     Deja que falle. Un fallo ruidoso es un instrumento que funciona; uno
     silencioso es un instrumento roto que parece evidencia.
  3. **Pon el canario al modo de fallo, no solo al instrumento.** Una sonda puede
     estar perfectamente construida y aun así no demostrar nada, porque la
     perturbación que aplica no es la que aplica producción. Un test sintético
     renombró los *contenedores* en los que se agrupaban las cosas y alteró un
     pequeño porcentaje de los elementos, recuperó el 100% del mapeo y se dio por
     "verificado". La reconstrucción real cambió algo que el test nunca tocó, los
     **identificadores de los propios elementos**, el 88% de ellos, y la
     recuperación cayó por debajo del 1%. El instrumento era correcto; el
     experimento estaba mal. Antes de fiarte de un canario en verde, di en una
     frase *qué le hace producción a estos datos* y comprueba que el canario hace
     lo mismo. Si no puedes, di que el gate no está probado: "el test que pude
     construir pasó" no es "el riesgo está descartado".
- **Una regla que no coincide con nada se ve exactamente igual que una regla que
  funciona.** Filtros, exclusiones, guardas, listas permitidas: cuando el
  comportamiento correcto es el *silencio*, el éxito y el fracaso total producen la
  misma salida. En una sola tarde se encontraron cuatro defectos así en un mismo
  fichero: una exclusión anclada en el extremo equivocado de la ruta, otra que
  nombraba un directorio que ya no existía con ese nombre, una tercera a la que
  nunca se llegaba; y todas habían pasado la revisión, porque el patrón *se leía*
  bien. Ninguna se encontró inspeccionando. Las cuatro se encontraron ejecutando la
  operación en modo vista previa y **leyendo la lista de lo que realmente
  coincidía y se rechazaba**. La regla se generaliza: **nunca te fíes de un filtro
  que no hayas visto rechazar algo.** Si no puedes señalar un elemento que
  excluyó, no lo has probado, solo lo has leído.
- **Una comprobación debe distinguir "no" de "no pude preguntar".** Un cerrojo de
  coordinación respondía *"nadie lo tiene"* cada vez que fallaba su lectura:
  credencial caducada, sin red o permiso denegado se reducían a la misma respuesta
  tranquilizadora, porque el camino de fallo devolvía por defecto un resultado
  vacío. El comando de estado solo inducía a error; el comando de *reclamar* usaba
  la misma lectura, así que un token caducado habría concedido el cerrojo mientras
  otra persona lo tenía, que es justo la colisión que el cerrojo debía impedir.
  **Un resultado negativo y una medición fallida no deben compartir salida.**
  Cuando escribas una comprobación, enumera sus modos de fallo y haz que todos sean
  ruidosos; reserva la respuesta silenciosa para el caso que de verdad verificaste.
- **Descarta la lógica y la configuración antes que la "varianza".** "El modelo
  está siendo inestable" es una conclusión de último recurso. Cuando un sistema es
  de verdad no determinista, el bug suele ser una **sensibilidad**, no la varianza
  en sí: la misma entrada da un resultado correcto en una ejecución y uno erróneo
  en la siguiente porque alguna heurística está justo en un umbral. Arregla la
  sensibilidad (aleja la entrada del umbral, haz explícito el límite); no lo
  "arregles" repitiendo hasta que salga verde. Una ejecución en verde sobre un
  sistema no determinista no es un aprobado.
- **Verifica la premisa, no solo los pasos.** Un hecho que alguien afirma sobre la
  máquina, el entorno o la identidad con la que te ejecutas es una **hipótesis, no
  evidencia**, incluso si lo afirmaste tú hace una hora. Un procedimiento
  construido sobre una premisa sin verificar falla de la forma más cara posible:
  cada paso se ejecuta bien y el resultado sigue estando mal, así que un rastro de
  comprobaciones en verde apunta lejos de la causa. Verifica primero la premisa y
  diseña la comprobación para que *pueda fallar de verdad*: una sonda que devuelve
  la misma respuesta se cumpla o no la premisa no ha verificado nada. La trampa
  concreta en las preguntas de entorno y acceso: **un mensaje de error describe la
  petición que acabas de hacer, no el estado del mundo.** Un permiso denegado puede
  significar que falta el derecho de acceso, o solo que caducó una credencial en
  caché. Diagnosticar a partir del texto del error produjo tres conclusiones
  equivocadas distintas sobre la misma pregunta antes de que nadie consultara
  directamente el directorio autoritativo.
- **Sospecha de los manejadores de excepciones que hay entre tú y el síntoma.**
  Esto es una *heurística de depuración, no una regla de estilo*: los manejadores
  a menudo son exactamente lo correcto, y una prohibición general no es lo que
  necesita el ciclo. Pero cuando un defecto es invisible, intermitente o se
  presenta como "varianza", pregunta **qué manejador está entre tú y él** antes de
  culpar a la lógica o al modelo. Un error tragado llega como un valor plausible, y
  un valor plausible cierra una investigación. Dos costes que podemos medir: un
  `catch` amplio convirtió un fallo en un resultado degradado pero exitoso, y el
  defecto estuvo funcionando unos **diez meses** sin un solo reporte; y, por otro
  lado, un manejador que *sí* relanzaba la excepción perdía aun así la causa
  original, de modo que relanzar conservó el fallo y destruyó la única evidencia de
  dónde venía. **Relanzar no basta; conserva la cadena.** Una vez encontrado un
  manejador así, ciérralo de una de dos formas: arréglalo, o **acéptalo por
  escrito** en el registro duradero. Una decisión no registrada de dejarlo es
  indistinguible de no haberse dado cuenta.
- **El instrumento puede escribir en su propia entrada.** Un componente que
  ejecutas para observar un documento puede también *reescribir* el documento que
  abrió: volver a guardarlo, cambiar su fecha, normalizar su contenido. Ejecuta
  todo diagnóstico sobre una **copia** y comprueba después que la fecha de
  modificación y el hash del original no han cambiado. Una evidencia reescrita en
  silencio por el acto de medirla ya no es evidencia de lo que vio el sistema.
- **Un tiempo de espera agotado es una propiedad de tus herramientas hasta que se
  demuestre lo contrario.** En la prueba de campo, la primera importación del
  componente bajo prueba desde un disco montado lento tardó unos cinco minutos en
  frío (menos de dos con caché), y una herramienta basada en un servidor de
  lenguaje agotó el tiempo en su primera llamada mientras arrancaba. Las dos cosas
  parecían fallos; ninguna era un defecto. Antes de informar de que "se cuelga",
  repite una vez con un tiempo de espera generoso y anota los tiempos en frío y en
  caliente: así sabrás si encontraste un bug o un disco lento.

## 3. Regresión o preexistente: demuestra cuál antes de hacerte cargo

Cuando aparece un defecto durante tu cambio, establece su procedencia antes de
aceptarlo o rechazarlo:

- Reprodúcelo sobre la **base anterior al cambio** (el estado previo a tu
  trabajo).
- Compara la salida del contrato antes y después de tu cambio, idealmente byte a
  byte en la parte relevante. *Idéntica* antes y después ⇒ preexistente, y tu
  cambio queda exonerado; *distinta* ⇒ lo causaste tú.

No es echar balones fuera: cambia decisiones reales: la base desde la que creas
la rama, si el arreglo entra en el alcance del ticket actual y la historia que le
cuentas a quien da el visto bueno. Hacerse cargo en silencio de un bug antiguo, o
quitarle importancia a una regresión real, cuesta más después en ambos casos.
Haz que sea una prueba, no una afirmación.

## 4. La batería de tests: por capas, RED primero, cero regresiones

Cinco capas concéntricas, cada una un gate real:

1. **Unitaria:** la función de decisión o el helper aislado (la sonda barata del
   §2).
2. **Regresión acotada:** un fichero de tests dedicado a *este* defecto, escrito
   primero en RED: míralo fallar por la *razón correcta* antes de escribir el
   arreglo, para saber que el test ejercita de verdad el bug. Un test que nunca
   falló no demuestra nada.
3. **Regresión completa:** toda la suite existente en verde. El recuento *sube*
   exactamente en los tests que añadiste y nada de lo que ya existía pasa a rojo.
4. **De salida:** la reproducción del contrato en vivo del §1, recorriendo el
   camino real (probabilístico) de extremo a extremo.
5. **Artefacto desplegado:** la misma reproducción ejecutada *dentro del
   artefacto que realmente se entrega* (imagen de contenedor, paquete, runtime
   empaquetado), no solo en tu árbol de trabajo. Descarga o construye el
   artefacto, monta el código arreglado, repite la reproducción de salida y
   confirma que es byte a byte lo que produjo el local. "Los tests pasan" es una
   afirmación sobre tu máquina; lo que se entrega es lo que se ejecuta en el
   artefacto. Los defectos solo de entorno (un locale que falta, una fuente, una
   librería nativa) son invisibles para todas las capas anteriores y solo aparecen
   aquí. **Y demuestra que la comprobación puede fallar.** Un arnés que solo se ha
   ejecutado contra código arreglado no es un gate, es una captura de pantalla:
   ejecútalo dos veces, una contra el código *sin arreglar*, donde debe reproducir
   el síntoma, y otra contra el arreglo, donde debe salir limpio. La pareja es la
   evidencia; la segunda ejecución sola no lo es.

Hay una sexta capa de la que nadie es dueño, y es donde viven los fallos caros:
**el artefacto desplegado junto con su configuración.** La capa 5 demuestra que el
artefacto está bien. No demuestra que el entorno le vaya a dejar arrancar.

Dos propiedades hacen invisible este hueco. Primera, el código y la configuración
suelen entregarse por **repositorios distintos, con revisores distintos y sin
orden entre ellos**, así que entre "fusionado" y "funcionando" pasa lo que tarde
el segundo merge, y nada en ninguno de los dos pipelines sabe que el otro está
pendiente. En una ocasión ese hueco fueron cuatro horas con un entorno compartido
caído; los dos cambios eran correctos por separado. Segunda, la comprobación
automática posterior al despliegue responde a una *pregunta distinta* de la que
falló: una suite de humo que llama a la interfaz pública pasa tan contenta
mientras un listener en segundo plano se cae al arrancar por un nombre de cola que
falta, porque nada en la suite llega nunca al listener. Estuvo en verde durante
toda la caída.

Así que: cuando un cambio consume configuración nueva, dilo de forma explícita en
la entrega, nombra el otro repositorio e indica el orden necesario. Prefiere un
servicio que **se degrade de forma ruidosa** cuando le falta la configuración a
uno que la consume al arrancar y muere en silencio. Y cuando añadas una
comprobación posterior al despliegue, afirma sobre el componente que de verdad
puede fallar, no sobre el que es más fácil de consultar.

Conserva la suite acotada de cada defecto como un artefacto permanente con el
nombre del defecto, para que la siguiente persona vea a la vez la guarda y el
ejemplo que la motivó.

**Compara la suite completa con su propia base, y nombra lo que no se ejecutó.**
"Regresión completa en verde" rara vez es literal: algunos tests ya fallan en la
base, y algunos ficheros ni siquiera se pueden recoger en una máquina concreta
(una dependencia en la versión equivocada, un servicio que falta). Ejecuta la
suite entera sobre la **base** y sobre el **arreglo** permitiendo errores de
recogida, y presenta la pareja. En la prueba de campo quedó así: base 1552
pasan / 3 fallan / 5 ficheros sin recoger; con el arreglo 1566 pasan (+14,
exactamente los tests nuevos), los *mismos* 3 fallan, los *mismos* 5 sin recoger.
Fallos idénticos a ambos lados exoneran al arreglo; los 5 ficheros **no están
cubiertos**, y el informe tiene que decirlo en vez de meterlos dentro del "verde".
Cuando el entorno del host no puede ejecutar el camino real, ejecútalo dentro del
artefacto que se entrega (capa 5) con la rama montada en solo lectura.

**Una medición registrada es evidencia: guarda una copia exacta antes de
repetirla.** Repetir un barrido o un diff sobre el corpus suele reescribir su
fichero de salida en el sitio. En la prueba de campo eso sobrescribió el
resultado registrado en el ticket; las cifras nuevas coincidían, pero los bytes
no, y hubo que restaurar el original desde el almacén compartido. Copia antes el
fichero registrado a un lado y después compara.

**Leer los resultados forma parte del gate.** Cinco hábitos separan un aprobado
real de uno que solo parece verde:

- **Afirma sobre la composición, nunca sobre el total.** Un recuento que coincide
  con lo esperado no es un test que pasa. Los totales pierden información: un
  elemento añadido por error y uno eliminado por error se cancelan exactamente.
  Afirma sobre la *lista de miembros* (títulos, ids, claves) e imprime los
  miembros junto a cualquier cifra de titular. Cuanto más cerca de lo esperado cae
  un recuento, más sospecha merece, no menos; el peor resultado posible es un
  número en verde con contenido erróneo dentro, porque nadie lo vuelve a abrir.
  Cuando un defecto tiene una dirección conocida, prefiere un **delta frente a una
  base** (ganados / perdidos) a dos totales.
- **Ajusta la medición a la clase de defecto.** Un defecto geométrico necesita
  una medición geométrica (comparar los rectángulos reales), no un recuento.
  Existen arreglos reales cuyos recuentos antes y después son *idénticos* mientras
  la salida se movió; cualquier comprobación basada en recuentos dice "no pasó
  nada" para ellos.
- **Di qué puede y qué no puede mostrar cada gate.** Si un gate es
  estructuralmente incapaz de fallar para este cambio (el corpus de referencia no
  tiene ningún ejemplo positivo de la forma que acabas de añadir), dilo de forma
  explícita y nombra lo que aporta la evidencia en su lugar. Una ejecución limpia
  sobre entradas que no pueden ejercitar el código nuevo demuestra *ausencia de
  regresión* y no dice absolutamente nada sobre la corrección. Presentarlo como
  validación es la forma más respetable de entregar un cambio sin verificar.
- **Pregunta si el gate distingue tu arreglo de uno más débil.** Un gate que no
  puede fallar es la trampa de arriba; la más sutil pasa *igual* para dos arreglos
  candidatos distintos, así que la suite ratifica en silencio el que te tocó
  escribir. Lo medimos en un defecto: una guarda de límites mínima y una guarda de
  límites con recorte eran **idénticas byte a byte en todos los casos que la suite
  unitaria podía expresar**, y solo un delta a escala de corpus, contando las
  salidas que *cambiaron*, las separó. Siempre que hayas elegido entre dos formas
  de arreglo, nombra la comprobación que las distingue; si la respuesta honesta es
  "ninguno de los tests", di qué medición lo hace y hazla obligatoria en vez de
  opcional. *(Un caso medido. La forma probablemente es más común, porque el motivo
  habitual para preferir el arreglo más amplio es un comportamiento que los tests
  estrechos nunca se escribieron para ver.)*
- **Tu suite no puede probar tu premisa.** El hábito anterior trata de dos
  arreglos candidatos; este trata de que la propia especificación esté mal, y es
  el más caro de los dos. Un test que escribiste y el código que escribiste tienen
  un antepasado común: tu modelo mental del problema. Un test solo puede detectar
  que el código se aparta de tu intención; cuando lo defectuoso es la *intención*,
  todos los tests están de acuerdo con el bug. Escribir más sube la confianza sin
  mejorar la cobertura del riesgo real, lo que es estrictamente peor que saber que
  no lo has comprobado. Lo vimos dos veces en un día. Una regla derivada de tres
  documentos pasó quince tests escritos a propósito y habría destruido salida
  correcta en seis de treinta y seis documentos reales, porque cada caso que
  inventó el autor ponía los datos donde el autor creía que estaban. Horas antes,
  un test de regresión reproducía una entrada malformada que fallaba por la razón
  equivocada: seis tests en verde contra un defecto que el sistema en realidad
  nunca produce. **El disparador es una propiedad del cambio, no de su tamaño:
  cuando un cambio solo puede eliminar o alterar salida existente y ya tienes
  respuestas que sabes correctas, ejecútalo contra ellas.** No es un test más
  amplio, es un instrumento distinto: un mundo cerrado de entradas que imaginaste,
  frente a uno abierto que no imaginaste. Hazte la pregunta literalmente: *¿esto
  destruye una respuesta correcta?*

## 5. Solución genérica, con prueba de que no hace nada fuera de su clase

Arregla la **clase**, nunca la instancia. El parche se basa en una *propiedad
estructural* de la entrada (un régimen de maquetación, un patrón de marcadores,
una forma de token), no en el valor concreto reportado. Dos obligaciones que hacen
real lo "genérico":

- **Cobertura positiva:** la suite acotada incluye entradas hermanas de la misma
  clase que el reporte no mencionaba.
- **Prueba estricta de no-op:** demuestra que el cambio *no hace nada* a las
  entradas fuera de la clase. Los documentos de regresión canónicos (tu conjunto
  de referencia conocido como bueno) salen idénticos byte a byte. Un arreglo que no
  puede demostrar que deja intactos los casos no afectados es un riesgo, no un
  arreglo.

## 6. Arquitectura del contexto: núcleo ligero, detalle bajo demanda, escribir una vez

El agente vuelve a cargar su contexto siempre presente en **cada turno**, así que
el tamaño de ese contexto es un coste recurrente, no puntual. Diséñalo:

- **Núcleo siempre cargado (pequeño):** el documento de orientación
  (arquitectura, convenciones, *decisiones cerradas* con su motivo, normas de
  trabajo), una **instantánea viva** del estado actual e **índices** (una línea
  por ticket / por arista peligrosa / por lección) que apuntan al detalle. El
  índice no tiene por qué quedarse en una lista plana: materialízalo como un
  **grafo consultable y determinista sobre el registro duradero** (los nodos son
  tickets/lecciones/áreas y las aristas, las relaciones entre ellos) para que
  "¿qué trabajo previo toca esta área?" y "¿cómo se conectan estas dos
  decisiones?" sean una consulta de coste cero que devuelve *qué leer* antes de
  abrir nada. Es el gemelo, en el rastro documental, de un grafo semántico del
  código (el índice precalculado sobre el código que aparece entre los oráculos
  gratuitos del §2): uno indexa el código y el otro las decisiones, y ambos son
  oráculos deterministas gratuitos (§2) que consultas antes de cualquier lectura
  lineal o ejecución de pago.
- **Ficheros de referencia bajo demanda (grandes):** los registros por ticket, el
  texto completo de las políticas, el manual de investigación, las plantillas de
  entrega; solo se abren cuando esa área está en juego.
- **Regla de escribir una vez:** cada registro se escribe en exactamente **un**
  registro canónico; el fichero del núcleo lleva un *puntero*, nunca una copia. El
  fallo que esto evita es la triplicación: el mismo cambio pegado en el documento
  de orientación, en el registro de estado y en la memoria, que después se
  desincronizan mientras inflan la factura de tokens de cada sesión futura. (En
  concreto: cuando nuestro conjunto siempre cargado había crecido demasiado, lo
  recortamos un ~73% sin perder información, solo moviendo el detalle a ficheros
  bajo demanda y sustituyéndolo por punteros.)
- **La memoria persistente** sigue la misma forma: una instantánea viva más un
  índice de temas abiertos que conserva explícitamente la *visibilidad* de todo lo
  aparcado o aplazado; ligero no significa con pérdidas.
- **Skills de Copilot bajo demanda (no siempre activas):** skills de proyecto en
  `.github/skills/` (las personales en `~/.copilot/skills/`): **`kg`** (consulta
  del grafo con el historial primero, antes de hacer grep en el rastro),
  **`kg-refresh`** (la máquina contribuidora presenta una solicitud; la
  publicadora reconstruye con el testigo; `--clear` debe borrar las claves
  consumidas en el almacén), **`day`** (abrir/cerrar la jornada sobre el registro
  compartido; `day start` también actualiza la tabla de estado de los tickets
  desde el gestor y cuenta los fallos del servicio de las últimas 24 h sin
  descargar nada), **`sanitise-diff`**, **`atlassian`** (consultas de solo lectura
  al gestor de tickets y a la wiki), **`evidence`** (recoger las entradas y
  salidas de una ejecución fallida *tal como estaban en esa ejecución*, en solo
  lectura). Son rutinas que se invocan, no documentación: la razón más fuerte para
  recurrir a una skill es **imponer** algo, no la comodidad.
- **Una capacidad configurada para un agente no está configurada para el
  siguiente.** Los servidores de herramientas, las skills y las instrucciones se
  registran *por agente*, a menudo en un fichero personal. En la prueba de campo,
  el servidor de navegación semántica "faltaba" en Copilot sin más motivo que el de
  que solo se había registrado para los dos agentes anteriores; una entrada en la
  configuración personal de Copilot (con una copia del fichero antes) y un
  reinicio lo hicieron funcionar. Cuando falte una herramienta, comprueba el
  registro antes de concluir que el agente no puede usarla, y deja por escrito un
  **orden de respaldo** (índice del código → referencias del editor → búsqueda de
  texto) para que el ciclo se degrade en lugar de pararse. Del mismo modo,
  **descubrir no es verificar**: que una skill aparezca en la vista de
  personalización del agente demuestra que se encontró, no que todas las
  operaciones que puede hacer sean seguras ni se hayan probado.

Todo lo anterior es *espacial*: qué va dónde y qué tamaño tiene. Otras dos
dimensiones deciden si la arquitectura aguanta en la práctica.

**Tiempo: el punto de entrada de la sesión.** El trabajo con agentes se
interrumpe constantemente: por límites de contexto, por el fin de la jornada, por
una tarea urgente sin relación. El núcleo siempre cargado describe el *proyecto*,
nunca lo que tenías a medias, así que, sin un sitio donde poner el estado en
curso, este se queda en la transcripción, que es justo lo que no sobrevive.
Mantén **un único documento de entrada rotativo**, reescrito (no ampliado) al
cerrar cada sesión de trabajo y leído lo primero al empezar la siguiente. Solo se
gana un sitio lo que está realmente en curso: lo que necesita a una persona en
concreto, lo que te toca construir, lo que está bloqueado por otra persona y, lo
más valioso y lo que más fácil se pierde, **las salvedades que si no habría que
volver a deducir a un coste alto, o que no se deducirían nunca**, como cuál es el
único gate capaz de detectar un error concreto. Hay dos propiedades que importan
más que el formato. Es **un** fichero, reemplazado cada vez, porque una carpeta de
notas de reanudación con fecha se convierte en contexto caducado que se lee como
actual. Y se **borra o se sustituye al cerrar**, por la misma razón. Fíjate en lo
que es en realidad: una entrega a *tu propia siguiente sesión de Copilot*, que
ocurre mucho más a menudo que la entrega entre personas del §8 (o entre acciones
irreversibles), y es la que casi nadie deja por escrito. *(Observado durante tres
días de uso deliberado: suficiente para confiar en la forma, no en los detalles.)*

**Densidad: el índice tiene un parámetro, y el gate estructural no lo ve.** El
índice consultable descrito arriba lo construye un proceso con sus propios
parámetros: lo fino que se divide la fuente antes de extraer, qué umbral agrupa
las cosas, cuánto contexto lleva cada unidad. **Esos parámetros deciden cuánto
del registro sobrevive en el índice, y la comprobación de salud obvia no puede
detectar un mal ajuste.** Reconstruimos el nuestro tras una división más gruesa:
el grafo salió bastante más delgado y el gate **pasó**, porque comprueba que cada
nodo está anclado, es único y es alcanzable, propiedades que un grafo pequeño
cumple *más* fácilmente que uno grande. Un gate estructural mide la integridad,
nunca la cobertura. Así que registra los parámetros de construcción junto al
artefacto, trata los recuentos de nodos y aristas de la construcción anterior como
la base con la que se compara la siguiente, y lee una caída como un defecto que
hay que explicar, no como un resultado más ordenado. *(Una reconstrucción: el
mecanismo se generaliza, la magnitud no está establecida.)*

## 7. Compartir el rastro: un registro, muchas máquinas y personas

El §6 hace que el rastro duradero sea *barato*. Esta sección hace que sea
**compartido**. El rastro descrito hasta ahora tiene una debilidad estructural:
suele vivir en un directorio excluido a propósito del control de versiones
(contiene notas de trabajo, diagnósticos, capturas e índices generados que no
pintan nada en el repositorio). Esa exclusión es correcta y tiene tres costes:

- No puedes enlazar el rastro desde un ticket, una solicitud de cambio o un
  documento de aprobación: la ruta solo se resuelve en tu máquina.
- Cambiar de máquina se convierte en archivar todo el directorio y copiarlo, lo
  que es lento, fácil de olvidar y pierde cosas en silencio.
- Cada compañero construye su propio índice privado de la misma historia
  compartida, así que el "único registro duradero" es una ficción en cuanto hay dos
  personas.

La solución es poner el rastro en un **almacenamiento de objetos compartido** y
darle un modelo de operación. El modelo importa más que la tecnología.

**Define el alcance a propósito, y estrecho.** Comparte *solo conocimiento de
ingeniería*: los registros escritos y el índice derivado. **No** lo amplíes a
documentos de clientes, fixtures de tests, capturas o binarios sin el visto bueno
explícito de un responsable. Es a la vez un límite de confidencialidad y de
tamaño, y es mucho más fácil ampliarlo después que retirarlo.

**Dos modos de acceso, y una regla que evita la mayoría de los accidentes.**

| | Sincronización (push / pull) | Montaje (vista de sistema de ficheros sobre el almacén) |
|---|---|---|
| Dónde trabajas | disco local real, rápido | una vista en vivo del almacén compartido |
| Sirve para | **escribir** registros, construir el índice, control de versiones, búsqueda | **leer** y explorar lo que tienen los demás |
| Concurrencia | explícita, y ves qué se movió | solo lectura, así que no hay nada que pisar |
| Salvedad | no es en vivo: la ejecutas cuando quieres | sin cerrojos, sin renombrado atómico, las escrituras parciales se ven |

> **Escribe con sincronización, lee con el montaje.** Monta el almacén compartido
> **en solo lectura a propósito**: el almacenamiento de objetos no tiene cerrojos
> de ficheros ni renombrado atómico, así que un montaje con escritura invita a una
> corrupción silenciosa que semanas después parece un bug misterioso. El montaje
> de solo lectura no es una limitación que haya que esquivar; es la propiedad de
> seguridad.

**Haz que la dirección destructiva sea opcional.** Los comandos de sincronización
deberían **simular por defecto** y exigir un flag explícito para transferir. El
borrado espejo (eliminar en un lado lo que se borró en el otro) es una opción
adicional y aparte: por defecto solo se debe añadir y actualizar, porque lo
habitual es que un compañero esté subiendo a la vez y no quieres borrar su trabajo
con una vista local caducada.

**Cuatro reglas de comportamiento que las estructurales no cubren** (la gente las
rompe porque nada se lo impide):

1. ⚠️⚠️ **La recuperación caduca, y cada usuario es dueño de su trabajo.** Al
   versionado se le suele llamar "la red de recuperación", sin más. Es una media
   verdad: una regla de ciclo de vida casi siempre **hace caducar las versiones no
   actuales a los ~30 días**. Una sobrescritura es recuperable *durante 30 días, y
   solo si alguien se da cuenta*; nadie revisa los ficheros de los demás. La frase
   literal para el onboarding: *haz pull antes de editar, haz push de lo que
   cambiaste, y si algo tuyo desaparece, dilo dentro del mes o se pierde.*
2. **Los registros compartidos son de solo añadir.** Los índices de estado /
   seguimientos / trabajo entregado son de "gana el último que escribe", sin
   merge: reescribir uno borra en silencio la línea de otra persona, sin conflicto
   ni error. Añade filas; nunca reestructures las de otro. Un aviso al hacer pull
   (una línea presente en local y ausente en lo que llega) prácticamente no da
   falsos positivos: es la **visibilidad** que el versionado no te da. ⚠️⚠️ **Esa
   comprobación cubre una dirección; el daño ocurre en la otra.** Dos máquinas
   editaron el mismo registro la misma tarde; el segundo **push** sustituyó al
   primero entero (11 líneas perdidas, sin conflicto). Protege también el push:
   rechaza (`exit 4` / `REFUSED`) cuando un fichero central compartido se haya
   movido en el almacén desde tu última sincronización; no te limites a avisar.
   Vía de escape `--allow-clobber`: publícala y publica el motivo para no usarla.
   Compara el **contenido**, no solo las fechas (una guarda basada solo en fechas
   da falsas alarmas con el primer push de un compañero de ficheros idénticos byte
   a byte).
3. **El almacén compartido gana cuando hay divergencia.** *"Lo tengo en local"*
   deja de ser un argumento en cuanto la versión publicada es la de otra persona.
   Acuérdalo de antemano; el instinto va en sentido contrario porque tu copia es la
   que ves.
4. **Un fichero por máquina necesita exactamente UN escritor, impuesto en la
   herramienta.** Dividir un registro en un fichero por máquina elimina la
   contención por diseño, y aun así la herramienta puede subir el fichero de cada
   máquina, incluida su copia caducada del de otra persona. El primer síntoma no
   fue un fichero corrupto: fue la conclusión errónea de que un compañero nunca
   había cerrado su jornada.

**Fuente de verdad frente a artefacto derivado, y la tercera categoría que se
olvida.** Los registros escritos son la fuente de verdad; el índice consultable
del §6 se **deriva** de ellos. Todo el mundo lee el índice; exactamente **una
máquina lo publica**. Que dos personas reconstruyan y suban el mismo índice
generado es el único punto real de contención en un sistema por lo demás sin
conflictos: las carpetas por tarea rara vez chocan porque cada persona trabaja en
tareas distintas.

> ⚠️ **"Derivado" es una propiedad de un fichero, nunca de un directorio.** Esta
> es la corrección que costó trabajo de verdad. La regla obvia, *no sincronices el
> índice construido, reconstrúyelo en local*, solo es segura mientras la
> reconstrucción **no pierda nada**. Deja de serlo en cuanto algo dentro de ese
> árbol generado está **escrito a mano y no se puede regenerar**: un conjunto
> curado de nombres de grupos, un fichero de umbrales ajustado, un mapeo revisado.
> Reconstruir entonces lo *destruye*, y como el fichero está en la carpeta
> "derivada", todas las reglas que escribiste dicen que se puede tirar.
> Clasifica por fichero: **fuente**, **derivado** o **escrito a mano pero viviendo
> dentro de lo derivado**, y trata el tercero como fuente: tiene que viajar y nunca
> debe pisarlo una copia caducada.

**Parejas que deben moverse juntas.** Las herramientas de sincronización mueven
los ficheros **de forma independiente**: una sincronización de objetos compara el
tamaño y la fecha de cada clave por separado. Así que dos ficheros que solo tienen
sentido *juntos* (un índice generado y la capa curada que lo anota) pueden llegar
de construcciones distintas, y el resultado no es un error evidente sino una
**respuesta equivocada y segura**: etiquetas pegadas a las cosas equivocadas. Dale
a la capa una **huella del artefacto contra el que se construyó** y haz que la
comprobación de salud falle de forma ruidosa cuando no coincidan. Una
sincronización por fichero no puede expresar atomicidad, así que la comprobación
de consistencia tiene que vivir en los datos.

**Coordinarse sin cerrojos.** El almacenamiento de objetos no tiene cerrojos ni
merge: las escrituras sobre la misma clave se resuelven en silencio a favor del
último. De ahí salen dos patrones. Primero, **un único escritor para todo lo
escrito a mano**: designa un publicador y haz el rol explícito en lugar de darlo
por supuesto. Segundo, cuando las máquinas contribuidoras necesitan avisar al
publicador (*"he cambiado entradas, toca reconstruir"*), que cada escritor cree
**su propio fichero con un nombre único** en lugar de añadir a uno compartido. Las
claves distintas nunca chocan, así que una cola de un fichero por solicitud no
tiene conflictos ni necesita coordinación, y es la misma interfaz que más adelante
puede consumir una tarea programada, de modo que el publicador manual se puede
sustituir sin cambiar nada de lo que hacen las contribuidoras.

> **Trata la regla del publicador único como andamio, no como arquitectura.**
> Atar la reconstrucción de un artefacto compartido a la máquina de una persona la
> bloquea cada vez que esa máquina está apagada u ocupada. Diseña el disparador
> como datos (la cola de solicitudes de arriba) para que la reconstrucción pueda
> pasar más adelante a una tarea programada o disparada por eventos; la migración
> cambia entonces *quién la ejecuta*, no la interfaz que usa nadie.

**Un rol que solo existe en la documentación es código sin probar.** El patrón de
arriba es correcto y aun así lo entregamos roto. El rol de contribuidora se
escribió, se revisó y se enseñó durante semanas antes de que nadie lo ejecutara;
la primera vez que se ejecutó no funcionó en absoluto, y aparecieron tres defectos
más, uno detrás de otro, a medida que se arreglaba cada uno. Ninguno se veía
leyendo el código. Los cuatro son de la misma familia, *el hueco entre un
protocolo descrito y uno en ejecución*, y vale la pena nombrarlos, porque cada uno
se repetirá en cualquier diseño de almacén compartido:

1. **Una guarda limitada a un directorio puede tragarse un canal de control que
   vive dentro.** La guarda de solo-publicador se restringió correctamente a la
   carpeta del artefacto construido, y la cola de solicitudes vivía *dentro* de
   esa carpeta, así que las contribuidoras podían presentar una solicitud que en
   silencio nunca salía de su máquina. Antes de proteger una ruta, enumera qué más
   hay debajo. Los datos de coordinación y los publicados suelen compartir carpeta
   sin mejor motivo que la comodidad.
2. **Una marca de "hecho" tiene que llegar al almacén compartido, no solo al disco
   local.** Marcar una solicitud como consumida moviendo el fichero en local parece
   completo y no lo es: una sincronización por fichero sin borrado deja el original
   en el almacén, así que el siguiente pull lo resucita en todas partes y la cola
   nunca se vacía. La solución es un borrado *dirigido* de las claves que de verdad
   consumiste, nunca un flag de borrado espejo, que es una operación sobre todo el
   árbol y el único comando que se dice a las contribuidoras que no ejecuten nunca.
3. **La sincronización no borra al entrar.** Los ficheros eliminados en remoto se
   quedan en el disco local, así que la copia del solicitante sobrevive a que se
   atienda la solicitud y se vuelve a subir en cada push posterior, acumulando
   elementos que parecen pendientes para cualquiera que liste el prefijo. Concilia
   contra el recibo en lugar de fiarte de la lista de ficheros de cualquiera de los
   dos lados.
4. **Por tanto: "haz pull antes de editar" es un consejo peligroso cuando tienes
   trabajo sin subir.** El mismo comportamiento de no borrar al hacer pull
   sobrescribirá sin problema un cambio local con la copia más antigua del almacén,
   y resucitará ficheros que borraste a propósito. Simula el pull, lee lo que va a
   sobrescribir y después aplícalo.

> **La práctica transferible es barata: simula el rol antes de incorporarte a él.**
> Una identidad de máquina distinta más un árbol local vacío ejercitan los scripts
> reales de forma segura: una ejecución que acierte por error no sube nada. Esa
> única sustitución convirtió cuatro fallos latentes en el trabajo de una tarde en
> lugar de la primera semana de una persona nueva.

> ⚠️⚠️ **Una guarda de seguridad puede desactivar en silencio el instrumento que
> demuestra el hábito.** Un snapshot previo al pull instaló su propio
> `trap ... EXIT` para limpiar un fichero temporal. Bash mantiene **un único** trap
> de EXIT, así que sustituyó al que escribía el registro de actividad. Ese bloque
> solo se ejecuta en el camino real (`--go`), así que las simulaciones seguían
> registrando y cada pull real se quedó sin registrar durante dos días mientras el
> panel seguía lleno y parecía plausible. Pregunta qué más ocupa el mismo recurso
> de una sola plaza; recuerda que el camino real y el del ensayo son código
> distinto. Una línea marcadora que sobrevivió a un pull real **idéntica byte a
> byte** distinguió *"escrito y luego sobrescrito"* de *"nunca escrito"* donde un
> recuento de líneas no podía.

> ⚠️ **Mide una optimización antes de citarla.** Se predijo que restringir el
> barrido al único directorio que cambia a diario llevaría la comprobación "de dos
> minutos a segundos". Medido: **212 s → 123 s, ~40%**. Citado de intuición, habría
> entrado en el onboarding como un hecho.

**La vista previa es donde se hace visible una violación de alcance.** En la
prueba de campo, la rutina de cierre solo se ejecutó como vista previa simulada de
la publicación, y esa vista previa mostró dos ficheros de la carpeta del corpus que
una máquina contribuidora nunca debe publicar. La regla existía; nada en la
sincronización la imponía; leer la vista previa lo detectó. La misma rutina al
*empezar* la jornada detectó un destino de sincronización local que apuntaba a
otro checkout **antes** de que se ejecutara ningún pull (una comprobación de
premisa, §2). Ambas cosas son el argumento a favor de rutinas que simulan por
defecto: el error aparece en una lista que lees, no en un almacén que tienes que
reparar. Excluye lo que marque la vista previa, no añadas nunca un borrado espejo
para "limpiar" y escribe la fila de estado antes de la publicación real.

> **Y el hábito necesita un mecanismo, no un párrafo.** "Pull al empezar, push al
> terminar" estuvo meses en el documento de operaciones sin que nadie lo siguiera.
> Empaqueta esos momentos como una **skill `day`** que se invoca (ver
> `docs/ai-agents-code-methodology/copilot/skills/day/` y
> `examples/methodology/s3-sync/`). La documentación no puede imponer un hábito;
> una rutina con rastro de auditoría sí.

**Presupuesta el criterio que cuesta una reconstrucción, no solo el cómputo.**
Cuando un artefacto compartido lleva etiquetas escritas a mano sobre una
estructura generada por máquina, mide cuántas sobreviven a una reconstrucción
antes de dar por hecho que el nombrado es un coste único. Las nuestras conservaron
el 48% en una reconstrucción y el 37% en la siguiente, con identificadores fijados
expresamente para que fueran estables: fijarlos resolvió la deduplicación *dentro*
de una ejecución y no hizo nada por la continuidad *entre* ejecuciones. Trata el
re-etiquetado como un coste recurrente de cada actualización y planifícalo; un
artefacto etiquetado a medias no pasa ninguna comprobación de salud y no le sirve
a nadie.


**Identidad de la máquina, para que el agente sepa en qué máquina está.** Es la
parte específica de los flujos con agentes y la que es fácil pasar por alto. En
cuanto el mismo rastro es accesible desde varias máquinas con *roles distintos*,
una sesión del agente tiene que saber **en qué máquina se está ejecutando y qué
puede hacer esa máquina**; si no, una máquina contribuidora reconstruirá y
publicará amablemente el índice compartido, que es justo lo único que no debe
hacer. Da a cada máquina una pequeña identidad declarada (un nombre y un rol),
genera a partir de ella una ficha de identidad local que además ejecuta
comprobaciones en vivo (¿se alcanza el almacén? ¿está el montaje? ¿con qué cuenta
estamos autenticados?), y haz que el documento de orientación siempre cargado
apunte a esa ficha para que cada sesión lea primero su propio rol. Mantén la ficha
local a la máquina y fuera tanto del control de versiones como del almacén
compartido: es el único fichero que *no* debe ser igual en todas partes.

**Mínimo privilegio, y por qué el permiso obvio amplía el acceso.** El rastro
necesita exactamente una capacidad: leer, escribir y borrar en **una** ubicación
del almacén compartido. Concederla es el momento en que los equipos recurren al
rol que su gente ya tiene, y ese es el error. Un rol o conjunto de políticas se
suele aprovisionar en **todos** los entornos a los que se asigna y se aplica a
**todas** las personas que lo tienen, así que añadir el permiso de escritura al rol
que ya tienes no da acceso a una ubicación en un entorno, lo da en todos los
sitios donde existe ese rol, producción incluida. El instrumento estrecho es un
**permiso dedicado limitado a esa única ubicación**, asociado a ese único propósito
y a nada más.

Dos cosas que hicimos mal y que ahora haríamos primero. **Mide los permisos que
realmente tienes antes de diseñar la solicitud.** Los nuestros resultaron ser
bastante más amplios de lo que nadie había pedido, heredados en silencio por
pertenencia a grupos y en entornos en los que nadie había pensado, y la solicitud
que habíamos redactado los habría ampliado más. Se escribió, se revisó y nunca se
envió. **Después pregunta al directorio autoritativo, nunca al mensaje de error de
la herramienta** (§2). Cuando presentes la solicitud, indica la *capacidad y el
alcance* en lugar de nombrar un rol, y comprueba que un permiso que pides que te
quiten no es justo lo único de lo que depende el flujo. El nuestro casi lo era.

**Antes del primer push compartido.** Revisa los registros en busca de secretos
incrustados. Las notas de investigación son el caso peligroso: a menudo capturan
URLs firmadas, tokens o cadenas de conexión *a propósito*, como evidencia, y son
justo las cadenas que no quieres que acaben en un almacén compartido. Ejecuta una
vez el escaneo de saneado del §8 sobre todo el rastro, no solo sobre un diff,
antes de que salga de la máquina por primera vez.

### Ampliar el alcance de un almacén compartido es un evento de seguridad

Cada vez que el rastro compartido crece para cubrir una nueva clase de contenido
(registros, luego diagnósticos, luego material fuente) cruza un límite que nunca
se revisó para esa nueva clase. Dos reglas, ambas aprendidas por estar a punto de
entregar el error:

**Escanea antes de cada ampliación, y pon antes un canario al escáner.** Un
escaneo sobre mil cien ficheros salió limpio. El canario, el mismo escaneo contra
una credencial plantada a propósito, *también* salió limpio, así que el primer
resultado no significaba nada: un nombre de fichero de la lista se había
interpretado como una opción de la línea de comandos, abortando el lote, mientras
la salida de error suprimida y un código de salida cero lo ocultaban. Una vez
reparado, el mismo escaneo encontró quince ficheros con URLs firmadas que llevaban
credenciales temporales con formato real, capturadas a propósito como evidencia en
notas de investigación antiguas. **El escáner es un instrumento y necesita su
propio caso de respuesta conocida**, cada vez, no una sola vez.

**Un informe de transferencia limpio no es una comprobación de que está
completo.** "Lo que me pidieron enviar, lo envié" es todo lo que puede decirte una
sincronización. No puede decirte lo que nunca se le pidió. En una ampliación se
omitieron dos directorios enteros y treinta documentos fuente: los documentos
porque la lista de inclusión **distinguía mayúsculas** y los ficheros tenían
extensiones en mayúsculas, y los directorios porque nadie los había añadido a la
lista del alcance. Las dos transferencias informaron de éxito, y la vista previa
posterior dijo que no quedaba nada por hacer. **Tras cualquier cambio de alcance,
concilia el inventario local con el publicado y justifica cada diferencia**,
incluidas las que buscas, por escrito. Las diferencias que puedes explicar son lo
importante; la que no puedes explicar es el hallazgo.

---

## 8. Entrega: artefactos, saneado, gate humano (GitHub Copilot)

**Una sola herramienta.** Este manual da por hecho que el agente de código del
equipo es **GitHub Copilot** (CLI, VS Code, agente en la nube) de principio a fin.
La persona mantiene el mismo rol sea cual sea la superficie que ejecuta la sesión;
solo cambian la sesión y los gates hacia fuera. La única entrega real entre
superficies, `/delegate` desde la CLI al agente en la nube, sigue terminando en un
PR en **borrador** que solo una persona puede marcar como listo, aprobar o
fusionar.

"Entrega" significa aquí, por tanto, dos cosas, ambas dentro de Copilot:

1. **Continuidad de la sesión:** reescribe el punto de entrada rotativo del §6
   para que la *siguiente* sesión de Copilot (o el día siguiente) no tenga que
   volver a deducir salvedades a partir de una transcripción muerta.
2. **Gate humano sobre las acciones hacia fuera:** el agente prepara; una persona
   (o una automatización dirigida por una persona) da cada paso irreversible o
   externo.

En concreto:

- **Artefactos por cambio:** un informe (causa raíz → arreglo → evidencia de la
  verificación), una actualización del registro de estado vivo, criterios de
  aceptación pensados para quien da el visto bueno y una breve nota de **próximas
  acciones** que dice exactamente qué tiene que hacer la persona para entregarlo
  (push, abrir/fusionar la solicitud de cambio, desplegar, avisar a los
  interesados). Esa nota *no* es una lista de migración de herramientas.
- **Gate de saneado (mecánico, siempre):** antes de que nada salga del banco de
  trabajo, escanea el **cambio preparado** en busca de contenido que no debe
  entrar en el registro permanente: identificadores de clientes o socios, ids de
  tickets internos en el cuerpo del código, secretos y auto-atribución del agente.
  Que sea un escaneo por patrones, no una cuestión de criterio. Cuidado con las
  trampas del propio escaneo: un escaneo ingenuo del diff también coincide con las
  líneas *eliminadas*, así que filtra solo las líneas **añadidas**, y excluye las
  rutas que son locales o ignoradas a propósito. La única vez que lo miras a ojo en
  lugar de ejecutar el escaneo es la vez que algo se filtra. Con Copilot, prefiere
  la **skill de proyecto `sanitise-diff`** antes que el criterio improvisado.
- **Separación de roles:** el agente de Copilot escribe el cambio y deja la rama;
  **no** hace push, no abre ni fusiona solicitudes de cambio, no despliega ni avisa
  a nadie salvo que la persona se lo pida **explícitamente** en esa sesión.
  Imponlo con instrucciones siempre activas (`AGENTS.md`, `.github/instructions/`)
  **y** un hook de denegación `preToolUse` (`.github/hooks/block-external-git.json`,
  exit 2), más `--deny-tool='shell(git push)'` en las ejecuciones sin interfaz; trata
  `/pr auto` / `/pr automerge` de la CLI y las aprobaciones de la revisión de código
  de Copilot como exclusivas de personas; y haz que los artefactos entregados se
  lean como obra de la persona autora (sin atribución al agente en el código, los
  mensajes de commit ni el texto de la solicitud de cambio). Leer el gestor de
  tickets y la wiki está bien y es útil (estado en vivo, enlaces, comentarios): usa
  una herramienta que solo pueda enviar peticiones de lectura, con el token propio
  de cada persona. Crear, editar, comentar o cambiar de estado los tickets, y
  actualizar páginas de la wiki, sigue siendo cosa de una persona.
- **Rol de la máquina antes de escribir en lo compartido:** si el rastro está en
  un almacenamiento de objetos compartido, lee primero el `IDENTITY.md` local a la
  máquina (`AGENTS.md` apunta a él): una sesión contribuidora no debe volver a
  publicar el índice derivado. Consulta ese índice con la **skill `kg`**; las
  contribuidoras piden una reconstrucción con **`kg-refresh`** (nunca reconstruyen
  en local). Ciclo diario: la **skill `day`** (`day start` / `day end`): un
  párrafo que dice "pull al empezar, push al terminar" no impone el hábito; una
  rutina que se invoca con rastro de auditoría sí. Protege **las dos**
  direcciones: un pull te pisa a ti, un push pisa a un compañero (`exit 4` /
  `REFUSED`: haz merge, no `--allow-clobber`).
- **Herramientas de refactorización: fíate de la negativa, vuelve a comprobar la
  edición.** Un borrado seguro semántico que **se niega** y lista todas las
  referencias es evidencia sobre el código y no cuesta nada. Un renombrado
  semántico informa de su número de cambios al responder, pero en la prueba de
  campo las ediciones llegaron al disco un momento *después*: un diff tomado al
  instante no mostraba nada. Espera, vuelve a leer el diff, compáralo con el
  número informado y revierte con el control de versiones si el renombrado era
  exploratorio.

## 9. La revisión automática forma parte del ciclo

Cuando un bot de revisión comenta en el cambio abierto, trata sus hallazgos como
de primera clase:

- **Clasifica cada uno** como harías con los de un revisor humano: confirma los
  defectos reales, prepara un **cambio de seguimiento** para ellos y descarta los
  falsos positivos **con un motivo indicado**, nunca en silencio.
- **No fusiones por encima de un hallazgo válido sin atender.** Un defecto
  señalado por una máquina sigue siendo un defecto. El commit de seguimiento
  cierra el ciclo antes de que el cambio entre; el descarte con motivo es en sí
  parte del registro duradero.

Un ejemplo real habitual de su valor: un arreglo que introduce una *nueva*
suposición de orden o de posición (p. ej. "esta comprobación ahora solo salta al
principio de una cadena") puede pasar todos los tests escritos a mano y aun así
tener un hueco que el bot detecta razonando sobre el flujo de control cambiado.
Clasifica, reproduce, añade el test de regresión que falta, arregla, vuelve a
verificar.

Dos cosas que conviene saber antes de responder a un bot:

- **Reproduce antes de darle la razón, y antes de rebatirlo.** Las dos
  direcciones son modos de fallo. Darle la razón por cortesía produce un
  "arreglo" innecesario de código que estaba bien; descartarlo por reflejo fusiona
  un defecto real. Mide el radio de impacto en ambos casos: un hallazgo válido es
  con frecuencia **latente más que inerte** (la lógica defectuosa se alcanza en una
  minoría de entradas y ahora mismo no produce salida errónea), y "latente" cambia
  la urgencia, pero no el veredicto.
- **Medir un hallazgo puede invalidar el arreglo obvio.** Más de una vez, la
  investigación de un fallo bien identificado ha sacado a la luz un *segundo*
  fallo en la dirección opuesta en el mismo sitio (uno hace la comprobación
  demasiado estrecha y el otro demasiado amplia) donde la corrección ingenua de una
  línea arregla la mitad reportada y empeora la mitad no reportada. Mide primero y
  diseña después; la descripción del problema que da el bot es una pista, no una
  especificación.

La misma disciplina se aplica a los comentarios de un revisor humano y a un
informe de QA: trata el hallazgo como **datos**, nunca como una especificación del
arreglo.

## 10. Validar la metodología en un agente nuevo

Pasar el ciclo a un agente nuevo invita a una frase: *"se espera paridad"*. Es una
predicción, no un resultado. Sustitúyela por una **validación acotada** cuyo
resultado es una tabla, una fila por skill o herramienta, cada una marcada como
**pasa (acotado)**, **mínimo**, **pendiente** o **fuera de alcance**, con lo que se
ejecutó de verdad y lo que no puede mostrar. Tres reglas hicieron que la prueba de
campo mereciera la pena:

- **Ejercita lo real dentro de su límite de mutación.** Descargas de solo lectura,
  vistas previas, renderizados locales de salidas capturadas, consultas de solo
  lectura aprobadas: todo eso puede ejecutarse en vivo en una jornada real.
  Cualquier cosa que escriba en un sitio compartido (publicar, subir, reconstruir
  un índice, cambiar un ticket) se queda tras su gate salvo que la persona lo abra
  para ese paso concreto, y el informe dice qué pasos se abrieron. Una
  autorización puntual para la prueba se limita a la prueba; no es una nueva regla
  permanente.
- **Repite un ticket pasado desde su commit anterior al arreglo.** Crea una rama
  en un clon de respaldo en el commit anterior al arreglo original, dale al agente
  el texto del problema y la evidencia, y recorre los gates: causa raíz con el
  oráculo gratuito, tests en RED, GREEN mínimo, diff del radio de impacto sobre el
  corpus, las reproducciones de salida y en el artefacto desplegado, saneado del
  diff real y suite completa frente a su base. El resultado registrado en el ticket
  es la respuesta conocida (§2): la misma causa raíz, las mismas cifras, el mismo
  contrato. Después revierte todo, archiva el diff, borra la rama y no subas nada.
- **Di si fue a ciegas.** Si el agente leyó antes en la sesión el plan de arreglo,
  el informe o el diff originales, la repetición demuestra que el agente sabe
  *ejecutar* el ciclo, no que sepa *encontrar* la respuesta. La repetición de campo
  no fue a ciegas y el informe lo dice en sus primeras líneas. El siguiente paso es
  una ejecución a ciegas sobre un ticket que el agente no haya visto nunca.

Presenta los límites junto a lo que pasó: qué no se ejercitó, qué ficheros de
tests no se pudieron ejecutar y por qué, qué comprobaciones siguen pendientes en
el flujo real (en la prueba de campo, la re-subida en la función desplegada tras un
merge). **Verificado significa exactamente lo que se ejecutó; pendiente significa
que aún no está demostrado.** No pongas nunca evidencia de clientes (documentos,
identificadores) en el informe; los resultados agregados bastan.

---

## Checklist por tarea (el ciclo, comprimido)

```
[ ] Orientarse: consulta el índice del registro para ver trabajo previo relacionado, lee esos registros completos Y comprueba el estado vivo (rama / trabajo abierto)
[ ] Gate de entrada: ¿síntoma reproducido en el CONTRATO DE SALIDA (el ÚLTIMO escritor del campo)? si no → devolverlo
[ ] Expectativa: ¿de dónde sale el valor "esperado"? derívalo de la estructura + el contrato, no de otro entorno
[ ] Regla del contrato: cumplir / revisar / registrar; elige una de forma explícita; el silencio no es una opción
[ ] Procedencia: ¿regresión o preexistente? demuéstralo sobre la base anterior al cambio
[ ] Premisa: todo hecho afirmado sobre máquina / entorno / acceso verificado contra la fuente AUTORITATIVA, no contra un mensaje de error
[ ] Causa raíz: confirmada con un ORÁCULO DETERMINISTA GRATUITO (aún sin ejecución de pago)
[ ] Manejadores: nombrados los manejadores de excepciones entre tú y el síntoma; arreglados o aceptados POR ESCRITO
[ ] Instrumento: sonda con canario sobre un caso de RESPUESTA CONOCIDA; sin try/except envolviendo la medición
[ ] Entradas: diagnósticos ejecutados sobre COPIAS; mtime/hash del original sin cambios; salidas registradas copiadas aparte antes de repetir
[ ] Plan: opciones + compromisos presentados; la persona está de acuerdo; opciones descartadas registradas
[ ] Implementar: test acotado en RED por la razón correcta → código mínimo → GREEN
[ ] Genérico: basado en una clase estructural; entradas hermanas cubiertas; prueba de no-op sobre el conjunto de referencia
[ ] Verificar: unitarios + acotados + regresión completa en verde; no determinismo = arregla la sensibilidad, no la varianza
[ ] Suite completa frente a la base: los mismos fallos a ambos lados; ficheros sin recoger NOMBRADOS como no cubiertos
[ ] Composición: afirma sobre la LISTA DE MIEMBROS, no sobre el recuento; delta frente a la base cuando el arreglo tiene dirección
[ ] Honestidad del gate: di qué puede y qué NO puede mostrar cada gate; nombra lo que aporta la evidencia si un gate no puede fallar
[ ] Discriminación: nombra la comprobación que separa el arreglo elegido del candidato más débil; "la suite" no suele serlo
[ ] Premisa frente a implementación: si el cambio solo puede ELIMINAR o ALTERAR salida, ejecútalo contra datos reales que sabes correctos; tus propios tests no pueden contradecir tu propio modelo
[ ] Gate de salida: contrato arreglado reproducido en el camino en vivo; el síntoma ha desaparecido
[ ] Artefacto desplegado: reproducción repetida DENTRO del artefacto que se entrega; DEMOSTRADO antes que falla sobre el código sin arreglar; salida idéntica a la local
[ ] Mirarlo: renderiza/inspecciona a ojo la salida real; artefactos de antes/después para todo lo visual
[ ] Documentar: informe + actualización del registro + criterios de aceptación + nota de próximas acciones (cada uno escrito UNA vez)
[ ] Sanear: escanea las líneas AÑADIDAS del cambio preparado en busca de nombres / IDs / secretos / atribución
[ ] Gate humano: la persona hace push / abre la solicitud de cambio / despliega; el agente de Copilot no (un hook deniega push/PR/merge)
[ ] Revisión automática: reproduce, mide el radio de impacto, y después commit de seguimiento o descarte con motivo
[ ] Persistir: actualiza los registros + la memoria ligera; **`day end`** (sincroniza el rastro compartido; nunca `--delete`, nunca publicar el KG desde una contribuidora); solicitud de **`kg-refresh`** si el corpus cambió; convierte cualquier lección reutilizable en parte del manual
[ ] Continuidad: reescribe el único documento de entrada rotativo: qué está en curso y las salvedades que costaría volver a deducir (siguiente sesión de Copilot)
```

---

## Antipatrones técnicos

- **Diagnosticar con el generador caro.** Se paga por uso y no es determinista;
  usa el oráculo gratuito para diagnosticar y el generador solo para verificar el
  arreglo terminado.
- **Demostrar un arreglo en la capa equivocada.** Unitarios internos en verde ≠
  contrato en verde. El consumidor lee el contrato; demuestra el contrato.
- **Tratar una sola ejecución en verde como un aprobado** en un sistema no
  determinista. Fija la sensibilidad, no la semilla.
- **Un arreglo de instancia disfrazado de arreglo de clase.** Si el parche hace
  referencia al valor reportado en lugar de a la propiedad estructural, arreglará
  la demo y romperá la siguiente entrada.
- **Dejar que el contexto siempre cargado crezca hasta ser un historial de
  cambios.** Cada línea ahí se paga en cada turno. El detalle va a ficheros bajo
  demanda; el núcleo sigue siendo un mapa.
- **Hacer pull/push del registro compartido de memoria** en lugar de con la
  **skill `day`.** El hábito documentado estuvo meses sin seguirse en la máquina
  publicadora; nada registraba una sincronización, así que nada podía mostrar la
  deriva.
- **Saltarse un push `REFUSED` / exit 4 con `--allow-clobber`.** Los ficheros
  centrales compartidos necesitan un merge, no un ganador. Esa anulación es como
  desapareció el registro de un compañero sin ningún error en la máquina de quien
  hizo el push.
- **Una contribuidora que reconstruye o publica el grafo de conocimiento.**
  Presenta una solicitud de **`kg-refresh`**. Dos publicadores destruyen en
  silencio los nombres escritos a mano.
- **Saltarse el escaneo de saneado porque "este está claramente limpio".**
  Ejecútalo siempre; las excepciones son justo donde ocurren las filtraciones.
- **Fusionar por encima de un hallazgo del bot** porque "parece un falso
  positivo" sin reproducirlo. Reprodúcelo, y después descártalo con motivo o
  arréglalo.
- **Fiarse de un instrumento sin canario.** Un diagnóstico que nunca ha producido
  una respuesta que sabes correcta no es evidencia, por muy segura que parezca su
  salida; y un resultado uniforme en todas las entradas es un síntoma, no un
  hallazgo.
- **Afirmar sobre el total.** Que el recuento coincida con lo esperado es la forma
  más común de que se entregue un elemento que falta. Afirma sobre los miembros.
- **Leer un gate estructural como si fuera semántico.** Una comprobación de que
  cada elemento está presente, es único y está bien conectado no dice nada sobre si
  algo de ello es *correcto*. Una migración dio un certificado de salud limpio
  (todos los grupos coincidían, ninguno perdido, sin huérfanos) mientras **el 56%
  de los nombres trasladados no describía aquello a lo que estaba pegado**, porque
  el mecanismo de respaldo había coincidido por un indicador superficial. Una
  etiqueta errónea es peor que una que falta: la que falta hace una pregunta; la
  errónea la responde mal y manda a la siguiente persona al sitio equivocado.
  Cuando la corrección de un valor es una cuestión de *significado*, ninguna
  comprobación automática la descarta; programa la lectura humana y dilo en la
  descripción del gate.
- **Creerse un canario en verde que nunca aplicó la perturbación real.** Ver la
  regla 3 del §2: "el test que pude construir pasó" no es "el riesgo está
  descartado".
- **Presentar como validación un gate que no puede fallar.** Si el conjunto de
  referencia no tiene ningún ejemplo de la forma que cambiaste, una ejecución
  limpia demuestra ausencia de regresión y nada más. Di cuál es cuál.
- **Demostrarlo en local y darlo por entregado.** Lo que se entrega es el
  artefacto que se ejecuta en el entorno de destino; tu árbol de trabajo no lo es.
- **Fiarse de una regla que nunca has visto rechazar nada.** Cuando el
  comportamiento correcto es el silencio, una regla rota y una que funciona son
  indistinguibles. Lee con qué coincidió.
- **Dejar que una medición fallida devuelva la misma respuesta que un resultado
  negativo.** "Nadie tiene el cerrojo" y "no pude averiguarlo" nunca deben imprimir
  la misma línea.
- **Leer un pipeline de despliegue en verde como evidencia de que el servicio
  funciona.** Una suite de humo que ejercita la interfaz pública no dice nada de un
  listener en segundo plano que no arranca. Afirma sobre lo que se rompió, no
  sobre lo que es fácil de consultar.
- **Entregar el código y su configuración por pipelines separados sin nada que
  los ordene.** Cada repositorio es correcto por separado y la composición no está
  definida; el hueco entre los dos merges es una ventana de caída que nadie vigila.
  Si tienen que ir separados, el código debe degradarse de forma ruidosa cuando
  falta su configuración, no consumirla al arrancar y morir en silencio.
- **Un montaje compartido con escritura.** El almacenamiento de objetos no tiene
  cerrojos ni renombrado atómico. Monta en solo lectura y escribe mediante una
  sincronización explícita.
- **Dejar que dos máquinas publiquen el índice derivado.** Los registros son la
  fuente de verdad y en la práctica no tienen conflictos; el índice generado es el
  único sitio donde dos personas chocan de verdad. Un publicador, o reconstruir en
  local.
- **Tratar una suite en verde como evidencia de que la especificación está
  bien.** Los tests y el defecto tienen un antepasado común: tu modelo del
  problema. Cuando lo que está mal es ese modelo, todos los tests están de acuerdo
  con el bug, y añadir tests solo sube la confianza. Los datos reales que sabes
  correctos son el único instrumento que puede llevarte la contraria.
- **Un gate que no distingue entre dos arreglos candidatos.** Distinto de un gate
  que no puede fallar: este pasa para *los dos*, así que la suite ratifica en
  silencio el arreglo que te tocó escribir. Nombra la medición que los separa.
- **Una comprobación dentro del artefacto que nunca se ejecutó contra el código
  sin arreglar.** No se ha visto fallar, así que es una captura de pantalla, no un
  gate.
- **Construir un procedimiento sobre una premisa sin verificar** sobre la máquina,
  el entorno o el acceso que tienes, y después diagnosticar esa premisa a partir de
  un mensaje de error en lugar de la fuente autoritativa.
- **Dejar sin registrar un error suprimido.** Arreglar el manejador y aceptarlo
  son ambas cosas legítimas; el silencio no, y se lee igual que no haberse dado
  cuenta.
- **Guardar el estado en curso solo en la transcripción**, la única parte de la
  sesión que seguro que no sobrevive.
- **Leer un gate estructural del índice como un gate de cobertura.** Un índice más
  delgado pasa las comprobaciones de integridad *más* fácilmente que uno completo.
  Compara con los recuentos de la construcción anterior.
- **Conceder el acceso de escritura al registro compartido a través de un rol que
  ya tienes.** Un conjunto de permisos aterriza en todos los entornos en los que se
  aprovisiona; el instrumento estrecho es un permiso dedicado a una sola ubicación.
- **"Se espera paridad."** Una predicción sobre un agente nuevo no es un
  resultado. Ejecuta la validación acotada (§10) y presenta juntos lo que pasó y
  los límites.
- **Llamar a ciegas a una repetición cuando el agente ya había visto la
  respuesta.** Demuestra que el agente sabe ejecutar el ciclo, no que sepa
  encontrar el arreglo.
- **Medir sobre el original.** Un instrumento que reescribe su entrada destruye la
  evidencia que debía leer. Trabaja sobre copias.
- **Meter los tests que no se pudieron recoger dentro de "suite completa en
  verde".** Los ficheros que no se ejecutaron no están cubiertos; nómbralos.
- **Concluir que una herramienta no está disponible sin comprobar que está
  registrada para este agente.** La configuración no viaja entre agentes.

---

*Documento interno. Mantenlo genérico: sin nombres de clientes, sin detalles del
entorno, sin secretos. Está pensado para que lo pueda leer cualquier ingeniero con
cualquier stack.*
