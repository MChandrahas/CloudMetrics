import time
import threading
import psycopg2
import random

# DB Config
DB_HOST = "db"
DB_NAME = "cloudmetrics_db"
DB_USER = "admin"
DB_PASS = "password123"

def run_load(thread_id):
    # Each thread gets its own connection
    try:
        conn = psycopg2.connect(
            host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASS
        )
        cur = conn.cursor()
        print(f"✅ Thread-{thread_id} connected. Starting load...")
        
        while True:
            try:
                # 1. Fast query (High QPS noise)
                for _ in range(5):
                    cur.execute("SELECT 1")
                
                # 2. Slow query (simulates heavy processing)
                # Sleep between 0.1s and 0.5s
                sleep_time = random.uniform(0.1, 0.5)
                cur.execute(f"SELECT pg_sleep({sleep_time})")
                
                # 3. Random "heavy" calculation
                cur.execute("SELECT count(*) FROM pg_stat_statements")
                
                conn.commit()
                # Tiny sleep to prevent crashing your laptop completely
                time.sleep(0.1)
                
            except Exception as e:
                print(f"⚠️ Thread-{thread_id} error: {e}")
                conn.rollback()
                time.sleep(1)
                
    except Exception as e:
        print(f"❌ Thread-{thread_id} connection failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting Load Simulator with 5 concurrent threads...")
    # Launch 5 parallel threads
    threads = []
    for i in range(5):
        t = threading.Thread(target=run_load, args=(i,))
        t.start()
        threads.append(t)
        
    # Keep main thread alive
    for t in threads:
        t.join()