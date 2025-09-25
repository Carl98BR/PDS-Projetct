from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
from collections import deque
from datetime import datetime
import pytz

app = Flask(__name__)
socketio = SocketIO(app)

dados_armazenados = deque(maxlen=100)
fuso_horario_br = pytz.timezone('America/Fortaleza')

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_browser_connect():
    print('Navegador conectado!')
    emit('initial_data', list(dados_armazenados))

@socketio.on('esp_data')
def handle_esp_data(data):
    volume = data.get('volume')
    if volume is not None:
        ponto_de_dado = {
            "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
            "valor": volume
        }
        dados_armazenados.append(ponto_de_dado)
        
        # LINHA TEMPORARIAMENTE DESATIVADA PARA TESTE:
        # socketio.emit('new_data', ponto_de_dado, broadcast=True)

        # Adicionamos um print para ver os dados chegando nos logs do Render
        print(f"Dado recebido do ESP: {ponto_de_dado}")
            
# Removido o return do http post, pois não é mais usado
# E a função __main__ também não é necessária no gunicorn