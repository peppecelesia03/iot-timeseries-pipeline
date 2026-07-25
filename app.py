import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import psycopg2

app = FastAPI(title="IoT Analytics Dashboard")

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iot_data"
DB_USER = "admin"
DB_PASS = "secretpassword"

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASS
    )

html_code = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <title>IoT Live Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
        .container { max-width: 1000px; margin: 0 auto; }
        h1 { text-align: center; color: #38bdf8; font-weight: 600; }
        .status { text-align: center; font-size: 0.9em; margin-bottom: 20px; color: #4ade80; }
        .card { background-color: #1e293b; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3); margin-bottom: 20px; }
        canvas { width: 100% !important; max-height: 400px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📡 IoT Sensor Stream - TimescaleDB</h1>
        <div class="status" id="connection-status">🟢 Connesso al WebSocket Backend</div>

        <div class="card">
            <canvas id="tempChart"></canvas>
        </div>
    </div>

    <script>
        const ctx = document.getElementById('tempChart').getContext('2d');
        const tempChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Sensor Temp 01 (°C)',
                        borderColor: '#38bdf8',
                        backgroundColor: 'rgba(56, 189, 248, 0.2)',
                        data: [],
                        tension: 0.3,
                        fill: true
                    },
                    {
                        label: 'Sensor Temp 02 (°C)',
                        borderColor: '#f43f5e',
                        backgroundColor: 'rgba(244, 63, 94, 0.2)',
                        data: [],
                        tension: 0.3,
                        fill: true
                    }
                ]
            },
            options: {
                responsive: true,
                scales: {
                    x: { title: { display: true, text: 'Ora', color: '#94a3b8' }, ticks: { color: '#94a3b8' } },
                    y: { 
                        title: { display: true, text: 'Temperatura (°C)', color: '#94a3b8' }, 
                        ticks: { color: '#94a3b8' },
                        suggestedMin: 15,
                        suggestedMax: 35
                    }
                },
                plugins: {
                    legend: { labels: { color: '#f8fafc' } }
                }
            }
        });

        const ws = new WebSocket("ws://" + window.location.host + "/ws");

        ws.onmessage = function(event) {
            try {
                const dataList = JSON.parse(event.data);
                
                // dataList contiene entrambi i sensori
                dataList.forEach(data => {
                    let datasetIndex = -1;
                    if (data.device_id === 'sensor_temp_01') datasetIndex = 0;
                    if (data.device_id === 'sensor_temp_02') datasetIndex = 1;

                    if (datasetIndex !== -1) {
                        const timeStr = new Date(data.timestamp).toLocaleTimeString();

                        // Aggiorniamo l'asse X con l'ora
                        if (datasetIndex === 0 && (tempChart.data.labels.length === 0 || tempChart.data.labels[tempChart.data.labels.length - 1] !== timeStr)) {
                            tempChart.data.labels.push(timeStr);
                            if (tempChart.data.labels.length > 15) {
                                tempChart.data.labels.shift();
                            }
                        }

                        tempChart.data.datasets[datasetIndex].data.push(data.value);
                        if (tempChart.data.datasets[datasetIndex].data.length > 15) {
                            tempChart.data.datasets[datasetIndex].data.shift();
                        }
                    }
                });

                tempChart.update();
            } catch (err) {
                console.error("Errore grafico:", err);
            }
        };

        ws.onclose = function() {
            document.getElementById('connection-status').innerText = "🔴 WebSocket Disconnesso";
            document.getElementById('connection-status').style.color = "#f43f5e";
        };
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    return HTMLResponse(content=html_code)

@app.get("/api/history")
def get_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, device_id, sensor_type, value, unit 
        FROM sensor_data 
        ORDER BY timestamp DESC 
        LIMIT 10;
    """)
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return {
        "history": [
            {
                "timestamp": row[0].isoformat(),
                "device_id": row[1],
                "sensor_type": row[2],
                "value": row[3],
                "unit": row[4]
            }
            for row in rows
        ]
    }

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Prende l'ultimo valore sia di sensor_temp_01 che di sensor_temp_02
            cursor.execute("""
                SELECT DISTINCT ON (device_id) timestamp, device_id, sensor_type, value, unit
                FROM sensor_data
                WHERE sensor_type = 'temperature'
                ORDER BY device_id, timestamp DESC;
            """)
            rows = cursor.fetchall()
            cursor.close()
            conn.close()

            if rows:
                payload_list = [
                    {
                        "timestamp": row[0].isoformat(),
                        "device_id": row[1],
                        "sensor_type": row[2],
                        "value": row[3],
                        "unit": row[4]
                    }
                    for row in rows
                ]
                # Invia l'elenco con entrambi i sensori
                await websocket.send_text(json.dumps(payload_list))
            
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass