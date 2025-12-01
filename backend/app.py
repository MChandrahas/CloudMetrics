import os
import time
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS
from psycopg2.extras import RealDictCursor

app = Flask(__name__)
CORS(app)  # Allow the frontend to talk to us

# Database Connection Config
DB_HOST = "db"
DB_NAME = "cloudmetrics_db"
DB_USER = "admin"
DB_PASS = "password123"

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        print(f"Error connecting to DB: {e}")
        return None

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/metrics/current')
def get_metrics():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database unavailable"}), 500

    try:
        cur = conn.cursor()
        query = """
            SELECT 
                SUM(calls) as total_calls, 
                SUM(total_exec_time) as total_time_ms 
            FROM pg_stat_statements;
        """
        cur.execute(query)
        result = cur.fetchone()
        
        # --- FIX STARTS HERE ---
        # Force everything to be a standard float to avoid Decimal vs Float errors
        total_calls = float(result['total_calls']) if result['total_calls'] else 0.0
        total_time = float(result['total_time_ms']) if result['total_time_ms'] else 0.0
        
        avg_time = (total_time / total_calls) if total_calls > 0 else 0
        # --- FIX ENDS HERE ---

        cur.close()
        conn.close()

        return jsonify({
            "total_calls": total_calls,
            "avg_query_time_ms": round(avg_time, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Wait for DB to start up
    time.sleep(5) 
    app.run(host='0.0.0.0', port=5000)