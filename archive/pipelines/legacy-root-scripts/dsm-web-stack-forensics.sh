#!/bin/sh

set -eu

# Enable pipefail when the shell supports it.
(set -o pipefail) 2>/dev/null && set -o pipefail || true

DO_RESTART=0

for arg in "$@"; do
  case "$arg" in
    --restart)
      DO_RESTART=1
      ;;
    --help|-h)
      cat <<'EOF'
Usage: dsm-web-stack-forensics.sh [--restart]

Runs a DSM web stack diagnostic sweep.
Default mode is read-only. Pass --restart to attempt a safe synoscgi/nginx restart.
EOF
      exit 0
      ;;
    *)
      echo "Unknown argument: $arg" >&2
      exit 2
      ;;
  esac
done

have() {
  command -v "$1" >/dev/null 2>&1
}

section() {
  echo
  echo "=== $1 ==="
}

show_listeners() {
  if have netstat; then
    netstat -tulpn 2>/dev/null | egrep ':(80|443|5000|5001|9900|9901|3001)\s' || true
    return
  fi

  if have ss; then
    ss -lntup 2>/dev/null | egrep ':(80|443|5000|5001|9900|9901|3001)\b' || true
    return
  fi

  if have lsof; then
    lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | egrep ':(80|443|5000|5001|9900|9901|3001)\b' || true
    return
  fi

  echo "No supported listener inspection tool found (netstat/ss/lsof)"
}

local_probe() {
  proto="$1"
  port="$2"

  if ! have curl; then
    echo "curl not found"
    return 0
  fi

  if [ "$proto" = "https" ]; then
    curl -skv --max-time 3 "https://127.0.0.1:${port}/" 2>&1 | tail -n 30 || true
  else
    curl -sv --max-time 3 "http://127.0.0.1:${port}/" 2>&1 | tail -n 30 || true
  fi
}

service_status() {
  service_name="$1"

  if have synosystemctl; then
    synosystemctl get-active-status "$service_name" || true
  else
    echo "synosystemctl not found"
  fi
}

restart_service() {
  service_name="$1"

  if have synosystemctl; then
    synosystemctl restart "$service_name" || true
  else
    echo "synosystemctl not found; cannot restart $service_name"
  fi
}

section "0) Timestamp / box"
date || true
uname -a || true

section "1) Who is LISTENing on key ports? (should be nginx only)"
show_listeners

section "2) Show ALL processes that could fight nginx (docker/node/python/cloudflared/apache)"
ps -ef | egrep 'nginx|synow3tool|synoscgi|httpd|apache|docker|containerd|cloudflared|node|python|caddy|traefik' | grep -v egrep || true

section "3) Verify nginx config parses cleanly"
if [ -x /usr/bin/nginx ] && [ -f /etc/nginx/nginx.conf.run ]; then
  /usr/bin/nginx -t -c /etc/nginx/nginx.conf.run || true
else
  echo "DSM nginx binary or config not found"
fi

section "4) Check nginx pid + workers"
if [ -f /run/nginx.pid ]; then
  echo "nginx pid file:"
  cat /run/nginx.pid || true
  PID="$(cat /run/nginx.pid 2>/dev/null || true)"
  if [ -n "$PID" ]; then
    echo "ps for nginx pid:"
    ps -ef | awk -v pid="$PID" '$2==pid || $3==pid {print}'
  fi
else
  echo "/run/nginx.pid not found"
fi
echo "nginx worker grep:"
ps -ef | grep '[n]ginx: worker' || true

section "5) Quick local probes (HTTP + HTTPS)"
local_probe http 5000
local_probe https 5001

section "6) Check synoscgi sockets + perms"
if [ -d /run ]; then
  ls -la /run 2>/dev/null | grep synoscgi || true
else
  echo "/run not found"
fi
ps -ef | grep '[s]ynoscgi' || true

section "7) Look for recent edits to nginx configs (last 2 days)"
if [ -d /etc/nginx ]; then
  find /etc/nginx -type f -mtime -2 -maxdepth 3 -print -exec ls -l {} \; 2>/dev/null || true
else
  echo "/etc/nginx not found"
fi

section "8) Check for firewall rules that might block loopback/ports"
if have iptables; then
  iptables -S 2>/dev/null | head -n 200 || true
  iptables -L -n 2>/dev/null | head -n 200 || true
else
  echo "iptables not found"
fi

section "9) Check disk space (full disks can cause very weird DSM behavior)"
df -h | sed -n '1,120p' || true
df -i | sed -n '1,120p' || true

section "10) Service state"
service_status synoscgi
service_status nginx

if [ "$DO_RESTART" -eq 1 ]; then
  echo "--- restarting synoscgi then nginx ---"
  restart_service synoscgi
  sleep 2
  restart_service nginx
  sleep 2

  section "11) Re-probe after restart"
  show_listeners
  local_probe http 5000
  local_probe https 5001
else
  echo "Restart skipped. Re-run with --restart to attempt a safe service restart."
fi

section "12) If STILL resetting: capture live nginx errors from syslog"
if have synologset1; then
  echo "synologset1 exists; dumping recent nginx errors (best effort)"
  synologset1 syslog-ng --print 2>/dev/null | tail -n 200 || true
else
  echo "synologset1 not found"
fi

if [ -f /var/log/messages ]; then
  tail -n 200 /var/log/messages 2>/dev/null | strings | egrep -i 'nginx|synoscgi|emerg|crit|alert|error' | tail -n 120 || true
else
  echo "/var/log/messages not found"
fi

section "DONE"
echo "Capture this output from the DSM host and inspect listener ownership, nginx parse results, probe failures, and recent errors."
