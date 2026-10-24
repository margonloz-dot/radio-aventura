# Radio Aventura

Juego educativo local en español para aprender ingeniería de radio mediante explicaciones, experimentos y retos. Incluye 20 sectores y 166 misiones basadas en *Radio Systems Engineering, Revised First Edition*, de Steven W. Ellingson (2023).

## Ejecutar

Necesitas Python 3.10 o posterior y un navegador moderno. No requiere instalar paquetes ni conectarse a Internet para jugar.

1. Descarga el proyecto con **Code → Download ZIP** y extrae toda la carpeta, o clona el repositorio.
2. En Windows, abre `INICIAR_RADIO_AVENTURA.cmd`.
3. Como alternativa, ejecuta desde esta carpeta:

```sh
python app.py
```

En los sistemas donde Python se llama `python3`, usa `python3 app.py`. El supervisor y los archivos `.cmd` son específicos de Windows.

Abre la dirección local que imprime el programa. La dirección inicial es `http://127.0.0.1:8765/`; si ese puerto está ocupado, el inicio normal busca uno cercano. Mantén el proceso activo y pulsa Ctrl+C para cerrarlo. El servidor escucha únicamente en la computadora donde se ejecuta.

Para seleccionar un puerto distinto:

```sh
python app.py --port 9000
```

## Qué incluye

- Campaña progresiva con explicación, experimento y pregunta conceptual por misión.
- Laboratorio libre con 15 familias de experimentos.
- Lecturas en español de México y consulta del original en inglés.
- Búsqueda de las 531 páginas y PDF original para contrastar ecuaciones, tablas y figuras.
- Cuaderno, notas, exportación de avance y preferencias de apariencia.

Las actividades y los modelos son material didáctico añadido. El programa no configura equipos RF ni predice el desempeño de una instalación real. La traducción de apoyo utiliza traducción automática con ajustes terminológicos; conserva el original para contrastar. Consulta [LEEME.md](LEEME.md) y [COBERTURA.md](COBERTURA.md).

## Partidas y privacidad

El programa crea `datos/` para guardar el avance y las notas en la computadora de cada persona. Esa carpeta queda excluida de Git. Esta copia no incluye partidas, notas, registros, accesos directos ni configuración de inicio de la computadora de origen.

Las preferencias de color se guardan en el navegador. Para cambiar de equipo, usa **Exportar avance** y sigue las instrucciones de [LEEME.md](LEEME.md).

## Pruebas

```sh
python -m unittest -v test_radio.py
```

Las pruebas usan carpetas temporales y comprueban contenido, fórmulas de referencia, traducción, progresión, HTTP y recuperación de datos. Las 6 pruebas pasaron durante la revisión del 24 de octubre de 2026. [VERIFICACION.md](VERIFICACION.md) conserva el registro histórico de verificaciones previas.

## Estructura

| Archivo | Función |
|---|---|
| `app.py` | Servidor local, cálculos y evaluación |
| `game.js`, `index.html`, `style.css` | Interfaz del juego |
| `curso.json` | Lecciones, preguntas y campaña |
| `fuentes.json` | Lecturas y fórmulas para el lector |
| `libro_busqueda.json` | Búsqueda del contenido del libro |
| `libro/` | PDF original |
| `test_radio.py` | Pruebas automatizadas |
| `servidor_persistente.py` | Supervisor opcional para Windows |

`fuentes.json` y el PDF son recursos del programa; deben conservarse para disponer del lector completo sin Internet.

## Supervisor opcional de Windows

`MANTENER_SERVIDOR.cmd` inicia el supervisor y `DETENER_SERVIDOR.cmd` lo detiene. Descargar el proyecto no instala un inicio automático. Consulta [SERVIDOR_LOCAL.md](SERVIDOR_LOCAL.md).

Limitación conocida: el supervisor comprueba siempre el puerto 8765, mientras que el juego permite buscar un puerto alternativo. Si otro programa ocupa 8765, utiliza el inicio normal con un puerto explícito; el supervisor puede interpretar como fallo una instancia que responde en otro puerto.

## Licencias y atribución

El código original se distribuye bajo la licencia MIT de [LICENCIA_CODIGO.txt](LICENCIA_CODIGO.txt).

El libro y el contenido educativo adaptado tienen condiciones distintas: **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)**, salvo las excepciones indicadas en el libro. La licencia MIT del código no sustituye esas condiciones.

Ellingson, Steven W. (2023). *Radio Systems Engineering, Revised First Edition*. Virginia Tech Publishing. DOI: [10.21061/radiosystemsengineering-revised1st](https://doi.org/10.21061/radiosystemsengineering-revised1st). [Licencia CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/).

Se conserva el PDF original sin modificaciones. La narrativa, las preguntas y los experimentos son añadidos didácticos. Este proyecto no implica respaldo del autor ni de Virginia Tech.
