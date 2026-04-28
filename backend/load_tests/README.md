# Load Testing Guide untuk SIKAP

## Pengenalan

Load testing adalah proses untuk mengukur seberapa banyak request yang bisa ditangani sistem Anda, dan bagaimana performa sistem saat traffic tinggi.

## Tools: Locust

Locust adalah framework Python untuk load testing yang mudah digunakan. Keuntungan:
- ✅ Python-based (sesuai stack SIKAP)
- ✅ Bisa define user behavior dengan code Python
- ✅ Distributed testing support
- ✅ HTML report yang bagus
- ✅ Real-time statistics

## Setup

### 1. Install Locust
```bash
cd backend
pip install locust
```

### 2. File Structure
```
backend/
├── load_tests/
│   ├── locustfile.py        # Define test behavior
│   ├── run_load_tests.py    # Script untuk automated testing
│   ├── quick_test.sh        # Quick start script
│   └── reports/             # Output reports
```

## Cara Menggunakan

### Opsi A: GUI Mode (Interaktif)
```bash
cd backend
locust --host=http://localhost:5000 --locustfile=load_tests/locustfile.py
```

Kemudian buka browser ke `http://localhost:8089`

- Input jumlah users
- Input spawn rate (users/sec)
- Klik "Start"
- Monitor di real-time

### Opsi B: Headless Mode (Scripted)
Tanpa UI, dijalankan dari command line:

```bash
cd backend

# 10 users, 1 user/sec, run 1 minute
locust \
  --headless \
  --host=http://localhost:5000 \
  --users=10 \
  --spawn-rate=1 \
  --run-time=1m \
  --locustfile=load_tests/locustfile.py \
  --csv=load_tests/reports/stats
```

### Opsi C: Automated All Scenarios
```bash
cd backend
python load_tests/run_load_tests.py http://localhost:5000
```

Ini akan jalankan 5 scenarios:
1. **Light Load** - 10 users / 1 min
2. **Medium Load** - 50 users / 2 min
3. **Heavy Load** - 100 users / 3 min
4. **Stress Test** - 200 users / 3 min
5. **Spike Test** - 500 users / 2 min

## Interpretasi Results

Saat test selesai, lihat report HTML. Penting untuk perhatikan:

| Metrik | Target | Penjelasan |
|--------|--------|-----------|
| **Response Time (avg)** | < 200ms | Rata-rata response time |
| **Response Time (p95)** | < 500ms | 95% request harus lebih cepat dari ini |
| **Response Time (p99)** | < 1000ms | 99% request harus lebih cepat |
| **Failure Rate** | 0% | Tidak boleh ada error |
| **Requests/sec** | Max throughput | Berapa request/sec sistem support |
| **Users** | Max concurrent | Berapa user sekaligus sistem support |

## Contoh Hasil Test

### ✅ GOOD Performance
```
Users: 100 | Requests/sec: 150
Response Time (avg): 120ms
Response Time (p95): 250ms
Failure Rate: 0%
```
→ Sistem siap untuk production!

### ⚠️ DEGRADED Performance
```
Users: 100 | Requests/sec: 80
Response Time (avg): 450ms
Response Time (p95): 1200ms
Failure Rate: 2%
```
→ Ada bottleneck, perlu investigate

### ❌ FAILING Performance
```
Users: 100 | Requests/sec: 30
Response Time (avg): 2000ms
Response Time (p95): 5000ms
Failure Rate: 15%
```
→ Sistem tidak stabil, JANGAN go production!

## Troubleshooting

### Tidak bisa connect ke server
```bash
# Pastikan backend running
cd backend
python run.py

# Di terminal lain
python load_tests/run_load_tests.py http://localhost:5000
```

### Authentication error
Edit `locustfile.py` - ganti username/password dengan yang sesuai database Anda:
```python
payload = {
    "username": "admin",      # ← ganti
    "password": "admin12345"  # ← ganti
}
```

### Endpoint 404 Not Found
Pastikan endpoint masih ada di backend. Update di `locustfile.py` section "Task - Endpoint yang DiTest"

## Tips untuk Load Testing yang Baik

1. **Test di environment yang clean** - jangan ada background task
2. **Mulai dari load rendah** - 10 users, terus naik gradually
3. **Jalankan berulang kali** - results bisa bervariasi, ambil rata-rata
4. **Monitor database/server resources** - CPU, Memory, Disk I/O
5. **Test realistic scenarios** - mimic actual user behavior
6. **Perhatikan database connection pool** - bisa jadi bottleneck

## Next Steps

Setelah mendapat hasil load test:

1. **Analyze bottleneck** - API endpoint mana yang lambat?
2. **Optimize** - query database, cache, async processing
3. **Re-test** - verifikasi improvement
4. **Monitor production** - setup monitoring dengan Prometheus + Grafana (sudah ada di docker-compose)

## Dokumentasi Lebih Lanjut

- [Locust Official Docs](https://docs.locust.io/)
- [Load Testing Best Practices](https://docs.locust.io/en/stable/writing-a-locustfile.html)
