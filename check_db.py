import psycopg2

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iot_data"
DB_USER = "admin"
DB_PASS = "secretpassword"

def check_data():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cursor = conn.cursor()

    # 1. Contiamo i record totali
    cursor.execute("SELECT COUNT(*) FROM sensor_data;")
    total_count = cursor.fetchone()[0]
    print(f" Total records in DB: {total_count}")

    # 2. Ultimi 5 record
    print("\n Last 5 records:")
    cursor.execute("""
        SELECT timestamp, device_id, sensor_type, value, unit
        FROM sensor_data
        ORDER BY timestamp DESC
        LIMIT 5;
    """)
    for row in cursor.fetchall():
        print(f" {row[0]} | Device: {row[1]} | Type: {row[2]} | Value: {row[3]} {row[4]}")

    # 3. Media temperature per dispositivo
    print("\n Average Temperature for each device:")
    cursor.execute("""
        SELECT device_id, ROUND(AVG(value)::numeric, 2) as avg_value
        FROM sensor_data
        WHERE sensor_type = 'temperature'
        GROUP BY device_id;
    """)
    for row in cursor.fetchall():
        # FIX: Usiamo solo row[0] (device_id) e row[1] (avg_value)
        print(f" Device: {row[0]} | Average Temperature: {row[1]} °C")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    check_data()