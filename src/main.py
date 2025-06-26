import sys
import os

# Agregar el directorio src al path para importar módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from interface.user_interface import DiskSimulatorInterface

def main():
    print("Iniciando Simulador de Disco...")
    print("Sistema de almacenamiento con indexación AVL para Bases de Datos II")
    print("=" * 60)
    
    try:
        app = DiskSimulatorInterface()
        app.run()
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
