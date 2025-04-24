from flask import Flask, request, render_template, redirect, url_for
import os
import json
from datetime import datetime

app = Flask(__name__)
UPLOAD_FOLDER = 'static/videos_teamwork'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {'mp4', 'mov', 'avi', 'webm'}

RESULTS_FILE = "teamwork_results.json"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Simulated AI evaluation function (we'll later hook with GPT or another LLM)
def evaluar_teamwork(transcripcion):
    score = 85  # simulate logic
    justificacion = "Se observó una comunicación fluida, respeto mutuo y toma de decisiones compartida."
    return score, justificacion

def guardar_resultado(datos):
    resultados = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            resultados = json.load(f)

    # Normaliza el path del video para evitar errores de Windows
    datos["video"] = datos["video"].replace("\\", "/")
    
    resultados.append(datos)
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(resultados, f, indent=2, ensure_ascii=False)

@app.route('/limpiar_todo', methods=['POST'])
def limpiar_todo():
    # Limpia el archivo JSON
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

    # Borra videos de prueba
    for archivo in os.listdir(UPLOAD_FOLDER):
        if archivo.endswith(('.mp4', '.mov', '.avi', '.webm')):
            os.remove(os.path.join(UPLOAD_FOLDER, archivo))

    return "Sistema limpiado correctamente"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/teamwork_awards')
def teamwork_awards():
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            resultados = json.load(f)
    else:
        resultados = []
    return render_template("teamwork_awards.html", resultados=resultados)

@app.route('/evaluar', methods=['POST'])
def evaluar():
    nombre1 = request.form.get('nombre1')
    nombre2 = request.form.get('nombre2')
    archivo = request.files.get('video')

    if not archivo or not allowed_file(archivo.filename):
        return "Formato de video inválido", 400

    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    filename = f"{timestamp}_{archivo.filename}"
    ruta_video = os.path.join(UPLOAD_FOLDER, filename)
    archivo.save(ruta_video)

    transcripcion_simulada = f"Simulando la transcripción de {filename}..."
    puntuacion, justificacion = evaluar_teamwork(transcripcion_simulada)

    guardar_resultado({
        "nombre1": nombre1,
        "nombre2": nombre2,
        "video": ruta_video,
        "puntuacion": puntuacion,
        "justificacion": justificacion
    })

    return render_template('resultado.html',
                           nombre1=nombre1,
                           nombre2=nombre2,
                           video=ruta_video,
                           puntuacion=puntuacion,
                           justificacion=justificacion)

if __name__ == '__main__':
    app.run(debug=True)
