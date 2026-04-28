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
            "username": "admin",
            "password": "admin12345"
        }
        response = self.client.post(
            "/api/auth/login",
            json=payload,
            name="/api/auth/login"
        )
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.user_id = data.get("user_id")
    
    def setup_test_data(self):
        """Ambil ID kelas dan siswa untuk testing"""
        headers = self.get_auth_headers()
        
        # Ambil kelas
        response = self.client.get(
            "/api/kelas?page=1&limit=1",
            headers=headers,
            name="/api/kelas"
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("data"):
                self.kelas_id = data["data"][0]["id_kelas"]
        
        # Ambil siswa
        if self.kelas_id:
            response = self.client.get(
                f"/api/kelas/{self.kelas_id}/siswa?page=1&limit=1",
                headers=headers,
                name="/api/kelas/{id}/siswa"
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
        """GET /api/dashboard - baca dashboard utama"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/dashboard",
            headers=headers,
            name="/api/dashboard"
        )
    
    @task(8)
    def read_attendance_summary(self):
        """GET /api/absensi/ringkasan - baca ringkasan absensi"""
        headers = self.get_auth_headers()
        params = {
            "page": 1,
            "limit": 10,
            "sort_by": "tanggal",
            "sort_dir": "desc"
        }
        self.client.get(
            "/api/absensi/ringkasan",
            headers=headers,
            params=params,
            name="/api/absensi/ringkasan"
        )
    
    @task(7)
    def read_notifications(self):
        """GET /api/notifikasi - baca notifikasi user"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/notifikasi?page=1&limit=20",
            headers=headers,
            name="/api/notifikasi"
        )
    
    @task(6)
    def read_users_list(self):
        """GET /api/users - list user (admin only)"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/users?page=1&limit=50&role=siswa",
            headers=headers,
            name="/api/users"
        )
    
    @task(5)
    def read_kelas_list(self):
        """GET /api/kelas - list kelas"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/kelas?page=1&limit=20",
            headers=headers,
            name="/api/kelas"
        )
    
    @task(5)
    def read_siswa_in_kelas(self):
        """GET /api/kelas/{id}/siswa - list siswa per kelas"""
        if self.kelas_id:
            headers = self.get_auth_headers()
            self.client.get(
                f"/api/kelas/{self.kelas_id}/siswa?page=1&limit=30",
                headers=headers,
                name="/api/kelas/{id}/siswa"
            )
    
    @task(4)
    def read_waktu_sholat(self):
        """GET /api/waktu-sholat - baca jadwal waktu sholat"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/waktu-sholat",
            headers=headers,
            name="/api/waktu-sholat"
        )
    
    @task(3)
    def read_sesi_sholat(self):
        """GET /api/sesi-sholat - baca sesi sholat aktif"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/sesi-sholat?status=aktif&page=1&limit=10",
            headers=headers,
            name="/api/sesi-sholat"
        )
    
    @task(3)
    def read_attendance_history(self):
        """GET /api/absensi - baca history absensi"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/absensi?page=1&limit=50&sort_by=timestamp&sort_dir=desc",
            headers=headers,
            name="/api/absensi"
        )
    
    @task(2)
    def generate_report_pdf(self):
        """POST /api/laporan/generate - generate laporan PDF"""
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
                "/api/laporan/generate",
                json=payload,
                headers=headers,
                name="/api/laporan/generate [PDF]"
            )
    
    @task(2)
    def generate_report_excel(self):
        """POST /api/laporan/generate - generate laporan Excel"""
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
                "/api/laporan/generate",
                json=payload,
                headers=headers,
                name="/api/laporan/generate [EXCEL]"
            )
    
    @task(2)
    def read_audit_log(self):
        """GET /api/audit-log - baca audit log"""
        headers = self.get_auth_headers()
        self.client.get(
            "/api/audit-log?page=1&limit=50",
            headers=headers,
            name="/api/audit-log"
        )
    
    @task(1)
    def health_check(self):
        """GET /api/health - check kesehatan sistem"""
        self.client.get(
            "/api/health",
            name="/api/health"
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
