# Supervisor local opcional para Windows

`MANTENER_SERVIDOR.cmd` ejecuta `servidor_persistente.py` sin ventana mediante Python para Windows. El supervisor comprueba el servidor cada cinco segundos y puede volver a iniciar el proceso propio si termina o deja de responder. `DETENER_SERVIDOR.cmd` solicita su detención y conserva el avance.

La dirección supervisada es `http://127.0.0.1:8765/`. El servidor sólo es accesible desde la computadora donde se ejecuta. Si otro programa ocupa ese puerto, utiliza el inicio normal y elige un puerto diferente, por ejemplo `python app.py --port 9000`. El supervisor actual comprueba un puerto fijo y no sigue automáticamente el puerto alternativo.

El estado está en `datos/servidor.json` y el registro en `datos/servidor.log`, con rotación de tamaño. Esos archivos se generan en cada computadora y no están incluidos en Git.

Esta distribución no incluye accesos directos ni instala el inicio automático de Windows. En una configuración propia, un acceso directo en la carpeta Inicio depende de la ubicación de la aplicación; debe actualizarse si se mueve. La carpeta Inicio del usuario está bajo `%APPDATA%/Microsoft/Windows/Start Menu/Programs/Startup`.

Windows necesita estar encendido y activo para responder. El supervisor no atiende durante la suspensión, hibernación o apagado y no cambia los ajustes de energía, firewall ni privilegios.
