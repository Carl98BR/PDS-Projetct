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

# --- Eventos do SocketIO ---

@socketio.on('connect')
def handle_browser_connect():
    # Quando um NAVEGADOR se conecta, envia o histórico de dados
    print('Navegador conectado!')
    emit('initial_data', list(dados_armazenados))

@socketio.on('esp_data')
def handle_esp_data(data):
    # Quando o ESP32 envia dados pelo WebSocket...
    volume = data.get('volume')
    if volume is not None:
        ponto_de_dado = {
            "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
            "valor": volume
        }
        dados_armazenados.append(ponto_de_dado)
        
        # ...nós retransmitimos esses dados para TODOS os navegadores conectados
        # O evento que os navegadores ouvem é o 'new_data'
        emit('new_data', ponto_de_dado, broadcast=True)

if __name__ == '__main__':
    socketio.run(app)