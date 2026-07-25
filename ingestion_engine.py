import json
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
import psycopg2

MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TOPIC_PATTERN = "iot/sensors/#"

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iot_data"
DB_USER = "admin"
DB_PASS = "secretpassword"

print(" Connecting to TimescaleDB...")
db_conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASS
)
db_cursor = db_conn.cursor()
print(" Connected to Database!")

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f" Connected to MQTT Broker!, Subscribing to '{TOPIC_PATTERN}'...")
        client.subscribe(TOPIC_PATTERN)
    else:
        print(f" Failed to connect to MQTT Broker, return code: {rc}")

def on_message(client, userdata, msg):
    try:
        payload_str = msg.payload.decode('utf-8')
        data = json.loads(payload_str)

        dt_object = datetime.fromtimestamp(data["timestamp"], tz = timezone.utc)

        insert_query = """
        INSERT INTO sensor_data (timestamp, device_id, sensor_type, value, unit)
        VALUES (%s, %s, %s, %s, %s);
        """

        db_cursor.execute(insert_query, (
            dt_object,
            data["device_id"],
            data["type"],
            data["value"],
            data["unit"]
        ))

        db_conn.commit()

        print(f" [STORED] {data['device_id']} ({data['type']}): {data['value']} {data['unit']}")

    except json.JSONDecodeError:
        print(f" Error: Received invalid JSON payload on {msg.topic}")
    except KeyError as e:
        print(f" Error: Missing key in JSON payload: {e}")
    except Exception as e:
        print(f" Database Insert Error: {e}")

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.on_connect = on_connect
    client.on_message = on_message

    print(" Connecting to MQTT Broker...")
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print("\n Stopping Ingestion Engine...")
        client.disconnect()
        db_cursor.close()
        db_conn.close()
        print(" Engine stopped safely.")

if __name__ == "__main__":
    main()