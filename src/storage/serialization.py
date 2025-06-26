# Convierte registros a formato binario de longitud fija y viceversa

import struct
from typing import Dict, Any, List, Optional

class RecordSerializer:
    # Convierte registros a formato binario de longitud fija y viceversa
    
    def __init__(self):
        self.type_formats = {
            'INTEGER': 'i',
            'INT': 'i',
            'BIGINT': 'q',
            'SMALLINT': 'h',
            'TINYINT': 'b',
            'DECIMAL': 'd',
            'FLOAT': 'f',
            'DOUBLE': 'd',
            'CHAR': 's',
            'VARCHAR': 's',
            'TEXT': 's',
            'DATE': 's',
            'DATETIME': 's',
            'BOOLEAN': '?',
            'BOOL': '?'
        }
    
    def serialize_record(self, record: Dict[str, Any], schema: Dict[str, Any]) -> bytes:
        # Serializa un registro a formato binario de longitud fija
        serialized_parts = []
        
        for field in schema['fields']:
            field_name = field['name']
            field_type = field['type']
            field_size = field['size']
            
            value = record.get(field_name)
            
            if value is None:
                serialized_parts.append(b'\x00' * field_size)
            else:
                serialized_part = self._serialize_field(value, field_type, field_size)
                serialized_parts.append(serialized_part)
        
        return b''.join(serialized_parts)
    
    def _serialize_field(self, value: Any, field_type: str, field_size: int) -> bytes:
        # Serializa un campo individual
        if field_type in ('INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT'):
            return self._serialize_integer(value, field_type)
        elif field_type in ('DECIMAL', 'FLOAT', 'DOUBLE'):
            return self._serialize_decimal(value, field_type)
        elif field_type in ('CHAR', 'VARCHAR', 'TEXT'):
            return self._serialize_string(value, field_size)
        elif field_type in ('DATE', 'DATETIME'):
            return self._serialize_datetime(value, field_size)
        elif field_type in ('BOOLEAN', 'BOOL'):
            return self._serialize_boolean(value)
        else:
            return self._serialize_string(str(value), field_size)
    
    def _serialize_integer(self, value: int, field_type: str) -> bytes:
        # Serializa un entero
        format_char = self.type_formats.get(field_type, 'i')
        return struct.pack(f'<{format_char}', value)
    
    def _serialize_decimal(self, value: float, field_type: str) -> bytes:
        # Serializa un decimal
        format_char = self.type_formats.get(field_type, 'd')
        return struct.pack(f'<{format_char}', value)
    
    def _serialize_string(self, value: str, field_size: int) -> bytes:
        # Serializa un string
        value_bytes = value.encode('utf-8')
        
        if len(value_bytes) > field_size:
            value_bytes = value_bytes[:field_size]
        elif len(value_bytes) < field_size:
            value_bytes = value_bytes.ljust(field_size, b' ')
        
        return value_bytes
    
    def _serialize_datetime(self, value: str, field_size: int) -> bytes:
        # Serializa un datetime (trata como string)
        return self._serialize_string(value, field_size)
    
    def _serialize_boolean(self, value: bool) -> bytes:
        # Serializa un booleano
        return struct.pack('<?', value)
    
    def deserialize_record(self, data: bytes, schema: Dict[str, Any]) -> Dict[str, Any]:
        # Deserializa un registro desde formato binario
        record = {}
        offset = 0
        
        for field in schema['fields']:
            field_name = field['name']
            field_type = field['type']
            field_size = field['size']
            
            field_data = data[offset:offset + field_size]
            offset += field_size
            
            value = self._deserialize_field(field_data, field_type, field_size)
            record[field_name] = value
        
        return record
    
    def _deserialize_field(self, data: bytes, field_type: str, field_size: int) -> Any:
        # Deserializa un campo individual
        if field_type in ('INTEGER', 'INT', 'BIGINT', 'SMALLINT', 'TINYINT'):
            return self._deserialize_integer(data, field_type)
        elif field_type in ('DECIMAL', 'FLOAT', 'DOUBLE'):
            return self._deserialize_decimal(data, field_type)
        elif field_type in ('CHAR', 'VARCHAR', 'TEXT'):
            return self._deserialize_string(data, field_size)
        elif field_type in ('DATE', 'DATETIME'):
            return self._deserialize_datetime(data, field_size)
        elif field_type in ('BOOLEAN', 'BOOL'):
            return self._deserialize_boolean(data)
        else:
            return self._deserialize_string(data, field_size)
    
    def _deserialize_integer(self, data: bytes, field_type: str) -> int:
        # Deserializa un entero
        format_char = self.type_formats.get(field_type, 'i')
        return struct.unpack(f'<{format_char}', data)[0]
    
    def _deserialize_decimal(self, data: bytes, field_type: str) -> float:
        # Deserializa un decimal
        format_char = self.type_formats.get(field_type, 'd')
        return struct.unpack(f'<{format_char}', data)[0]
    
    def _deserialize_string(self, data: bytes, field_size: int) -> Optional[str]:
        # Deserializa un string
        if all(b == 0 for b in data):
            return None
        
        value = data.decode('utf-8').rstrip()
        return value
    
    def _deserialize_datetime(self, data: bytes, field_size: int) -> Optional[str]:
        # Deserializa un datetime (trata como string)
        return self._deserialize_string(data, field_size)
    
    def _deserialize_boolean(self, data: bytes) -> bool:
        # Deserializa un booleano
        return struct.unpack('<?', data)[0]