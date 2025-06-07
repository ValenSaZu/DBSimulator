# Simula la estructura física del disco (platos, pistas, sectores)

import os
from dataclasses import dataclass
from typing import Dict, List
import struct

@dataclass
class DiskGeometry:
    """Estructura que define la geometría del disco virtual"""
    platters: int      # Número de platos
    tracks: int        # Pistas por superficie
    sectors: int       # Sectores por pista
    sector_size: int   # Tamaño de sector en bytes
    
    @property
    def surfaces(self):
        """Siempre 2 superficies por plato"""
        return 2

class Disk:
    def __init__(self, geometry: DiskGeometry, filename: str = "data/virtual_disk.bin"):
        """
        Inicializa el disco virtual con la geometría especificada
        
        Args:
            geometry (DiskGeometry): Configuración de la geometría
            filename (str, optional): Ruta del archivo que simulará el almacenamiento físico. 
                                    Por defecto es "data/virtual_disk.bin"
        """
        self.geometry = geometry
        self.filename = filename
        self.sector_map = {}
        self.total_sectors = geometry.platters * 2 * geometry.tracks * geometry.sectors
        self.sector_size = geometry.sector_size
        self.total_capacity = self.total_sectors * self.sector_size
        
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        
        if not os.path.exists(self.filename):
            self._initialize_disk()
        else:
            self._load_sector_map()
    
    def _initialize_disk(self):
        """Crea un nuevo archivo de disco con todos los sectores inicializados a cero como libres"""
        with open(self.filename, 'wb') as f:
            f.write(b'\x00' * self.total_capacity)
        
        self.sector_map = {i: False for i in range(self.total_sectors)}
        self._save_sector_map()
    
    def _get_physical_location(self, sector_num: int) -> Dict[str, int]:
        """
        Convierte un número de sector lógico en coordenadas físicas (CHS - Cylinder-Head-Sector)

        Args:
            sector_num (int): Número de sector lógico a convertir (0-based)
        
        Returns:
            Dict[str, int]: Diccionario con las coordenadas físicas:
        """
        if sector_num >= self.total_sectors:
            raise ValueError("Número de sector fuera de rango")
        
        sectors_per_track = self.geometry.sectors
        tracks_per_surface = self.geometry.tracks
        
        sectors_remaining = sector_num
        
        platter = sectors_remaining // (2 * tracks_per_surface * sectors_per_track)
        sectors_remaining %= (2 * tracks_per_surface * sectors_per_track)
        
        surface = sectors_remaining // (tracks_per_surface * sectors_per_track)
        sectors_remaining %= (tracks_per_surface * sectors_per_track)
        
        track = sectors_remaining // sectors_per_track
        sector = sectors_remaining % sectors_per_track
        
        return {
            'platter': platter,
            'surface': surface,
            'track': track,
            'sector': sector
        }
    
    def find_free_sectors(self, num_sectors: int = 1) -> List[int]:
        """
        Encuentra sectores libres contiguos en el disco
        
        Args:
            num_sectors (int, optional): Número de sectores contiguos necesarios. 
                                        Por defecto es 1.
        
        Returns:
            List[int]: Lista con los números de sector iniciales de cada bloque encontrado,
                     o None si no hay suficiente espacio contiguo.
                     La lista contiene rangos consecutivos como [inicio, inicio+1, ..., inicio+n-1]
        """
        consecutive_free = 0
        start_sector = None
        
        for sector in range(self.total_sectors):
            if not self.sector_map.get(sector, False):
                if consecutive_free == 0:
                    start_sector = sector
                consecutive_free += 1
                
                if consecutive_free >= num_sectors:
                    return list(range(start_sector, start_sector + num_sectors))
            else:
                consecutive_free = 0
        
        return None
    
    def get_disk_status(self) -> Dict:
        """
        Devuelve estadísticas detalladas del disco
        
        Returns:
            Dict: Diccionario con las siguientes métricas:
                - total_sectors: Número total de sectores en el disco
                - used_sectors: Sectores actualmente en uso
                - free_sectors: Sectores libres
                - total_capacity: Capacidad total en bytes
                - used_space: Espacio usado en bytes
                - free_space: Espacio libre en bytes
                - sector_size: Tamaño de cada sector en bytes
                - platters: Número de platos físicos
                - tracks_per_surface: Pistas por superficie
                - sectors_per_track: Sectores por pista
                - surfaces_per_platter: Superficies por plato (siempre 2)
        """
        used_sectors = sum(1 for occupied in self.sector_map.values() if occupied)
        free_sectors = self.total_sectors - used_sectors
        
        return {
            'total_sectors': self.total_sectors,
            'used_sectors': used_sectors,
            'free_sectors': free_sectors,
            'total_capacity': self.total_capacity,
            'used_space': used_sectors * self.sector_size,
            'free_space': free_sectors * self.sector_size,
            'sector_size': self.sector_size,
            'platters': self.geometry.platters,
            'tracks_per_surface': self.geometry.tracks,
            'sectors_per_track': self.geometry.sectors,
            'surfaces_per_platter': 2
        }