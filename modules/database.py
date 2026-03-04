import sqlite3
import requests
from datetime import datetime, date, timedelta
from pathlib import Path

DB_PATH = Path("machinetrack.db")

# ── Jam kerja ─────────────────────────────────────────────────
WORK_START    = 8.0        # 08:00
WORK_END      = 17.0       # 17:00
BREAK_START   = 12.5       # 12:30
BREAK_END     = 13.5       # 13:30
WORK_PER_DAY  = 8.0        # jam kerja efektif per hari

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS machine_info (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                mesin     TEXT    NOT NULL UNIQUE,
                merek     TEXT,
                tipe      TEXT,
                tahun     INTEGER,
                serial_no TEXT,
                year      INTEGER
            );
            CREATE TABLE IF NOT EXISTS failure_data (
                id                   INTEGER PRIMARY KEY AUTOINCREMENT,
                mesin                TEXT NOT NULL,
                failure_start_date   TEXT,
                failure_start_time   TEXT,
                failure_type         TEXT,
                failure_details      TEXT,
                repair_complete_date TEXT,
                repair_complete_time TEXT,
                total_repair_hours   REAL,
                FOREIGN KEY (mesin) REFERENCES machine_info(mesin)
            );
            CREATE TABLE IF NOT EXISTS holiday_cache (
                tanggal     TEXT PRIMARY KEY,
                keterangan  TEXT
            );
        """)

# ── Hari Libur Nasional ───────────────────────────────────────
def fetch_holidays(year: int):
    """Ambil hari libur dari API dan simpan ke cache."""
    try:
        url  = f"https://api-harilibur.vercel.app/api?year={year}"
        resp = requests.get(url, timeout=5)
        data = resp.json()
        with get_conn() as conn:
            for item in data:
                conn.execute(
                    "INSERT OR IGNORE INTO holiday_cache (tanggal, keterangan) VALUES (?,?)",
                    (item["holiday_date"], item["holiday_name"])
                )
        return True
    except Exception:
        return False

def get_holidays(year: int):
    """Ambil hari libur dari cache, fetch dari API jika belum ada."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT tanggal FROM holiday_cache WHERE tanggal LIKE ?",
            (f"{year}%",)
        ).fetchall()
    if not rows:
        fetch_holidays(year)
        with get_conn() as conn:
            rows = conn.execute(
                "SELECT tanggal FROM holiday_cache WHERE tanggal LIKE ?",
                (f"{year}%",)
            ).fetchall()
    return set(r["tanggal"] for r in rows)

def is_work_day(d: date, holidays: set) -> bool:
    """Cek apakah hari ini hari kerja (Senin-Jumat, bukan libur)."""
    return d.weekday() < 5 and str(d) not in holidays

def work_hours_in_day(start_hour: float, end_hour: float) -> float:
    """Hitung jam kerja efektif dalam satu hari."""
    # Clip ke jam kerja
    s = max(start_hour, WORK_START)
    e = min(end_hour,   WORK_END)
    if s >= e:
        return 0.0
    total = e - s
    # Kurangi waktu istirahat
    overlap_start = max(s, BREAK_START)
    overlap_end   = min(e, BREAK_END)
    if overlap_end > overlap_start:
        total -= (overlap_end - overlap_start)
    return max(total, 0.0)

def calc_repair_hours(start_date, start_time, end_date, end_time):
    """Hitung TTR berdasarkan jam kerja efektif saja."""
    try:
        s = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        e = datetime.strptime(f"{end_date} {end_time}",     "%Y-%m-%d %H:%M")
        if e <= s:
            return None

        # Kumpulkan semua tahun yang terlibat
        years    = set(range(s.year, e.year + 1))
        holidays = set()
        for yr in years:
            holidays |= get_holidays(yr)

        total_hours = 0.0
        current     = s.date()
        end_d       = e.date()

        while current <= end_d:
            if is_work_day(current, holidays):
                if current == s.date() == end_d:
                    # Mulai dan selesai di hari yang sama
                    sh = s.hour + s.minute / 60
                    eh = e.hour + e.minute / 60
                    total_hours += work_hours_in_day(sh, eh)
                elif current == s.date():
                    # Hari pertama
                    sh = s.hour + s.minute / 60
                    total_hours += work_hours_in_day(sh, WORK_END)
                elif current == end_d:
                    # Hari terakhir
                    eh = e.hour + e.minute / 60
                    total_hours += work_hours_in_day(WORK_START, eh)
                else:
                    # Hari penuh di tengah
                    total_hours += WORK_PER_DAY
            current += timedelta(days=1)

        return round(total_hours, 2) if total_hours > 0 else None
    except Exception:
        return None

# ── Machine Info CRUD ─────────────────────────────────────────
def get_all_machines():
    with get_conn() as conn:
        return conn.execute("SELECT * FROM machine_info ORDER BY mesin").fetchall()

def get_machine_names():
    with get_conn() as conn:
        rows = conn.execute("SELECT mesin FROM machine_info ORDER BY mesin").fetchall()
        return [r["mesin"] for r in rows]

def get_machine_types():
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT tipe FROM machine_info ORDER BY tipe").fetchall()
        return [r["tipe"] for r in rows if r["tipe"]]

def get_machines_by_type(tipe: str):
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT mesin FROM machine_info WHERE tipe=? ORDER BY mesin", (tipe,)
        ).fetchall()
        return [r["mesin"] for r in rows]

def get_machine(mesin: str):
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM machine_info WHERE mesin=?", (mesin,)
        ).fetchone()

def insert_machine(data: dict):
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO machine_info (mesin,merek,tipe,tahun,serial_no,year)
            VALUES (:mesin,:merek,:tipe,:tahun,:serial_no,:year)
        """, data)

def update_machine(mesin: str, data: dict):
    with get_conn() as conn:
        conn.execute("""
            UPDATE machine_info
            SET merek=:merek, tipe=:tipe, tahun=:tahun,
                serial_no=:serial_no, year=:year
            WHERE mesin=:mesin
        """, {**data, "mesin": mesin})

def delete_machine(mesin: str):
    with get_conn() as conn:
        conn.execute("DELETE FROM failure_data WHERE mesin=?",   (mesin,))
        conn.execute("DELETE FROM machine_info WHERE mesin=?",   (mesin,))

# ── Failure Data CRUD ─────────────────────────────────────────
def insert_failure(data: dict):
    h = calc_repair_hours(
        data["failure_start_date"], data["failure_start_time"],
        data["repair_complete_date"], data["repair_complete_time"],
    )
    with get_conn() as conn:
        conn.execute("""
            INSERT INTO failure_data
            (mesin,failure_start_date,failure_start_time,failure_type,
             failure_details,repair_complete_date,repair_complete_time,total_repair_hours)
            VALUES (:mesin,:failure_start_date,:failure_start_time,:failure_type,
                    :failure_details,:repair_complete_date,:repair_complete_time,:hours)
        """, {**data, "hours": h})

def update_failure(record_id: int, data: dict):
    h = calc_repair_hours(
        data["failure_start_date"], data["failure_start_time"],
        data["repair_complete_date"], data["repair_complete_time"],
    )
    with get_conn() as conn:
        conn.execute("""
            UPDATE failure_data
            SET failure_start_date=:failure_start_date,
                failure_start_time=:failure_start_time,
                failure_type=:failure_type,
                failure_details=:failure_details,
                repair_complete_date=:repair_complete_date,
                repair_complete_time=:repair_complete_time,
                total_repair_hours=:hours
            WHERE id=:id
        """, {**data, "hours": h, "id": record_id})

def delete_failure(record_id: int):
    with get_conn() as conn:
        conn.execute("DELETE FROM failure_data WHERE id=?", (record_id,))

def get_failures_by_machine(mesin: str):
    with get_conn() as conn:
        return conn.execute(
            """SELECT * FROM failure_data WHERE mesin=?
               ORDER BY failure_start_date DESC, failure_start_time DESC""",
            (mesin,)
        ).fetchall()

def get_all_failures():
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM failure_data ORDER BY failure_start_date DESC"
        ).fetchall()

def get_ttr_by_machine(mesin: str):
    with get_conn() as conn:
        rows = conn.execute(
            """SELECT total_repair_hours FROM failure_data
               WHERE mesin=? AND failure_type='Corrective'
               AND total_repair_hours IS NOT NULL AND total_repair_hours > 0
               ORDER BY failure_start_date""",
            (mesin,)
        ).fetchall()
        return [r["total_repair_hours"] for r in rows]