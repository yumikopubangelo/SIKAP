# Load Testing Best Practices & Implementation Guide

## 📌 MENGAPA LOAD TESTING ITU PENTING?

### 1. **Validasi Kapasitas Sistem**
Sebelum go-live ke sekolah, Anda perlu tahu:
- Berapa banyak siswa yang bisa login bersamaan?
- Berapa banyak RFID reader yang bisa mengirim data simultaneously?
- Sistem stabil atau crash saat traffic tinggi?

**Contoh Skenario Real:**
- Pukul 12:00 semua siswa scan RFID untuk sholat Dzuhur
- Di saat yang sama, kepala sekolah buka dashboard
- Guru membuat laporan PDF
- Notifikasi dikirim ke 500 parents via email

**Tanpa load testing:** Sistem bisa crash, absensi hilang, laporan error

**Dengan load testing:** Anda sudah tahu sistemnya bisa handle atau perlu optimasi

---

### 2. **Identify Bottlenecks**
Menemukan bagian sistem yang paling lambat:

| Bottleneck | Impact | Solution |
|-----------|--------|----------|
| Database queries lambat | Response time tinggi | Optimize query, add index |
| Memory leak | Sistem crash setelah berjalan jam | Fix memory leak, use profiler |
| API endpoint inefficient | Load berat terpusat di 1 endpoint | Refactor logic, cache data |
| Network bandwidth | Timeout saat generate laporan besar | Implement pagination, compression |

---

### 3. **Production Readiness**
Sebelum deploy ke production, pastikan:
- ✅ Response time < 500ms untuk 95% request
- ✅ No error saat traffic normal + spike
- ✅ Database connection pool tidak exhausted
- ✅ Memory stable, tidak ada memory leak

---

### 4. **Capacity Planning & Cost Optimization**
Tentukan berapa resources yang dibutuhkan:
```
Scenario: 500 concurrent users
Load Test Result: Butuh 2 GB RAM, 2 CPU cores

Production Planning:
- Ambil safety margin 30%
- Buy: 3 GB RAM, 3 CPU cores / server
- Jika perlu handle 1000 users, butuh 2 servers
```

---

### 5. **Performance Regression Detection**
Setelah update code, cek apakah performance menurun:
```
Before Update: 10 users → avg response 150ms
After Update:  10 users → avg response 300ms
→ Ada 2x regression! Cari tahu apa yang berubah.
```

---

## 🔧 IMPLEMENTASI UNTUK SIKAP

### Architecture Tested

```
Load Test Simulator (Locust)
        ↓
    Mehrere Virtual Users (10-500)
        ↓
    HTTP Requests ke Backend API
        ↓
    Backend Flask Application
        ↓
    MySQL Database
        ↓
    Response kembali ke Load Test
        ↓
    Collect Metrics & Generate Report
```

### Endpoints yang DiTest

| Endpoint | Weight | Rationale |
|----------|--------|-----------|
| `/api/dashboard` | 10% | Most frequent, critical |
| `/api/absensi/ringkasan` | 8% | Heavy aggregation query |
| `/api/notifikasi` | 7% | Real-time data |
| `/api/users` (list) | 6% | Admin uses frequently |
| `/api/kelas` | 5% | Setup phase |
| `/api/kelas/{id}/siswa` | 5% | Classroom view |
| `/api/waktu-sholat` | 4% | Reference data |
| `/api/sesi-sholat` | 3% | Session state |
| `/api/absensi` (history) | 3% | Historical data |
| `/api/laporan/generate` (PDF) | 2% | Heavy processing |
| `/api/laporan/generate` (Excel) | 2% | Heavy processing |
| `/api/audit-log` | 2% | Audit trail |
| `/api/health` | 1% | Health check |

### User Profiles Simulated

1. **AdminUser** - wait 1-3 sec antar request
2. **TeacherUser** - wait 2-5 sec antar request
3. **StudentUser** - wait 3-8 sec antar request

---

## 📊 HASIL YANG DIHARAPKAN

### Green Zone ✅ (GOOD)
```
Load: 100 concurrent users
Duration: 3 minutes

Results:
  Total Requests: 15,000
  Requests/sec: 83
  Response Time (avg): 150ms
  Response Time (p95): 300ms
  Response Time (p99): 500ms
  Failure Rate: 0%
  
Conclusion: PRODUCTION READY! Sistem handle 100 users dengan baik.
```

### Yellow Zone ⚠️ (DEGRADED)
```
Load: 200 concurrent users
Duration: 3 minutes

Results:
  Total Requests: 18,000
  Requests/sec: 100
  Response Time (avg): 400ms
  Response Time (p95): 800ms
  Response Time (p99): 1500ms
  Failure Rate: 2%
  
Conclusion: PERLU OPTIMASI. Ada bottleneck saat 200 users.
Actions:
  1. Check database slow query log
  2. Add caching untuk frequent queries
  3. Scale database resources
```

### Red Zone ❌ (FAILING)
```
Load: 300 concurrent users
Duration: 3 minutes

Results:
  Total Requests: 8,000
  Requests/sec: 44
  Response Time (avg): 1800ms
  Response Time (p95): 4000ms
  Response Time (p99): 6000ms
  Failure Rate: 18%
  
Conclusion: TIDAK SIAP! Sistem crash/error rate tinggi.
Actions:
  1. System redesign diperlukan
  2. Refactor code architecture
  3. Implement database replication
  4. Use load balancer
```

---

## 🎯 QUICK START COMMANDS

### 1. Minimal Test (10 users, 1 minute)
```powershell
# Windows
cd backend
python -m pip install locust  # Install if needed
powershell .\load_tests\quick_test.ps1 -Users 10 -Duration 1m
```

### 2. Medium Test (50 users, 2 minutes)
```powershell
powershell .\load_tests\quick_test.ps1 -Users 50 -Duration 2m
```

### 3. Stress Test (200 users, 3 minutes)
```powershell
powershell .\load_tests\quick_test.ps1 -Users 200 -Duration 3m
```

### 4. Interactive GUI (Recommended untuk pertama kali)
```powershell
cd backend
locust --host=http://localhost:5000 --locustfile=load_tests/locustfile.py
# Open http://localhost:8089 in browser
```

---

## 📈 ANALYZING RESULTS

Setiap load test menghasilkan HTML report. Berikut yang harus diperhatikan:

### 1. Response Time Distribution
```
Grafik yang bagus:
- Mayoritas request < 200ms
- Curve smooth, tidak ada sudden spike

Grafik yang jelek:
- Banyak request > 1000ms
- Curve jagged, spike tinggi di akhir test
```

### 2. Requests Per Second (Throughput)
```
Metric: Requests/sec

Ideal: Stabil, tidak menurun seiring waktu
Jelek: Menurun drastis saat load tinggi
Action: Investigate memory leak, database connection pool
```

### 3. Failure Rate
```
Metric: % Failed requests

Ideal: 0% untuk semua scenarios
Jelek: > 1% failure rate
Action: Check error log, fix bugs, scale resources
```

### 4. Response Time Percentiles
```
p50 (Median): 50% request lebih cepat dari nilai ini
p95: 95% request lebih cepat dari nilai ini
p99: 99% request lebih cepat dari nilai ini

Target:
  p50: < 100ms
  p95: < 300ms
  p99: < 500ms
```

---

## 🔍 TROUBLESHOOTING

### "Connection refused" error
```
Penyebab: Backend tidak running
Solution:
1. cd backend
2. python run.py
3. Jalankan load test di terminal lain
```

### "401 Unauthorized" error
```
Penyebab: Credentials di locustfile.py salah
Solution:
1. Edit backend/load_tests/locustfile.py
2. Ganti username/password dengan user yang ada di DB
3. Cek di MySQL: SELECT * FROM users WHERE username='admin';
```

### "404 Not Found" error
```
Penyebab: Endpoint tidak ada atau URL typo
Solution:
1. Cek endpoint ada di backend routes
2. Update URL di locustfile.py
3. Test endpoint pakai Postman dulu sebelum load test
```

### Hasil test tidak realistic
```
Penyebab: Database kosong, data setup tidak optimal
Solution:
1. Seed database dengan data realistic
2. Run test multiple times, ambil average
3. Monitor dari clean state (restart backend/database)
```

---

## 📋 CHECKLIST SEBELUM PRODUCTION

Sebelum deploy SIKAP ke sekolah, pastikan:

- [ ] Load test berhasil untuk minimum 100 concurrent users
- [ ] Response time p95 < 500ms untuk semua endpoints
- [ ] Failure rate 0% untuk normal load test
- [ ] Stress test sampai 200-300 users untuk tahu limit
- [ ] Database backup strategy sudah ready
- [ ] Monitoring setup di Prometheus + Grafana
- [ ] Error logging setup
- [ ] SSL/HTTPS certificate sudah install
- [ ] Rate limiting sudah configure (RFID requests)
- [ ] Database connection pool size sudah optimize

---

## 📚 ADDITIONAL RESOURCES

- [Locust Documentation](https://docs.locust.io/)
- [Python Performance Best Practices](https://docs.python.org/3/library/profile.html)
- [Flask Best Practices](https://flask.palletsprojects.com/en/latest/foreword/)
- [MySQL Optimization](https://dev.mysql.com/doc/refman/8.0/)
