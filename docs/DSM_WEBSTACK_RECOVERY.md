# DSM Web Stack Recovery

**Target:** Synology DSM 7.1.1  
**Goal:** Diagnose and fully repair the DSM web stack.

## Prerequisites

- SSH access to DSM
- Cursor connected via SSH Target:
  - Host: `192.168.1.45`
  - User: `admin`
  - Enable sudo escalation

---

## Phase 1: Identify

```bash
# ss or netstat for port listing; map inodes to PIDs if needed
ss -tlnp 2>/dev/null | grep -E ':(80|443|5000|5001)\s' || netstat -tlnp 2>/dev/null | grep -E ':(80|443|5000|5001)\s'

for port in 80 443 5000 5001; do
  echo "=== Port $port ==="
  ss -tlnp 2>/dev/null | grep ":$port " || netstat -tlnp 2>/dev/null | grep ":$port "
  lsof -i :$port 2>/dev/null
done
```

**Checkpoint:** List all PIDs holding these ports. Record them.

---

## Phase 2: Stop Services

```bash
# Stop in dependency order (synosystemctl for DSM 7.x)
synosystemctl stop nginx
synosystemctl stop synoscgi
synosystemctl stop pkgctl-DSM
synosystemctl stop WebStation

# Alternative if synosystemctl fails
systemctl stop nginx 2>/dev/null
systemctl stop synoscgi 2>/dev/null
systemctl stop pkgctl-DSM 2>/dev/null
systemctl stop WebStation 2>/dev/null
```

**Checkpoint:** Confirm services stopped. Re-run Phase 1; if ports still held, proceed to Phase 3.

---

## Phase 3: Kill Port Holders

```bash
for port in 80 443 5000 5001; do
  pids=$(lsof -t -i :$port 2>/dev/null)
  [ -n "$pids" ] && echo "Port $port: $pids" && kill -9 $pids
done
```

**Checkpoint:** `lsof -i :80 -i :443 -i :5000 -i :5001` should show nothing.

---

## Phase 4: Remove Stale Files

```bash
rm -f /run/nginx.pid /run/webstation_default.sock
ls -la /run/nginx.pid /run/webstation_default.sock 2>&1
```

**Checkpoint:** Both files should be gone (or never existed).

---

## Phase 5: Validate nginx Config

```bash
nginx -t
```

**Checkpoint:** Must see `syntax is ok` and `test is successful`. If not, fix config before restart.

---

## Phase 6: Restart Services (Order Matters)

```bash
synosystemctl start synoscgi
sleep 3
synosystemctl start nginx
sleep 2
synosystemctl start pkgctl-DSM
# WebStation optional: synosystemctl start WebStation
```

**Checkpoint:** No errors. `ps aux | grep -E 'nginx|synoscgi'` shows processes.

---

## Phase 7: Test

```bash
curl -k -v https://127.0.0.1:5001 2>&1 | head -30
```

**Checkpoint:** Should get HTTP response (200 or redirect), not connection reset.

---

## Phase 8: If Still Failing — Inspect Logs

```bash
tail -100 /var/log/nginx/error.log
journalctl -u synoscgi -n 50 --no-pager 2>/dev/null
systemctl status nginx synoscgi
```

**Report:** Root cause from log output. Do not guess.

---

## Fallback: synopkg / systemctl Repair

If DSM service manager is corrupted:

```bash
synopkg status nginx
synopkg status synoscgi
synopkg repair nginx
synopkg repair synoscgi

systemctl daemon-reload
systemctl reset-failed
systemctl start synoscgi
systemctl start nginx
```

---

## Quick Reference: Service Order

| Order | Service     | Depends On   |
|-------|-------------|--------------|
| 1     | synoscgi    | —            |
| 2     | nginx       | synoscgi     |
| 3     | pkgctl-DSM  | nginx        |
| 4     | WebStation  | nginx        |

---

## Final Status

| Outcome | Meaning |
|---------|---------|
| **Fixed** | `curl -k https://127.0.0.1:5001` returns HTTP response |
| **Partially fixed with root cause** | Some improvement; log/status shows specific blocker |
| **Not fixable without package reinstall** | Config or package corruption; synopkg repair failed |

Report ends with one-line root cause summary from actual log/status output.

---

## Execution Notes

- Run phases sequentially.
- Do not skip Phase 1 — it informs Phase 3.
- If `bind() address already in use` persists, Phase 3 was incomplete; re-identify and kill.
- Execute from Cursor SSH session (or SSH as admin) so logs and output are visible directly.
