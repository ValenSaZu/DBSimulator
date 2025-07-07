# DBSimulator

Python Version 3.13.3 : https://www.python.org/downloads/

Sistema de almacenamiento con indexación AVL para Bases de Datos II

## Descripción

DBSimulator es un simulador de disco que permite:
- Configurar parámetros del disco (platos, pistas, sectores, bytes por sector)
- Cargar esquemas SQL desde archivos .txt
- Validar y cargar datos desde archivos CSV
- Almacenar registros en formato binario de longitud fija
- Indexar registros usando árboles AVL
- Realizar búsquedas por ID con información de ubicación física

## Instalación

```bash
git clone https://github.com/ValenSaZu/DBSimulator.git
cd DBSimulator
```

## Uso

### Ejecutar el simulador

```bash
cd src
python main.py
```

### Flujo de trabajo

1. **Configurar el Disco**: 
   - Ingresa el número de platos, pistas, sectores y bytes por sector
   - Haz clic en "Crear Disco"

2. **Cargar Esquema SQL**:
   - Haz clic en "Buscar" y selecciona un archivo .txt con CREATE TABLE
   - Haz clic en "Cargar Esquema"
   - El sistema parseará la estructura y calculará el tamaño de los registros

3. **Cargar Datos CSV**:
   - Haz clic en "Buscar" y selecciona un archivo CSV con los datos
   - Haz clic en "Validar y Cargar Datos"
   - El sistema validará la estructura y tipos de datos
   - Los registros se escribirán al disco y se indexarán en el árbol AVL

4. **Realizar Búsquedas**:
   - Ingresa un ID en el campo de búsqueda
   - Haz clic en "Buscar"
   - El sistema mostrará la ubicación física y los datos del registro

### Formato de archivos

#### Esquema SQL (.txt)
```sql
CREATE TABLE PRODUCTO(
    index INTEGER(10) PRIMARY KEY,
    item VARCHAR(40) NOT NULL,
    cost DECIMAL(10, 2) NOT NULL,
    tax DECIMAL(10, 2) NOT NULL,
    total DECIMAL(10, 2) NOT NULL
);
```

#### Datos CSV
```csv
"Index", "Item", "Cost", "Tax", "Total"
1, "Fruit of the Loom Girl's Socks", 7.97, 0.60, 8.57
2, "Rawlings Little League Baseball", 2.97, 0.22, 3.19
```

## Características

- **Simulación de disco físico**: Platos, pistas, sectores
- **Serialización binaria**: Registros de longitud fija
- **Indexación AVL**: Búsquedas eficientes por los atributos de la tabla
- **Validación de datos**: Verificación de tipos y restricciones
- **Interfaz gráfica**: Fácil de usar con tkinter
- **Persistencia**: Los datos se guardan en archivos binarios

## Estructura del proyecto

```
DBSimulator/
├── data/                  # Archivos de datos de ejemplo
│   ├── a.csv             # Datos CSV de ejemplo
│   └── struct_table.txt  # Esquema SQL de ejemplo
├── src/
│   ├── data_management/  # Gestión de datos
│   │   ├── csv_loader.py
│   │   ├── data_validator.py
│   │   └── schema_parser.py
│   ├── indexing/         # Indexación
│   │   ├── avl_tree.py
│   │   └── location_mapper.py
│   ├── interface/        # Interfaz de usuario
│   │   └── user_interface.py
│   ├── storage/          # Almacenamiento
│   │   ├── disk.py
│   │   ├── sector_manager.py
│   │   └── serialization.py
│   └── main.py           # Punto de entrada
└── README.md
```

## Requisitos

- Python 3.13.3 o superior
- tkinter (incluido con Python)
- Módulos estándar: os, sys, csv, re, struct, pickle, threading

## Autor

Valentina Salazar, Gino Diaz y Diego Astorga - Base de Datos II
