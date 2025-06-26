import re
from typing import Dict, Any, Union

class DataValidator:
    # Reglas de validación para tipos de datos y restricciones
    
    def __init__(self):
        # Patrones de validación para diferentes tipos
        self.patterns = {
            'INTEGER': r'^-?\d+$',
            'INT': r'^-?\d+$',
            'BIGINT': r'^-?\d+$',
            'SMALLINT': r'^-?\d+$',
            'TINYINT': r'^-?\d+$',
            'DECIMAL': r'^-?\d+(\.\d+)?$',
            'FLOAT': r'^-?\d+(\.\d+)?$',
            'DOUBLE': r'^-?\d+(\.\d+)?$',
            'CHAR': r'^.*$',
            'VARCHAR': r'^.*$',
            'TEXT': r'^.*$',
            'DATE': r'^\d{4}-\d{2}-\d{2}$',
            'DATETIME': r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
            'BOOLEAN': r'^(true|false|1|0|yes|no)$',
            'BOOL': r'^(true|false|1|0|yes|no)$'
        }
    
    def validate_data(self, data: list, schema: Dict[str, Any]) -> list:
        # Valida una lista de registros contra el tipo de dato en el esquema
        validated_data = []
        
        for i, record in enumerate(data, 1):
            try:
                validated_record = self.validate_record(record, schema)
                validated_data.append(validated_record)
            except Exception as e:
                print(f"Error en registro {i}: {e}")
                continue
        
        return validated_data
    
    def validate_record(self, record: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        # Valida un registro individual contra el tipo de dato en el esquema
        validated_record = {}
        
        for field in schema['fields']:
            field_name = field['name']
            field_type = field['type']
            field_size = field['size']
            is_nullable = field['nullable']
            
            value = record.get(field_name, None)
            
            if value is None or value == "":
                if not is_nullable:
                    raise ValueError(f"Campo '{field_name}' no puede ser NULL")
                validated_record[field_name] = None
                continue
            
            validated_value = self._validate_and_convert_value(value, field_type, field_size)
            validated_record[field_name] = validated_value
        
        return validated_record
    
    def _validate_and_convert_value(self, value: str, field_type: str, field_size: int) -> Any:
        # Valida y convierte un valor según el tipo de campo
        value = str(value).strip()
        
        pattern = self.patterns.get(field_type, r'^.*$')
        if not re.match(pattern, value, re.IGNORECASE):
            raise ValueError(f"Valor '{value}' no coincide con el patrón para tipo '{field_type}'")
        
        if field_type in ('INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT'):
            return self._convert_integer(value, field_type)
        elif field_type in ('DECIMAL', 'FLOAT', 'DOUBLE'):
            return self._convert_decimal(value, field_type)
        elif field_type in ('CHAR', 'VARCHAR', 'TEXT'):
            return self._convert_string(value, field_size)
        elif field_type in ('DATE', 'DATETIME'):
            return self._convert_datetime(value, field_type)
        elif field_type in ('BOOLEAN', 'BOOL'):
            return self._convert_boolean(value)
        else:
            return value
    
    def _convert_integer(self, value: str, field_type: str) -> int:
        # Convierte un valor a entero
        try:
            int_value = int(value)
            
            if field_type == 'TINYINT' and not (-128 <= int_value <= 127):
                raise ValueError(f"Valor fuera de rango para TINYINT: {int_value}")
            elif field_type == 'SMALLINT' and not (-32768 <= int_value <= 32767):
                raise ValueError(f"Valor fuera de rango para SMALLINT: {int_value}")
            elif field_type == 'INTEGER' and not (-2147483648 <= int_value <= 2147483647):
                raise ValueError(f"Valor fuera de rango para INTEGER: {int_value}")
            
            return int_value
        except ValueError as e:
            raise ValueError(f"No se pudo convertir '{value}' a entero: {e}")
    
    def _convert_decimal(self, value: str, field_type: str) -> float:
        # Convierte un valor a decimal
        try:
            return float(value)
        except ValueError as e:
            raise ValueError(f"No se pudo convertir '{value}' a decimal: {e}")
    
    def _convert_string(self, value: str, field_size: int) -> str:
        # Convierte un valor a string y valida longitud
        if len(value) > field_size:
            value = value[:field_size]
        
        return value
    
    def _convert_datetime(self, value: str, field_type: str) -> str:
        # Convierte un valor a datetime (mantiene como string)
        return value
    
    def _convert_boolean(self, value: str) -> bool:
        # Convierte un valor a booleano
        value_lower = value.lower()
        if value_lower in ('true', '1', 'yes'):
            return True
        elif value_lower in ('false', '0', 'no'):
            return False
        else:
            raise ValueError(f"No se pudo convertir '{value}' a booleano")