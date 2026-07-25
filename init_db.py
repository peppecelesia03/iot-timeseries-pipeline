import psycopg2
import time

DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "iot_data"
DB_USER = "admin"
DB_PASS = "secretpassword"

def init_database():
    print(" Connecting to TimescaleDB...")

    conn = None
    for _ in range(5):
        try:
            conn = psycopg2.connect(
                host=DB_HOST,
                port=DB_PORT,
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS
            )
            break
        except psycopg2.OperationalError:
            print("Database not ready yet, retrying in 2 seconds...")
            time.sleep(2)


    if not conn:
        print(" Could not connect to the database!")
        return

    cursor = conn.cursor()

    cursor.execute("CREATE EXTENSION IF NOT EXISTS timescaledb;")

    create_table_query = """
    CREATE TABLE IF NOT EXISTS sensor_data (
        timestamp TIMESTAMPTZ NOT NULL,
        device_id VARCHAR(50) NOT NULL,
        sensor_type VARCHAR(50) NOT NULL,
        value DOUBLE PRECISION NOT NULL,
        unit VARCHAR(20) NOT NULL  
    );
    """
    cursor.execute(create_table_query)

    try:
        create_hypertable_query = """
        SELECT create_hypertable('sensor_data', 'timestamp', if_not_exists => TRUE);
        """
        cursor.execute(create_hypertable_query)
        print(" Hypertable 'sensor_data' created successfully!")
    except Exception as e:
        print(f"Note on Hypertable creation: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print(" Database setup completed succesfully!")

   
if __name__ == "__main__":
    init_database()


