# debug_completo.py
import sqlite3
import requests
import json
from datetime import datetime

TOKEN = "8cf3842ca6513e201da3af637a94bd30"
CNPJ = "61430409000132"
API_URL = "https://api.buonny.com.br/portal/viagens.json"
DB_NAME = "marilog_tracking.db"

print("="*70)
print("🔍 DEBUG COMPLETO DO SISTEMA MARILOG")
print("="*70)

# TESTE 1: A API DA BUONNY ESTÁ RESPONDENDO?
print("\n📡 TESTE 1: API Buonny")
print("-"*50)
try:
    params = {
        'token': TOKEN,
        'cnpj': CNPJ,
        'status_viagem': 'V'
    }
    response = requests.get(API_URL, params=params, timeout=10)
    print(f"Status HTTP: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        veiculos_api = data.get('sucesso', [])
        print(f"✅ API respondeu com {len(veiculos_api)} veículos")
        for v in veiculos_api:
            print(f"   • {v.get('placa')} - {v.get('data_hora')}")
    else:
        print(f"❌ Erro na API: {response.status_code}")
        print(response.text[:200])
except Exception as e:
    print(f"❌ Exceção: {e}")

# TESTE 2: O BANCO DE DADOS EXISTE?
print("\n📁 TESTE 2: Banco de Dados")
print("-"*50)
import os
if os.path.exists(DB_NAME):
    print(f"✅ Banco encontrado: {DB_NAME} ({os.path.getsize(DB_NAME)} bytes)")
else:
    print(f"❌ Banco NÃO encontrado: {DB_NAME}")

# TESTE 3: CONSEGUE CONECTAR NO BANCO?
print("\n🔌 TESTE 3: Conexão com Banco")
print("-"*50)
try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    print("✅ Conexão OK")
    
    # Listar tabelas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tabelas = cursor.fetchall()
    print(f"📋 Tabelas: {len(tabelas)}")
    for t in tabelas:
        print(f"   • {t[0]}")
    
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")

# TESTE 4: DADOS NA TABELA vehicle_last_positions
print("\n📍 TESTE 4: Dados na tabela vehicle_last_positions")
print("-"*50)
try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM vehicle_last_positions")
    count = cursor.fetchone()[0]
    print(f"Total de registros: {count}")
    
    if count > 0:
        cursor.execute("SELECT * FROM vehicle_last_positions LIMIT 5")
        colunas = [description[0] for description in cursor.description]
        print(f"Colunas: {colunas}")
        
        for row in cursor.fetchall():
            print(f"\n   Registro:")
            for i, col in enumerate(colunas):
                print(f"      {col}: {row[i]}")
    else:
        print("⚠️ Nenhum registro encontrado!")
    
    conn.close()
except Exception as e:
    print(f"❌ Erro: {e}")

# TESTE 5: TESTE A FUNÇÃO get_all_positions (simulada)
print("\n🔄 TESTE 5: Simulando get_all_positions")
print("-"*50)
try:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            placa,
            latitude,
            longitude,
            descricao,
            data_hora,
            sm_number
        FROM vehicle_last_positions
        WHERE latitude IS NOT NULL AND longitude IS NOT NULL
    ''')
    
    rows = cursor.fetchall()
    print(f"Registros encontrados: {len(rows)}")
    
    positions = []
    for row in rows:
        positions.append({
            'placa': row[0],
            'lat': row[1],
            'lng': row[2],
            'descricao': row[3],
            'data_hora': row[4],
            'sm': row[5]
        })
        print(f"   → {row[0]}: {row[1]}, {row[2]}")
    
    conn.close()
    
    # TESTE 6: SIMULAR ROTA /api/veiculos
    print("\n🌐 TESTE 6: Simulando rota /api/veiculos")
    print("-"*50)
    print(f"JSON retornado: {json.dumps(positions, indent=2)}")
    
except Exception as e:
    print(f"❌ Erro: {e}")

print("\n" + "="*70)
print("✅ FIM DO DEBUG")
print("="*70)