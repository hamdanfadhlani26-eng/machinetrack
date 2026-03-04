# ============================================================
#  seed_data.py
#  Jalankan: python seed_data.py
# ============================================================

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from modules.database import init_db, insert_machine, insert_failure, get_machine_names

machines = [
    {
        "mesin":     "CNC CUTTING",
        "merek":     "ERGOSTAR",
        "tipe":      "EXA 4500",
        "tahun":     2012,
        "serial_no": "",
        "year":      2024,
    },
]

failures = [
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-04-16", "failure_start_time": "08:00", "failure_type": "Preventive", "failure_details": "General Cleaning",                                              "repair_complete_date": "2024-04-16", "repair_complete_time": "12:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-07-29", "failure_start_time": "09:00", "failure_type": "Corrective", "failure_details": "Pelumasan bearing X Axis",                                      "repair_complete_date": "2024-07-29", "repair_complete_time": "11:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-08-05", "failure_start_time": "13:00", "failure_type": "Corrective", "failure_details": "Perbaikan ac pendingin dan kalibrasi rel",                      "repair_complete_date": "2024-08-08", "repair_complete_time": "10:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-08-22", "failure_start_time": "08:00", "failure_type": "Corrective", "failure_details": "Plasma cutting tidak berfungsi / short pada filter capasitor",  "repair_complete_date": "2024-08-27", "repair_complete_time": "12:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-09-09", "failure_start_time": "09:00", "failure_type": "Corrective", "failure_details": "Bearing motor torch rusak",                                     "repair_complete_date": "2024-09-10", "repair_complete_time": "15:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-09-17", "failure_start_time": "08:00", "failure_type": "Corrective", "failure_details": "Mesin mati total",                                             "repair_complete_date": "2024-09-19", "repair_complete_time": "10:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-10-16", "failure_start_time": "08:00", "failure_type": "Corrective", "failure_details": "Mesin mati total",                                             "repair_complete_date": "2024-10-17", "repair_complete_time": "10:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-10-23", "failure_start_time": "08:00", "failure_type": "Corrective", "failure_details": "Perbaikan ac pendingin dan kalibrasi rel",                     "repair_complete_date": "2024-11-08", "repair_complete_time": "17:00"},
    {"mesin": "CNC CUTTING", "failure_start_date": "2024-11-26", "failure_start_time": "08:00", "failure_type": "Corrective", "failure_details": "Ganti CF Card software cadangan",                             "repair_complete_date": "2024-11-27", "repair_complete_time": "12:00"},
]

def main():
    print("Inisialisasi database...")
    init_db()

    existing = get_machine_names()

    print("Memasukkan data mesin...")
    for m in machines:
        if m["mesin"] not in existing:
            insert_machine(m)
            print(f"  ✅ Mesin {m['mesin']} ditambahkan.")
        else:
            print(f"  ⚠️  Mesin {m['mesin']} sudah ada, dilewati.")

    print("Memasukkan data kerusakan...")
    for f in failures:
        insert_failure(f)
        print(f"  ✅ {f['failure_start_date']} — {f['failure_details'][:40]}")

    print("\n🎉 Selesai! Database berhasil diisi.")

if __name__ == "__main__":
    main()