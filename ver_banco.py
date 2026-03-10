# ver_banco.py
import sqlite3

conn = sqlite3.connect('marilog_tracking.db')
cursor = conn.cursor()

print("="*60)
print("🔍 VERIFICANDO BANCO DE DADOS")
print("="*60)

# Ver todas as tabelas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print(f"\n📋 Tabelas encontradas: {len(tabelas)}")
for t in tabelas:
    print(f"   • {t[0]}")

# Ver dados da tabela vehicle_last_positions
print("\n📍 ÚLTIMAS POSIÇÕES:")
cursor.execute("SELECT placa, latitude, longitude, descricao, data_hora FROM vehicle_last_positions")
dados = cursor.fetchall()

if dados:
    for d in dados:
        print(f"\n   🚛 {d[0]}")
        print(f"      Lat: {d[1]}")
        print(f"      Lng: {d[2]}")
        print(f"      Local: {d[3]}")
        print(f"      Hora: {d[4]}")
else:
    print("   ⚠️ Nenhum dado encontrado!")

conn.close()