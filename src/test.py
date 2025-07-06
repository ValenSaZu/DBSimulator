import sys
import os
import struct

# Agregar el directorio src al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_schema_parser():
    print("Probando SchemaParser")
    try:
        from data_management.schema_parser import SchemaParser
        parser = SchemaParser()

        test_sql = """
        CREATE TABLE PRODUCTO(
            index INTEGER(10) PRIMARY KEY,
            item VARCHAR(40) NOT NULL,
            cost DECIMAL(10, 2) NOT NULL,
            tax DECIMAL(10, 2) NOT NULL,
            total DECIMAL(10, 2) NOT NULL
        );
        """
        
        schema = parser.parse_create_table(test_sql)
        print(f"✓ Esquema parseado: {schema['table_name']}")
        print(f"  Clave primaria: {schema['primary_key']}")
        print(f"  Tamaño de registro: {schema['record_size']} bytes")
        return True
    except Exception as e:
        print(f"✗ Error en SchemaParser: {e}")
        return False

def test_disk():
    print("\nProbando creación de Disk")
    try:
        from storage.disk import Disk, DiskGeometry
        
        geometry = DiskGeometry(platters=2, tracks=100, sectors=63, sector_size=512)
        disk = Disk(geometry, "test_disk.bin")
        
        status = disk.get_disk_status()
        print(f"✓ Disco creado: {status['total_capacity']} BYTES")
        return True
    except Exception as e:
        print(f"✗ Error en Disk: {e}")
        return False

def test_avl():
    print("\nProbando AVL Tree")
    try:
        from indexing.avl_tree import AVL
        
        avl = AVL()
        avl.insert(5, 100)
        avl.insert(3, 200)
        avl.insert(7, 300)
        
        node = avl.search(5)
        if node and node.address == 100:
            print("✓ Árbol AVL funciona correctamente")
            return True
        else:
            print("✗ Error en búsqueda AVL")
            return False
    except Exception as e:
        print(f"✗ Error en AVL: {e}")
        return False

def test_serialization():
    print("\nProbando Serialización")
    try:
        from storage.serialization import RecordSerializer
        
        serializer = RecordSerializer()
        
        # Esquema de prueba
        schema = {
            'fields': [
                {'name': 'id', 'type': 'INTEGER', 'size': 4},
                {'name': 'name', 'type': 'VARCHAR', 'size': 20}
            ]
        }
        
        record = {'id': 1, 'name': 'Test'}
        serialized = serializer.serialize_record(record, schema)
        deserialized = serializer.deserialize_record(serialized, schema)
        
        if deserialized['id'] == 1 and deserialized['name'] == 'Test':
            print("✓ Serialización funciona correctamente")
            return True
        else:
            print("✗ Error en deserialización")
            return False
    except Exception as e:
        print(f"✗ Error en serializacióon: {e}")
        return False

def test_fragmented_write_read():
    print("\nProbando escritura y lectura fragmentada")
    try:
        from storage.disk import Disk, DiskGeometry
        from storage.sector_manager import SectorManager

        geometry = DiskGeometry(platters=1, tracks=1, sectors=4, sector_size=70)
        disk = Disk(geometry, "test_fragmented_disk.bin")
        manager = SectorManager(disk)

        data = b"ABCDEFGHIJ1234567890abcdefghij"  # 30 bytes
        print(f"Registro original: {data}")
        print(f"Tamaño del registro: {len(data)} bytes")

        sector, offset = manager.write_record(data)
        print(f"Primer fragmento en sector {sector}, offset {offset}")

        fragments = []
        current_sector, current_offset = sector, offset
        total_read = 0
        while True:
            with open(disk.filename, 'rb') as f:
                f.seek(current_sector * disk.sector_size + current_offset)
                header = f.read(6)
                if len(header) < 6:
                    break
                fragment_size, next_sector, next_offset = struct.unpack('<H H H', header)
                fragment_data = f.read(fragment_size)
                fragments.append((current_sector, current_offset, fragment_size, fragment_data))
                total_read += fragment_size
            print(f"  Fragmento en sector {current_sector}, offset {current_offset}, tamaño {fragment_size}, next=({next_sector},{next_offset})")
            if next_sector == 0xFFFF:
                break
            current_sector, current_offset = next_sector, next_offset
        print(f"Total leído en fragmentos: {total_read} bytes")

        read_data = manager.read_record(sector, offset)
        print(f"Registro leído: {read_data}")
        print(f"¿Coincide con el original? {'SI' if read_data == data else 'NO'}")
        return read_data == data
    except Exception as e:
        print(f"✗ Error en fragmentación: {e}")
        return False

def main():
    print("=== PRUEBAS DEL SIMULADOR DE DISCO ===\n")
    
    tests = [
        test_schema_parser,
        test_disk,
        test_avl,
        test_serialization,
        test_fragmented_write_read
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n=== RESULTADOS ===")
    print(f"Pruebas completadas con éxito: {passed}/{total}")
    
    if passed == total:
        print("✓ Todas las pruebas pasaron")
    else:
        print("✗ Algunas pruebas fallaron")

if __name__ == "__main__":
    main()