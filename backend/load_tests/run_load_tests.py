"""
Script untuk menjalankan automated load test scenarios
Bisa run dari CLI tanpa Locust UI
"""

import subprocess
import json
from datetime import datetime
from pathlib import Path

def run_load_test(
    host: str,
    num_users: int,
    spawn_rate: int,
    run_time: str,
    test_name: str
):
    """
    Run load test dengan parameter tertentu
    
    Args:
        host: URL server (e.g., http://localhost:5000)
        num_users: Jumlah concurrent users
        spawn_rate: Berapa user per detik yang dibuat
        run_time: Berapa lama test jalan (e.g., "5m", "300s")
        test_name: Nama test untuk report
    """
    
    print(f"\n{'='*60}")
    print(f"🔥 Load Test: {test_name}")
    print(f"{'='*60}")
    print(f"Host: {host}")
    print(f"Users: {num_users}")
    print(f"Spawn Rate: {spawn_rate}/sec")
    print(f"Duration: {run_time}")
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    # Output file untuk hasil test
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    html_report = f"load_tests/reports/report_{test_name}_{timestamp}.html"
    csv_stats = f"load_tests/reports/stats_{test_name}_{timestamp}.csv"
    
    # Build Locust command
    cmd = [
        "locust",
        "--headless",  # No web UI
        "--host", host,
        "--users", str(num_users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", run_time,
        "--csv", f"load_tests/reports/stats_{test_name}_{timestamp}",
        "--html", html_report,
        "--locustfile", "load_tests/locustfile.py",
        "--only-summary"  # Only print summary
    ]
    
    # Jalankan test
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    
    print(f"\n✅ Report saved to: {html_report}")
    print(f"✅ Stats saved to: {csv_stats}")
    
    return result.returncode == 0


def run_all_scenarios(host: str = "http://localhost:5000"):
    """Jalankan semua test scenarios"""
    
    scenarios = [
        # (num_users, spawn_rate, run_time, name)
        (10, 1, "1m", "light_load"),           # 10 user selama 1 menit
        (50, 5, "2m", "medium_load"),          # 50 user selama 2 menit
        (100, 10, "3m", "heavy_load"),         # 100 user selama 3 menit
        (200, 20, "3m", "stress_test"),        # 200 user hingga sistem stress
        (500, 50, "2m", "spike_test"),         # Spike mendadak ke 500 user
    ]
    
    results = []
    
    for num_users, spawn_rate, run_time, test_name in scenarios:
        success = run_load_test(host, num_users, spawn_rate, run_time, test_name)
        results.append({
            "test": test_name,
            "users": num_users,
            "spawn_rate": spawn_rate,
            "duration": run_time,
            "success": success
        })
        
        # Pause antar test
        print("\n⏳ Waiting 30 seconds before next test...\n")
        import time
        time.sleep(30)
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 LOAD TEST SUMMARY")
    print(f"{'='*60}")
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{result['test']:20} {status:15} | Users: {result['users']:3} | Time: {result['duration']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    import sys
    
    # Setup
    Path("load_tests/reports").mkdir(parents=True, exist_ok=True)
    
    # Ambil host dari argument atau default
    host = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    print(f"\n🚀 Starting SIKAP Load Testing Suite")
    print(f"Target: {host}\n")
    
    # Run all scenarios
    run_all_scenarios(host)
    
    print("\n📈 All tests completed!")
    print("📂 Check 'load_tests/reports/' folder for detailed results")
