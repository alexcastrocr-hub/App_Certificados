"""
app.py - Punto de entrada de la aplicación Flask.
Expone la variable app para el servidor local y despliegues en Vercel.
"""
import os
import secrets
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask
from controllers.tablero import tablero_bp
from controllers.certificados import certificados_bp
from controllers.cargas import cargas_bp

# Carpeta raíz del proyecto (donde está este archivo).
# Sirve de ancla para rutas absolutas a insumos/ sin depender del cwd.
BASE_DIR = Path(__file__).resolve().parent

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, template_folder="views")

# Clave secreta obtenida de forma segura desde el entorno o generada dinámicamente
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY") or secrets.token_hex(32)

# Registrar controladores
app.register_blueprint(tablero_bp)
app.register_blueprint(certificados_bp)
app.register_blueprint(cargas_bp)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
