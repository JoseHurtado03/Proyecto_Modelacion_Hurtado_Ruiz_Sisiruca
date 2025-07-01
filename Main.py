import heapq
from collections import deque, defaultdict
import tkinter as tk
from tkinter import ttk, messagebox
import ttkbootstrap as ttkbs
from ttkbootstrap.constants import *

# === Cargar destinos ===
def cargar_destinos(path):
    visas = {}
    try:
        with open(path, "r") as file:
            for line in file:
                parts = line.strip().split(";")
                if len(parts) >= 2:
                    codigo, requiere_visa = parts[0], parts[1]
                    visas[codigo] = requiere_visa.lower() == "si"
        return visas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar destinos:\n{str(e)}")
        return {}

# === Cargar conexiones ===
def cargar_tarifas(path):
    grafo = defaultdict(list)
    try:
        with open(path, "r") as file:
            for line in file:
                parts = line.strip().split(";")
                if len(parts) >= 3:
                    origen, destino, costo = parts[0], parts[1], float(parts[2])
                    grafo[origen].append((destino, costo))
                    grafo[destino].append((origen, costo))  # bidireccional
        return grafo
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo cargar tarifas:\n{str(e)}")
        return defaultdict(list)

# === Filtrado por visa ===
def filtrar_por_visa(grafo, visas, tiene_visa):
    if tiene_visa:
        return grafo  # sin filtro
    
    # Crear nuevo grafo solo con nodos que no requieren visa
    nuevo_grafo = defaultdict(list)
    for origen in grafo:
        if visas.get(origen, False):  # Si requiere visa, saltar
            continue
        for destino, costo in grafo[origen]:
            if not visas.get(destino, False):  # Solo si destino no requiere visa
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
        for vecino, peso in grafo.get(actual, []):
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
            return len(ruta) - 1, ruta  # escalas = nodos - 1
        if actual in visitados:
            continue
        visitados.add(actual)
        for vecino, _ in grafo.get(actual, []):
            if vecino not in visitados:
                cola.append((vecino, ruta + [vecino]))
    return float("inf"), []

# === Interfaz Gráfica ===
class FlightPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("✈️ Planificador de Vuelos")
        self.root.geometry("700x550")
        self.root.resizable(True, True)
        
        # Cargar datos
        self.visas = cargar_destinos("Destinos.txt")
        self.grafo = cargar_tarifas("Tarifas.txt")
        
        # Configurar tema moderno
        self.style = ttkbs.Style(theme="morph")
        self.style.configure("TLabel", font=("Segoe UI", 10))
        self.style.configure("TButton", font=("Segoe UI", 10, "bold"))
        self.style.configure("Header.TLabel", font=("Segoe UI", 14, "bold"))
        
        # Crear widgets
        self.create_widgets()
        
    def create_widgets(self):
        # Marco principal
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Encabezado
        header = ttk.Label(
            main_frame, 
            text="PLANIFICADOR DE VUELOS", 
            style="Header.TLabel",
            anchor="center"
        )
        header.pack(pady=(0, 15))
        
        # Marco de entrada
        input_frame = ttk.LabelFrame(main_frame, text="Detalles del Viaje", padding=15)
        input_frame.pack(fill=tk.X, pady=10)
        
        # Entrada de aeropuerto de origen
        ttk.Label(input_frame, text="Aeropuerto Origen:").grid(row=0, column=0, sticky=tk.W, pady=8, padx=5)
        self.origen_entry = ttk.Entry(input_frame, width=8)
        self.origen_entry.grid(row=0, column=1, sticky=tk.W, padx=5)
        self.origen_entry.focus()
        
        # Entrada de aeropuerto de destino
        ttk.Label(input_frame, text="Aeropuerto Destino:").grid(row=1, column=0, sticky=tk.W, pady=8, padx=5)
        self.destino_entry = ttk.Entry(input_frame, width=8)
        self.destino_entry.grid(row=1, column=1, sticky=tk.W, padx=5)
        
        # Visa
        ttk.Label(input_frame, text="Posee Visa:").grid(row=2, column=0, sticky=tk.W, pady=8, padx=5)
        self.visa_var = tk.StringVar(value="no")
        ttk.Radiobutton(input_frame, text="Sí", variable=self.visa_var, value="sí").grid(row=2, column=1, sticky=tk.W)
        ttk.Radiobutton(input_frame, text="No", variable=self.visa_var, value="no").grid(row=2, column=2, sticky=tk.W)
        
        # Criterio de optimización
        ttk.Label(input_frame, text="Criterio:").grid(row=3, column=0, sticky=tk.W, pady=8, padx=5)
        self.criterio_var = tk.StringVar(value="costo")
        criterio_combo = ttk.Combobox(
            input_frame, 
            textvariable=self.criterio_var,
            values=["costo", "escalas"],
            state="readonly",
            width=10
        )
        criterio_combo.grid(row=3, column=1, sticky=tk.W, padx=5)
        
        # Botones
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=15)
        
        ttk.Button(
            button_frame, 
            text="Buscar Ruta Óptima", 
            style="success.TButton",
            command=self.buscar_ruta
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Ver Aeropuertos", 
            style="info.TButton",
            command=self.mostrar_aeropuertos
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            button_frame, 
            text="Limpiar", 
            style="warning.TButton",
            command=self.limpiar
        ).pack(side=tk.RIGHT, padx=5)
        
        # Resultados
        result_frame = ttk.LabelFrame(main_frame, text="Resultados", padding=10)
        result_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        self.resultado_text = tk.Text(
            result_frame, 
            height=10, 
            wrap=tk.WORD,
            font=("Consolas", 10),
            padx=10,
            pady=10,
            bg="#f8f9fa"
        )
        self.resultado_text.pack(fill=tk.BOTH, expand=True)
        self.resultado_text.insert(tk.END, "Ingrese los datos del viaje y haga clic en 'Buscar Ruta Óptima'")
        self.resultado_text.config(state=tk.DISABLED)
        
        # Barra de estado
        self.status_var = tk.StringVar(value="Cargados: destinos.txt y tarifas.txt")
        ttk.Label(
            main_frame, 
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=3
        ).pack(fill=tk.X, pady=(10, 0))
    
    def buscar_ruta(self):
        origen = self.origen_entry.get().strip().upper()
        destino = self.destino_entry.get().strip().upper()
        visa_input = self.visa_var.get()
        criterio = self.criterio_var.get()
        
        # Habilitar el texto para actualizar
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        
        # Validaciones
        if not origen or not destino:
            self.resultado_text.insert(tk.END, "ERROR: Debe ingresar origen y destino")
            self.resultado_text.config(state=tk.DISABLED)
            return
        
        if origen not in self.visas or destino not in self.visas:
            self.resultado_text.insert(tk.END, "ERROR: Códigos de aeropuerto inválidos\n\n")
            self.resultado_text.insert(tk.END, "Use el botón 'Ver Aeropuertos' para ver los códigos disponibles")
            self.resultado_text.config(state=tk.DISABLED)
            return
        
        tiene_visa = (visa_input == 'sí')
        
        # Verificar visa para aeropuerto de origen
        if not tiene_visa and self.visas.get(origen, False):
            self.resultado_text.insert(tk.END, f"ERROR: El aeropuerto de origen {origen} requiere visa y usted no la tiene")
            self.resultado_text.config(state=tk.DISABLED)
            return
        
        # Filtrar grafo por visa
        grafo_filtrado = filtrar_por_visa(self.grafo, self.visas, tiene_visa)
        
        # Buscar ruta según criterio
        try:
            if criterio == "costo":
                costo, ruta = dijkstra(grafo_filtrado, origen, destino)
                if not ruta:
                    raise ValueError("No hay ruta disponible con los criterios actuales")
                
                self.resultado_text.insert(tk.END, "RUTA MÁS ECONÓMICA\n")
                self.resultado_text.insert(tk.END, "="*30 + "\n")
                self.resultado_text.insert(tk.END, f"✈️ Ruta: {' → '.join(ruta)}\n\n")
                self.resultado_text.insert(tk.END, f"💵 Costo total: ${costo:.2f}\n")
                self.resultado_text.insert(tk.END, f"📌 Escalas: {max(0, len(ruta)-2)}")
                
            elif criterio == "escalas":
                escalas, ruta = bfs(grafo_filtrado, origen, destino)
                if not ruta:
                    raise ValueError("No hay ruta disponible con los criterios actuales")
                
                self.resultado_text.insert(tk.END, "RUTA CON MENOS ESCALAS\n")
                self.resultado_text.insert(tk.END, "="*30 + "\n")
                self.resultado_text.insert(tk.END, f"✈️ Ruta: {' → '.join(ruta)}\n\n")
                self.resultado_text.insert(tk.END, f"📌 Escalas totales: {max(0, len(ruta)-2)}\n")
                
                # Calcular costo para esta ruta
                costo_total = 0
                for i in range(len(ruta)-1):
                    for vecino, costo in grafo_filtrado.get(ruta[i], []):
                        if vecino == ruta[i+1]:
                            costo_total += costo
                            break
                
                self.resultado_text.insert(tk.END, f"💵 Costo estimado: ${costo_total:.2f}")
                
            else:
                self.resultado_text.insert(tk.END, "ERROR: Criterio no válido. Seleccione 'costo' o 'escalas'")
            
        except Exception as e:
            self.resultado_text.insert(tk.END, f"ERROR: {str(e)}")
        
        self.resultado_text.config(state=tk.DISABLED)
    
    def mostrar_aeropuertos(self):
        # Crear ventana emergente
        popup = tk.Toplevel(self.root)
        popup.title("Aeropuertos Disponibles")
        popup.geometry("400x400")
        popup.transient(self.root)
        popup.grab_set()
        
        # Crear marco con scrollbar
        frame = ttk.Frame(popup)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Lista de aeropuertos
        ttk.Label(frame, text="Códigos de Aeropuertos", font=("Segoe UI", 11, "bold")).pack(pady=5)
        
        # Crear árbol para mostrar aeropuertos
        columns = ("Código", "Requiere Visa")
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        # Configurar columnas
        tree.column("Código", width=100, anchor=tk.CENTER)
        tree.column("Requiere Visa", width=120, anchor=tk.CENTER)
        
        # Configurar encabezados
        tree.heading("Código", text="Código")
        tree.heading("Requiere Visa", text="Requiere Visa")
        
        # Agregar datos
        for codigo, requiere_visa in sorted(self.visas.items()):
            tree.insert("", tk.END, values=(codigo, "Sí" if requiere_visa else "No"))
        
        # Añadir scrollbar
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Botón de cierre
        ttk.Button(
            popup, 
            text="Cerrar", 
            command=popup.destroy,
            style="danger.TButton"
        ).pack(pady=10)
    
    def limpiar(self):
        self.origen_entry.delete(0, tk.END)
        self.destino_entry.delete(0, tk.END)
        self.visa_var.set("no")
        self.criterio_var.set("costo")
        
        self.resultado_text.config(state=tk.NORMAL)
        self.resultado_text.delete(1.0, tk.END)
        self.resultado_text.insert(tk.END, "Ingrese los datos del viaje y haga clic en 'Buscar Ruta Óptima'")
        self.resultado_text.config(state=tk.DISABLED)
        
        self.origen_entry.focus()

if __name__ == "__main__":
    root = ttkbs.Window(themename="morph")
    app = FlightPlannerApp(root)
    root.mainloop()