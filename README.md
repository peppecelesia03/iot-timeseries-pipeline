# 📡 Real-Time IoT Data Pipeline & Stream Dashboard

Una pipeline End-to-End scalabile per l'ingestione, l'archiviazione time-series e la visualizzazione in tempo reale di metriche provenienti da sensori IoT.

---

## 🏗️ Architettura del Sistema

Il flusso dei dati segue un'architettura ad alte prestazioni basata su disaccoppiamento tramite Message Broker e streaming bidirezionale via WebSockets:

 [ Simulatore Sensori IoT ]
             │
             │ (MQTT Stream)
             ▼
   [ Mosquitto Broker ] ──(Port 1883)
             │
             ▼
  [ Ingestion Engine Python ]
             │
             │ (SQL Transactional Commit)
             ▼
      [ TimescaleDB ] ────(Port 5432)
             │
             ▼
   [ FastAPI Backend ] ───(Port 8000)
             │
             │ (WebSocket Streaming)
             ▼
 [ Dashboard Web Chart.js ]

---

## 🛠️ Tech Stack & Strumenti

| Componente | Tecnologia | Descrizione |
| :--- | :--- | :--- |
| Message Broker | Eclipse Mosquitto | Broker MQTT per il trasporto leggero e a bassa latenza dei messaggi IoT. |
| Database | TimescaleDB | Database Time-Series basato su PostgreSQL per l'analisi temporale ad alte prestazioni. |
| Ingestion Engine | Python (Paho-MQTT, Psycopg2) | Worker per il parsing JSON e l'inserimento atomicamente sicuro dei dati. |
| Backend & WebSockets | FastAPI & Uvicorn | Framework Python asincrono per l'erogazione delle API REST e dello streaming live. |
| Frontend | HTML5, JavaScript, Chart.js | Dashboard grafica moderna in Dark Mode con grafico dinamico in real-time. |
| Infrastruttura | Docker | Containerizzazione dei servizi di supporto (Database e Message Broker). |

---

## 🚀 Guida all'Installazione e Avvio

### 1. Prerequisiti
Assicurati di avere installato sul tuo sistema:
* Python 3.10+
* Docker Engine e Docker CLI

---

### 2. Avvio dei Servizi Docker (Database & Broker)

Apri il terminale ed esegui i container per Mosquitto e TimescaleDB:

# 1. Avvia il Broker MQTT Mosquitto
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto:latest

# 2. Avvia TimescaleDB (PostgreSQL con estensioni time-series)
docker run -d --name timescale_db -p 5432:5432 \
  -e POSTGRES_USER=admin \
  -e POSTGRES_PASSWORD=secretpassword \
  -e POSTGRES_DB=iot_data \
  timescale/timescaledb:latest-pg15

---

### 3. Setup della Tabella nel Database

Crea la tabella sensor_data per accogliere le metriche temporali dei sensori:

docker exec -i timescale_db psql -U admin -d iot_data << 'EOF'
CREATE TABLE IF NOT EXISTS sensor_data (
    timestamp TIMESTAMPTZ NOT NULL,
    device_id VARCHAR(50) NOT NULL,
    sensor_type VARCHAR(50) NOT NULL,
    value NUMERIC(10, 2) NOT NULL,
    unit VARCHAR(20) NOT NULL
);

-- Trasformazione in Hypertable TimescaleDB
SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);
EOF

---

### 4. Configurazione Ambiente Virtuale Python

# Crea e attiva l'ambiente virtuale
python3 -m venv venv
source venv/bin/activate

# Installa tutte le dipendenze necessarie
pip install paho-mqtt psycopg2-binary fastapi uvicorn websockets

---

### 5. Esecuzione dei Moduli della Pipeline

Per far funzionare l'intero flusso, avvia i seguenti servizi nei rispettivi terminali (con il venv attivo):

#### Terminale 1 — Ingestion Engine
In ascolto sul broker MQTT per salvare i dati su TimescaleDB:
python ingestion_engine.py

#### Terminale 2 — Simulatore Sensori IoT
Genera telemetria di temperatura, umidità e pressione ogni pochi secondi:
python sensor_simulator.py

#### Terminale 3 — Web App & Server WebSocket
Avvia l'applicazione FastAPI:
uvicorn app:app --reload

---

## 📊 Dashboard Web Live

Una volta avviati tutti i moduli, apri il browser al seguente indirizzo:

👉 http://localhost:8000

### Caratteristiche dell'Interfaccia:
* Live Telemetry Chart: Grafico della temperatura a doppio canale (sensor_temp_01 e sensor_temp_02) aggiornato dal vivo via WebSocket.
* Auto-Resizing: Finestra temporale scorrevole sugli ultimi punti registrati.
* REST API Endpoint: /api/history disponibile per recuperare lo storico dei dati in formato JSON.

---

## 📄 Licenza

Questo progetto è distribuito sotto Licenza MIT. Libero di essere modificato e riutilizzato.
