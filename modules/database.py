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
            CREATE TABLE IF NOT EXISTS rencana_inspeksi (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                mesin         TEXT    NOT NULL,
                tahun         INTEGER NOT NULL,
                n             INTEGER NOT NULL,
                jam_kerja     REAL    NOT NULL,
                waktu_ins     REAL    NOT NULL,
                periode       INTEGER NOT NULL,
                created_at    TEXT    NOT NULL
            );
            CREATE TABLE IF NOT EXISTS jadwal_inspeksi (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                rencana_id    INTEGER NOT NULL,
                mesin         TEXT    NOT NULL,
                tahun         INTEGER NOT NULL,
                bulan         INTEGER NOT NULL,
                minggu        INTEGER NOT NULL,
                FOREIGN KEY (rencana_id) REFERENCES rencana_inspeksi(id)
            );
            CREATE TABLE IF NOT EXISTS realisasi_inspeksi (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                jadwal_id     INTEGER NOT NULL UNIQUE,
                mesin         TEXT    NOT NULL,
                tahun         INTEGER NOT NULL,
                bulan_aktual  INTEGER,
                minggu_aktual INTEGER,
                status        TEXT,
                keterangan    TEXT,
                updated_at    TEXT,
                FOREIGN KEY (jadwal_id) REFERENCES jadwal_inspeksi(id)
            );
        """)

# ── Hari Libur Nasional ───────────────────────────────────────
def fetch_holidays(year: int):
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
    return d.weekday() < 5 and str(d) not in holidays

def work_hours_in_day(start_hour: float, end_hour: float) -> float:
    s = max(start_hour, WORK_START)
    e = min(end_hour,   WORK_END)
    if s >= e:
        return 0.0
    total = e - s
    overlap_start = max(s, BREAK_START)
    overlap_end   = min(e, BREAK_END)
    if overlap_end > overlap_start:
        total -= (overlap_end - overlap_start)
    return max(total, 0.0)

def calc_repair_hours(start_date, start_time, end_date, end_time):
    try:
        s = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M")
        e = datetime.strptime(f"{end_date} {end_time}",     "%Y-%m-%d %H:%M")
        if e <= s:
            return None
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
                    sh = s.hour + s.minute / 60
                    eh = e.hour + e.minute / 60
                    total_hours += work_hours_in_day(sh, eh)
                elif current == s.date():
                    sh = s.hour + s.minute / 60
                    total_hours += work_hours_in_day(sh, WORK_END)
                elif current == end_d:
                    eh = e.hour + e.minute / 60
                    total_hours += work_hours_in_day(WORK_START, eh)
                else:
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

# ── Rencana Inspeksi CRUD ─────────────────────────────────────

def simpan_rencana_inspeksi(mesin: str, tahun: int, n: int,
                             jam_kerja: float, waktu_ins: float,
                             periode: int, jadwal_slots: list) -> int:
    """
    Simpan rencana inspeksi baru (versi baru) beserta jadwal slotnya.
    jadwal_slots: list of (bulan, minggu)
    Return: rencana_id yang baru dibuat
    """
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        cur = conn.execute("""
            INSERT INTO rencana_inspeksi
            (mesin, tahun, n, jam_kerja, waktu_ins, periode, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (mesin, tahun, n, jam_kerja, waktu_ins, periode, created_at))
        rencana_id = cur.lastrowid
        for (bulan, minggu) in jadwal_slots:
            conn.execute("""
                INSERT INTO jadwal_inspeksi
                (rencana_id, mesin, tahun, bulan, minggu)
                VALUES (?, ?, ?, ?, ?)
            """, (rencana_id, mesin, tahun, bulan, minggu))
    return rencana_id


def get_versi_rencana(mesin: str, tahun: int) -> list:
    """
    Ambil semua versi rencana untuk mesin & tahun tertentu.
    Return: list of dict {id, created_at, n}
    """
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT id, n, created_at
            FROM rencana_inspeksi
            WHERE mesin=? AND tahun=?
            ORDER BY created_at DESC
        """, (mesin, tahun)).fetchall()
    return [dict(r) for r in rows]


def get_jadwal_by_rencana(rencana_id: int) -> list:
    """
    Ambil semua slot jadwal untuk rencana_id tertentu,
    beserta data realisasi jika sudah ada.
    """
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT
                j.id         AS jadwal_id,
                j.mesin,
                j.tahun,
                j.bulan,
                j.minggu,
                r.id         AS realisasi_id,
                r.bulan_aktual,
                r.minggu_aktual,
                r.status,
                r.keterangan,
                r.updated_at
            FROM jadwal_inspeksi j
            LEFT JOIN realisasi_inspeksi r ON r.jadwal_id = j.id
            WHERE j.rencana_id = ?
            ORDER BY j.bulan, j.minggu
        """, (rencana_id,)).fetchall()
    return [dict(r) for r in rows]


def get_tahun_tersedia() -> list:
    """Ambil semua tahun yang sudah ada rencana inspeksinya."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT DISTINCT tahun FROM rencana_inspeksi ORDER BY tahun DESC
        """).fetchall()
    return [r["tahun"] for r in rows]


def get_mesin_by_tahun(tahun: int) -> list:
    """Ambil daftar mesin yang punya rencana inspeksi di tahun tertentu."""
    with get_conn() as conn:
        rows = conn.execute("""
            SELECT DISTINCT mesin FROM rencana_inspeksi
            WHERE tahun=? ORDER BY mesin
        """, (tahun,)).fetchall()
    return [r["mesin"] for r in rows]


def simpan_realisasi_batch(realisasi_list: list):
    """
    Simpan/update realisasi inspeksi secara batch.
    realisasi_list: list of dict {
        jadwal_id, mesin, tahun,
        bulan_aktual, minggu_aktual,
        status, keterangan
    }
    """
    updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with get_conn() as conn:
        for r in realisasi_list:
            conn.execute("""
                INSERT INTO realisasi_inspeksi
                (jadwal_id, mesin, tahun, bulan_aktual, minggu_aktual,
                 status, keterangan, updated_at)
                VALUES (:jadwal_id, :mesin, :tahun, :bulan_aktual, :minggu_aktual,
                        :status, :keterangan, :updated_at)
                ON CONFLICT(jadwal_id) DO UPDATE SET
                    bulan_aktual  = excluded.bulan_aktual,
                    minggu_aktual = excluded.minggu_aktual,
                    status        = excluded.status,
                    keterangan    = excluded.keterangan,
                    updated_at    = excluded.updated_at
            """, {**r, "updated_at": updated_at})


def get_rekap_tahunan(mesin: str, tahun: int, rencana_id: int) -> list:
    """Ambil rekap lengkap rencana vs realisasi untuk export Excel."""
    return get_jadwal_by_rencana(rencana_id)