# Real-Time IoT Streaming Pipeline & Analytics Dashboard

Una soluzione **End-to-End** moderna per l'acquisizione, la gestione e la visualizzazione in streaming di dati provenienti da sensori IoT in tempo reale.

---

## Informazioni sul Progetto

Questo progetto dimostra l'architettura completa di una pipeline di dati industriale per il mondo IoT. 

I sensori generano metriche (temperatura, umidità, pressione) che vengono inviate a un broker di messaggi leggero, persistite in un database ottimizzato per serie temporali e infine trasmesse a una dashboard web live in tempo reale tramite WebSockets, evitando il sovraccarico delle richieste HTTP tradizionali.

---

## Caratteristiche Principali

* **Ingestione in Tempo Reale**: Ricezione di flussi di dati continui a bassa latenza via protocollo MQTT.
* **Archiviazione Time-Series**: Database ottimizzato per gestire grandi volumi di dati temporali ed eseguire query ad alte prestazioni.
* **Streaming Bidirezionale**: Connessione diretta WebSockets per aggiornare la dashboard live ad ogni singola misurazione.
* **Dashboard Reattiva**: Interfaccia web moderna in Dark Mode con grafici dinamici multi-canale per il monitoraggio visivo dei sensori.
* **Architettura Disaccoppiata**: Sviluppata a componenti indipendenti e containerizzati per garantire modularità e scalabilità.

---

## Flusso dei Dati

1. **Sensori IoT** ➔ Inviano la telemetria al Broker MQTT.
2. **Ingestion Engine** ➔ Processa i messaggi e li salva sul Database Time-Series.
3. **Backend Server** ➔ Legge i dati e li invia via WebSocket al client.
4. **Dashboard Web** ➔ Renderizza i grafici dal vivo in tempo reale.

---

## Tech Stack

* **Message Broker**: Eclipse Mosquitto (MQTT)
* **Database**: TimescaleDB (PostgreSQL)
* **Backend**: Python, FastAPI, WebSockets
* **Frontend**: HTML5, CSS3, JavaScript, Chart.js
* **Infrastruttura**: Docker
