"""
Main application untuk SkillHub Management System

"""

import streamlit as st
import pandas as pd
import os

from models.participant import Participant
from models.course import Course
from databaseConnection import DatabaseConnection
from models.enrollment import Enrollment
from datetime import datetime

class SkillHubApp:

    def __init__(self):

        if 'db_config' not in st.session_state:
            st.session_state.db_config = {
                'host': os.getenv("DB_HOST", "localhost"),
                'user': os.getenv("DB_USER", "root"),
                'password':  os.getenv("DB_PASSWORD", ""),
                'database': os.getenv("DB_NAME", "skillhub_db")
            }

        self.db = DatabaseConnection(
            host=st.session_state.db_config['host'],
            user=st.session_state.db_config['user'],
            password=st.session_state.db_config['password'],
            database=st.session_state.db_config['database']
        )
        self.main()

    # ==================== DATABASE INITIALIZATION ====================
    def init_database(self) -> bool:
        """
        Inisialisasi struktur database (tabel).
        
        Args:
            db: Instance DatabaseConnection
            
        Returns:
            bool: True jika berhasil, False jika gagal
        """
        try:
            # Tabel participants
            create_participants = """
            CREATE TABLE IF NOT EXISTS participants (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                no_telp VARCHAR(20),
                alamat TEXT,
                tanggal_daftar DATETIME,
                INDEX idx_email (email)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            
            # Tabel courses
            create_courses = """
            CREATE TABLE IF NOT EXISTS courses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nama_kelas VARCHAR(100) NOT NULL,
                deskripsi TEXT,
                instruktur VARCHAR(100),
                tanggal_dibuat DATETIME,
                INDEX idx_nama_kelas (nama_kelas)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            
            # Tabel enrollments (relasi many-to-many)
            create_enrollments = """
            CREATE TABLE IF NOT EXISTS enrollments (
                id INT AUTO_INCREMENT PRIMARY KEY,
                participant_id INT NOT NULL,
                course_id INT NOT NULL,
                tanggal_daftar DATETIME,
                FOREIGN KEY (participant_id) REFERENCES participants(id),
                FOREIGN KEY (course_id) REFERENCES courses(id),
                UNIQUE KEY unique_enrollment (participant_id, course_id),
                INDEX idx_participant (participant_id),
                INDEX idx_course (course_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
            """
            
            self.db.execute_query(create_participants)
            self.db.execute_query(create_courses)
            self.db.execute_query(create_enrollments)
            
            return True
        except Exception as e:
            st.error(f"Error inisialisasi database: {e}")
            return False


    # ==================== UI COMPONENTS ====================
    def show_participant_management(self):
        """Tampilan untuk manajemen data peserta."""
        st.header("📋 Manajemen Data Peserta")
        
        participant_model = Participant(self.db)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "➕ Tambah", "📊 Daftar", "🔍 Detail", "✏️ Edit", "🗑️ Hapus"
        ])
        
        # TAB: Tambah Peserta
        with tab1:
            st.subheader("Tambah Peserta Baru")
            with st.form("add_participant_form"):
                nama = st.text_input("Nama Lengkap *", max_chars=100)
                email = st.text_input("Email *", max_chars=100)
                no_telp = st.text_input("No. Telepon", max_chars=20)
                alamat = st.text_area("Alamat", max_chars=500)
                
                submitted = st.form_submit_button("💾 Simpan Peserta")
                
                if submitted:
                    if not nama or not email:
                        st.error("Nama dan Email wajib diisi!")
                    else:
                        if participant_model.create(nama, email, no_telp, alamat):
                            st.success("✅ Peserta berhasil ditambahkan!")

        
        # TAB: Daftar Peserta
        with tab2:
            st.subheader("Daftar Seluruh Peserta")
            participants = participant_model.get_all()
            
            if participants:
                df = pd.DataFrame(participants)
                df['tanggal_daftar'] = pd.to_datetime(df['tanggal_daftar']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total Peserta: {len(participants)}")
            else:
                st.info("Belum ada data peserta.")
        
        # TAB: Detail Peserta
        with tab3:
            st.subheader("Detail Peserta")
            participants = participant_model.get_all()
            
            if participants:
                participant_options = {f"{p['id']} - {p['nama']}": p['id'] for p in participants}
                selected = st.selectbox("Pilih Peserta", options=list(participant_options.keys()))
                
                if st.button("🔍 Lihat Detail"):
                    participant_id = participant_options[selected]
                    detail = participant_model.get_by_id(participant_id)
                    
                    if detail:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {detail['id']}")
                            st.write(f"**Nama:** {detail['nama']}")
                            st.write(f"**Email:** {detail['email']}")
                        with col2:
                            st.write(f"**No. Telepon:** {detail['no_telp']}")
                            st.write(f"**Alamat:** {detail['alamat']}")
                            st.write(f"**Tanggal Daftar:** {detail['tanggal_daftar']}")
                        
                        # Tampilkan kelas yang diikuti
                        st.divider()
                        st.write("**Kelas yang Diikuti:**")
                        enrollment_model = Enrollment(self.db)
                        courses = enrollment_model.get_courses_by_participant(participant_id)
                        
                        if courses:
                            for course in courses:
                                st.write(f"- {course['nama_kelas']} (Instruktur: {course['instruktur']})")
                        else:
                            st.info("Belum mengikuti kelas apapun.")
            else:
                st.info("Belum ada data peserta.")
        
        # TAB: Edit Peserta
        with tab4:
            st.subheader("Edit Data Peserta")
            participants = participant_model.get_all()
            
            if participants:
                participant_options = {f"{p['id']} - {p['nama']}": p['id'] for p in participants}
                selected = st.selectbox("Pilih Peserta untuk Diedit", options=list(participant_options.keys()))
                
                participant_id = participant_options[selected]
                detail = participant_model.get_by_id(participant_id)
                
                if detail:
                    with st.form("edit_participant_form"):
                        nama = st.text_input("Nama Lengkap *", value=detail['nama'], max_chars=100)
                        email = st.text_input("Email *", value=detail['email'], max_chars=100)
                        no_telp = st.text_input("No. Telepon", value=detail['no_telp'] or "", max_chars=20)
                        alamat = st.text_area("Alamat", value=detail['alamat'] or "", max_chars=500)
                        
                        submitted = st.form_submit_button("💾 Update Data")
                        
                        if submitted:
                            if not nama or not email:
                                st.error("Nama dan Email wajib diisi!")
                            else:
                                if participant_model.update(participant_id, nama, email, no_telp, alamat):
                                    st.session_state["success_edit"] = True
                                    st.experimental_rerun()

                        # Tampilkan setelah reload
                        if st.session_state.get("success_edit"):
                            st.success("✅ Data kelas berhasil diupdate!")
                            del st.session_state["success_edit"]

            else:
                st.info("Belum ada data peserta.")
        
        # TAB: Hapus Peserta
        with tab5:
            st.subheader("Hapus Peserta")
            participants = participant_model.get_all()
            
            if participants:
                participant_options = {f"{p['id']} - {p['nama']}": p['id'] for p in participants}
                selected = st.selectbox("Pilih Peserta untuk Dihapus", options=list(participant_options.keys()))
                
                st.warning("⚠️ Menghapus peserta akan menghapus semua pendaftaran kelas peserta ini!")
                
                if st.button("🗑️ Hapus Peserta", type="primary"):
                    participant_id = participant_options[selected]
                    if participant_model.delete(participant_id):
                        st.session_state["success_delete_participant"] = True
                        st.experimental_rerun()

                if st.session_state.get("success_delete_participant"):   
                    st.success("✅ Participant berhasil dihapus!")
                    del st.session_state["success_delete_participant"]

            else:
                st.info("Belum ada data peserta.")


    def show_course_management(self):
        """Tampilan untuk manajemen data kelas."""
        st.header("🎓 Manajemen Data Kelas")
        
        course_model = Course(self.db)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "➕ Tambah", "📊 Daftar", "🔍 Detail", "✏️ Edit", "🗑️ Hapus"
        ])
        
        # TAB: Tambah Kelas
        with tab1:
            st.subheader("Tambah Kelas Baru")
            with st.form("add_course_form"):
                nama_kelas = st.text_input("Nama Kelas *", max_chars=100)
                deskripsi = st.text_area("Deskripsi", max_chars=1000)
                instruktur = st.text_input("Instruktur *", max_chars=100)
                
                submitted = st.form_submit_button("💾 Simpan Kelas")
                
                if submitted:
                    if not nama_kelas or not instruktur:
                        st.error("Nama Kelas dan Instruktur wajib diisi!")
                    else:
                        if course_model.create(nama_kelas, deskripsi, instruktur):
                            st.success("✅ Kelas berhasil ditambahkan!")
        
        
        # TAB: Daftar Kelas
        with tab2:
            st.subheader("Daftar Seluruh Kelas")
            courses = course_model.get_all()
            
            if courses:
                df = pd.DataFrame(courses)
                df['tanggal_dibuat'] = pd.to_datetime(df['tanggal_dibuat']).dt.strftime('%Y-%m-%d %H:%M')
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.info(f"Total Kelas: {len(courses)}")
            else:
                st.info("Belum ada data kelas.")
        
        # TAB: Detail Kelas
        with tab3:
            st.subheader("Detail Kelas")
            courses = course_model.get_all()
            
            if courses:
                course_options = {f"{c['id']} - {c['nama_kelas']}": c['id'] for c in courses}
                selected = st.selectbox("Pilih Kelas", options=list(course_options.keys()))
                
                if st.button("🔍 Lihat Detail"):
                    course_id = course_options[selected]
                    detail = course_model.get_by_id(course_id)
                    
                    if detail:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**ID:** {detail['id']}")
                            st.write(f"**Nama Kelas:** {detail['nama_kelas']}")
                            st.write(f"**Instruktur:** {detail['instruktur']}")
                        with col2:
                            st.write(f"**Tanggal Dibuat:** {detail['tanggal_dibuat']}")
                        
                        st.write(f"**Deskripsi:** {detail['deskripsi']}")
                        
                        # Tampilkan peserta yang terdaftar
                        st.divider()
                        st.write("**Peserta yang Terdaftar:**")
                        enrollment_model = Enrollment(self.db)
                        participants = enrollment_model.get_participants_by_course(course_id)
                        
                        if participants:
                            for p in participants:
                                st.write(f"- {p['nama']} ({p['email']})")
                        else:
                            st.info("Belum ada peserta yang terdaftar.")
            else:
                st.info("Belum ada data kelas.")
        
        # TAB: Edit Kelas
        with tab4:
            st.subheader("Edit Data Kelas")
            courses = course_model.get_all()
            
            if courses:
                course_options = {f"{c['id']} - {c['nama_kelas']}": c['id'] for c in courses}
                selected = st.selectbox("Pilih Kelas untuk Diedit", options=list(course_options.keys()))
                
                course_id = course_options[selected]
                detail = course_model.get_by_id(course_id)
                
                if detail:
                    with st.form("edit_course_form"):
                        nama_kelas = st.text_input("Nama Kelas *", value=detail['nama_kelas'], max_chars=100)
                        deskripsi = st.text_area("Deskripsi", value=detail['deskripsi'] or "", max_chars=1000)
                        instruktur = st.text_input("Instruktur *", value=detail['instruktur'], max_chars=100)
                        
                        submitted = st.form_submit_button("💾 Update Data")
                        
                        if submitted:
                            if not nama_kelas or not instruktur:
                                st.error("Nama Kelas dan Instruktur wajib diisi!")
                            else:
                                if course_model.update(course_id, nama_kelas, deskripsi, instruktur):
                                    st.session_state["success_edit"] = True
                                    st.experimental_rerun()

                        # Tampilkan setelah reload
                        if st.session_state.get("success_edit"):
                            st.success("✅ Data kelas berhasil diupdate!")
                            del st.session_state["success_edit"]

            else:
                st.info("Belum ada data kelas.")
                
        
        # TAB: Hapus Kelas
        with tab5:
            st.subheader("Hapus Kelas")
            courses = course_model.get_all()
            
            if courses:
                course_options = {f"{c['id']} - {c['nama_kelas']}": c['id'] for c in courses}
                selected = st.selectbox("Pilih Kelas untuk Dihapus", options=list(course_options.keys()))
                
                st.warning("⚠️ Menghapus kelas akan menghapus semua pendaftaran peserta di kelas ini!")
                
                if st.button("🗑️ Hapus Kelas", type="primary"):
                    course_id = course_options[selected]
                    if course_model.delete(course_id):
                        st.session_state["success_delete_course"] = True
                        st.experimental_rerun()

                if st.session_state.get("success_delete_course"):   
                    st.success("✅ Kelas berhasil dihapus!")
                    del st.session_state["success_delete_course"]

            else:
                st.info("Belum ada data kelas.")


    def show_enrollment_management(self):
        """Tampilan untuk manajemen pendaftaran."""
        st.header("📝 Manajemen Pendaftaran")
        
        enrollment_model = Enrollment(self.db)
        participant_model = Participant(self.db)
        course_model = Course(self.db)
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "➕ Daftarkan", "📋Semua Pendaftaran", "👤 Kelas per Peserta", "🎓 Peserta per Kelas", "🗑️ Hapus Pendaftaran"
        ])
        
        # TAB: Daftarkan Peserta ke Kelas
        with tab1:
            st.subheader("Daftarkan Peserta ke Kelas")

            participants = participant_model.get_all()
            courses = course_model.get_all()

            if not participants:
                st.warning("⚠️ Belum ada data peserta. Tambahkan peserta terlebih dahulu.")
                st.stop()

            if not courses:
                st.warning("⚠️ Belum ada data kelas. Tambahkan kelas terlebih dahulu.")
                st.stop()

            participant_options = {f"{p['id']} - {p['nama']}": p['id'] for p in participants}

            selected_participant_label = st.selectbox(
                "Pilih Peserta *",
                options=list(participant_options.keys()),
                key="select_participant" 
            )

            participant_id = participant_options[selected_participant_label]

            # Ambil kelas yang sudah diikuti peserta
            enrolled = enrollment_model.get_courses_by_participant(participant_id)
            enrolled_ids = {e['id'] for e in enrolled}

            # Kelas yang belum diambil
            available_courses = [c for c in courses if c['id'] not in enrolled_ids]

            with st.form("add_enrollment_form"):

                if available_courses:
                    course_options = {
                        f"{c['id']} - {c['nama_kelas']}": c['id']
                        for c in available_courses
                    }

                    selected_course_label = st.selectbox(
                        "Pilih Kelas",
                        options=list(course_options.keys()),
                        key="select_course"
                    )

                    submitted = st.form_submit_button("💾 Daftarkan")

                    if submitted:
                        course_id = course_options[selected_course_label]
                        if enrollment_model.create(participant_id, course_id):
                            st.session_state["success_enrollment"] = True
                            st.experimental_rerun()

                    if st.session_state.get("success_enrollment"):
                        st.success("✅ Peserta berhasil didaftarkan ke kelas!")
                        del st.session_state["success_enrollment"]

                else:
                    st.warning("Peserta ini sudah mengambil semua kelas!")
                    st.form_submit_button("💾 Daftarkan", disabled=True)

        
            # TAB: Semua Pendaftaran
        with tab2:
            st.subheader("📋 Semua Pendaftaran")

            enrollments = enrollment_model.get_all_enrollments()

            if enrollments:
                df = pd.DataFrame(enrollments)
                df['tanggal_daftar'] = pd.to_datetime(df['tanggal_daftar']).dt.strftime('%Y-%m-%d %H:%M')

                st.dataframe(
                    df[['id', 'nama_peserta', 'nama_kelas', 'tanggal_daftar']],
                    use_container_width=True,
                    hide_index=True
                )

                st.info(f"Total Pendaftaran: {len(enrollments)}")
            else:
                st.info("Belum ada data pendaftaran.")

        # TAB: Kelas per Peserta
        with tab3:
            st.subheader("Kelas yang Diikuti Peserta")
            
            participants = participant_model.get_all()
            
            if participants:
                participant_options = {f"{p['id']} - {p['nama']}": p['id'] for p in participants}
                selected = st.selectbox("Pilih Peserta", options=list(participant_options.keys()), key="view_courses")
                
                if st.button("🔍 Lihat Kelas"):
                    participant_id = participant_options[selected]
                    courses = enrollment_model.get_courses_by_participant(participant_id)
                    
                    if courses:
                        st.success(f"Peserta ini mengikuti {len(courses)} kelas:")
                        
                        df = pd.DataFrame(courses)
                        df['tanggal_daftar'] = pd.to_datetime(df['tanggal_daftar']).dt.strftime('%Y-%m-%d %H:%M')
                        display_df = df[['id', 'nama_kelas', 'instruktur', 'deskripsi', 'tanggal_daftar']]
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Peserta ini belum mengikuti kelas apapun.")
            else:
                st.info("Belum ada data peserta.")
        
        # TAB: Peserta per Kelas
        with tab4:
            st.subheader("Peserta yang Terdaftar di Kelas")
            
            courses = course_model.get_all()
            
            if courses:
                course_options = {f"{c['id']} - {c['nama_kelas']}": c['id'] for c in courses}
                selected = st.selectbox("Pilih Kelas", options=list(course_options.keys()), key="view_participants")
                
                if st.button("🔍 Lihat Peserta"):
                    course_id = course_options[selected]
                    participants = enrollment_model.get_participants_by_course(course_id)
                    
                    if participants:
                        st.success(f"Kelas ini diikuti oleh {len(participants)} peserta:")
                        
                        df = pd.DataFrame(participants)
                        df['tanggal_daftar'] = pd.to_datetime(df['tanggal_daftar']).dt.strftime('%Y-%m-%d %H:%M')
                        display_df = df[['id', 'nama', 'email', 'no_telp', 'tanggal_daftar']]
                        st.dataframe(display_df, use_container_width=True, hide_index=True)
                    else:
                        st.info("Belum ada peserta yang terdaftar di kelas ini.")
            else:
                st.info("Belum ada data kelas.")
        
        # TAB: Hapus Pendaftaran
        with tab5:
            st.subheader("Hapus Pendaftaran")
            
            enrollments = enrollment_model.get_all_enrollments()
            
            if enrollments:
                st.info(f"Total Pendaftaran: {len(enrollments)}")
                
                enrollment_options = {
                    f"{e['id']} - {e['nama_peserta']} → {e['nama_kelas']}": 
                    (e['participant_id'], e['course_id']) 
                    for e in enrollments
                }
                
                selected = st.selectbox("Pilih Pendaftaran untuk Dihapus", options=list(enrollment_options.keys()))
                
                st.warning("⚠️ Hanya menghapus relasi pendaftaran, tidak menghapus peserta atau kelas.")
                
                if st.button("🗑️ Hapus Pendaftaran", type="primary"):
                    participant_id, course_id = enrollment_options[selected]
                    if enrollment_model.delete(participant_id, course_id):
                        st.session_state["success_delete_enrollment"] = True
                        st.experimental_rerun()

                if st.session_state.get("success_delete_enrollment"):   
                    st.success("✅ Pendaftaran berhasil dihapus!")
                    del st.session_state["success_delete_enrollment"]

            else:
                st.info("Belum ada data pendaftaran.")


    def show_dashboard(self):
        """Tampilan dashboard dengan statistik."""
        st.header("📊 Dashboard SkillHub")
        
        participant_model = Participant(self.db)
        course_model = Course(self.db)
        enrollment_model = Enrollment(self.db)
        
        # Statistik
        participants = participant_model.get_all()
        courses = course_model.get_all()
        enrollments = enrollment_model.get_all_enrollments()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Total Peserta", len(participants))
        
        with col2:
            st.metric("🎓 Total Kelas", len(courses))
        
        with col3:
            st.metric("📝 Total Pendaftaran", len(enrollments))
        
        st.divider()
        
        # Informasi Terbaru
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🆕 Peserta Terbaru")
            if participants:
                recent_participants = participants[-3:]
                for p in recent_participants:
                    st.write(f"• **{p['nama']}** - {p['email']}")
            else:
                st.info("Belum ada peserta.")
        
        with col2:
            st.subheader("🆕 Kelas Terbaru")
            if courses:
                recent_courses = courses[-3:]
                for c in recent_courses:
                    st.write(f"• **{c['nama_kelas']}** - Instruktur: {c['instruktur']}")
            else:
                st.info("Belum ada kelas.")
        
        st.divider()
        
        st.subheader("🆕 Pendaftaran Terbaru")
        if enrollments:
            df = pd.DataFrame(enrollments[-5:])
            df['tanggal_daftar'] = pd.to_datetime(df['tanggal_daftar']).dt.strftime('%Y-%m-%d %H:%M')
            st.dataframe(df[['nama_peserta', 'nama_kelas', 'tanggal_daftar']], 
                        use_container_width=True, hide_index=True)
        else:
            st.info("Belum ada pendaftaran.")


    # ==================== MAIN APPLICATION ====================
    def main(self):
        """
        Fungsi utama aplikasi.
        Mengatur layout, navigasi, dan alur aplikasi.
        """
        # Konfigurasi halaman
        st.set_page_config(
            page_title="SkillHub Management System",
            page_icon="🎓",
            layout="wide",
            initial_sidebar_state="expanded"
        )
        
        # Header
        st.title("🎓 SkillHub Management System")
        st.markdown("*Sistem Manajemen Kursus Keterampilan*")

        # Inisialisasi menu
        if "menu" not in st.session_state:
            st.session_state["menu"] = "Dashboard"
        
        # Sidebar untuk konfigurasi database
        with st.sidebar:
            st.header("🧭 Menu Navigasi")
            col1 = st.container()
            if st.button("📊 Dashboard", use_container_width=True):
                st.session_state["menu"] = "Dashboard"
            if st.button("👥 Manajemen Peserta", use_container_width=True):
                st.session_state["menu"] = "Manajemen Peserta"
            if st.button("🎓 Manajemen Kelas", use_container_width=True):
                st.session_state["menu"] = "Manajemen Kelas"
            if st.button("📝 Manajemen Pendaftaran", use_container_width=True):
                st.session_state["menu"] = "Manajemen Pendaftaran"
            
        
        # Inisialisasi koneksi database
        try:
            db = DatabaseConnection(
                host=st.session_state.db_config['host'],
                user=st.session_state.db_config['user'],
                password=st.session_state.db_config['password'],
                database=st.session_state.db_config['database']
            )
            
            if db.connect():
                # Inisialisasi tabel jika belum ada
                self.init_database()
                
                # Routing menu
                if st.session_state["menu"] == "Dashboard":
                    self.show_dashboard()
                elif st.session_state["menu"] == "Manajemen Peserta":
                    self.show_participant_management()
                elif st.session_state["menu"] == "Manajemen Kelas":
                    self.show_course_management()
                elif st.session_state["menu"] == "Manajemen Pendaftaran":
                    self.show_enrollment_management()
                
                # Tutup koneksi setelah selesai
                db.disconnect()
            else:
                st.error("❌ Gagal terhubung ke database. Periksa konfigurasi database.")
        
        except Exception as e:
            st.error(f"❌ Error: {e}")


if __name__ == "__main__":
    app = SkillHubApp()   # buat instance class SkillHubApp