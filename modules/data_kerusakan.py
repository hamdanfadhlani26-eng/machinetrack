import streamlit as st
import pandas as pd
from datetime import date, time
from modules import database
from modules.theme import page_header, step_badge

def show():
    page_header("📋", "Data Kerusakan", "Manajemen mesin dan riwayat kerusakan")

    tab_mesin, tab_failure = st.tabs(["🏭  Manajemen Mesin", "🔧  Data Kerusakan"])

    # ── TAB 1: Manajemen Mesin ─────────────────────────────
    with tab_mesin:
        step_badge("01", "Daftar Mesin")

        if st.button("➕  Tambah Mesin Baru"):
            st.session_state["show_add_machine"] = True

        if st.session_state.get("show_add_machine"):
            with st.form("form_add_machine", clear_on_submit=True):
                st.markdown("#### Form Tambah Mesin")
                c1, c2 = st.columns(2)
                mesin     = c1.text_input("Nama Mesin *",  placeholder="CNC-01")
                merek     = c2.text_input("Merek",         placeholder="Fanuc")
                tipe      = c1.text_input("Tipe / Model",  placeholder="Robodrill")
                tahun     = c2.number_input("Tahun Mesin", min_value=1990, max_value=2100, value=2020, step=1)
                serial_no = c1.text_input("Serial No",     placeholder="SN-XXXXX")
                year      = c2.number_input("Tahun Data",  min_value=2000, max_value=2100, value=date.today().year, step=1)

                cs, cc = st.columns(2)
                submitted = cs.form_submit_button("💾  Simpan", use_container_width=True)
                cancelled = cc.form_submit_button("✖  Batal",  use_container_width=True)

                if submitted:
                    if not mesin:
                        st.error("Nama mesin wajib diisi.")
                    else:
                        try:
                            database.insert_machine({
                                "mesin":     mesin,
                                "merek":     merek,
                                "tipe":      tipe,
                                "tahun":     int(tahun),
                                "serial_no": serial_no,
                                "year":      int(year),
                            })
                            st.success(f"Mesin **{mesin}** berhasil ditambahkan.")
                            st.session_state["show_add_machine"] = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal: {e}")
                if cancelled:
                    st.session_state["show_add_machine"] = False
                    st.rerun()

        all_machines = database.get_all_machines()
        if not all_machines:
            st.info("Belum ada data mesin. Klik **Tambah Mesin Baru** untuk memulai.")
        else:
            df_m = pd.DataFrame([dict(r) for r in all_machines])
            df_m = df_m.drop(columns=["id"], errors="ignore")
            df_m.columns = [c.replace("_", " ").title() for c in df_m.columns]
            st.dataframe(df_m, use_container_width=True, hide_index=True)

            step_badge("02", "Edit / Hapus Mesin")
            sel_mesin = st.selectbox("Pilih mesin", [r["mesin"] for r in all_machines], key="sel_edit_mesin")

            if sel_mesin:
                m = database.get_machine(sel_mesin)
                col_e, col_d = st.columns(2)
                with col_e:
                    if st.button("✏️  Edit Mesin", use_container_width=True):
                        st.session_state["edit_machine"] = sel_mesin
                with col_d:
                    if st.button("🗑️  Hapus Mesin", use_container_width=True):
                        st.session_state["confirm_del_machine"] = sel_mesin

                if st.session_state.get("confirm_del_machine") == sel_mesin:
                    st.warning(f"⚠️ Yakin hapus mesin **{sel_mesin}**? Semua data kerusakannya ikut terhapus.")
                    c1, c2 = st.columns(2)
                    if c1.button("✅  Ya, Hapus", use_container_width=True):
                        database.delete_machine(sel_mesin)
                        st.success(f"Mesin **{sel_mesin}** berhasil dihapus.")
                        st.session_state.pop("confirm_del_machine", None)
                        st.rerun()
                    if c2.button("Batal", use_container_width=True):
                        st.session_state.pop("confirm_del_machine", None)
                        st.rerun()

                if st.session_state.get("edit_machine") == sel_mesin:
                    with st.form("form_edit_machine"):
                        st.markdown(f"#### Edit: {sel_mesin}")
                        c1, c2 = st.columns(2)
                        e_merek  = c1.text_input("Merek",        value=m["merek"]     or "")
                        e_tipe   = c2.text_input("Tipe / Model", value=m["tipe"]      or "")
                        e_tahun  = c1.number_input("Tahun Mesin", min_value=1990, max_value=2100, value=int(m["tahun"] or 2020))
                        e_serial = c2.text_input("Serial No",    value=m["serial_no"] or "")
                        e_year   = c1.number_input("Tahun Data",  min_value=2000, max_value=2100, value=int(m["year"] or date.today().year))
                        cs, cc   = st.columns(2)
                        if cs.form_submit_button("💾  Simpan", use_container_width=True):
                            database.update_machine(sel_mesin, {
                                "merek":     e_merek,
                                "tipe":      e_tipe,
                                "tahun":     int(e_tahun),
                                "serial_no": e_serial,
                                "year":      int(e_year),
                            })
                            st.success("Data mesin berhasil diperbarui.")
                            st.session_state.pop("edit_machine", None)
                            st.rerun()
                        if cc.form_submit_button("✖  Batal", use_container_width=True):
                            st.session_state.pop("edit_machine", None)
                            st.rerun()

    # ── TAB 2: Data Kerusakan ──────────────────────────────
    with tab_failure:
        types = database.get_machine_types()
        if not types:
            st.warning("Tambahkan mesin terlebih dahulu di tab **Manajemen Mesin**.")
            return

        step_badge("01", "Pilih Tipe & Mesin")
        c1, c2 = st.columns(2)
        sel_tipe   = c1.selectbox("Tipe Mesin", types, key="sel_tipe")
        mesin_list = database.get_machines_by_type(sel_tipe) if sel_tipe else []
        sel_mesin  = c2.selectbox("Mesin", mesin_list, key="sel_failure_mesin") if mesin_list else None

        if not sel_mesin:
            st.info("Tidak ada mesin untuk tipe ini.")
            return

        m_info = database.get_machine(sel_mesin)
        if m_info:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Mesin",      m_info["mesin"])
            c2.metric("Merek",      m_info["merek"]     or "—")
            c3.metric("Serial No",  m_info["serial_no"] or "—")
            c4.metric("Tahun Data", m_info["year"]      or "—")

        st.markdown("---")

        if st.button("➕  Tambah Data Kerusakan"):
            st.session_state["show_add_failure"] = True

        if st.session_state.get("show_add_failure"):
            with st.form("form_add_failure", clear_on_submit=True):
                st.markdown(f"#### Tambah Kerusakan — {sel_mesin}")
                c1, c2 = st.columns(2)
                fs_date   = c1.date_input("Failure Start Date *", value=date.today())
                fs_time   = c2.time_input("Failure Start Time *", value=time(8, 0))
                f_type    = c1.selectbox("Failure Type", ["Corrective", "Preventive"])
                f_details = c2.text_area("Failure Details", placeholder="Deskripsi kerusakan...")
                rc_date   = c1.date_input("Repair Complete Date", value=date.today())
                rc_time   = c2.time_input("Repair Complete Time", value=time(9, 0))

                h = database.calc_repair_hours(
                    str(fs_date), fs_time.strftime("%H:%M"),
                    str(rc_date), rc_time.strftime("%H:%M")
                )
                if h:
                    st.info(f"⏱️  Total Repair Hours (jam kerja efektif): **{h} jam**")
                else:
                    st.warning("⚠️ Periksa kembali tanggal dan waktu.")

                cs, cc = st.columns(2)
                if cs.form_submit_button("💾  Simpan", use_container_width=True):
                    if not h:
                        st.error("Waktu tidak valid.")
                    else:
                        database.insert_failure({
                            "mesin":                sel_mesin,
                            "failure_start_date":   str(fs_date),
                            "failure_start_time":   fs_time.strftime("%H:%M"),
                            "failure_type":         f_type,
                            "failure_details":      f_details,
                            "repair_complete_date": str(rc_date),
                            "repair_complete_time": rc_time.strftime("%H:%M"),
                        })
                        st.success("Data kerusakan berhasil disimpan.")
                        st.session_state["show_add_failure"] = False
                        st.rerun()
                if cc.form_submit_button("✖  Batal", use_container_width=True):
                    st.session_state["show_add_failure"] = False
                    st.rerun()

        step_badge("02", f"Riwayat Kerusakan — {sel_mesin}")
        rows = database.get_failures_by_machine(sel_mesin)
        if not rows:
            st.info("Belum ada data kerusakan untuk mesin ini.")
        else:
            df = pd.DataFrame([dict(r) for r in rows])
            disp = df[["id", "failure_start_date", "failure_start_time", "failure_type",
                        "failure_details", "repair_complete_date", "repair_complete_time",
                        "total_repair_hours"]].copy()
            disp.columns = ["ID", "Fail Date", "Fail Time", "Type", "Details",
                             "Repair Date", "Repair Time", "Hours"]
            st.dataframe(disp, use_container_width=True, hide_index=True)

            step_badge("03", "Edit / Hapus Record")
            sel_id = st.selectbox("Pilih ID", [r["id"] for r in rows], key="sel_rec_id")

            if sel_id:
                rec = next(r for r in rows if r["id"] == sel_id)
                col_e, col_d = st.columns(2)
                with col_e:
                    if st.button("✏️  Edit Record", use_container_width=True):
                        st.session_state["edit_failure_id"] = sel_id
                with col_d:
                    if st.button("🗑️  Hapus Record", use_container_width=True):
                        st.session_state["confirm_del_failure"] = sel_id

                if st.session_state.get("confirm_del_failure") == sel_id:
                    st.warning(f"Yakin hapus record ID {sel_id}?")
                    c1, c2 = st.columns(2)
                    if c1.button("✅  Ya, Hapus", key="yes_del_f", use_container_width=True):
                        database.delete_failure(sel_id)
                        st.success("Record berhasil dihapus.")
                        st.session_state.pop("confirm_del_failure", None)
                        st.rerun()
                    if c2.button("Batal", key="no_del_f", use_container_width=True):
                        st.session_state.pop("confirm_del_failure", None)
                        st.rerun()

                if st.session_state.get("edit_failure_id") == sel_id:
                    with st.form("form_edit_failure"):
                        st.markdown(f"#### Edit Record ID {sel_id}")
                        c1, c2 = st.columns(2)
                        e_fs_date   = c1.date_input("Failure Start Date", value=pd.to_datetime(rec["failure_start_date"]).date())
                        e_fs_time   = c2.time_input("Failure Start Time", value=pd.to_datetime(rec["failure_start_time"], format="%H:%M").time())
                        e_f_type    = c1.selectbox("Failure Type", ["Corrective", "Preventive"], index=0 if rec["failure_type"] == "Corrective" else 1)
                        e_f_details = c2.text_area("Failure Details", value=rec["failure_details"] or "")
                        e_rc_date   = c1.date_input("Repair Complete Date", value=pd.to_datetime(rec["repair_complete_date"]).date())
                        e_rc_time   = c2.time_input("Repair Complete Time", value=pd.to_datetime(rec["repair_complete_time"], format="%H:%M").time())
                        cs, cc = st.columns(2)
                        if cs.form_submit_button("💾  Simpan", use_container_width=True):
                            database.update_failure(sel_id, {
                                "failure_start_date":   str(e_fs_date),
                                "failure_start_time":   e_fs_time.strftime("%H:%M"),
                                "failure_type":         e_f_type,
                                "failure_details":      e_f_details,
                                "repair_complete_date": str(e_rc_date),
                                "repair_complete_time": e_rc_time.strftime("%H:%M"),
                            })
                            st.success("Record berhasil diperbarui.")
                            st.session_state.pop("edit_failure_id", None)
                            st.rerun()
                        if cc.form_submit_button("✖  Batal", use_container_width=True):
                            st.session_state.pop("edit_failure_id", None)
                            st.rerun()