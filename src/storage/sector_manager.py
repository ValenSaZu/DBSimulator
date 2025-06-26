from typing import List, Optional, Tuple
from .disk import Disk
import struct

FRAGMENT_HEADER_SIZE = 6  # 2 bytes tamaño, 2 bytes sector, 2 bytes offset
FRAGMENT_END = 0xFFFF

class SectorManager:
    # Administra la asignación y liberación de sectores con soporte para fragmentación de registros
    
    def __init__(self, disk: Disk):
        self.disk = disk

    def _pack_pointer(self, sector: int, offset: int) -> bytes:
        return struct.pack('<IH', sector, offset)

    def _unpack_pointer(self, data: bytes) -> Tuple[int, int]:
        sector, offset = struct.unpack('<IH', data)
        return sector, offset

    def _pack_fragment_header(self, fragment_size: int, next_sector: int, next_offset: int) -> bytes:
        return struct.pack('<H H H', fragment_size, next_sector, next_offset)

    def _unpack_fragment_header(self, data: bytes) -> Tuple[int, int, int]:
        fragment_size, next_sector, next_offset = struct.unpack('<H H H', data)
        return fragment_size, next_sector, next_offset

    def find_free_space_for_record(self, record_size: int) -> Optional[Tuple[int, int, int]]:
        # Busca el primer sector y offset donde quepa el registro completo.
        # Si el registro es más grande que un sector, retorna el primer sector y offset con espacio disponible.
        # Returns (sector, offset, espacio_restante)
        for sector in range(self.disk.total_sectors):
            with open(self.disk.filename, 'rb') as f:
                f.seek(sector * self.disk.sector_size)
                data = f.read(self.disk.sector_size)
            offset = 0
            while offset + FRAGMENT_HEADER_SIZE <= self.disk.sector_size:
                header = data[offset:offset+FRAGMENT_HEADER_SIZE]
                if all(b == 0 for b in header):
                    break
                fragment_size = int.from_bytes(header[:2], 'little')
                offset += FRAGMENT_HEADER_SIZE + fragment_size
            espacio_restante = self.disk.sector_size - offset
            if espacio_restante >= FRAGMENT_HEADER_SIZE + record_size:
                return (sector, offset, espacio_restante)
            elif espacio_restante > FRAGMENT_HEADER_SIZE:
                return (sector, offset, espacio_restante)
        return None

    def write_record(self, data: bytes) -> Tuple[int, int]:
        # Escribe un registro secuencialmente en sectores, llenando un sector antes de pasar al siguiente.
        total_size = len(data)
        bytes_written = 0
        first_sector = None
        first_offset = None
        prev_sector = None
        prev_offset = None
        while bytes_written < total_size:
            pos = self.find_free_space_for_record(total_size - bytes_written)
            if pos is None:
                raise Exception("No hay suficiente espacio en el disco para el registro")
            sector, offset, espacio_restante = pos
            max_fragment_size = espacio_restante - FRAGMENT_HEADER_SIZE
            fragment_size = min(total_size - bytes_written, max_fragment_size)
            if bytes_written + fragment_size < total_size:
                next_sector = 0
                next_offset = 0
            else:
                next_sector = FRAGMENT_END
                next_offset = FRAGMENT_END
            header = self._pack_fragment_header(fragment_size, next_sector, next_offset)
            fragment_data = data[bytes_written:bytes_written+fragment_size]
            with open(self.disk.filename, 'r+b') as f:
                f.seek(sector * self.disk.sector_size + offset)
                f.write(header)
                f.write(fragment_data)
            self.disk._save_sector_map()
            if first_sector is None:
                first_sector = sector
                first_offset = offset
            if prev_sector is not None:
                with open(self.disk.filename, 'r+b') as f:
                    f.seek(prev_sector * self.disk.sector_size + prev_offset + 2)
                    f.write(struct.pack('<H H', sector, offset))
            prev_sector = sector
            prev_offset = offset
            bytes_written += fragment_size
        return first_sector, first_offset

    def read_record(self, sector: int, offset: int) -> bytes:
        # Lee un registro fragmentado a partir de (sector, offset)
        result = b''
        while True:
            with open(self.disk.filename, 'rb') as f:
                f.seek(sector * self.disk.sector_size + offset)
                header = f.read(FRAGMENT_HEADER_SIZE)
                if len(header) < FRAGMENT_HEADER_SIZE:
                    break
                fragment_size, next_sector, next_offset = self._unpack_fragment_header(header)
                fragment_data = f.read(fragment_size)
                result += fragment_data
            if next_sector == FRAGMENT_END:
                break
            sector = next_sector
            offset = next_offset
        return result

    def free_sectors(self, sector: int, offset: int) -> bool:
        # Libera los sectores ocupados por un registro fragmentado
        try:
            while True:
                with open(self.disk.filename, 'r+b') as f:
                    f.seek(sector * self.disk.sector_size + offset)
                    header = f.read(FRAGMENT_HEADER_SIZE)
                    if len(header) < FRAGMENT_HEADER_SIZE:
                        break
                    fragment_size, next_sector, next_offset = self._unpack_fragment_header(header)
                    f.seek(sector * self.disk.sector_size + offset)
                    f.write(b'\x00' * (FRAGMENT_HEADER_SIZE + fragment_size))
                self.disk.sector_map[sector] = False
                if next_sector == FRAGMENT_END:
                    break
                sector = next_sector
                offset = next_offset
            self.disk._save_sector_map()
            return True
        except Exception as e:
            print(f"Error al liberar sectores: {e}")
            return False

    def get_sector_status(self, sector: int) -> bool:
        # Obtiene el estado de un sector
        if sector >= self.disk.total_sectors:
            raise ValueError(f"Sector {sector} fuera de rango")
        return self.disk.sector_map.get(sector, False)

    def get_contiguous_free_sectors(self, num_sectors: int) -> Optional[List[int]]:
        # Obtiene sectores libres contiguos
        return self.disk.find_free_sectors(num_sectors)