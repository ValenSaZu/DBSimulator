# Interpreta archivos .txt tipo CREATE TABLE y genera esquemas de tablas

import re
from typing import Dict, List, Any, Optional

class SchemaParser:
    """Parser para interpretar archivos CREATE TABLE y generar esquemas de tablas"""
    
    def __init__(self):
        # Mapeo de tipos SQL a tamaños en bytes
        self.type_sizes = {
            'INTEGER': 4,
            'INT': 4,
            'BIGINT': 8,
            'SMALLINT': 2,
            'TINYINT': 1,
            'DECIMAL': 8,
            'FLOAT': 4,
            'DOUBLE': 8,
            'CHAR': 1,
            'VARCHAR': 1,
            'TEXT': 255,
            'DATE': 8,
            'DATETIME': 8,
            'BOOLEAN': 1,
            'BOOL': 1
        }
    
    def parse_schema_file(self, file_path: str) -> Dict[str, Any]:
        # Parsea un archivo de texto con CREATE TABLE y retorna el esquema
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_create_table(content)
    
    def parse_create_table(self, sql_content: str) -> Dict[str, Any]:
        # Parsea el contenido SQL de CREATE TABLE
        sql = self._normalize_sql(sql_content)
        
        table_match = re.search(r'CREATE\s+TABLE\s+(\w+)', sql, re.IGNORECASE)
        if not table_match:
            raise ValueError("No se pudo encontrar el nombre de la tabla")
        
        table_name = table_match.group(1)
        
        columns_match = re.search(r'\((.*)\)', sql, re.DOTALL | re.IGNORECASE)
        if not columns_match:
            raise ValueError("No se pudo encontrar la definición de columnas")
        
        columns_def = columns_match.group(1)
        
        fields = self._parse_columns(columns_def)
        
        primary_key = self._find_primary_key(columns_def, fields)
        
        record_size = self._calculate_record_size(fields)
        
        return {
            'table_name': table_name,
            'primary_key': primary_key,
            'fields': fields,
            'record_size': record_size
        }
    
    def _normalize_sql(self, sql: str) -> str:
        # Normaliza el SQL removiendo comentarios y espacios extra
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        
        sql = re.sub(r'\s+', ' ', sql)
        sql = sql.strip()
        
        return sql
    
    def _parse_columns(self, columns_def: str) -> List[Dict[str, Any]]:
        # Parsea la definición de columnas
        fields = []
        
        column_defs = self._split_column_definitions(columns_def)
        
        for col_def in column_defs:
            col_def = col_def.strip()
            # No omitir columnas con PRIMARY KEY
            if not col_def or col_def.upper().startswith(('PRIMARY', 'KEY', 'FOREIGN', 'UNIQUE', 'INDEX')):
                if col_def.upper().startswith('PRIMARY'):
                    continue
            
            field = self._parse_column_definition(col_def)
            if field:
                fields.append(field)
        
        return fields
    
    def _split_column_definitions(self, columns_def: str) -> List[str]:
        # Divide las definiciones de columnas respetando paréntesis
        result = []
        current = ""
        paren_count = 0
        
        for char in columns_def:
            if char == '(':
                paren_count += 1
            elif char == ')':
                paren_count -= 1
            elif char == ',' and paren_count == 0:
                result.append(current.strip())
                current = ""
                continue
            
            current += char
        
        if current.strip():
            result.append(current.strip())
        
        return result
    
    def _parse_column_definition(self, col_def: str) -> Optional[Dict[str, Any]]:
        # Parsea una definición de columna individual
        # Patrón para extraer nombre, tipo y restricciones
        pattern = r'(\w+)\s+(\w+)(?:\(([^)]+)\))?\s*(.*)'
        match = re.match(pattern, col_def, re.IGNORECASE)
        
        if not match:
            return None
        
        name = match.group(1)
        data_type = match.group(2).upper()
        size_str = match.group(3)
        constraints = match.group(4).upper()
        
        # Determinar tamaño
        size = self._get_field_size(data_type, size_str)
        
        # Determinar si es nullable
        is_nullable = 'NOT NULL' not in constraints
        
        return {
            'name': name,
            'type': data_type,
            'size': size,
            'nullable': is_nullable,
            'constraints': constraints
        }
    
    def _get_field_size(self, data_type: str, size_str: str) -> int:
        # Determina el tamaño en bytes de un campo
        base_size = self.type_sizes.get(data_type, 1)
        
        if size_str and data_type in ('CHAR', 'VARCHAR'):
            try:
                return int(size_str) * base_size
            except ValueError:
                return base_size
        
        return base_size
    
    def _find_primary_key(self, columns_def: str, fields: List[Dict]) -> str:
        # Encuentra la clave primaria en la definición
        pk_match = re.search(r'PRIMARY\s+KEY\s*\(([^)]+)\)', columns_def, re.IGNORECASE)
        if pk_match:
            pk_field = pk_match.group(1).strip()
            return pk_field
        
        for field in fields:
            if 'PRIMARY KEY' in field['constraints']:
                return field['name']
        
        if fields:
            return fields[0]['name']
        
        raise ValueError("No se pudo determinar la clave primaria")
    
    def _calculate_record_size(self, fields: List[Dict]) -> int:
        # Calcula el tamaño total del registro
        total_size = 0
        
        for field in fields:
            total_size += field['size']
        
        return total_size