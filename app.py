from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from collections import deque
from datetime import datetime
import pytz
from queue import Queue
import time

app = Flask(__name__)
# Permitimos o fallback para "polling", o que aumenta a compatibilidade
socketio = SocketIO(app, async_mode='gevent') 

# Fila segura para comunicação entre threads
data_queue = Queue()

dados_armazenados = deque(maxlen=100)
fuso_horario_br = pytz.timezone('America/Fortaleza')

def background_thread_emitter():
    """Este é o nosso 'assistente'. Ele fica rodando em segundo plano."""
    print("Thread de emissão iniciada.")
    while True:
        # Pega um item da fila (se não tiver, espera)
        ponto_de_dado = data_queue.get()
        if ponto_de_dado:
            # Envia o dado para todos os navegadores
            socketio.emit('new_data', ponto_de_dado, broadcast=True)
            print(f"--> Emitido para o navegador: {ponto_de_dado['valor']}")
        # Uma pequena pausa para não sobrecarregar a CPU
        socketio.sleep(0.01)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_browser_connect():
    print('Navegador conectado!')
    emit('initial_data', list(dados_armazenados))

@socketio.on('esp_data')
def handle_esp_data(data):
    """Este é o 'atendente'. Ele só recebe e põe na fila."""
    volume = data.get('volume')
    if volume is not None:
        ponto_de_dado = {
            "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
            "valor": volume
        }
        dados_armazenados.append(ponto_de_dado)
        # Coloca o dado na fila para o 'assistente' pegar
        data_queue.put(ponto_de_dado)
        print(f"<-- Recebido do ESP: {ponto_de_dado['valor']}")

# Inicia a thread de segundo plano uma única vez quando o servidor liga
socketio.start_background_task(target=background_thread_emitter)