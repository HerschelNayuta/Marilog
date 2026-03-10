# dashboard_simples.py
from flask import Flask, jsonify
import sqlite3
import webbrowser

app = Flask(__name__)
DB_NAME = "marilog_tracking.db"

def get_veiculos():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT placa, latitude, longitude, descricao, data_hora FROM vehicle_last_positions")
    dados = cursor.fetchall()
    conn.close()
    return dados

@app.route('/')
def index():
    dados = get_veiculos()
    
    html = '<html><head><title>Marilog</title></head><body>'
    html += '<h1>🚛 MARILOG TRANSPORTES</h1>'
    html += f'<p>Total de veículos: {len(dados)}</p>'
    html += '<table border="1"><tr><th>Placa</th><th>Lat</th><th>Lng</th><th>Local</th><th>Data/Hora</th></tr>'
    
    for d in dados:
        html += f'<tr><td>{d[0]}</td><td>{d[1]}</td><td>{d[2]}</td><td>{d[3]}</td><td>{d[4]}</td></tr>'
    
    html += '</table>'
    html += '<p><a href="/api/veiculos">Ver JSON</a></p>'
    html += '</body></html>'
    
    return html

@app.route('/api/veiculos')
def api_veiculos():
    dados = get_veiculos()
    veiculos = []
    for d in dados:
        veiculos.append({
            'placa': d[0],
            'lat': d[1],
            'lng': d[2],
            'descricao': d[3],
            'data_hora': d[4]
        })
    return jsonify(veiculos)

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚛 MARILOG - MÍNIMO TESTE")
    print("="*60)
    print("📡 http://localhost:5000")
    print("="*60 + "\n")
    
    # Mostrar dados no console
    dados = get_veiculos()
    print(f"📍 Veículos no banco: {len(dados)}")
    for d in dados:
        print(f"   • {d[0]} - {d[3]}")
    
    webbrowser.open('http://localhost:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)