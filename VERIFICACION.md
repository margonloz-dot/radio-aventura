# Verificación de Radio Aventura

Verificado el 21 de octubre de 2026 en Windows con la instalación local de Python 3.14.7 y Microsoft Edge.

- 166 secciones principales del índice representadas, en 20 sectores; 276 subapartados detectados para profundizar.
- Las 531 páginas del libro están incluidas en la búsqueda y el PDF adjunto coincide por SHA-256 con el original entregado.
- Cada objetivo numérico de las 166 misiones tiene al menos una solución alcanzable con el control visible.
- Se compararon valores conocidos de longitud de onda, polarización, ruido térmico, espacio libre, reflexión, filtro RC, bits por símbolo, mezcla, PLL y alias.
- Una prueba HTTP completó las 166 misiones y los 20 retos de sector, alcanzando los 10 300 XP previstos.
- Las pruebas verificaron rechazo de respuestas antes de sus requisitos, sectores bloqueados y puntuación que no se duplica al repetir.
- Se verificaron persistencia en disco, notas, recuperación desde respaldo y preservación de un archivo no legible.
- La prueba en navegador completó la primera misión, un intento incorrecto y uno correcto, recargó el avance y comprobó exportación y notas.
- Se ejercitaron los controles de las 15 familias de laboratorio y la búsqueda en el texto del libro.
- Se comprobaron seis vistas a 390 y 320 píxeles de ancho, sin desbordamiento horizontal. Se inspeccionaron capturas de inicio, laboratorio y pantalla estrecha.
- La ejecución probada no produjo errores de JavaScript ni solicitudes de red externas.

Las pruebas utilizaron datos temporales separados. La partida que se entrega no contiene avance ni notas de prueba.

Para repetir las verificaciones del motor sin modificar tu partida, abre una terminal en esta carpeta y ejecuta:

```text
python -m unittest -v test_radio.py
```

Los laboratorios son modelos didácticos con las hipótesis indicadas en cada uno. Esta verificación comprueba el software y sus fórmulas de referencia; no constituye una medición de equipos RF.

## Actualización del lector: español de México (23 de octubre de 2026)

- Se verificó que las 166 secciones tengan lectura en español de México, original en inglés y metadatos de idioma.
- Se contrastaron los hashes del texto original para comprobar que se conserva sin cambios.
- Se conservaron 1724 bloques de expresiones matemáticas; 1724 incluyen una imagen tomada del PDF para mantener fracciones y exponentes.
- Se comprobó en la interfaz que el español sea el idioma inicial y que el selector permita pasar al inglés y regresar al español.
- La primera lectura se revisó editorialmente. El resto utiliza traducción automática local con ajustes de terminología técnica y uso de México; el visor lo indica y conserva el original para comparar.
- La aplicación continúa usando sólo la biblioteca estándar de Python para ejecutarse; el traductor se utilizó al preparar el contenido y no se incluye como requisito de ejecución.

## Actualización de apariencia (23 de octubre de 2026)

- Se comprobaron en el navegador los selectores de fondo y letras con una combinación personalizada.
- Se recargó la página y se verificó que tanto el fondo como el texto de las lecciones conservaran los colores elegidos.
- Se verificó el color del texto en el lector en español y se comprobó la combinación sepia.
- Las preferencias se guardan únicamente en el navegador; no se cambiaron datos de la partida ni la configuración del supervisor de Python.
- Se validó la sintaxis de game.js con node --check.
