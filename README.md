¡Acá tenés, Juano! Un `README.md` es fundamental para que tu proyecto destaque. Armé este documento con una estructura súper profesional. Destaca los algoritmos que implementaste, la interfaz gráfica y tu excelente cobertura de tests.

Copiá todo el bloque de texto que está acá abajo, creá un archivo llamado `README.md` en tu repositorio de GitHub (podés hacerlo con el botón "Add file" en la web) y pegalo ahí adentro.

---

```markdown
# 🐍 Snake Bot - Code Challenge

Un bot automatizado y altamente competitivo desarrollado en Python para el torneo de WebSockets de Code Challenge. Este bot no solo busca comida de forma eficiente, sino que analiza el entorno para predecir y evadir los movimientos enemigos en tiempo real.

## 🚀 Características Principales

*   **Inteligencia y Supervivencia:** Utiliza algoritmos de búsqueda del camino más corto (BFS - Breadth-First Search) para localizar la comida más cercana y un algoritmo de relleno por difusión (Flood Fill) para medir el espacio libre y evitar encierros.
*   **Visión de Peligro:** El bot mapea las zonas adyacentes a la cabeza del enemigo y las clasifica como "lava" (zonas de muerte segura), priorizando la supervivencia y evitando bloqueos estratégicos ("trampas").
*   **Interfaz Gráfica en Vivo:** Incluye un visualizador (`interfaz.py`) construido con Tkinter que corre en un hilo secundario (Threading). Permite monitorear las partidas, el tablero y el marcador en tiempo real sin bloquear la conexión de red del bot.
*   **Integración Continua (CI):** Configurado con GitHub Actions para ejecutar pruebas unitarias automáticas ante cada subida de código, garantizando la estabilidad del algoritmo.

## 🛠️ Requisitos del Sistema

*   Python 3.11 o superior.
*   Dependencias de Python: `websockets`, `coverage`.
*   Librería del sistema para la interfaz gráfica: `python3-tk` (o su equivalente según tu sistema operativo).
*   Archivos de imagen (`.png`) incluidos en el repositorio para renderizar el tablero en la interfaz.

## 🎮 Cómo ejecutar el Bot

Para iniciar el bot y conectarlo al servidor del torneo, abre tu terminal y ejecuta el script principal pasando tu token de jugador como argumento:

```bash
python botaver.py <TU_TOKEN_DE_JUGADOR>

```

Al ejecutarse, el bot se conectará automáticamente mediante WebSockets y desplegará la interfaz gráfica para observar las partidas en vivo.

## 🧪 Pruebas y Cobertura (Test Coverage)

Este proyecto cuenta con una sólida base de pruebas unitarias y asíncronas (`test_codigobot.py`) que evalúan:

* Mapeo y lectura del tablero.
* Eficiencia de los algoritmos de evasión (Flood Fill / BFS).
* Manejo de desconexiones y recepción de mensajes WebSocket.

El proyecto mantiene un **Test Coverage superior al 90%**. Para correr las pruebas localmente y generar el reporte, ejecuta:

```bash
coverage run --omit="interfaz.py" -m unittest test_codigobot.py
coverage report -m --omit="interfaz.py"

```

## 📁 Estructura del Proyecto

* `botaver.py`: Script principal que contiene la lógica del bot, la conexión de red asíncrona y la toma de decisiones.
* `interfaz.py`: Módulo del visualizador gráfico con soporte para múltiples pestañas simultáneas.
* `test_codigobot.py`: Archivo de pruebas unitarias y simulación del entorno.
* `.github/workflows/tests.yml`: Configuración de GitHub Actions para el testing automático.

```

```
