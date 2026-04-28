"""
Load Testing untuk SIKAP menggunakan Locust
Test kapasitas sistem, response time, dan stability
"""

from locust import HttpUser, TaskSet, task, between
from locust.contrib.fasthttp import FastHttpUser
import json
import random

# ============ Helper Functions ============

class SikapBehavior(TaskSet):
    """Definisi perilaku user dalam load testing"""
    
    token = None
    user_id = None
    kelas_id = None
    siswa_id = None
    
    def on_start(self):
        """Dijalankan saat user mulai - login dulu"""
        self.login_as_admin()
        self.setup_test_data()
    
    def login_as_admin(self):
        """Login dan ambil JWT token"""
        payload = {
            "username": "loadtest",
            "password": "loadtest123"
        }
        response = self.client.post(
            "/api/v1/auth/login",
            json=payload,
            name="/api/v1/auth/login"
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("data", {}).get("access_token")
            user_data = data.get("data", {}).get("user", {})
            self.user_id = user_data.get("id_user")
    
    def setup_test_data(self):
        """Ambil ID kelas dan siswa untuk testing"""
        headers = self.get_auth_headers()
        
        # Ambil kelas
        response = self.client.get(
            "/api/v1/kelas?page=1&limit=1",
            headers=headers,
            name="/api/v1/kelas"
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                self.kelas_id = data["data"][0]["id_kelas"]
        
        # Ambil siswa
        response = self.client.get(
            "/api/v1/siswa?page=1&limit=1",
            headers=headers,
            name="/api/v1/siswa"
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                self.siswa_id = data["data"][0]["id_siswa"]
    
    def get_auth_headers(self):
        """Return header dengan JWT token"""
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    # ============ Task - Endpoint yang DiTest ============
    
    @task(10)  # Weight: sering di-access
    def read_dashboard(self):
        """GET /api/v1/dashboard - baca dashboard utama"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/dashboard",
            headers=headers,
            name="/api/v1/dashboard"
        )
    
    @task(8)
    def read_attendance_summary(self):
        """GET /api/v1/rekapitulasi/sekolah - baca rekapitulasi sekolah"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/rekapitulasi/sekolah",
            headers=headers,
            name="/api/v1/rekapitulasi/sekolah"
        )
    
    @task(7)
    def read_notifications(self):
        """GET /api/v1/notifikasi - baca notifikasi user"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/notifikasi?page=1&limit=20",
            headers=headers,
            name="/api/v1/notifikasi"
        )
    
    @task(6)
    def read_users_list(self):
        """GET /api/v1/users - list user (admin only)"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/users?page=1&limit=50&role=siswa",
            headers=headers,
            name="/api/v1/users"
        )
    
    @task(5)
    def read_kelas_list(self):
        """GET /api/v1/kelas - list kelas"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/kelas?page=1&limit=20",
            headers=headers,
            name="/api/v1/kelas"
        )
    
    @task(5)
    def read_siswa_in_kelas(self):
        """GET /api/v1/siswa - list siswa"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/siswa?page=1&limit=30",
            headers=headers,
            name="/api/v1/siswa"
        )
    
    @task(4)
    def read_waktu_sholat(self):
        """GET /api/v1/waktu-sholat - baca jadwal waktu sholat"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/waktu-sholat",
            headers=headers,
            name="/api/v1/waktu-sholat"
        )
    
    @task(3)
    def read_rekapitulasi_sekolah(self):
        """GET /api/v1/rekapitulasi/sekolah - baca rekapitulasi sekolah"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/rekapitulasi/sekolah",
            headers=headers,
            name="/api/v1/rekapitulasi/sekolah"
        )
    
    @task(3)
    def read_attendance_history(self):
        """GET /api/v1/absensi - baca history absensi"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/absensi?page=1&limit=50&sort_by=timestamp&sort_dir=desc",
            headers=headers,
            name="/api/v1/absensi"
        )
    
    @task(2)
    def generate_report_pdf(self):
        """POST /api/v1/laporan/generate - generate laporan PDF"""
        if self.kelas_id:
            headers = self.get_auth_headers()
            payload = {
                "jenis_laporan": "ringkasan_kelas",
                "id_kelas": self.kelas_id,
                "format": "pdf",
                "periode_awal": "2026-04-01",
                "periode_akhir": "2026-04-28"
            }
            self.client.post(
                "/api/v1/laporan/generate",
                json=payload,
                headers=headers,
                name="/api/v1/laporan/generate [PDF]"
            )
    
    @task(2)
    def generate_report_excel(self):
        """POST /api/v1/laporan/generate - generate laporan Excel"""
        if self.kelas_id:
            headers = self.get_auth_headers()
            payload = {
                "jenis_laporan": "ringkasan_kelas",
                "id_kelas": self.kelas_id,
                "format": "excel",
                "periode_awal": "2026-04-01",
                "periode_akhir": "2026-04-28"
            }
            self.client.post(
                "/api/v1/laporan/generate",
                json=payload,
                headers=headers,
                name="/api/v1/laporan/generate [EXCEL]"
            )
    
    @task(2)
    def read_izin_list(self):
        """GET /api/v1/izin - baca daftar izin"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/izin?page=1&limit=50",
            headers=headers,
            name="/api/v1/izin"
        )
    
    @task(1)
    def read_school_info(self):
        """GET /api/v1/school - check info sekolah"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/v1/school/",
            headers=headers,
            name="/api/v1/school"
        )


# ============ User Profiles ============

class AdminUser(FastHttpUser):
    """Simulasi admin user"""
    tasks = [SikapBehavior]
    wait_time = between(1, 3)  # Wait 1-3 detik antar request


class TeacherUser(FastHttpUser):
    """Simulasi guru user"""
    tasks = [SikapBehavior]
    wait_time = between(2, 5)  # Wait 2-5 detik antar request


class StudentUser(FastHttpUser):
    """Simulasi siswa user"""
    tasks = [SikapBehavior]
    wait_time = between(3, 8)  # Wait 3-8 detik antar request
