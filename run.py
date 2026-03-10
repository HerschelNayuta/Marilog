# run.py
import webbrowser
import time
import os

print("""
╔════════════════════════════════════════════════════╗
║                                                    ║
║   🚛  MARILOG TRANSPORTES E LOGÍSTICA              ║
║                                                    ║
╚════════════════════════════════════════════════════╝
""")

# Verificar se o banco existe
if not os.path.exists('marilog_tracking.db'):
    print("📁 Criando banco de dados...")
    from marilog_tracker import MarilogTracker
    tracker = MarilogTracker()

print("🚀 Iniciando sistema...")
time.sleep(2)
webbrowser.open('http://localhost:5000')

import dashboard