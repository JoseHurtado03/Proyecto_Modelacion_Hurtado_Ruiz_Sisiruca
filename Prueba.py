import csv
import heapq
from collections import deque
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkbs
from ttkbootstrap.constants import *


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


def main():
    # Leer datos y construir grafo
    try:
        destinos_visa = leer_destinos("Visa.cvs")
        vuelos = leer_vuelos("Vuelos.cvs")
        grafo = construir_grafo(vuelos)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{str(e)}")
        return

    # Configurar interfaz gráfica
    app = ttkbs.Window(themename="morph")
    app.title("Planificador de Vuelos")
    app.geometry("600x500")
    app.resizable(False, False)

    # Estilo personalizado
    style = ttkbs.Style()
    style.configure("TLabel", font=("Helvetica", 10))
    style.configure("TButton", font=("Helvetica", 10, "bold"))
    style.configure("Header.TLabel", font=("Helvetica", 14, "bold"))

    # Marco principal
    main_frame = ttk.Frame(app, padding=20)
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Título
    ttk.Label(
        main_frame, 
        text="✈️ PLANIFICADOR DE VUELOS", 
        style="Header.TLabel"
    ).pack(pady=10)

    # Formulario
    form_frame = ttk.LabelFrame(main_frame, text="Datos del Viaje", padding=15)
    form_frame.pack(fill=tk.X, pady=10)

    # Campo Origen
    ttk.Label(form_frame, text="Aeropuerto Origen:").grid(row=0, column=0, sticky=tk.W, pady=5)
    origen_entry = ttk.Entry(form_frame, width=10)
    origen_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
    origen_entry.focus()

    # Campo Destino
    ttk.Label(form_frame, text="Aeropuerto Destino:").grid(row=1, column=0, sticky=tk.W, pady=5)
    destino_entry = ttk.Entry(form_frame, width=10)
    destino_entry.grid(row=1, column=1, sticky=tk.W, padx=5)

    # Visa
    ttk.Label(form_frame, text="Posee Visa:").grid(row=2, column=0, sticky=tk.W, pady=5)
    visa_var = tk.StringVar(value="no")
    ttk.Radiobutton(form_frame, text="Sí", variable=visa_var, value="sí").grid(row=2, column=1, sticky=tk.W)
    ttk.Radiobutton(form_frame, text="No", variable=visa_var, value="no").grid(row=2, column=2, sticky=tk.W)

    # Criterio
    ttk.Label(form_frame, text="Criterio de Optimización:").grid(row=3, column=0, sticky=tk.W, pady=5)
    criterio_var = tk.StringVar(value="costo")
    ttk.Combobox(
        form_frame,
        textvariable=criterio_var,
        values=["costo", "escalas"],
        state="readonly",
        width=8
    ).grid(row=3, column=1, sticky=tk.W)

    # Botón de búsqueda
    buscar_btn = ttk.Button(
        main_frame,
        text="BUSCAR RUTA ÓPTIMA",
        style="success.TButton",
        command=lambda: buscar_ruta(
            origen_entry.get().strip().upper(),
            destino_entry.get().strip().upper(),
            visa_var.get(),
            criterio_var.get(),
            destinos_visa,
            grafo,
            resultado_text
        )
    )
    buscar_btn.pack(pady=20)

    # Resultados
    result_frame = ttk.Frame(main_frame)
    result_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(result_frame, text="Resultado:").pack(anchor=tk.W)
    resultado_text = tk.Text(
        result_frame, 
        height=8, 
        wrap=tk.WORD,
        font=("Consolas", 10),
        bg="#f8f9fa",
        padx=10,
        pady=10
    )
    resultado_text.pack(fill=tk.BOTH, expand=True)
    resultado_text.insert(tk.END, "Ingrese los datos y presione 'BUSCAR RUTA ÓPTIMA'")
    resultado_text.config(state=tk.DISABLED)

    app.mainloop()

def buscar_ruta(origen, destino, visa_input, criterio, destinos_visa, grafo, text_widget):
    text_widget.config(state=tk.NORMAL)
    text_widget.delete(1.0, tk.END)
    
    # Validaciones
    if not origen or not destino:
        text_widget.insert(tk.END, "ERROR: Debe ingresar origen y destino")
        text_widget.config(state=tk.DISABLED)
        return
        
    if origen not in destinos_visa or destino not in destinos_visa:
        text_widget.insert(tk.END, f"ERROR: Códigos inválidos\n\nAeropuertos válidos:\n{', '.join(destinos_visa.keys())}")
        text_widget.config(state=tk.DISABLED)
        return
        
    tiene_visa = (visa_input == 'sí' or visa_input == 'si')
    
    try:
        grafo_usar = filtrar_por_visa(grafo, destinos_visa, tiene_visa, origen, destino)
    except ValueError as e:
        text_widget.insert(tk.END, f"ERROR DE VISA:\n{str(e)}")
        text_widget.config(state=tk.DISABLED)
        return
        
    # Calcular ruta
    try:
        if criterio == "costo":
            costo, ruta = dijkstra(grafo_usar, origen, destino)
            if not ruta:
                raise ValueError("No existe ruta con las restricciones")
                
            text_widget.insert(tk.END, "RUTA ÓPTIMA (COSTO)\n")
            text_widget.insert(tk.END, "➜ " + " → ".join(ruta) + "\n\n")
            text_widget.insert(tk.END, f"COSTO TOTAL: ${costo:.2f} USD")
            
        elif criterio == "escalas":
            escalas, ruta = bfs_escalas(grafo_usar, origen, destino)
            if not ruta:
                raise ValueError("No existe ruta con las restricciones")
                
            text_widget.insert(tk.END, "RUTA ÓPTIMA (ESCALAS)\n")
            text_widget.insert(tk.END, "➜ " + " → ".join(ruta) + "\n\n")
            text_widget.insert(tk.END, f"TOTAL ESCALAS: {escalas}")
            
        else:
            text_widget.insert(tk.END, "Criterio inválido. Use 'costo' o 'escalas'")
            
    except Exception as e:
        text_widget.insert(tk.END, f"ERROR: {str(e)}")
    
    text_widget.config(state=tk.DISABLED)

if __name__ == "__main__":
    main()