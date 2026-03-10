# teste_flask.py
from flask import Flask
import webbrowser

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>🚛 MARILOG</h1><p>Servidor Flask funcionando!</p>"

if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚛 TESTE MÍNIMO DO FLASK")
    print("="*50)
    print("📡 http://localhost:5000")
    print("="*50 + "\n")
    
    webbrowser.open('http://localhost:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)