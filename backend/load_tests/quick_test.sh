#!/bin/bash

# Quick Load Test Script untuk SIKAP
# Usage: bash load_tests/quick_test.sh [host] [users] [duration]
# Example: bash load_tests/quick_test.sh localhost:5000 50 2m

set -e

# Default values
HOST="${1:-localhost:5000}"
USERS="${2:-50}"
DURATION="${3:-2m}"
SPAWN_RATE=$((USERS / 5 + 1))  # Auto calculate spawn rate

# Jika host tidak punya http://, tambahkan
if [[ ! $HOST == http://* ]]; then
    HOST="http://$HOST"
fi

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="load_tests/reports"
STATS_FILE="$REPORT_DIR/stats_quick_$TIMESTAMP"
HTML_REPORT="$REPORT_DIR/report_quick_$TIMESTAMP.html"

# Create reports directory
mkdir -p "$REPORT_DIR"

echo "╔════════════════════════════════════════════╗"
echo "║   SIKAP Load Test - Quick Start            ║"
echo "╚════════════════════════════════════════════╝"
echo ""
echo "Configuration:"
echo "  Host:        $HOST"
echo "  Users:       $USERS"
echo "  Spawn Rate:  $SPAWN_RATE/sec"
echo "  Duration:    $DURATION"
echo "  Report:      $HTML_REPORT"
echo ""
echo "Starting load test..."
echo "════════════════════════════════════════════"
echo ""

locust \
    --headless \
    --host="$HOST" \
    --users="$USERS" \
    --spawn-rate="$SPAWN_RATE" \
    --run-time="$DURATION" \
    --csv="$STATS_FILE" \
    --html="$HTML_REPORT" \
    --locustfile=load_tests/locustfile.py

echo ""
echo "════════════════════════════════════════════"
echo "✅ Load test completed!"
echo ""
echo "📊 Results:"
echo "   HTML Report: $HTML_REPORT"
echo "   CSV Stats:   ${STATS_FILE}_stats.csv"
echo ""
echo "Open HTML report in browser to see detailed statistics"
