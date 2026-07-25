import time
import paho.mqtt.client as mqtt

TOPIC = "sensors/test/temperature"

def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print("Connecrted successfully to MQTT broker")
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.on_connect = on_connect
client.on_message = on_message

print("Connecting to broker...")
client.connect("localhost", 1883, 60)
client.loop_start()

time.sleep(1)
print(f"Publishing test message to topic '{TOPIC}'...")
client.publish(TOPIC, '{"device_id": "sensor_01", "value":23.5}')

time.sleep(2)
client.loop_stop()
client.disconnect()
print("Test Finished.")