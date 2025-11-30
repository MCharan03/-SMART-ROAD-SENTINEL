import sqlite3
import datetime
import os
import shutil
import glob
import csv
import io
from flask import make_response # Removed request

class DataManager:
    def __init__(self, db_path='database.db', local_data_dir=None, retention_days=30):
        self.db_path = db_path
        self.local_data_dir = local_data_dir
        self.retention_days = retention_days
        self.conn = self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS potholes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                timestamp DATETIME NOT NULL,
                session_timestamp TEXT,
                image_filename TEXT,
                confidence REAL
            )
        ''')
        conn.commit()
        return conn

    def add_pothole_entry(self, latitude, longitude, timestamp, session_timestamp=None, image_filename=None, confidence=None):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO potholes (latitude, longitude, timestamp, session_timestamp, image_filename, confidence) VALUES (?, ?, ?, ?, ?, ?)",
                       (latitude, longitude, timestamp, session_timestamp, image_filename, confidence))
        self.conn.commit()
        return cursor.lastrowid

    def cleanup_old_data(self):
        """Cleans up old data (image directories and DB entries) based on retention policy."""
        if not self.local_data_dir or not os.path.exists(self.local_data_dir):
            print(f"Cleanup: Data root directory {self.local_data_dir} does not exist or is not set.")
            return

        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=self.retention_days)

        # Clean up file system directories
        for session_dir_path in glob.glob(os.path.join(self.local_data_dir, '*')):
            if os.path.isdir(session_dir_path):
                try:
                    dir_name = os.path.basename(session_dir_path)
                    try:
                        session_date = datetime.datetime.strptime(dir_name, '%Y-%m-%d_%H-%M-%S')
                    except ValueError:
                        session_date = datetime.datetime.strptime(dir_name.split('_')[0], '%Y-%m-%d')
                    
                    if session_date < cutoff_date:
                        print(f"Cleanup: Deleting old session directory {session_dir_path}")
                        shutil.rmtree(session_dir_path)
                except Exception as e:
                    print(f"Cleanup: Error processing directory {session_dir_path}: {e}")

        # Clean up database entries
        try:
            cursor = self.conn.cursor()
            cutoff_timestamp_str = cutoff_date.strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute("DELETE FROM potholes WHERE timestamp < ?", (cutoff_timestamp_str,))
            self.conn.commit()
            print(f"Cleanup: Deleted database entries older than {cutoff_date}")
        except Exception as e:
            print(f"Cleanup: Error cleaning database: {e}")

    def export_pothole_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, latitude, longitude, timestamp, confidence FROM potholes ORDER BY timestamp DESC")
        potholes = cursor.fetchall()

        si = io.StringIO()
        cw = csv.writer(si)
        
        cw.writerow(['ID', 'Latitude', 'Longitude', 'Timestamp', 'Confidence'])
        
        for pothole in potholes:
            cw.writerow(pothole)
        
        output = make_response(si.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=pothole_data.csv"
        output.headers["Content-type"] = "text/csv"
        return output

    def get_historical_potholes_data(self, date_filter_str=None):
        query = "SELECT id, latitude, longitude, timestamp, confidence FROM potholes"
        params = []

        if date_filter_str:
            try:
                datetime.datetime.strptime(date_filter_str, '%Y-%m-%d')
                query += " WHERE DATE(timestamp) = ?"
                params.append(date_filter_str)
            except ValueError:
                # Return an error or handle invalid date gracefully
                return {"error": "Invalid date format. Use YYYY-MM-DD."}, 400
        
        query += " ORDER BY timestamp DESC"

        cursor = self.conn.cursor()
        cursor.execute(query, tuple(params))
        potholes_data = cursor.fetchall()

        potholes_list = []
        for pothole in potholes_data:
            potholes_list.append({
                "id": pothole[0],
                "latitude": pothole[1],
                "longitude": pothole[2],
                "timestamp": datetime.datetime.strptime(pothole[3], '%Y-%m-%d %H:%M:%S').isoformat(),
                "confidence": pothole[4]
            })
        
        return potholes_list, 200

    def get_summary_statistics_data(self):
        cursor = self.conn.cursor()

        total_defects = cursor.execute("SELECT COUNT(*) FROM potholes").fetchone()[0]

        today = datetime.date.today()
        start_of_today_str = today.strftime('%Y-%m-%d %H:%M:%S')
        defects_today = cursor.execute("SELECT COUNT(*) FROM potholes WHERE timestamp >= ?", (start_of_today_str,)).fetchone()[0]

        seven_days_ago = today - datetime.timedelta(days=7)
        start_of_seven_days_ago_str = seven_days_ago.strftime('%Y-%m-%d %H:%M:%S')
        defects_7_days = cursor.execute("SELECT COUNT(*) FROM potholes WHERE timestamp >= ?", (start_of_seven_days_ago_str,)).fetchone()[0]
        
        return {
            "total_defects": total_defects,
            "defects_today": defects_today,
            "defects_7_days": defects_7_days,
            "most_common_defect": "Pothole" # Currently only one type
        }, 200

    def get_defect_details(self, defect_id):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, latitude, longitude, timestamp, session_timestamp, image_filename, confidence FROM potholes WHERE id = ?", (defect_id,))
        defect = cursor.fetchone()

        if not defect:
            return {"error": "Defect not found"}, 404

        # Reconstruct image URL
        image_url = None
        if defect[4] and defect[5]: # session_timestamp and image_filename exist
            image_url = f"/images/{defect[4]}/{defect[5]}"

        return {
            "id": defect[0],
            "latitude": defect[1],
            "longitude": defect[2],
            "timestamp": datetime.datetime.strptime(defect[3], '%Y-%m-%d %H:%M:%S').isoformat(),
            "session_timestamp": defect[4],
            "image_filename": defect[5],
            "confidence": defect[6],
            "image_url": image_url
        }, 200

    def close(self):
        self.conn.close()