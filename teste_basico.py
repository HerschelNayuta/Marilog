# teste_basico.py
print("="*50)
print("🔍 TESTE BÁSICO - Python está funcionando!")
print("="*50)

import sys
print(f"Versão do Python: {sys.version}")

import sqlite3
print("✅ Módulo sqlite3 OK")

import flask
print("✅ Módulo flask OK")

print("\n📁 Verificando arquivos...")
import os
arquivos = os.listdir('.')
print(f"Arquivos na pasta: {len(arquivos)}")
for f in arquivos:
    if f.endswith('.py') or f.endswith('.db'):
        print(f"   • {f}")

print("\n✅ Teste concluído!")