#!/bin/bash
# DSM Web Stack Repair — run on DSM 7.1.1 via SSH (admin or root)
# Usage: scp to DSM, then: chmod +x dsm_webstack_repair.sh && ./dsm_webstack_repair.sh

set -e

echo "=== Step 1: Identify port holders ==="
ss -tlnp 2>/dev/null | grep -E ':(80|443|5000|5001)\s' || netstat -tlnp 2>/dev/null | grep -E ':(80|443|5000|5001)\s' || true
for port in 80 443 5000 5001; do
  echo "=== Port $port ==="
  ss -tlnp 2>/dev/null | grep ":$port " || netstat -tlnp 2>/dev/null | grep ":$port " || true
  lsof -i :$port 2>/dev/null || true
done

echo ""
echo "=== Step 2: Stop services ==="
synosystemctl stop nginx 2>/dev/null || true
synosystemctl stop synoscgi 2>/dev/null || true
synosystemctl stop pkgctl-DSM 2>/dev/null || true
synosystemctl stop WebStation 2>/dev/null || true

echo ""
echo "=== Step 3: Kill remaining port holders ==="
for port in 80 443 5000 5001; do
  pids=$(lsof -t -i :$port 2>/dev/null || true)
  [ -n "$pids" ] && echo "Killing port $port: $pids" && kill -9 $pids 2>/dev/null || true
done

echo ""
echo "=== Step 4: Remove stale runtime files ==="
rm -f /run/nginx.pid /run/webstation_default.sock
ls -la /run/nginx.pid /run/webstation_default.sock 2>&1 || true

echo ""
echo "=== Step 5: Validate nginx config ==="
nginx -t

echo ""
echo "=== Step 6: Restart services ==="
synosystemctl start synoscgi
sleep 3
synosystemctl start nginx
sleep 2
synosystemctl start pkgctl-DSM

echo ""
echo "=== Step 7: Test ==="
curl -k -s -o /dev/null -w "%{http_code}" https://127.0.0.1:5001 && echo " OK" || {
  echo "FAILED"
  echo ""
  echo "=== Step 8: Inspect logs ==="
  tail -100 /var/log/nginx/error.log 2>/dev/null || true
  journalctl -u synoscgi -n 50 --no-pager 2>/dev/null || true
  systemctl status nginx synoscgi 2>/dev/null || true
}
