# testar_banco.py
import sqlite3

conn = sqlite3.connect('marilog_tracking.db')
cursor = conn.cursor()

print("🔍 VERIFICANDO BANCO DE DADOS")
print("="*50)

# Ver veículos
cursor.execute("SELECT * FROM vehicles")
veiculos = cursor.fetchall()
print(f"\n🚛 Veículos cadastrados: {len(veiculos)}")
for v in veiculos:
    print(f"   • ID: {v[0]} - Placa: {v[1]}")

# Ver últimas posições
cursor.execute("SELECT * FROM vehicle_last_positions")
posicoes = cursor.fetchall()
print(f"\n📍 Últimas posições: {len(posicoes)}")
for p in posicoes:
    print(f"   • Veículo ID: {p[0]} - Placa: {p[1]} - Lat: {p[4]} - Lng: {p[5]}")

conn.close()