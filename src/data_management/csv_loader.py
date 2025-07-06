# Carga y valida datos desde archivos CSV contra el esquema definido

import csv
import re
from typing import List, Dict, Any

class CSVLoader:
    #Carga y valida datos desde archivos CSV comparando con el esquema definido
    
    def __init__(self):
        pass
    
    def load_csv(self, file_path: str) -> List[Dict[str, Any]]:
        # Carga datos desde un archivo CSV
        data = []
        
        with open(file_path, 'r', encoding='utf-8') as f:
            # Detectar delimitador
            sample = f.read(1024)
            f.seek(0)
            
            delimiter = self._detect_delimiter(sample)
            
            reader = csv.DictReader(f, delimiter=delimiter)
            
            for row in reader:
                # Limpiar espacios en blanco de claves y valores
                cleaned_row = {}
                for key, value in row.items():
                    cleaned_key = (key or '').strip().strip('"').strip("'").lower()  # <-- minúsculas
                    if value is None:
                        cleaned_value = ''
                    else:
                        cleaned_value = value.strip().strip('"').strip("'")
                    cleaned_row[cleaned_key] = cleaned_value
                
                data.append(cleaned_row)
        
        return data
    
    def _detect_delimiter(self, sample: str) -> str:
        #Detecta como se separan los datos en el CSV
        delimiters = [',', ';', '\t', '|']
        counts = {}
        
        for delimiter in delimiters:
            counts[delimiter] = sample.count(delimiter)
        
        return max(counts.items(), key=lambda x: x[1])[0]
    
    def validate_csv_structure(self, data: List[Dict[str, Any]], schema: Dict[str, Any]) -> bool:
        # Valida que la estructura del CSV coincida con el esquema
        if not data:
            return False
        
        expected_fields = {field['name'] for field in schema['fields']}
        
        csv_fields = set(data[0].keys())
        
        missing_fields = expected_fields - csv_fields
        if missing_fields:
            raise ValueError(f"Campos faltantes en CSV: {missing_fields}")
        
        extra_fields = csv_fields - expected_fields
        if extra_fields:
            print(f"Advertencia: Campos extra en CSV (serán ignorados): {extra_fields}")
        
        return True
    
    def load_and_validate_csv(self, file_path: str, schema: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Carga y valida el CSV comparando con el esquema
        data = self.load_csv(file_path)
        
        self.validate_csv_structure(data, schema)
        
        from .data_validator import DataValidator
        validator = DataValidator()
        validated_data = []
        for i, record in enumerate(data, 1):
            try:
                validated_record = validator.validate_record(record, schema)
                validated_data.append(validated_record)
            except Exception as e:
                print(f"Error en registro {i}: {e}")
                continue
        
        return validated_data