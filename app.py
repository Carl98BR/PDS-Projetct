from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO
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

@app.route('/dados', methods=['POST'])
def receber_dados_esp():
    dados_recebidos = request.get_json()
    if not dados_recebidos:
        return jsonify({"status": "erro"}), 400
    
    volume = dados_recebidos.get('volume')
    if volume is not None:
        ponto_de_dado = {
            "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
            "valor": volume
        }
        dados_armazenados.append(ponto_de_dado)
        
        # A MÁGICA ACONTECE AQUI:
        # Emite o novo ponto de dado para todos os navegadores conectados.
        socketio.emit('new_data', ponto_de_dado)
        
    return jsonify({"status": "sucesso"}), 201

@socketio.on('connect')
def handle_connect():
    # Quando um novo navegador se conecta, envia o histórico de dados
    # apenas para ele.
    socketio.emit('initial_data', list(dados_armazenados))

if __name__ == '__main__':
    socketio.run(app)