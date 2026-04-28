# SIKAP Load Testing - Quick Reference

## 🚀 Start Here (5 Menit)

### 1. Install Locust
```bash
cd backend
pip install locust
```

### 2. Jalankan Test (Pilih Salah Satu)

#### Opsi A: GUI (Recommended untuk pemula)
```bash
locust --host=http://localhost:5000 --locustfile=load_tests/locustfile.py
# Buka browser: http://localhost:8089
# Input users, click Start
```

#### Opsi B: Command Line (Windows)
```powershell
# Light test: 10 users, 1 minute
powershell .\load_tests\quick_test.ps1 -Users 10 -Duration 1m

# Medium test: 50 users, 2 minute
powershell .\load_tests\quick_test.ps1 -Users 50 -Duration 2m

# Heavy test: 100 users, 3 minute
powershell .\load_tests\quick_test.ps1 -Users 100 -Duration 3m
```

#### Opsi C: Python Script (Automated)
```bash
cd backend
python load_tests/run_load_tests.py http://localhost:5000
```

### 3. Lihat Hasil
- HTML Report: `backend/load_tests/reports/report_*.html`
- CSV Stats: `backend/load_tests/reports/stats_*.csv`
- **Buka HTML di browser → Lihat response time, failures, throughput**

---

## 📊 Hasil Apa yang Baik?

| Metric | Target | Status |
|--------|--------|--------|
| Response Time (p95) | < 500ms | ✅ Good |
| Failure Rate | 0% | ✅ Good |
| Users Supported | 100+ | ✅ Good |

**Jika tidak capai target → Ada bottleneck, perlu optimize**

---

## 🔍 Advanced Usage

### Test Specific Scenario
```bash
# RFID attendance stress
locust \
  --headless \
  --host=http://localhost:5000 \
  --users=500 \
  --spawn-rate=50 \
  --run-time=2m \
  --locustfile=load_tests/advanced_scenarios.py:RfidAttendanceScenario

# Dashboard monitoring
locust \
  --headless \
  --host=http://localhost:5000 \
  --users=20 \
  --spawn-rate=5 \
  --run-time=3m \
  --locustfile=load_tests/advanced_scenarios.py:DashboardMonitoringScenario

# Report generation
locust \
  --headless \
  --host=http://localhost:5000 \
  --users=10 \
  --spawn-rate=2 \
  --run-time=3m \
  --locustfile=load_tests/advanced_scenarios.py:ReportGenerationScenario
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| "Connection refused" | Pastikan `python run.py` running di terminal lain |
| "401 Unauthorized" | Update username/password di `locustfile.py` |
| "404 Not Found" | Endpoint tidak ada, check di backend routes |
| Report kosong | Tunggu test selesai dulu sebelum buka report |

---

## 📁 File Structure

```
backend/load_tests/
├── locustfile.py              # Main test scenarios
├── advanced_scenarios.py       # Specific use cases
├── run_load_tests.py          # Automated runner
├── quick_test.ps1             # Windows quick start
├── quick_test.sh              # Linux/Mac quick start
├── README.md                  # Detailed guide
├── BEST_PRACTICES.md          # Why & How to load test
├── QUICK_REFERENCE.md         # This file
└── reports/                   # Test results
    ├── report_*.html
    └── stats_*.csv
```

---

## 💡 Tips

1. **Backend harus running** - buka terminal baru, `cd backend && python run.py`
2. **Mulai dari load rendah** - 10 users dulu, naikkan gradually
3. **Run multiple times** - hasil bisa bervariasi, ambil rata-rata
4. **Monitor resources** - buka Task Manager / top command saat test
5. **Check error logs** - jika ada failure, lihat backend logs untuk error details

---

## 📞 Next Steps

1. ✅ Jalankan test ringan (10 users)
2. ✅ Analisa hasil di HTML report
3. ✅ Jalankan test medium (50-100 users)
4. ✅ Jika ada bottleneck, baca BEST_PRACTICES.md
5. ✅ Optimize code/database berdasarkan findings
6. ✅ Re-test untuk verify improvements
7. ✅ Dokumentasikan hasil untuk laporan final

---

## 📖 Baca Lebih Lanjut

- `README.md` - Dokumentasi lengkap dengan interpretasi hasil
- `BEST_PRACTICES.md` - Detail mengapa penting, cara analisa, troubleshooting
- Locust Docs: https://docs.locust.io/

---

## ⏱️ Estimasi Waktu

- Setup + first test: **10 menit**
- 5 test scenarios: **30 menit**
- Analisa hasil: **15 menit**
- Total: **~1 jam untuk complete load testing**

**Investasi terbaik sebelum production deployment! 🚀**
