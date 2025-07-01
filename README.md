# Planificador de Vuelos

Este proyecto es una aplicación de escritorio en Python que permite planificar rutas de vuelo entre aeropuertos, optimizando por costo o cantidad de escalas, y considerando la necesidad de visa para cada destino.

## Estructura del Proyecto

- Main.py: Código principal de la aplicación y la interfaz gráfica.
- Destinos.txt: Lista de aeropuertos y si requieren visa.
- Tarifas.txt: Conexiones entre aeropuertos y sus costos.

## Requisitos

- Python 3.8+
- Paquetes: ttkbootstrap, tkinter

Instala las dependencias con:

```bash
pip install ttkbootstrap
```

## Uso

1. Ejecuta Main.py:
   ```bash
   python Main.py
   ```
2. Ingresa el código del aeropuerto de origen y destino.
3. Indica si posees visa.
4. Selecciona el criterio de optimización: costo o escalas.
5. Haz clic en "Buscar Ruta Óptima".

## Formato de Archivos

### Destinos.txt

```
CODIGO_AEROPUERTO;SI/NO
```

Ejemplo:

```
JFK;NO
LIM;SI
```

### Tarifas.txt

```
ORIGEN;DESTINO;COSTO
```

Ejemplo:

```
JFK;LIM;500
LIM;BOG;200
```

## Funcionalidades

- Búsqueda de ruta más económica (Dijkstra).
- Búsqueda de ruta con menos escalas (BFS).
- Filtro de rutas según necesidad de visa.
- Visualización de aeropuertos disponibles.
- Interfaz gráfica moderna y fácil de usar.

## Créditos

Desarrollado por Hurtado, Ruiz y Sisiruca.
