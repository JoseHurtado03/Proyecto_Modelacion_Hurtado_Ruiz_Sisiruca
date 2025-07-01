import csv

def leer_destinos(ruta_archivo):
    """
    Lee el archivo de destinos. Devuelve un diccionario {código: requiere_visa (True/False)}.
    """
    destinos = {}
    with open(ruta_archivo, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Omitir cabecera
        for codigo, nombre, visa in reader:
            requiere_visa = (visa.strip().lower() == 'sí')  # Asume "Sí"/"No" en columna Visa
            destinos[codigo.strip()] = requiere_visa
    return destinos

def leer_vuelos(ruta_archivo):
    """
    Lee el archivo de vuelos. Devuelve una lista de tuplas (origen, destino, costo).
    """
    vuelos = []
    with open(ruta_archivo, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Omitir cabecera
        for origen, destino, costo in reader:
            vuelos.append((origen.strip(), destino.strip(), float(costo)))
    return vuelos

def construir_grafo(vuelos):
    """
    Construye un grafo (dict de dicts) de los vuelos. Grafo[a][b] = costo.
    """
    grafo = {}
    for ori, dst, costo in vuelos:
        grafo.setdefault(ori, {})[dst] = costo
        grafo.setdefault(dst, {})[ori] = costo
    return grafo

import heapq
from collections import deque

def dijkstra(grafo, inicio, fin):
    """
    Devuelve (distancia, ruta) de menor costo desde inicio hasta fin usando Dijkstra.
    """
    dist = {nodo: float('inf') for nodo in grafo}
    dist[inicio] = 0
    prev = {}
    pq = [(0, inicio)]
    while pq:
        d, nodo = heapq.heappop(pq)
        if nodo == fin:
            break
        if d > dist[nodo]:
            continue
        for vecino, peso in grafo[nodo].items():
            nd = d + peso
            if nd < dist[vecino]:
                dist[vecino] = nd
                prev[vecino] = nodo
                heapq.heappush(pq, (nd, vecino))
    # Reconstruir ruta
    if fin not in prev and inicio != fin:
        return float('inf'), []  # Sin ruta
    ruta = []
    nodo = fin
    while nodo != inicio:
        ruta.append(nodo)
        nodo = prev[nodo]
    ruta.append(inicio)
    ruta.reverse()
    return dist[fin], ruta

def bfs_escalas(grafo, inicio, fin):
    """
    Devuelve (escalas, ruta) de menor número de saltos desde inicio hasta fin usando BFS.
    """
    visitado = {inicio}
    queue = deque([(inicio, [inicio])])
    while queue:
        nodo, path = queue.popleft()
        if nodo == fin:
            return len(path)-1, path  # escalas = aristas = nodos-1
        for vecino in grafo[nodo]:
            if vecino not in visitado:
                visitado.add(vecino)
                queue.append((vecino, path + [vecino]))
    return None, []  # Sin ruta

def filtrar_por_visa(grafo, destinos_visa, tiene_visa, origen, destino):
    """
    Si no tiene visa, remueve del grafo todos los nodos (y aristas) de aeropuertos que requieran visa.
    Verifica además que origen/destino sean válidos.
    """
    if not tiene_visa:
        if destinos_visa.get(origen, True):
            raise ValueError(f"Origen {origen} requiere visa y el pasajero no la tiene")
        if destinos_visa.get(destino, True):
            raise ValueError(f"Destino {destino} requiere visa y el pasajero no la tiene")
        # Construir subgrafo solo con nodos sin visa
        permitido = {a for a,v in destinos_visa.items() if not v}
        grafo_filtrado = {}
        for a, vecinos in grafo.items():
            if a in permitido:
                grafo_filtrado[a] = {b:c for b,c in vecinos.items() if b in permitido}
        return grafo_filtrado
    else:
        return grafo  # sin cambios si tiene visa


if __name__ == "__main__":
    # Leer archivos de datos
    destinos_visa = leer_destinos("Visa.cvs")
    vuelos = leer_vuelos("Vuelos.cvs")
    grafo = construir_grafo(vuelos)

    # Input del usuario
    origen = input("Código aeropuerto de origen: ").strip().upper()
    destino = input("Código aeropuerto de destino: ").strip().upper()
    visa_input = input("¿Posee visa? (sí/no): ").strip().lower()
    criterio = input("Optimizar por 'costo' o por 'escalas': ").strip().lower()

    # Validar códigos
    if origen not in destinos_visa or destino not in destinos_visa:
        print("Código de aeropuerto inválido.")
        exit(1)
    tiene_visa = (visa_input == 'sí' or visa_input == 'si')

    try:
        # Aplicar filtro de visa al grafo
        grafo_usar = filtrar_por_visa(grafo, destinos_visa, tiene_visa, origen, destino)
    except ValueError as e:
        print(e)
        exit(1)

    # Calcular ruta según criterio
    if criterio == "costo":
        costo, ruta = dijkstra(grafo_usar, origen, destino)
        if ruta:
            print(f"Itinerario: {' -> '.join(ruta)}")
            print(f"Costo total: {costo:.2f} USD")
        else:
            print("No hay ruta disponible con las restricciones dadas.")
    elif criterio == "escalas":
        escalas, ruta = bfs_escalas(grafo_usar, origen, destino)
        if ruta:
            print(f"Itinerario: {' -> '.join(ruta)}")
            print(f"Número de escalas: {escalas}")
        else:
            print("No hay ruta disponible con las restricciones dadas.")
    else:
        print("Criterio inválido. Elija 'costo' o 'escalas'.")