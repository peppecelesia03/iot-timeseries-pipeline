import json
import random
import time
from xmlrpc import client
import paho.mqtt.client as mqtt

BROKER_HOST = "localhost"
BROKER_PORT = 1883

DEVICES = [

    {"id": "sensor_temp_01", "type": "temperature", "unit": "Celsius",    "base": 22.0,   "range": 3.0},
    {"id": "sensor_temp_02", "type": "temperature", "unit": "Celsius",    "base": 25.0,   "range": 4.0},
    {"id": "sensor_hum_01",  "type": "humidity",    "unit": "Percentage", "base": 50.0,   "range":10.0},
    {"id": "sensor_press_01","type": "pressure",    "unit": "hpa",        "base": 1013.0, "range": 5.0 }

]

def generate_sensor_data(device):
    variation = random.uniform(-device["range"], device["range"])
    value = round(device["base"] + variation, 2)

    return {
        "device_id": device["id"],
        "type": device["type"],
        "value": value,
        "unit": device["unit"],
        "timestamp": time.time()
    }

def main():
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

    print(" Connecting simulator to MQTT broker...")
    client.connect(BROKER_HOST, BROKER_PORT, 60)
    client.loop_start()

    print(" Simulator running! Press Ctrl+C to stop.\n")
    try:
        while True:
            for device in DEVICES:
                payload = generate_sensor_data(device)
                topic = f"iot/sensors/{device['type']}/{device['id']}"

                json_payload = json.dumps(payload)

                client.publish(topic, json_payload)
                print(f"Published on [{topic}]: {json_payload}")

            print("-" * 50)
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n Stopping simulator...")
        client.loop_stop()
        client.disconnect()
        print(" Simulator stopped.")

if __name__ == "__main__":
    main()