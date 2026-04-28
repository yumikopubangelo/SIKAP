"""
Advanced Load Testing Scenarios untuk SIKAP

Scenario khusus untuk test kasus-kasus real yang mungkin terjadi
"""

from locust import HttpUser, task, between, events
from datetime import datetime
import json

class RfidAttendanceScenario(HttpUser):
    """
    Scenario: RFID reader mengirim banyak attendance data secara bersamaan
    Saat sholat Dzuhur, 200+ siswa scan RFID dalam 5 menit
    """
    
    wait_time = between(0.5, 2)  # RFID reader lebih cepat
    
    def on_start(self):
        """Setup - register device dan auth"""
        # Register device RFID
        payload = {
            "device_id": f"ESP-LOAD-{self.client}",
            "nama_device": "Load Test Reader",
            "lokasi": "Masjid",
            "api_key": "load-test-key"
        }
        response = self.client.post(
            "/api/perangkat",
            json=payload,
            name="/api/perangkat [register]"
        )
    
    @task
    def send_rfid_attendance(self):
        """Kirim RFID attendance data"""
        import random
        
        payload = {
            "device_id": "ESP-LOAD-001",
            "uid_card": f"CARD-{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat()
        }
        
        headers = {
            "X-API-Key": "load-test-key"
        }
        
        self.client.post(
            "/api/absensi/rfid",
            json=payload,
            headers=headers,
            name="/api/absensi/rfid"
        )


class ReportGenerationScenario(HttpUser):
    """
    Scenario: Multiple admin/guru buat laporan PDF + Excel bersamaan
    Saat akhir bulan, 10+ guru request laporan kelas mereka
    """
    
    wait_time = between(3, 8)  # Admin work slower than RFID
    
    def on_start(self):
        """Login as teacher"""
        payload = {
            "username": "guru_1",
            "password": "guru12345"
        }
        response = self.client.post(
            "/api/auth/login",
            json=payload
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.kelas_id = 1  # Assume kelas 1 exists
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(5)
    def generate_pdf_report(self):
        """Generate PDF laporan"""
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
            headers=self.get_headers(),
            name="/api/laporan/generate [PDF]"
        )
    
    @task(3)
    def generate_excel_report(self):
        """Generate Excel laporan"""
        payload = {
            "jenis_laporan": "detail_siswa",
            "id_kelas": self.kelas_id,
            "format": "excel",
            "periode_awal": "2026-04-01",
            "periode_akhir": "2026-04-28"
        }
        
        self.client.post(
            "/api/laporan/generate",
            json=payload,
            headers=self.get_headers(),
            name="/api/laporan/generate [EXCEL]"
        )


class DashboardMonitoringScenario(HttpUser):
    """
    Scenario: Kepala Sekolah + Staff monitoring dashboard real-time
    Open dashboard, refresh every 30 seconds
    """
    
    wait_time = between(5, 15)  # Dashboard usage pattern
    
    def on_start(self):
        """Login as admin/kepala sekolah"""
        payload = {
            "username": "admin",
            "password": "admin12345"
        }
        response = self.client.post(
            "/api/auth/login",
            json=payload
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(10)
    def refresh_dashboard(self):
        """Refresh dashboard data"""
        self.client.get(
            "/api/dashboard",
            headers=self.get_headers(),
            name="/api/dashboard"
        )
    
    @task(5)
    def check_notifications(self):
        """Check notifications"""
        self.client.get(
            "/api/notifikasi?page=1&limit=10",
            headers=self.get_headers(),
            name="/api/notifikasi"
        )
    
    @task(3)
    def view_attendance_summary(self):
        """View attendance summary"""
        self.client.get(
            "/api/absensi/ringkasan?page=1&limit=50",
            headers=self.get_headers(),
            name="/api/absensi/ringkasan"
        )


class MobileAppScenario(HttpUser):
    """
    Scenario: Parents access app via mobile untuk cek absensi anak
    Slower network, lower bandwidth
    """
    
    wait_time = between(2, 10)  # Mobile user behavior
    
    def on_start(self):
        """Login as parent"""
        payload = {
            "username": "orangtua_1",
            "password": "orangtua12345"
        }
        response = self.client.post(
            "/api/auth/login",
            json=payload
        )
        if response.status_code == 200:
            self.token = response.json().get("access_token")
            self.siswa_id = 1  # Child student ID
    
    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    @task(8)
    def view_child_attendance(self):
        """Parent view anak's attendance"""
        self.client.get(
            f"/api/siswa/{self.siswa_id}/absensi?page=1&limit=30",
            headers=self.get_headers(),
            name="/api/siswa/{id}/absensi"
        )
    
    @task(3)
    def check_warnings(self):
        """Check surat peringatan"""
        self.client.get(
            f"/api/siswa/{self.siswa_id}/surat-peringatan",
            headers=self.get_headers(),
            name="/api/siswa/{id}/surat-peringatan"
        )
    
    @task(2)
    def view_notifications(self):
        """View notifications"""
        self.client.get(
            "/api/notifikasi?page=1&limit=20",
            headers=self.get_headers(),
            name="/api/notifikasi"
        )


# ============ Event Handlers untuk Custom Logging ============

@events.request.add_listener
def on_request(request_type, name, response_time, response_length, response, context, exception, **kwargs):
    """Log setiap request untuk analysis"""
    if exception:
        print(f"❌ {name} - {exception}")
    elif response_time > 1000:
        print(f"⚠️  {name} - {response_time}ms (slow)")


@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    """Dijalankan saat test selesai"""
    print("\n" + "="*60)
    print("📊 LOAD TEST SUMMARY")
    print("="*60)
    
    # Print summary statistics
    stats = environment.stats
    total_requests = stats.total.num_requests
    total_failures = stats.total.num_failures
    
    print(f"Total Requests: {total_requests}")
    print(f"Total Failures: {total_failures}")
    
    if total_requests > 0:
        failure_rate = (total_failures / total_requests) * 100
        print(f"Failure Rate: {failure_rate:.2f}%")
    
    print("="*60)
