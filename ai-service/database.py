import sqlite3
from pathlib import Path


# Database file
DATABASE_PATH = Path(__file__).resolve().parent / "advsystem.db"


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the scan_history table if it does not already exist.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            domain TEXT,
            ads_count INTEGER NOT NULL DEFAULT 0,
            trackers_count INTEGER NOT NULL DEFAULT 0,
            normal_resources INTEGER NOT NULL DEFAULT 0,
            total_resources INTEGER NOT NULL DEFAULT 0,
            risk_score INTEGER NOT NULL DEFAULT 0,
            risk_level TEXT NOT NULL,
            scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    )

    connection.commit()
    connection.close()


def save_scan(
    url,
    domain,
    ads_count,
    trackers_count,
    normal_resources,
    total_resources,
    risk_score,
    risk_level
):
    """
    Save one webpage scan result.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        INSERT INTO scan_history (
            url,
            domain,
            ads_count,
            trackers_count,
            normal_resources,
            total_resources,
            risk_score,
            risk_level
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            url,
            domain,
            ads_count,
            trackers_count,
            normal_resources,
            total_resources,
            risk_score,
            risk_level
        )
    )

    connection.commit()

    scan_id = cursor.lastrowid

    connection.close()

    return scan_id


def get_scan_history():
    """
    Return all previous scans, newest first.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            url,
            domain,
            ads_count,
            trackers_count,
            normal_resources,
            total_resources,
            risk_score,
            risk_level,
            scan_date
        FROM scan_history
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return [dict(row) for row in rows]


def get_dashboard_summary():
    """
    Calculate summary statistics from all stored scans.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            COUNT(*) AS total_scans,
            COALESCE(SUM(ads_count), 0) AS total_ads,
            COALESCE(SUM(trackers_count), 0) AS total_trackers,
            COALESCE(SUM(total_resources), 0) AS total_resources,
            COALESCE(AVG(risk_score), 0) AS average_risk_score,
            COALESCE(
                SUM(
                    CASE
                        WHEN risk_level = 'HIGH' THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS high_risk_scans
        FROM scan_history
        """
    )

    row = cursor.fetchone()

    connection.close()

    return {
        "total_scans": row["total_scans"],
        "total_ads": row["total_ads"],
        "total_trackers": row["total_trackers"],
        "total_resources": row["total_resources"],
        "average_risk_score": round(
            row["average_risk_score"],
            2
        ),
        "high_risk_scans": row["high_risk_scans"]
    }


def delete_scan_history():
    """
    Delete all stored scan history.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("DELETE FROM scan_history")

    connection.commit()
    connection.close()