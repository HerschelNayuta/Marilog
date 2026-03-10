# marilog_tracker.py - VERSÃO COMPLETA COM BUONNY + NOX GR (PostgreSQL)
import requests
import psycopg2
import psycopg2.extras
import json
from datetime import datetime, timedelta
import time
import os
import sys
import math
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth

class MarilogTracker:
    def __init__(self):
        # Configuração das transportadoras (mesmo código)
        self.transportadoras = [
            {
                'nome': 'Marilog',
                'cnpj': '61430409000132',
                'apis': [
                    {
                        'provedor': 'Buonny',
                        'token': '8cf3842ca6513e201da3af637a94bd30',
                        'cnpj': '61430409000132'
                    }
                ]
            },
            {
                'nome': 'JMR',
                'cnpj': '15048675000188',
                'apis': [
                    {
                        'provedor': 'Buonny',
                        'token': '9469de8443217ee629fe9f1782065053',
                        'cnpj': '15048675000188'
                    },
                    {
                        'provedor': 'NOX_GR',
                        'login': 'WS-HERSCHEL',
                        'senha': 'hEr5ChElTESTE',
                        'token': 'e8e8d52723acc26fc4c3851bf855d8fe',
                        'cnpj': '15048675000188'
                    }
                ]
            }
        ]
        
        # Configuração dos provedores (mesmo código)
        self.provedores = {
            'Buonny': {
                'url': 'https://api.buonny.com.br/portal/viagens.json',
                'nome': 'Buonny',
                'tipo': 'REST'
            },
            'NOX_GR': {
                'url': 'https://www.noxgr.srv.br/NOXWebService/IntegraGR.wso',
                'wsdl': 'https://www.noxgr.srv.br/NOXWebService/IntegraGR.wso?wsdl',
                'nome': 'NOX GR',
                'tipo': 'SOAP'
            }
        }
        
        # Parâmetros de conexão PostgreSQL (substitua pelos seus dados)
        self.db_params = {
            'host': 'localhost',
            'database': 'marilog',
            'user': 'marilog_user',
            'password': 'sua_senha_forte'
        }
        
        if getattr(sys, 'frozen', False):
            self.base_path = os.path.dirname(sys.executable)
        else:
            self.base_path = os.path.dirname(os.path.abspath(__file__))
        
        # O nome do banco agora é usado apenas para referência, não para conexão SQLite
        self.db_name = os.path.join(self.base_path, "marilog_tracking.db")
        self.init_database()
    
    def get_connection(self):
        """Retorna uma conexão PostgreSQL"""
        return psycopg2.connect(**self.db_params)
    
    def init_database(self):
        """Cria as tabelas no PostgreSQL se não existirem"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de transportadoras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transportadoras (
                id SERIAL PRIMARY KEY,
                nome TEXT NOT NULL,
                cnpj TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de provedores
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS provedores (
                id SERIAL PRIMARY KEY,
                nome TEXT UNIQUE NOT NULL,
                base_url TEXT,
                tipo TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de veículos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicles (
                id SERIAL PRIMARY KEY,
                placa TEXT UNIQUE NOT NULL,
                transportadora_id INTEGER NOT NULL REFERENCES transportadoras(id),
                transportadora_nome TEXT NOT NULL,
                modelo TEXT,
                motorista TEXT,
                ativo INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de rotas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS routes (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                sm_number TEXT,
                origem TEXT,
                destino TEXT,
                km_total REAL,
                route_geometry TEXT,
                atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de últimas posições (COM CAMPO LIBERACAO)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_last_positions (
                vehicle_id INTEGER PRIMARY KEY REFERENCES vehicles(id),
                placa TEXT NOT NULL,
                transportadora_id INTEGER NOT NULL REFERENCES transportadoras(id),
                transportadora_nome TEXT NOT NULL,
                provedor_id INTEGER NOT NULL REFERENCES provedores(id),
                provedor_nome TEXT NOT NULL,
                sm_number TEXT,
                latitude REAL,
                longitude REAL,
                descricao TEXT,
                data_hora TEXT,
                raw_data TEXT,
                status TEXT DEFAULT 'desconhecido',
                tempo_parado INTEGER DEFAULT 0,
                ultimo_movimento TIMESTAMP,
                liberacao TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de histórico
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vehicle_positions_history (
                id SERIAL PRIMARY KEY,
                vehicle_id INTEGER NOT NULL REFERENCES vehicles(id),
                placa TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                data_hora TEXT,
                status TEXT,
                liberacao TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inserir dados iniciais (ignorar se já existir)
        for t in self.transportadoras:
            cursor.execute(
                "INSERT INTO transportadoras (nome, cnpj) VALUES (%s, %s) ON CONFLICT (cnpj) DO NOTHING",
                (t['nome'], t['cnpj'])
            )
        
        for p in self.provedores.values():
            cursor.execute(
                "INSERT INTO provedores (nome, base_url, tipo) VALUES (%s, %s, %s) ON CONFLICT (nome) DO NOTHING",
                (p['nome'], p.get('url', ''), p.get('tipo', 'REST'))
            )
        
        conn.commit()
        conn.close()
        print("✅ Banco de dados PostgreSQL inicializado (com NOX GR)")
    
    # Demais métodos (fetch_buonny_positions, fetch_nox_positions, etc.) permanecem IGUAIS
    # até a parte de banco de dados. Apenas os métodos que acessam o banco serão alterados.
    
    def fetch_buonny_positions(self, transportadora, api):
        # (código original, sem alterações)
        try:
            params = {
                'token': api['token'],
                'cnpj': api['cnpj'],
                'status_viagem': 'V'
            }
            
            response = requests.get(self.provedores['Buonny']['url'], params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                vehicles = data.get('sucesso')
                
                if vehicles is None:
                    print(f"   ⚠️ API retornou null (sem veículos)")
                    vehicles = []
                else:
                    print(f"   ✅ {len(vehicles)} veículos")
                
                for v in vehicles:
                    v['_transportadora'] = transportadora['nome']
                    v['_transportadora_cnpj'] = transportadora['cnpj']
                    v['_provedor'] = 'Buonny'
                
                return vehicles
            else:
                print(f"   ❌ Erro HTTP: {response.status_code}")
                return []
        except Exception as e:
            print(f"   ❌ Erro Buonny: {e}")
            return []
    
    def fetch_nox_positions(self, transportadora, api):
        # (código original, sem alterações)
        try:
            print(f"   🔄 Conectando NOX GR...")
            
            client = Client(self.provedores['NOX_GR']['wsdl'])
            
            login = {
                'sUserName': api['login'],
                'sPassWord': api['senha'],
                'sToken': api['token']
            }
            
            response = client.service.Get_ConsultaVeiculoEmViagem(
                Login=login,
                sCd_CnpjUnidNeg=api['cnpj']
            )
            
            vehicles = []
            
            if response and hasattr(response, 'Veiculo'):
                veiculos_lista = response.Veiculo
                
                if not isinstance(veiculos_lista, list):
                    veiculos_lista = [veiculos_lista]
                
                for v in veiculos_lista:
                    if hasattr(v, 'UltimaPosicao'):
                        pos = v.UltimaPosicao
                        
                        vehicle_data = {
                            'placa': v.sCd_Placa,
                            'sm': str(getattr(v, 'InfoViagem', {}).get('iCd_Viagem', '')),
                            'latitude': pos.sCd_Latitude,
                            'longitude': pos.sCd_Longitude,
                            'data_hora': pos.dDh_GeracaoEv.strftime('%d/%m/%Y %H:%M:%S') if hasattr(pos, 'dDh_GeracaoEv') else '',
                            'descricao': getattr(pos, 'sDc_Referencia', ''),
                            'velocidade': float(pos.nDc_VelocInst) if hasattr(pos, 'nDc_VelocInst') else 0,
                            'ignicao': pos.iSt_Ignicao if hasattr(pos, 'iSt_Ignicao') else 0,
                            'odometro': pos.iOdometro if hasattr(pos, 'iOdometro') else 0,
                            '_transportadora': transportadora['nome'],
                            '_transportadora_cnpj': transportadora['cnpj'],
                            '_provedor': 'NOX GR',
                            'alvos': []
                        }
                        vehicles.append(vehicle_data)
                
                print(f"   ✅ NOX GR retornou {len(vehicles)} veículos")
            else:
                print(f"   ⚠️ Nenhum veículo retornado pela NOX")
            
            return vehicles
            
        except Exception as e:
            print(f"   ❌ Erro NOX GR: {e}")
            return []
    
    def fetch_all_positions(self):
        # (código original, sem alterações)
        all_vehicles = []
        
        for transportadora in self.transportadoras:
            for api in transportadora['apis']:
                provedor = api['provedor']
                
                print(f"📡 {transportadora['nome']} via {provedor}...")
                
                if provedor == 'Buonny':
                    vehicles = self.fetch_buonny_positions(transportadora, api)
                elif provedor == 'NOX_GR':
                    vehicles = self.fetch_nox_positions(transportadora, api)
                else:
                    print(f"   ⚠️ Provedor desconhecido: {provedor}")
                    vehicles = []
                
                all_vehicles.extend(vehicles)
        
        return all_vehicles
    
    def get_osrm_route(self, origin_lat, origin_lng, dest_lat, dest_lng):
        # (código original, sem alterações)
        try:
            url = f"http://router.project-osrm.org/route/v1/driving/{origin_lng},{origin_lat};{dest_lng},{dest_lat}"
            params = {
                'overview': 'full',
                'geometries': 'geojson',
                'steps': 'false'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['code'] == 'Ok' and data['routes']:
                    route = data['routes'][0]
                    return {
                        'geometry': route['geometry'],
                        'distance': route['distance'] / 1000,
                        'duration': route['duration'] / 3600
                    }
            return None
        except Exception as e:
            return None
    
    def extract_route_info(self, vehicle_data):
        # (código original, sem alterações)
        try:
            alvos = vehicle_data.get('alvos', [])
            if not alvos or len(alvos) < 2:
                return None
            
            origem = None
            destino = None
            
            for alvo in alvos:
                if alvo.get('tipo_parada') == 'ORIGEM' and not origem:
                    if alvo.get('latitude') and alvo.get('longitude'):
                        origem = {
                            'descricao': alvo.get('descricao'),
                            'cidade': alvo.get('cidade'),
                            'estado': alvo.get('estado'),
                            'lat': float(alvo.get('latitude')),
                            'lng': float(alvo.get('longitude'))
                        }
                
                if alvo.get('tipo_parada') == 'DESTINO' and not destino:
                    if alvo.get('latitude') and alvo.get('longitude'):
                        destino = {
                            'descricao': alvo.get('descricao'),
                            'cidade': alvo.get('cidade'),
                            'estado': alvo.get('estado'),
                            'lat': float(alvo.get('latitude')),
                            'lng': float(alvo.get('longitude'))
                        }
            
            if origem and destino:
                return {
                    'origem': origem,
                    'destino': destino
                }
            
            return None
        except Exception as e:
            return None
    
    def determinar_status(self, vehicle_data, ultima_posicao=None):
        # (código original, sem alterações)
        try:
            alvos = vehicle_data.get('alvos', [])
            
            for alvo in alvos:
                if alvo.get('entrada_alvo') and not alvo.get('saida_alvo'):
                    if 'ORIGEM' in alvo.get('tipo_parada', ''):
                        return 'carregando'
                    elif 'DESTINO' in alvo.get('tipo_parada', ''):
                        return 'descarregando'
            
            if ultima_posicao:
                agora = datetime.now()
                try:
                    ultima = datetime.strptime(ultima_posicao, '%d/%m/%Y %H:%M:%S')
                    diferenca = (agora - ultima).total_seconds() / 60
                    
                    if diferenca > 30:
                        return 'parado'
                except:
                    pass
            
            return 'em_andamento'
        except:
            return 'desconhecido'
    
    def calcular_tempo_parado(self, vehicle_data, ultima_posicao):
        # (código original, sem alterações)
        try:
            if not ultima_posicao:
                return 0
            
            agora = datetime.now()
            ultima = datetime.strptime(ultima_posicao, '%d/%m/%Y %H:%M:%S')
            minutos = int((agora - ultima).total_seconds() / 60)
            
            return minutos
        except:
            return 0
    
    def save_positions(self, vehicles):
        """Salva posições no banco PostgreSQL"""
        if not vehicles:
            return 0
        
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            saved = 0
            
            for v in vehicles:
                placa = v.get('placa')
                if not placa:
                    continue
                
                # Verificar se veículo existe
                cursor.execute("SELECT id FROM vehicles WHERE placa = %s", (placa,))
                result = cursor.fetchone()
                
                if result:
                    vehicle_id = result[0]
                else:
                    # Inserir novo veículo
                    cursor.execute('''
                        INSERT INTO vehicles (placa, transportadora_id, transportadora_nome) 
                        VALUES (%s, (SELECT id FROM transportadoras WHERE nome = %s), %s)
                        RETURNING id
                    ''', (placa, v['_transportadora'], v['_transportadora']))
                    vehicle_id = cursor.fetchone()[0]
                    print(f"      🆕 Novo veículo {placa} ({v['_transportadora']})")
                
                # Converter coordenadas
                try:
                    lat = float(v.get('latitude')) if v.get('latitude') else None
                    lng = float(v.get('longitude')) if v.get('longitude') else None
                except:
                    lat, lng = None, None
                
                # Determinar status
                status = self.determinar_status(v, v.get('data_hora'))
                tempo_parado = self.calcular_tempo_parado(v, v.get('data_hora')) if status == 'parado' else 0
                
                # Salvar no histórico
                if lat and lng:
                    cursor.execute('''
                        INSERT INTO vehicle_positions_history
                        (vehicle_id, placa, latitude, longitude, data_hora, status)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (vehicle_id, placa, lat, lng, v.get('data_hora'), status))
                
                # Extrair rota (apenas para Buonny)
                if v.get('_provedor') == 'Buonny':
                    route_info = self.extract_route_info(v)
                    
                    if route_info:
                        cursor.execute('''
                            SELECT id FROM routes 
                            WHERE vehicle_id = %s AND sm_number = %s
                        ''', (vehicle_id, v.get('sm')))
                        
                        existing_route = cursor.fetchone()
                        
                        if not existing_route:
                            osrm_route = self.get_osrm_route(
                                route_info['origem']['lat'], route_info['origem']['lng'],
                                route_info['destino']['lat'], route_info['destino']['lng']
                            )
                            
                            if osrm_route:
                                cursor.execute('''
                                    INSERT INTO routes 
                                    (vehicle_id, sm_number, origem, destino, km_total, route_geometry)
                                    VALUES (%s, %s, %s, %s, %s, %s)
                                ''', (
                                    vehicle_id,
                                    v.get('sm'),
                                    json.dumps(route_info['origem']),
                                    json.dumps(route_info['destino']),
                                    round(osrm_route['distance'], 1),
                                    json.dumps(osrm_route['geometry'])
                                ))
                
                # Atualizar última posição (UPSERT)
                cursor.execute('''
                    INSERT INTO vehicle_last_positions 
                    (vehicle_id, placa, transportadora_id, transportadora_nome, 
                     provedor_id, provedor_nome, sm_number, latitude, longitude, 
                     descricao, data_hora, raw_data, status, tempo_parado, updated_at)
                    VALUES (%s, %s, (SELECT id FROM transportadoras WHERE nome = %s), %s, 
                            (SELECT id FROM provedores WHERE nome = %s), %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                    ON CONFLICT (vehicle_id) DO UPDATE SET
                        placa = EXCLUDED.placa,
                        transportadora_id = EXCLUDED.transportadora_id,
                        transportadora_nome = EXCLUDED.transportadora_nome,
                        provedor_id = EXCLUDED.provedor_id,
                        provedor_nome = EXCLUDED.provedor_nome,
                        sm_number = EXCLUDED.sm_number,
                        latitude = EXCLUDED.latitude,
                        longitude = EXCLUDED.longitude,
                        descricao = EXCLUDED.descricao,
                        data_hora = EXCLUDED.data_hora,
                        raw_data = EXCLUDED.raw_data,
                        status = EXCLUDED.status,
                        tempo_parado = EXCLUDED.tempo_parado,
                        updated_at = EXCLUDED.updated_at
                ''', (
                    vehicle_id, placa, v['_transportadora'], v['_transportadora'],
                    v['_provedor'], v['_provedor'], v.get('sm'), lat, lng,
                    v.get('descricao'), v.get('data_hora'), json.dumps(v),
                    status, tempo_parado
                ))
                
                saved += 1
            
            conn.commit()
            print(f"   💾 {saved} posições salvas")
            return saved
            
        except Exception as e:
            print(f"   ❌ Erro ao salvar: {e}")
            import traceback
            traceback.print_exc()
            return 0
        finally:
            if conn:
                conn.close()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        # (código original, sem alterações)
        R = 6371
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        
        return round(R * c, 1)
    
    def get_vehicle_positions_history(self, vehicle_id, limit=50):
        """Busca histórico de posições"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT latitude, longitude, data_hora
                FROM vehicle_positions_history
                WHERE vehicle_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            ''', (vehicle_id, limit))
            
            positions = []
            for row in cursor.fetchall():
                positions.append({
                    'lat': row[0],
                    'lng': row[1],
                    'data_hora': row[2]
                })
            
            return positions
        except Exception as e:
            return []
        finally:
            if conn:
                conn.close()
    
    def get_all_positions(self):
        """Retorna todas as últimas posições"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            cursor.execute('''
                SELECT 
                    v.vehicle_id,
                    v.placa,
                    v.latitude,
                    v.longitude,
                    v.descricao,
                    v.data_hora,
                    v.sm_number,
                    v.updated_at,
                    v.transportadora_nome,
                    v.provedor_nome,
                    v.status,
                    v.tempo_parado,
                    v.liberacao,
                    r.km_total,
                    r.route_geometry,
                    r.origem,
                    r.destino
                FROM vehicle_last_positions v
                LEFT JOIN routes r ON v.vehicle_id = r.vehicle_id AND v.sm_number = r.sm_number
                ORDER BY v.updated_at DESC
            ''')
            
            positions = []
            for row in cursor.fetchall():
                pos = dict(row)
                
                # Traduzir status
                status_map = {
                    'em_andamento': '🚛 Em Andamento',
                    'carregando': '⏫ Carregando',
                    'descarregando': '⏬ Descarregando',
                    'parado': '⏸️ Parado',
                    'desconhecido': '❓ Desconhecido'
                }
                pos['status_texto'] = status_map.get(pos['status'], pos['status'])
                
                # Adicionar dados de rota
                if pos.get('km_total'):
                    origem = json.loads(pos['origem']) if pos.get('origem') else None
                    destino = json.loads(pos['destino']) if pos.get('destino') else None
                    progresso = self.calculate_progress(
                        pos['lat'], pos['lng'],
                        origem, destino,
                        pos['km_total']
                    )
                    
                    pos['rota'] = {
                        'km_total': pos['km_total'],
                        'km_total_resumido': f"{pos['km_total']}km",
                        'route_geometry': json.loads(pos['route_geometry']) if pos.get('route_geometry') else None,
                        'origem': origem,
                        'destino': destino,
                        'progresso': progresso
                    }
                    
                    # Buscar histórico
                    history = self.get_vehicle_positions_history(pos['vehicle_id'], 20)
                    if history:
                        pos['historico'] = history
                
                positions.append(pos)
            
            return positions
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return []
        finally:
            if conn:
                conn.close()
    
    def calculate_progress(self, current_lat, current_lng, origem, destino, km_total):
        # (código original, sem alterações)
        try:
            if not origem or not destino or not current_lat or not current_lng:
                return 0
            
            dist_origem = self.calculate_distance(
                origem['lat'], origem['lng'],
                current_lat, current_lng
            )
            
            if km_total > 0:
                return min(100, round((dist_origem / km_total) * 100, 1))
            return 0
        except:
            return 0
    
    def get_statistics(self):
        """Retorna estatísticas do sistema"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            stats = {}
            
            cursor.execute("SELECT COUNT(*) FROM vehicles")
            stats['total_veiculos'] = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT COUNT(*) FROM vehicle_last_positions 
                WHERE updated_at > NOW() - INTERVAL '1 day'
            ''')
            stats['veiculos_ativos_24h'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM vehicle_positions_history")
            stats['total_posicoes'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM routes WHERE route_geometry IS NOT NULL")
            stats['rotas_reais'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT MAX(updated_at) FROM vehicle_last_positions")
            stats['ultima_atualizacao'] = cursor.fetchone()[0]
            
            # Estatísticas por transportadora
            cursor.execute('''
                SELECT transportadora_nome, COUNT(*) 
                FROM vehicle_last_positions 
                GROUP BY transportadora_nome
            ''')
            stats['por_transportadora'] = dict(cursor.fetchall())
            
            # Estatísticas por provedor
            cursor.execute('''
                SELECT provedor_nome, COUNT(*) 
                FROM vehicle_last_positions 
                GROUP BY provedor_nome
            ''')
            stats['por_provedor'] = dict(cursor.fetchall())
            
            # Estatísticas por status
            cursor.execute('''
                SELECT status, COUNT(*) 
                FROM vehicle_last_positions 
                GROUP BY status
            ''')
            stats['por_status'] = dict(cursor.fetchall())
            
            return stats
            
        except Exception as e:
            print(f"❌ Erro: {e}")
            return {}
        finally:
            if conn:
                conn.close()
    
    def update_liberacao(self, placa, liberacao):
        """Atualiza o número de liberação de um veículo"""
        conn = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE vehicle_last_positions 
                SET liberacao = %s 
                WHERE placa = %s
            ''', (liberacao, placa))
            
            cursor.execute('''
                UPDATE vehicle_positions_history 
                SET liberacao = %s 
                WHERE placa = %s 
                ORDER BY created_at DESC LIMIT 1
            ''', (liberacao, placa))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"❌ Erro ao atualizar liberação: {e}")
            return False
        finally:
            if conn:
                conn.close()
