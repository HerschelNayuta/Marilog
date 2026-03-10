# dashboard.py - VERSÃO COMPLETA E CORRIGIDA (COM LOGO)
from flask import Flask, render_template_string, jsonify, request
from marilog_tracker import MarilogTracker
import threading
import time
import webbrowser
from datetime import datetime

app = Flask(__name__)
tracker = MarilogTracker()

def coleta_automatica():
    while True:
        try:
            vehicles = tracker.fetch_all_positions()
            if vehicles:
                tracker.save_positions(vehicles)
            time.sleep(60)
        except Exception as e:
            print(f"❌ Erro na coleta: {e}")
            time.sleep(60)

threading.Thread(target=coleta_automatica, daemon=True).start()

@app.route('/')
def index():
    veiculos = tracker.get_all_positions()

    html = '''
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Marilog - Torre de Controle</title>

        <!-- Google Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700;800&family=Roboto:wght@300;400;500;700&display=swap" rel="stylesheet">

        <!-- Font Awesome 6 -->
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">

        <!-- Leaflet CSS -->
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />

        <!-- Tailwind CSS -->
        <script src="https://cdn.tailwindcss.com"></script>

        <script>
            tailwind.config = {
                theme: {
                    extend: {
                        colors: {
                            'marilog-blue': '#0D1B2A',
                            'marilog-green': '#66CC33',
                            'marilog-gray': '#B0B3B5',
                        },
                        fontFamily: {
                            'heading': ['Montserrat', 'sans-serif'],
                            'body': ['Roboto', 'sans-serif'],
                        }
                    }
                }
            }
        </script>

        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            body {
                font-family: 'Roboto', sans-serif;
                background: #0D1B2A;
                color: white;
                overflow: hidden;
            }
            h1, h2, h3, h4, h5, h6 {
                font-family: 'Montserrat', sans-serif;
            }
            .header {
                background: #0D1B2A;
                padding: 1rem 2rem;
                border-bottom: 4px solid #66CC33;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.5);
            }
            .logo-img {
                height: 50px; /* Ajuste a altura conforme necessário */
                width: auto;
            }
            .stats-container {
                display: flex;
                gap: 2rem;
            }
            .stat-item {
                text-align: center;
            }
            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: #66CC33;
                line-height: 1.2;
            }
            .stat-label {
                font-size: 0.8rem;
                color: #B0B3B5;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .main-container {
                display: grid;
                grid-template-columns: 450px 1fr;
                height: calc(100vh - 5rem);
            }
            .sidebar {
                background: rgba(0,0,0,0.3);
                padding: 1.5rem;
                overflow-y: auto;
                border-right: 2px solid #66CC33;
                backdrop-filter: blur(10px);
            }
            .sidebar-title {
                font-size: 1.3rem;
                color: #66CC33;
                margin-bottom: 1.5rem;
                text-transform: uppercase;
                letter-spacing: 2px;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .vehicle-card {
                background: #0D1B2A;
                border: 1px solid #B0B3B5;
                border-radius: 12px;
                padding: 1.2rem;
                margin-bottom: 1rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            .vehicle-card:hover {
                border-color: #66CC33;
                transform: translateX(5px) translateY(-2px);
                box-shadow: 0 6px 15px rgba(102, 204, 51, 0.2);
            }
            .vehicle-card.selected {
                border-color: #66CC33;
                border-width: 2px;
                background: rgba(102, 204, 51, 0.1);
            }
            .vehicle-placa {
                font-size: 1.4rem;
                font-weight: 700;
                color: #66CC33;
                margin-bottom: 0.8rem;
                font-family: 'Montserrat', sans-serif;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            .vehicle-badge {
                font-size: 0.7rem;
                padding: 0.2rem 0.5rem;
                border-radius: 4px;
                background: rgba(255,255,255,0.1);
            }
            .vehicle-info {
                font-size: 0.9rem;
                color: #B0B3B5;
                margin: 0.5rem 0;
                display: flex;
                align-items: center;
                gap: 0.5rem;
            }
            .vehicle-info i {
                color: #66CC33;
                width: 1.2rem;
            }
            .vehicle-info strong {
                color: white;
                font-weight: 500;
            }
            .status-badge {
                display: inline-block;
                padding: 0.2rem 0.8rem;
                border-radius: 20px;
                font-size: 0.8rem;
                font-weight: 600;
            }
            .status-em_andamento { background: #66CC33; color: #0D1B2A; }
            .status-carregando { background: #FFA500; color: #0D1B2A; }
            .status-descarregando { background: #FF4500; color: white; }
            .status-parado { background: #808080; color: white; }
            .liberacao-input {
                background: rgba(255,255,255,0.1);
                border: 1px solid #66CC33;
                color: white;
                padding: 0.3rem 0.5rem;
                border-radius: 4px;
                width: 100%;
                font-size: 0.9rem;
            }
            .liberacao-input:focus {
                outline: none;
                border-color: #66CC33;
                box-shadow: 0 0 0 2px rgba(102, 204, 51, 0.3);
            }
            .btn-salvar {
                background: #66CC33;
                color: #0D1B2A;
                border: none;
                padding: 0.3rem 0.8rem;
                border-radius: 4px;
                font-size: 0.8rem;
                font-weight: 600;
                cursor: pointer;
                margin-left: 0.5rem;
            }
            .btn-salvar:hover {
                background: #7ed957;
            }
            .progress-bar {
                width: 100%;
                height: 8px;
                background: rgba(255,255,255,0.1);
                border-radius: 4px;
                margin: 0.8rem 0;
                overflow: hidden;
            }
            .progress-fill {
                height: 100%;
                background: #66CC33;
                border-radius: 4px;
                transition: width 0.3s ease;
            }
            .route-info {
                margin-top: 0.8rem;
                padding-top: 0.8rem;
                border-top: 1px solid rgba(176, 179, 181, 0.3);
                font-size: 0.85rem;
            }
            #map {
                height: 100%;
                width: 100%;
                z-index: 1;
            }
            .footer {
                background: #0D1B2A;
                padding: 0.8rem;
                text-align: center;
                border-top: 1px solid #B0B3B5;
                color: #B0B3B5;
                font-size: 0.9rem;
                position: fixed;
                bottom: 0;
                width: 100%;
            }
            .nav-links {
                display: flex;
                gap: 0.5rem;
                margin-top: 1rem;
                flex-wrap: wrap;
            }
            .nav-btn {
                background: transparent;
                border: 1px solid #66CC33;
                color: #66CC33;
                padding: 0.5rem 1rem;
                border-radius: 20px;
                font-size: 0.8rem;
                cursor: pointer;
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                gap: 0.3rem;
                transition: all 0.3s;
            }
            .nav-btn:hover {
                background: #66CC33;
                color: #0D1B2A;
            }
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-track {
                background: #0D1B2A;
            }
            ::-webkit-scrollbar-thumb {
                background: #66CC33;
                border-radius: 4px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <img src="/static/Logo_Branca.png" alt="Marilog Logo" class="logo-img">
            <div class="stats-container">
                <div class="stat-item">
                    <div class="stat-value" id="total">{{ veiculos|length }}</div>
                    <div class="stat-label">ATIVOS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="stats-rotas">0</div>
                    <div class="stat-label">ROTAS</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" id="hora"></div>
                    <div class="stat-label">ATUALIZAÇÃO</div>
                </div>
            </div>
        </div>

        <div class="main-container">
            <div class="sidebar">
                <div class="sidebar-title">
                    <i class="fas fa-map-marked-alt"></i>
                    FROTA EM MOVIMENTO
                </div>

                <div id="vehicle-list">
                    {% if veiculos %}
                        {% for v in veiculos %}
                        <div class="vehicle-card" onclick="selectVehicle('{{ v.placa }}', {{ v.lat }}, {{ v.lng }}, {{ v.rota|tojson if v.rota else 'null' }}, {{ v.historico|tojson if v.historico else 'null' }})">
                            <div class="vehicle-placa">
                                <span><i class="fas fa-truck mr-2"></i>{{ v.placa }}</span>
                                <span class="vehicle-badge">{{ v.transportadora }} | {{ v.provedor }}</span>
                            </div>

                            <div class="vehicle-info">
                                <i class="fas fa-map-pin"></i>
                                <strong>Local:</strong> {{ v.descricao or 'N/A' }}
                            </div>

                            <div class="vehicle-info">
                                <i class="fas fa-clock"></i>
                                <strong>Hora:</strong> {{ v.data_hora or 'N/A' }}
                            </div>

                            <div class="vehicle-info">
                                <i class="fas fa-info-circle"></i>
                                <strong>Status:</strong>
                                <span class="status-badge status-{{ v.status }}">
                                    {{ v.status_texto }}
                                    {% if v.status == 'parado' and v.tempo_parado > 0 %}
                                        ({{ v.tempo_parado }} min)
                                    {% endif %}
                                </span>
                            </div>

                            <div class="vehicle-info">
                                <i class="fas fa-hashtag"></i>
                                <strong>Liberação:</strong>
                                <input type="text" id="liberacao_{{ v.placa }}" value="{{ v.liberacao or '' }}" placeholder="Digite o nº" class="liberacao-input" style="width: 120px;" onclick="event.stopPropagation()">
                                <button class="btn-salvar" onclick="event.stopPropagation(); salvarLiberacao('{{ v.placa }}')">Salvar</button>
                            </div>

                            {% if v.rota %}
                            <div class="progress-bar">
                                <div class="progress-fill" style="width: {{ v.rota.progresso }}%"></div>
                            </div>

                            <div class="route-info">
                                <div class="flex justify-between">
                                    <span><i class="fas fa-flag-checkered text-marilog-green"></i> {{ v.rota.destino.cidade }}/{{ v.rota.destino.estado }}</span>
                                    <span class="text-marilog-gray">{{ v.rota.km_total_resumido }}</span>
                                </div>
                            </div>
                            {% endif %}
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-state text-center p-8">
                            <i class="fas fa-truck fa-3x text-marilog-green mb-4"></i>
                            <p class="text-marilog-gray">Aguardando dados das APIs...</p>
                        </div>
                    {% endif %}
                </div>

                <div class="nav-links">
                    <a href="/stats" class="nav-btn">
                        <i class="fas fa-chart-bar"></i> Stats
                    </a>
                    <a href="/api/veiculos" target="_blank" class="nav-btn">
                        <i class="fas fa-code"></i> API
                    </a>
                </div>
            </div>

            <div id="map"></div>
        </div>

        <div class="footer">
            <i class="fas fa-satellite-dish text-marilog-green mr-2"></i>
            MARILOG TRANSPORTES - TORRE DE CONTROLE 24/7
            <span class="update-time" id="footer-time"></span>
        </div>

        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>

        <script>
            var map = L.map('map').setView([-23.5505, -46.6333], 6);
            L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                attribution: '© OpenStreetMap | Marilog'
            }).addTo(map);

            var markers = {};
            var routeLayer = null;
            var historyLayer = null;

            function decodePolyline(encoded) {
                if (!encoded || typeof encoded !== 'string') return [];
                var points = [];
                var index = 0, len = encoded.length;
                var lat = 0, lng = 0;
                while (index < len) {
                    var b, shift = 0, result = 0;
                    do { b = encoded.charCodeAt(index++) - 63; result |= (b & 0x1f) << shift; shift += 5; } while (b >= 0x20);
                    var dlat = ((result & 1) ? ~(result >> 1) : (result >> 1)); lat += dlat;
                    shift = 0; result = 0;
                    do { b = encoded.charCodeAt(index++) - 63; result |= (b & 0x1f) << shift; shift += 5; } while (b >= 0x20);
                    var dlng = ((result & 1) ? ~(result >> 1) : (result >> 1)); lng += dlng;
                    points.push([lat * 1e-5, lng * 1e-5]);
                }
                return points;
            }

            // FUNÇÃO CORRIGIDA PARA SELECIONAR VEÍCULO
            window.selectVehicle = function(placa, lat, lng, rota, historico) {
                console.log('🚛 Selecionado:', placa, lat, lng);

                // Remover seleção anterior
                document.querySelectorAll('.vehicle-card').forEach(card => {
                    card.classList.remove('selected');
                });

                // Marcar card selecionado (se o evento existir)
                if (event && event.currentTarget) {
                    event.currentTarget.classList.add('selected');
                }

                // Voar para o veículo (CORRIGIDO!)
                if (lat && lng && !isNaN(lat) && !isNaN(lng)) {
                    map.flyTo([lat, lng], 14, {
                        animate: true,
                        duration: 1.5
                    });

                    // Abrir popup automaticamente
                    if (markers[placa]) {
                        markers[placa].openPopup();
                    }
                } else {
                    console.warn('Coordenadas inválidas:', lat, lng);
                }

                // Remover rotas anteriores
                if (routeLayer) { map.removeLayer(routeLayer); routeLayer = null; }
                if (historyLayer) { map.removeLayer(historyLayer); historyLayer = null; }

                // Mostrar histórico
                if (historico && historico.length > 1) {
                    var historyPoints = historico.map(h => [h.lat, h.lng]);
                    historyLayer = L.polyline(historyPoints, {
                        color: '#66CC33', weight: 4, opacity: 0.6, dashArray: '5, 8'
                    }).addTo(map);
                }

                // Mostrar rota
                if (rota && rota.route_geometry) {
                    var routePoints;
                    if (rota.route_geometry.type === 'LineString') {
                        routePoints = rota.route_geometry.coordinates.map(coord => [coord[1], coord[0]]);
                    } else if (typeof rota.route_geometry === 'string') {
                        routePoints = decodePolyline(rota.route_geometry);
                    }
                    if (routePoints && routePoints.length > 0) {
                        routeLayer = L.polyline(routePoints, {
                            color: '#66CC33', weight: 5, opacity: 0.8
                        }).addTo(map);
                    }
                }
            };

            window.salvarLiberacao = function(placa) {
                event.stopPropagation();
                var input = document.getElementById('liberacao_' + placa);
                var liberacao = input.value.trim();
                if (!liberacao) { alert('Digite o número da liberação'); return; }
                fetch('/api/liberacao', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ placa: placa, liberacao: liberacao })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'ok') { alert('Liberação salva com sucesso!'); }
                    else { alert('Erro ao salvar: ' + data.message); }
                })
                .catch(error => { console.error('Erro:', error); alert('Erro ao salvar liberação'); });
            };

            function updateVehicle(v) {
                if (!v.lat || !v.lng) return;
                var popupContent = `
                    <div style="min-width: 250px;">
                        <h3 style="color: #0D1B2A; font-weight: 700; margin: 0 0 10px 0;">
                            🚛 ${v.placa} (${v.transportadora})
                        </h3>
                        <p><strong>Provedor:</strong> ${v.provedor}</p>
                        <p><strong>Local:</strong> ${v.descricao || 'N/A'}</p>
                        <p><strong>Data/Hora:</strong> ${v.data_hora || 'N/A'}</p>
                        <p><strong>Status:</strong> ${v.status_texto}</p>
                        ${v.liberacao ? `<p><strong>Liberação:</strong> ${v.liberacao}</p>` : ''}
                `;
                if (v.rota) {
                    popupContent += `
                        <hr style="margin: 10px 0; border-color: #66CC33;">
                        <p><strong>Destino:</strong> ${v.rota.destino.cidade}/${v.rota.destino.estado}</p>
                        <p><strong>Distância:</strong> ${v.rota.km_total_resumido}</p>
                        <p><strong>Progresso:</strong> ${v.rota.progresso}%</p>
                    `;
                }
                popupContent += `<p style="margin-top: 10px;"><a href="https://www.google.com/maps?q=${v.lat},${v.lng}" target="_blank" style="color: #66CC33;">📍 Google Maps</a></p></div>`;

                if (markers[v.placa]) {
                    markers[v.placa].setLatLng([v.lat, v.lng]);
                    markers[v.placa].getPopup().setContent(popupContent);
                } else {
                    var marker = L.marker([v.lat, v.lng]).addTo(map);
                    marker.bindPopup(popupContent);
                    markers[v.placa] = marker;
                }
            }

            // Carregar veículos iniciais
            var veiculos = {{ veiculos | tojson }};
            document.getElementById('total').innerText = veiculos.length;
            document.getElementById('stats-rotas').innerText = veiculos.filter(v => v.rota).length;
            veiculos.forEach(updateVehicle);

            function updateTime() {
                var now = new Date();
                document.getElementById('hora').innerText = now.toLocaleTimeString('pt-BR');
                document.getElementById('footer-time').innerText = now.toLocaleTimeString('pt-BR');
            }
            updateTime();
            setInterval(updateTime, 1000);

            // Atualizar dados
            setInterval(function() {
                fetch('/api/veiculos')
                    .then(r => r.json())
                    .then(data => {
                        document.getElementById('total').innerText = data.length;
                        document.getElementById('stats-rotas').innerText = data.filter(v => v.rota).length;

                        var listHtml = '';
                        data.forEach(v => {
                            listHtml += `
                                <div class="vehicle-card" onclick="selectVehicle('${v.placa}', ${v.lat}, ${v.lng}, ${JSON.stringify(v.rota)}, ${JSON.stringify(v.historico)})">
                                    <div class="vehicle-placa">
                                        <span><i class="fas fa-truck mr-2"></i>${v.placa}</span>
                                        <span class="vehicle-badge">${v.transportadora} | ${v.provedor}</span>
                                    </div>
                                    <div class="vehicle-info"><i class="fas fa-map-pin"></i> <strong>Local:</strong> ${v.descricao || 'N/A'}</div>
                                    <div class="vehicle-info"><i class="fas fa-clock"></i> <strong>Hora:</strong> ${v.data_hora || 'N/A'}</div>
                                    <div class="vehicle-info">
                                        <i class="fas fa-info-circle"></i> <strong>Status:</strong>
                                        <span class="status-badge status-${v.status}">${v.status_texto}${v.status == 'parado' && v.tempo_parado > 0 ? ' (' + v.tempo_parado + ' min)' : ''}</span>
                                    </div>
                                    <div class="vehicle-info">
                                        <i class="fas fa-hashtag"></i> <strong>Liberação:</strong>
                                        <input type="text" id="liberacao_${v.placa}" value="${v.liberacao || ''}" placeholder="Digite o nº" class="liberacao-input" style="width: 120px;" onclick="event.stopPropagation()">
                                        <button class="btn-salvar" onclick="event.stopPropagation(); salvarLiberacao('${v.placa}')">Salvar</button>
                                    </div>
                            `;
                            if (v.rota) {
                                listHtml += `
                                    <div class="progress-bar"><div class="progress-fill" style="width: ${v.rota.progresso}%"></div></div>
                                    <div class="route-info">
                                        <div class="flex justify-between">
                                            <span><i class="fas fa-flag-checkered text-marilog-green"></i> ${v.rota.destino.cidade}/${v.rota.destino.estado}</span>
                                            <span class="text-marilog-gray">${v.rota.km_total_resumido}</span>
                                        </div>
                                    </div>
                                `;
                            }
                            listHtml += `</div>`;
                        });
                        document.getElementById('vehicle-list').innerHTML = listHtml;
                        data.forEach(updateVehicle);
                    });
            }, 30000);
        </script>
    </body>
    </html>
    '''

    return render_template_string(html, veiculos=veiculos)

@app.route('/api/veiculos')
def api_veiculos():
    return jsonify(tracker.get_all_positions())

@app.route('/api/liberacao', methods=['POST'])
def api_liberacao():
    data = request.json
    placa = data.get('placa')
    liberacao = data.get('liberacao')
    if not placa or not liberacao:
        return jsonify({'status': 'error', 'message': 'Placa e liberação são obrigatórios'}), 400
    if tracker.update_liberacao(placa, liberacao):
        return jsonify({'status': 'ok', 'message': 'Liberação salva'})
    else:
        return jsonify({'status': 'error', 'message': 'Erro ao salvar'}), 500

@app.route('/stats')
def stats_page():
    stats = tracker.get_statistics()
    veiculos = tracker.get_all_positions()
    html = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Marilog - Estatísticas</title>
        <style>
            body { background: #0D1B2A; color: white; font-family: Arial; padding: 20px; }
            h1 { color: #66CC33; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
            .stat-card { background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: center; }
            .stat-value { font-size: 2em; color: #66CC33; font-weight: bold; }
            .back-btn { display: inline-block; background: #66CC33; color: #0D1B2A; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
        </style>
    </head>
    <body>
        <a href="/" class="back-btn">← Voltar ao Mapa</a>
        <h1>📊 Estatísticas Marilog</h1>
        <div class="stats-grid">
            <div class="stat-card"><div class="stat-value">''' + str(stats.get('total_veiculos', 0)) + '''</div><div>Total de Veículos</div></div>
            <div class="stat-card"><div class="stat-value">''' + str(stats.get('veiculos_ativos_24h', 0)) + '''</div><div>Ativos 24h</div></div>
            <div class="stat-card"><div class="stat-value">''' + str(stats.get('rotas_reais', 0)) + '''</div><div>Rotas Reais</div></div>
            <div class="stat-card"><div class="stat-value">''' + str(stats.get('total_posicoes', 0)) + '''</div><div>Posições Históricas</div></div>
        </div>
        <h2>Por Transportadora</h2><div class="stats-grid">'''
    for nome, qtd in stats.get('por_transportadora', {}).items():
        html += f'<div class="stat-card"><div class="stat-value">{qtd}</div><div>{nome}</div></div>'
    html += '</div><h2>Por Provedor</h2><div class="stats-grid">'
    for nome, qtd in stats.get('por_provedor', {}).items():
        html += f'<div class="stat-card"><div class="stat-value">{qtd}</div><div>{nome}</div></div>'
    html += '</div><h2>Por Status</h2><div class="stats-grid">'
    status_map = {'em_andamento': '🚛 Em Andamento', 'carregando': '⏫ Carregando', 'descarregando': '⏬ Descarregando', 'parado': '⏸️ Parado'}
    for status, qtd in stats.get('por_status', {}).items():
        nome = status_map.get(status, status)
        html += f'<div class="stat-card"><div class="stat-value">{qtd}</div><div>{nome}</div></div>'
    html += '</div></body></html>'
    return html

if __name__ == '__main__':
    print("\n" + "="*80)
    print("🚛 MARILOG TRANSPORTES - TORRE DE CONTROLE".center(80))
    print("="*80)
    print("📡 Coleta automática: A cada 60 segundos")
    print("🌐 Dashboard: http://localhost:5000")
    print("📊 Stats: http://localhost:5000/stats")
    print("🔌 APIs: Buonny + NOX GR")
    print("="*80 + "\n")
    webbrowser.open('http://localhost:5000')
    app.run(host='127.0.0.1', port=5000, debug=False)