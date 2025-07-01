import heapq
from collections import deque, defaultdict

# === Cargar destinos ===
def cargar_destinos(path):
    visas = {}
    with open(path, "r") as file:
        for line in file:
            codigo, requiere_visa = line.strip().split(";")
            visas[codigo] = requiere_visa.lower() == "sí"
    return visas

# === Cargar conexiones ===
def cargar_tarifas(path):
    grafo = defaultdict(list)
    with open(path, "r") as file:
        for line in file:
            origen, destino, costo = line.strip().split(";")
            costo = float(costo)
            grafo[origen].append((destino, costo))
            grafo[destino].append((origen, costo))  # bidireccional
    return grafo

# === Filtrado por visa ===
def filtrar_por_visa(grafo, visas, tiene_visa):
    if tiene_visa:
        return grafo  # sin filtro
    # eliminar rutas que partan o lleguen a un nodo con visa
    nuevo_grafo = defaultdict(list)
    for origen in grafo:
        if visas.get(origen, False):
            continue
        for destino, costo in grafo[origen]:
            if not visas.get(destino, False):
                nuevo_grafo[origen].append((destino, costo))
    return nuevo_grafo

# === Dijkstra para costo mínimo ===
def dijkstra(grafo, inicio, fin):
    heap = [(0, inicio, [])]
    visitados = set()
    while heap:
        costo, actual, ruta = heapq.heappop(heap)
        if actual in visitados:
            continue
        ruta = ruta + [actual]
        if actual == fin:
            return costo, ruta
        visitados.add(actual)
        for vecino, peso in grafo[actual]:
            if vecino not in visitados:
                heapq.heappush(heap, (costo + peso, vecino, ruta))
    return float("inf"), []

# === BFS para menor cantidad de escalas ===
def bfs(grafo, inicio, fin):
    cola = deque([(inicio, [inicio])])
    visitados = set()
    while cola:
        actual, ruta = cola.popleft()
        if actual == fin:
            return len(ruta) - 1, ruta
        if actual in visitados:
            continue
        visitados.add(actual)
        for vecino, _ in grafo[actual]:
            if vecino not in visitados:
                cola.append((vecino, ruta + [vecino]))
    return float("inf"), []

# === Main ===
def main():
    visas = cargar_destinos("destinos.txt")
    grafo = cargar_tarifas("tarifas.txt")

    origen = input("Código aeropuerto origen: ").upper()
    destino = input("Código aeropuerto destino: ").upper()
    tiene_visa = input("¿Tiene visa? (s/n): ").lower() == "s"
    modo = input("¿Desea minimizar costo (c) o escalas (e)?: ").lower()

    if origen not in visas or destino not in visas:
        print("Origen o destino inválido.")
        return

    if not tiene_visa and visas[origen]:
        print("No se puede iniciar viaje en un destino que requiere visa sin poseerla.")
        return

    grafo_filtrado = filtrar_por_visa(grafo, visas, tiene_visa)

    if modo == "c":
        costo, ruta = dijkstra(grafo_filtrado, origen, destino)
        if ruta:
            print(f"Ruta más barata: {' -> '.join(ruta)} | Costo total: ${costo:.2f}")
        else:
            print("No hay ruta disponible.")
    elif modo == "e":
        escalas, ruta = bfs(grafo_filtrado, origen, destino)
        if ruta:
            print(f"Ruta con menos escalas: {' -> '.join(ruta)} | Escalas: {escalas}")
        else:
            print("No hay ruta disponible.")
    else:
        print("Opción no válida.")

if __name__ == "__main__":
    main()
