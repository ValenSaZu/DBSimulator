import os
import sys
from typing import Optional, Dict, Any
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from storage.disk import Disk, DiskGeometry
from data_management.schema_parser import SchemaParser
from data_management.csv_loader import CSVLoader
from data_management.data_validator import DataValidator
from indexing.avl_tree import AVL
from storage.serialization import RecordSerializer
from storage.sector_manager import SectorManager

class DiskSimulatorInterface:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulador de Disco - Base de Datos II")
        self.root.geometry("1000x700")
        
        # Variables de estado
        self.disk: Optional[Disk] = None
        self.schema: Optional[Dict] = None
        self.avl_tree = AVL()
        self.serializer: Optional[RecordSerializer] = None
        self.sector_manager: Optional[SectorManager] = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Configura la interfaz de usuario
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.setup_disk_config_tab(notebook)
        
        self.setup_schema_tab(notebook)
        
        self.setup_data_loading_tab(notebook)
        
        self.setup_search_tab(notebook)
        
        self.setup_disk_status_tab(notebook)
        
    def setup_disk_config_tab(self, notebook):
        # Configura la pestaña de configuración del disco
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Configuración del Disco")
        
        title_label = ttk.Label(frame, text="Configuración de Geometría del Disco", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        params_frame = ttk.LabelFrame(frame, text="Parámetros del Disco", padding=20)
        params_frame.pack(fill='x', padx=20, pady=10)
        
        self.platters_var = tk.StringVar(value="2")
        self.tracks_var = tk.StringVar(value="4")
        self.sectors_var = tk.StringVar(value="8")
        self.sector_size_var = tk.StringVar(value="64")
        
        ttk.Label(params_frame, text="Número de Platos:").grid(row=0, column=0, sticky='w', pady=5)
        ttk.Entry(params_frame, textvariable=self.platters_var, width=20).grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Pistas por Superficie:").grid(row=1, column=0, sticky='w', pady=5)
        ttk.Entry(params_frame, textvariable=self.tracks_var, width=20).grid(row=1, column=1, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Sectores por Pista:").grid(row=2, column=0, sticky='w', pady=5)
        ttk.Entry(params_frame, textvariable=self.sectors_var, width=20).grid(row=2, column=1, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Bytes por Sector:").grid(row=3, column=0, sticky='w', pady=5)
        ttk.Entry(params_frame, textvariable=self.sector_size_var, width=20).grid(row=3, column=1, padx=10, pady=5)
        
        create_btn = ttk.Button(params_frame, text="Crear Disco", 
                               command=self.create_disk)
        create_btn.grid(row=4, column=0, columnspan=2, pady=20)
        
        self.capacity_label = ttk.Label(params_frame, text="", font=("Arial", 10))
        self.capacity_label.grid(row=5, column=0, columnspan=2, pady=10)
        
    def setup_schema_tab(self, notebook):
        # Configura la pestaña de esquema de tabla
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Esquema de Tabla")
        
        title_label = ttk.Label(frame, text="Cargar Esquema SQL", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        schema_frame = ttk.LabelFrame(frame, text="Archivo de Esquema", padding=20)
        schema_frame.pack(fill='x', padx=20, pady=10)
        
        self.schema_path_var = tk.StringVar()
        
        ttk.Label(schema_frame, text="Archivo .txt con CREATE TABLE:").pack(anchor='w')
        
        file_frame = ttk.Frame(schema_frame)
        file_frame.pack(fill='x', pady=10)
        
        ttk.Entry(file_frame, textvariable=self.schema_path_var, width=50).pack(side='left', padx=(0, 10))
        ttk.Button(file_frame, text="Buscar", 
                  command=self.browse_schema_file).pack(side='left')
        
        ttk.Button(schema_frame, text="Cargar Esquema", 
                  command=self.load_schema).pack(pady=10)
        
        schema_display_frame = ttk.LabelFrame(frame, text="Esquema Cargado", padding=10)
        schema_display_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.schema_text = scrolledtext.ScrolledText(schema_display_frame, height=15)
        self.schema_text.pack(fill='both', expand=True)
        
    def setup_data_loading_tab(self, notebook):
        # Configura la pestaña de carga de datos
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Carga de Datos")
        
        title_label = ttk.Label(frame, text="Cargar Datos CSV", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        csv_frame = ttk.LabelFrame(frame, text="Archivo CSV", padding=20)
        csv_frame.pack(fill='x', padx=20, pady=10)
        
        self.csv_path_var = tk.StringVar()
        
        ttk.Label(csv_frame, text="Archivo CSV con datos:").pack(anchor='w')
        
        csv_file_frame = ttk.Frame(csv_frame)
        csv_file_frame.pack(fill='x', pady=10)
        
        ttk.Entry(csv_file_frame, textvariable=self.csv_path_var, width=50).pack(side='left', padx=(0, 10))
        ttk.Button(csv_file_frame, text="Buscar", 
                  command=self.browse_csv_file).pack(side='left')
        
        ttk.Button(csv_frame, text="Validar y Cargar Datos", 
                  command=self.load_csv_data).pack(pady=10)
        
        progress_frame = ttk.LabelFrame(frame, text="Progreso y Resultados", padding=10)
        progress_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=15)
        self.progress_text.pack(fill='both', expand=True)
        
    def setup_search_tab(self, notebook):
        # Configura la pestaña de búsquedas
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Búsquedas")
        
        title_label = ttk.Label(frame, text="Búsqueda por ID", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        search_frame = ttk.LabelFrame(frame, text="Buscar Registro", padding=20)
        search_frame.pack(fill='x', padx=20, pady=10)
        
        self.search_id_var = tk.StringVar()
        
        ttk.Label(search_frame, text="ID del registro:").pack(anchor='w')
        ttk.Entry(search_frame, textvariable=self.search_id_var, width=20).pack(anchor='w', pady=5)
        
        ttk.Button(search_frame, text="Buscar", 
                  command=self.search_record).pack(pady=10)
        
        results_frame = ttk.LabelFrame(frame, text="Resultados de Búsqueda", padding=10)
        results_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.search_results_text = scrolledtext.ScrolledText(results_frame, height=15)
        self.search_results_text.pack(fill='both', expand=True)
        
    def setup_disk_status_tab(self, notebook):
        # Configura la pestaña de estado del disco
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Estado del Disco")
        
        title_label = ttk.Label(frame, text="Información del Disco", 
                               font=("Arial", 14, "bold"))
        title_label.pack(pady=20)
        
        ttk.Button(frame, text="Actualizar Estado", 
                  command=self.update_disk_status).pack(pady=10)
        
        status_frame = ttk.LabelFrame(frame, text="Estado Actual", padding=10)
        status_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.status_text = scrolledtext.ScrolledText(status_frame, height=20)
        self.status_text.pack(fill='both', expand=True)
        
    def create_disk(self):
        # Crea un nuevo disco con los parámetros especificados
        try:
            platters = int(self.platters_var.get())
            tracks = int(self.tracks_var.get())
            sectors = int(self.sectors_var.get())
            sector_size = int(self.sector_size_var.get())
            
            if platters <= 0 or tracks <= 0 or sectors <= 0 or sector_size <= 0:
                messagebox.showerror("Error", "Todos los valores deben ser positivos")
                return
            
            geometry = DiskGeometry(platters, tracks, sectors, sector_size)
            self.disk = Disk(geometry)
            
            self.sector_manager = SectorManager(self.disk)
            self.serializer = RecordSerializer()
            
            total_capacity = geometry.platters * 2 * geometry.tracks * geometry.sectors * geometry.sector_size
            capacity_mb = total_capacity / (1024 * 1024)
            
            self.capacity_label.config(
                text=f"Capacidad Total: {capacity_mb:.2f} MB\n"
                     f"Sectores Totales: {geometry.platters * 2 * geometry.tracks * geometry.sectors:,}"
            )
            
            messagebox.showinfo("Éxito", "Disco creado exitosamente")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Error en los parámetros: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error al crear disco: {str(e)}")
    
    def browse_schema_file(self):
        # Abre diálogo para seleccionar archivo de esquema
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo de esquema",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.schema_path_var.set(filename)
    
    def browse_csv_file(self):
        # Abre diálogo para seleccionar archivo CSV
        filename = filedialog.askopenfilename(
            title="Seleccionar archivo CSV",
            filetypes=[("Archivos CSV", "*.csv"), ("Todos los archivos", "*.*")]
        )
        if filename:
            self.csv_path_var.set(filename)
    
    def load_schema(self):
        # Carga y parsea el esquema SQL
        if not self.disk:
            messagebox.showerror("Error", "Primero debe crear un disco")
            return
            
        schema_path = self.schema_path_var.get()
        if not schema_path:
            messagebox.showerror("Error", "Seleccione un archivo de esquema")
            return
            
        try:
            parser = SchemaParser()
            self.schema = parser.parse_schema_file(schema_path)
            
            # Mostrar esquema en el área de texto
            self.schema_text.delete(1.0, tk.END)
            self.schema_text.insert(tk.END, "Esquema cargado exitosamente:\n\n")
            self.schema_text.insert(tk.END, f"Tabla: {self.schema['table_name']}\n")
            self.schema_text.insert(tk.END, f"Clave Primaria: {self.schema['primary_key']}\n\n")
            self.schema_text.insert(tk.END, "Campos:\n")
            
            for field in self.schema['fields']:
                self.schema_text.insert(tk.END, 
                    f"  - {field['name']}: {field['type']} ({field['size']} bytes)\n")
            
            self.schema_text.insert(tk.END, f"\nTamaño total del registro: {self.schema['record_size']} bytes\n")
            
            messagebox.showinfo("Éxito", "Esquema cargado exitosamente")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar esquema: {str(e)}")
    
    def load_csv_data(self):
        # Carga y valida datos CSV
        if not self.disk:
            messagebox.showerror("Error", "Primero debe crear un disco")
            return
            
        if not self.schema:
            messagebox.showerror("Error", "Primero debe cargar un esquema")
            return
            
        csv_path = self.csv_path_var.get()
        if not csv_path:
            messagebox.showerror("Error", "Seleccione un archivo CSV")
            return
            
        try:
            thread = threading.Thread(target=self._load_csv_data_thread, args=(csv_path,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos: {str(e)}")
    
    def _load_csv_data_thread(self, csv_path):
        # Ejecuta la carga de datos CSV en un hilo separado
        try:
            self.progress_text.delete(1.0, tk.END)
            self.progress_text.insert(tk.END, "Iniciando carga de datos...\n")
            
            loader = CSVLoader()
            validator = DataValidator()
            
            self.progress_text.insert(tk.END, "Validando estructura del CSV...\n")
            data = loader.load_csv(csv_path)
            
            self.progress_text.insert(tk.END, "Validando datos contra esquema...\n")
            validated_data = validator.validate_data(data, self.schema)
            
            self.progress_text.insert(tk.END, f"Se cargaron {len(validated_data)} registros válidos\n")
            
            self.progress_text.insert(tk.END, "Escribiendo datos al disco...\n")
            
            records_written = 0
            for record in validated_data:
                serialized_record = self.serializer.serialize_record(record, self.schema)
                
                sectors_needed = (len(serialized_record) + self.disk.sector_size - 1) // self.disk.sector_size
                
                free_sectors = self.sector_manager.allocate_sectors(sectors_needed)
                if not free_sectors:
                    raise Exception("No hay suficiente espacio en el disco")
                
                self.sector_manager.write_data(serialized_record, free_sectors[0])
                
                primary_key = record[self.schema['primary_key']]
                self.avl_tree.insert(primary_key, free_sectors[0])
                
                records_written += 1
                
                if records_written % 100 == 0:
                    self.progress_text.insert(tk.END, f"Procesados {records_written} registros...\n")
                    self.progress_text.see(tk.END)
            
            self.progress_text.insert(tk.END, f"\n¡Carga completada! {records_written} registros escritos al disco.\n")
            self.progress_text.insert(tk.END, f"Índice AVL creado con {records_written} entradas.\n")
            
        except Exception as e:
            self.progress_text.insert(tk.END, f"\nError: {str(e)}\n")
    
    def search_record(self):
        # Busca un registro por ID
        if not self.disk or not self.schema:
            messagebox.showerror("Error", "Debe tener un disco y esquema cargados")
            return
            
        search_id = self.search_id_var.get()
        if not search_id:
            messagebox.showerror("Error", "Ingrese un ID para buscar")
            return
            
        try:
            primary_key_type = next(f['type'] for f in self.schema['fields'] 
                                  if f['name'] == self.schema['primary_key'])
            
            if 'INTEGER' in primary_key_type:
                search_id = int(search_id)
            elif 'DECIMAL' in primary_key_type:
                search_id = float(search_id)
            
            node = self.avl_tree.search(search_id)
            if not node:
                self.search_results_text.delete(1.0, tk.END)
                self.search_results_text.insert(tk.END, f"No se encontró el registro con ID: {search_id}")
                return
            
            sector_address = node.sector_address
            
            data = self.sector_manager.read_data(sector_address)
            
            record = self.serializer.deserialize_record(data, self.schema)
            
            self.search_results_text.delete(1.0, tk.END)
            self.search_results_text.insert(tk.END, f"Registro encontrado:\n\n")
            self.search_results_text.insert(tk.END, f"ID: {search_id}\n")
            self.search_results_text.insert(tk.END, f"Ubicación física: Sector {sector_address}\n\n")
            
            physical_location = self.disk._get_physical_location(sector_address)
            self.search_results_text.insert(tk.END, f"Coordenadas físicas:\n")
            self.search_results_text.insert(tk.END, f"  Plato: {physical_location['platter']}\n")
            self.search_results_text.insert(tk.END, f"  Superficie: {physical_location['surface']}\n")
            self.search_results_text.insert(tk.END, f"  Pista: {physical_location['track']}\n")
            self.search_results_text.insert(tk.END, f"  Sector: {physical_location['sector']}\n\n")
            
            self.search_results_text.insert(tk.END, f"Datos del registro:\n")
            for field_name, value in record.items():
                self.search_results_text.insert(tk.END, f"  {field_name}: {value}\n")
                
        except ValueError as e:
            messagebox.showerror("Error", f"ID inválido: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Error en la búsqueda: {str(e)}")
    
    def update_disk_status(self):
        # Actualiza la información del estado del disco
        if not self.disk:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "No hay disco creado")
            return
            
        try:
            status = self.disk.get_disk_status()
            
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, "ESTADO DEL DISCO\n")
            self.status_text.insert(tk.END, "=" * 50 + "\n\n")
            
            self.status_text.insert(tk.END, f"Geometría:\n")
            self.status_text.insert(tk.END, f"  Platos: {status['platters']}\n")
            self.status_text.insert(tk.END, f"  Pistas por superficie: {status['tracks_per_surface']:,}\n")
            self.status_text.insert(tk.END, f"  Sectores por pista: {status['sectors_per_track']}\n")
            self.status_text.insert(tk.END, f"  Superficies por plato: {status['surfaces_per_platter']}\n\n")
            
            self.status_text.insert(tk.END, f"Capacidad:\n")
            self.status_text.insert(tk.END, f"  Tamaño de sector: {status['sector_size']} bytes\n")
            self.status_text.insert(tk.END, f"  Sectores totales: {status['total_sectors']:,}\n")
            self.status_text.insert(tk.END, f"  Capacidad total: {status['total_capacity'] / (1024*1024):.2f} MB\n\n")
            
            self.status_text.insert(tk.END, f"Uso:\n")
            self.status_text.insert(tk.END, f"  Sectores usados: {status['used_sectors']:,}\n")
            self.status_text.insert(tk.END, f"  Sectores libres: {status['free_sectors']:,}\n")
            self.status_text.insert(tk.END, f"  Espacio usado: {status['used_space'] / (1024*1024):.2f} MB\n")
            self.status_text.insert(tk.END, f"  Espacio libre: {status['free_space'] / (1024*1024):.2f} MB\n")
            
            if self.schema:
                self.status_text.insert(tk.END, f"\nEsquema cargado:\n")
                self.status_text.insert(tk.END, f"  Tabla: {self.schema['table_name']}\n")
                self.status_text.insert(tk.END, f"  Tamaño de registro: {self.schema['record_size']} bytes\n")
                
        except Exception as e:
            self.status_text.delete(1.0, tk.END)
            self.status_text.insert(tk.END, f"Error al obtener estado: {str(e)}")
    
    def run(self):
        # Ejecuta la interfaz de usuario
        self.root.mainloop()

if __name__ == "__main__":
    app = DiskSimulatorInterface()
    app.run() 