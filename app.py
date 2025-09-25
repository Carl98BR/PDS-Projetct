from flask import Flask, request, jsonify, render_template
from collections import deque
from datetime import datetime
import pytz

app = Flask(__name__)

dados_armazenados = deque(maxlen=50)
fuso_horario_br = pytz.timezone('America/Fortaleza')

@app.route('/dados', methods=['POST'])
def receber_dados():
    dados_recebidos = request.get_json()
    if not dados_recebidos:
        return jsonify({"status": "erro", "mensagem": "Nenhum dado recebido"}), 400

    print(f"Dados recebidos do ESP: {dados_recebidos}")
    
    volume = dados_recebidos.get('volume')
    if volume is not None:
        ponto_de_dado = {
            "timestamp": datetime.now(fuso_horario_br).strftime('%H:%M:%S'),
            "valor": volume
        }
        dados_armazenados.append(ponto_de_dado)
        
    return jsonify({"status": "sucesso", "mensagem": "Dados recebidos"}), 201

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/dados')
def api_dados():
    return jsonify(list(dados_armazenados))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)