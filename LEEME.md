# Radio Aventura

Una campaña local en español basada en *Radio Systems Engineering, Revised First Edition*, de Steven W. Ellingson (2023).

## Para jugar

1. Si recibiste el ZIP, **extrae toda la carpeta** antes de abrirla.
2. Haz doble clic en **INICIAR_RADIO_AVENTURA.cmd**.
3. Se abrirá el navegador. Pulsa **Comenzar aventura**.

Necesitas Python 3.10 o posterior y un navegador moderno. No necesitas instalar paquetes ni conectarte a Internet. El iniciador busca instalaciones habituales de Python en Windows; también puedes ejecutar `python app.py` desde esta carpeta.

El servidor escucha exclusivamente en `127.0.0.1`. La dirección habitual es `http://127.0.0.1:8765`; si está ocupada se prueba un puerto cercano. La ventana de Python muestra la dirección exacta. Mantén esa ventana abierta mientras juegas. Para cerrar, presiona Ctrl+C en ella o ciérrala. Si vuelves a abrir el iniciador mientras la partida está activa, reutiliza la misma estación.

## Colores de fondo y letras

Pulsa **Apariencia** en la barra superior. Puedes elegir **Oscuro**, **Claro** o **Sepia**, o seleccionar por separado el color de fondo y el de las letras. Los cambios se ven al instante y se guardan en el navegador utilizado, sin modificar tu partida. Un indicador muestra el contraste para ayudarte a elegir una combinación legible.

**Restaurar colores originales** recupera el diseño inicial. Las lecturas también usan los colores elegidos; las imágenes de las fórmulas y el PDF conservan sus colores originales. Si el navegador bloquea el almacenamiento, los colores sólo duran durante la sesión y el panel lo indica.

## Servidor en segundo plano en Windows

`MANTENER_SERVIDOR.cmd` inicia un supervisor sin ventana que comprueba el servidor cada cinco segundos y lo vuelve a iniciar si termina o deja de responder. Abre `http://127.0.0.1:8765/` para jugar. Cerrar el navegador no detiene el servidor. No necesita paquetes adicionales y escucha únicamente en esta computadora.

`DETENER_SERVIDOR.cmd` permite detenerlo de forma intencional sin borrar la partida. El registro está en `datos/servidor.log`. Si hay un acceso directo de Radio Aventura en la carpeta **Inicio** de Windows, vuelve a arrancar al iniciar sesión; para desactivar ese inicio automático, quita únicamente ese acceso directo. El inicio automático apunta a la ubicación actual del programa: si mueves la carpeta, actualiza el acceso directo.

Mientras Windows esté suspendido, hibernando o apagado, el servidor no puede responder. Al reanudar se conserva la ejecución; después de reiniciar Windows, el acceso directo lo inicia al entrar a tu sesión. Esta configuración no modifica los ajustes de energía del equipo.

## Cómo se juega

Reconecta las balizas de un archipiélago de 20 sectores, correspondientes a los 18 capítulos y los apéndices A y B del libro. Hay **166 misiones**, una por cada sección principal del índice.

Cada misión tiene tres etapas:

1. **Entiende:** qué es el concepto, cómo funciona y para qué sirve o dónde encuentra sus límites. Otorga 5 XP.
2. **Experimenta:** mueve un control, observa un modelo didáctico y alcanza un objetivo numérico comprobado por Python. Otorga 15 XP.
3. **Resuelve:** responde una pregunta conceptual con retroalimentación explicativa. Otorga 30 XP.

Cada etapa entrega una estrella. Completa las tres para abrir la siguiente misión. Al terminar un sector, responde su reto de tres preguntas para encender la baliza, ganar 100 XP y abrir el siguiente. Los puntos se otorgan una sola vez por logro; repetir no infla la experiencia. Los errores no quitan puntos ni borran avance.

La campaña completa permite conseguir 10 300 XP: 166 × 50 y 20 × 100. No usa temporizadores, vidas limitadas ni castigos por aprender despacio. Los controles aceptan teclado y se respeta la preferencia del sistema por movimiento reducido.

**Laboratorio libre** abre 15 familias de experimentos sin requisitos ni puntuación. **Libro y conceptos** permite consultar todas las lecciones, buscar términos y abrir la página exacta del libro. **Cuaderno** muestra insignias, avance y notas personales.

## Alcance y fuente

Las explicaciones en español son una adaptación pedagógica original de las secciones, con preguntas y ejemplos añadidos. La narrativa y los objetivos numéricos son añadidos didácticos; no son ejercicios oficiales ni soluciones del autor. Los modelos se reutilizan dentro de un sector para practicar su mecanismo fundamental con objetivos diferentes. No constituyen un simulador electromagnético ni de cada circuito o estándar descrito.

Se incluyen las 166 secciones principales, los subapartados detectados, lectura por sección en **español de México**, consulta del original en inglés, búsqueda de las 531 páginas y el PDF completo. En **Leer sección original**, el selector de idioma abre el español de México de forma predeterminada; puedes alternar al inglés sin salir de la lectura.

La traducción de las lecturas se generó localmente mediante un modelo de traducción automática, con ajustes de terminología técnica y uso de México. Se almacena completa en `fuentes.json`, por lo que no requiere Internet, instalar un traductor ni enviar texto a un servicio al jugar. Se conserva el inglés para contrastar términos. Los bloques de expresiones matemáticas se mantienen sin traducir; las ecuaciones, derivaciones, figuras y problemas completos se consultan en el PDF, porque la extracción de texto puede alterar su disposición. El PDF adjunto permanece en inglés y sin modificaciones. La guía y esta traducción de apoyo no reemplazan todo el detalle universitario de la obra. Consulta **COBERTURA.md** para auditar la correspondencia entre misiones e índice.

El apéndice B y algunos estudios de caso describen tecnologías en el contexto histórico de la obra. Las frases del original acerca de lo «actual» no se presentan como afirmaciones sobre el despliegue vigente. El programa no necesita navegación externa para estudiar; sólo los enlaces de atribución y licencia abren recursos de Internet.

## Guardado y respaldo

El avance y tus notas se guardan en `datos/progreso.json` dentro de esta carpeta. El guardado usa un archivo temporal y reemplazo atómico, y conserva el estado anterior en `datos/progreso.anterior.json`. Si el principal es ilegible, se intenta cargar el anterior. Si ninguno puede leerse se preserva el archivo principal con otro nombre antes de comenzar una partida nueva.

Puedes descargar una copia con **Exportar avance**. Esa copia contiene estrellas, balizas y notas; no incluye el libro ni sustituye la carpeta de la aplicación. Para restaurarla manualmente: cierra la aplicación, conserva una copia de la carpeta `datos` y coloca el archivo exportado como `datos/progreso.json`. No cambies nombres de campos ni la versión del formato.

Para conservar todo al cambiar de equipo, copia la carpeta completa, incluido `datos`. No abras la aplicación desde el interior del ZIP ni desde una ubicación sin permiso de escritura.

## Problemas de inicio

- Si el navegador queda en «Sintonizando», recarga la página y verifica que la ventana Python siga abierta.
- Si el puerto está ocupado, usa `python app.py --port 9000`.
- Si no se abre automáticamente, copia la dirección que muestra Python al navegador.
- Si el iniciador no encuentra tu instalación, abre terminal en esta carpeta y ejecuta la ruta completa de tu `python.exe`, seguida de `app.py`.
- Si no se guarda el avance, extrae el programa a una carpeta donde tengas permiso de escritura.
- Para detener la estación, cierra su consola o usa Ctrl+C. Cerrar sólo la pestaña no detiene Python.

## Archivos

`app.py` contiene el servidor, cálculos y evaluación. `curso.json` contiene lecciones y preguntas. `game.js`, `index.html` y `style.css` presentan el juego. `fuentes.json` y `libro_busqueda.json` facilitan lectura y búsqueda sin dependencias. `libro/` contiene la fuente original. No cambies los nombres o separaciones de estos archivos al copiar la aplicación.

## Atribución

Ellingson, Steven W. (2023). *Radio Systems Engineering, Revised First Edition*. Virginia Tech Publishing. DOI: [10.21061/radiosystemsengineering-revised1st](https://doi.org/10.21061/radiosystemsengineering-revised1st). Licencia [Creative Commons Attribution-NonCommercial 4.0 International](https://creativecommons.org/licenses/by-nc/4.0/), salvo las excepciones indicadas en el propio libro.

Se adjunta el PDF sin modificaciones. La adaptación textual, ejemplos y actividades derivadas de la obra se comparten bajo CC BY-NC 4.0. Esta aplicación no implica respaldo ni autoría del juego por parte de Steven W. Ellingson o Virginia Tech. Los avisos de terceros del PDF permanecen en el original.

El código propio de la aplicación se distribuye bajo la licencia MIT indicada en `LICENCIA_CODIGO.txt`; esa licencia no sustituye la del libro ni la de la adaptación de su contenido.
