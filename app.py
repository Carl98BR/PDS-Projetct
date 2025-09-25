from flask import Flask, request, jsonify, render_template
from collections import deque
from datetime import datetime
import pytz
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

dados_armazenados = deque(maxlen=100)
fuso_horario_br = pytz.timezone('America/Fortaleza')

@app.route('/dados', methods=['POST'])
def receber_dados_esp():
    lista_de_dados = request.get_json()
    
    if not isinstance(lista_de_dados, list):
        return jsonify({"status": "erro", "mensagem": "esperava uma lista"}), 400

    for dados in lista_de_dados:
        volume = dados.get('volume')
        if volume is not None:
            ponto_de_dado = {
                "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
                "valor": volume
            }
            dados_armazenados.append(ponto_de_dado)
            socketio.emit('new_data', ponto_de_dado)
            
    return jsonify({"status": "sucesso"}), 201

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    socketio.emit('initial_data', list(dados_armazenados))

if __name__ == '__main__':
    socketio.run(app)