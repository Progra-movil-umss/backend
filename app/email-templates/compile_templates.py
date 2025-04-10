import os
import subprocess
from pathlib import Path

def compile_mjml_templates():
    """
    Compila los archivos MJML a HTML.
    """
    # Obtener la ruta base del directorio de templates
    base_dir = Path(__file__).parent
    src_dir = base_dir / "src"
    build_dir = base_dir / "build"
    
    # Asegurarse de que el directorio build existe
    build_dir.mkdir(exist_ok=True)
    
    # Obtener la ruta al ejecutable de MJML
    mjml_path = os.path.join(os.path.expanduser("~"), "AppData", "Roaming", "npm", "mjml.cmd")
    
    # Compilar cada archivo MJML
    for mjml_file in src_dir.glob("*.mjml"):
        html_file = build_dir / f"{mjml_file.stem}.html"
        try:
            # Ejecutar el comando mjml
            subprocess.run([
                mjml_path,
                str(mjml_file),
                "-o",
                str(html_file)
            ], check=True)
            print(f"✅ Compilado: {mjml_file.name} -> {html_file.name}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error al compilar {mjml_file.name}: {str(e)}")
        except Exception as e:
            print(f"❌ Error inesperado al compilar {mjml_file.name}: {str(e)}")

if __name__ == "__main__":
    compile_mjml_templates() 