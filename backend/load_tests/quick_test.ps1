# Quick Load Test Script untuk SIKAP (Windows)
# Usage: powershell .\load_tests\quick_test.ps1 -Host localhost:5000 -Users 50 -Duration 2m
# Example: powershell .\load_tests\quick_test.ps1 -Host localhost:5000 -Users 50 -Duration 2m

param(
    [string]$Host = "localhost:5000",
    [int]$Users = 50,
    [string]$Duration = "2m"
)

# Jika host tidak punya http://, tambahkan
if (-not $Host.StartsWith("http")) {
    $Host = "http://$Host"
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$ReportDir = "load_tests\reports"
$StatsFile = "$ReportDir\stats_quick_$Timestamp"
$HtmlReport = "$ReportDir\report_quick_$Timestamp.html"
$SpawnRate = [Math]::Max(1, [Math]::Floor($Users / 5))

# Create reports directory
if (-not (Test-Path $ReportDir)) {
    New-Item -ItemType Directory -Path $ReportDir -Force | Out-Null
}

Write-Host "╔════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   SIKAP Load Test - Quick Start (Windows)  ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Host:        $Host"
Write-Host "  Users:       $Users"
Write-Host "  Spawn Rate:  $SpawnRate/sec"
Write-Host "  Duration:    $Duration"
Write-Host "  Report:      $HtmlReport"
Write-Host ""
Write-Host "Starting load test..." -ForegroundColor Green
Write-Host "════════════════════════════════════════════"
Write-Host ""

# Run locust
locust `
    --headless `
    --host="$Host" `
    --users="$Users" `
    --spawn-rate="$SpawnRate" `
    --run-time="$Duration" `
    --csv="$StatsFile" `
    --html="$HtmlReport" `
    --locustfile=load_tests/locustfile.py

Write-Host ""
Write-Host "════════════════════════════════════════════" -ForegroundColor Green
Write-Host "✅ Load test completed!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Results:" -ForegroundColor Yellow
Write-Host "   HTML Report: $HtmlReport" -ForegroundColor Cyan
Write-Host "   CSV Stats:   ${StatsFile}_stats.csv" -ForegroundColor Cyan
Write-Host ""
Write-Host "📂 Open HTML report in browser to see detailed statistics" -ForegroundColor Green
