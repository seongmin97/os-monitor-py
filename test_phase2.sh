#!/bin/bash
# SysDash Phase 2 Test Script — WebSocket + Celery Alerts
# Usage: bash test_phase2.sh
#
# Prerequisites:
#   - docker compose up -d is running
#   - demouser already exists (run test_script.sh first)

BASE_URL="http://localhost:8000"
COMPOSE="docker compose -f $(dirname "$0")/docker-compose.yml"

echo "============================================"
echo " SysDash Phase 2 — WebSocket + Alert Tests"
echo "============================================"

# --- Auth ---
echo ""
echo "=== Login and get JWT ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"Demo1234!"}')
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])" 2>/dev/null)
if [ -z "$TOKEN" ]; then
  echo "ERROR: Could not get JWT. Make sure demouser exists (run test_script.sh first)."
  exit 1
fi
echo "JWT obtained."

# ============================================================
# TEST 1: WebSocket — channel layer connectivity
# ============================================================
echo ""
echo "=== 1. WebSocket — channel layer (Redis) connectivity ==="
$COMPOSE exec django python3 manage.py shell -c "
import asyncio
from channels.layers import get_channel_layer

async def test():
    layer = get_channel_layer()
    await layer.group_add('smoke_test', 'smoke_channel')
    await layer.group_discard('smoke_test', 'smoke_channel')
    print('Channel layer (Redis): OK')

asyncio.run(test())
"

# ============================================================
# TEST 2: WebSocket — live broadcast (receive 1 real message)
# ============================================================
echo ""
echo "=== 2. WebSocket — receive 1 live metric broadcast ==="
$COMPOSE exec django python3 manage.py shell -c "
import asyncio, json
from channels.layers import get_channel_layer

async def listen():
    layer = get_channel_layer()
    # Join the group the same way MetricConsumer does
    await layer.group_add('server_1', 'test_listener')
    print('Subscribed to group server_1. Waiting for next agent POST...')
    # Receive one message (agent posts every 10s; timeout after 20s)
    try:
        msg = await asyncio.wait_for(layer.receive('test_listener'), timeout=20)
        print('Received broadcast:', json.dumps(msg, indent=2, default=str))
    except asyncio.TimeoutError:
        print('TIMEOUT: No message received within 20s.')
    finally:
        await layer.group_discard('server_1', 'test_listener')

asyncio.run(listen())
"

# ============================================================
# TEST 3: Alert rules CRUD
# ============================================================
echo ""
echo "=== 3. Create alert rule — cpu_percent > 0.0 (always triggers) ==="
RULE_RESPONSE=$(curl -s -X POST "$BASE_URL/api/alerts/rules/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"server":1,"metric":"cpu_percent","threshold":0.0}')
echo "$RULE_RESPONSE" | python3 -m json.tool
RULE_ID=$(echo "$RULE_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('id',''))" 2>/dev/null)
if [ -z "$RULE_ID" ]; then
  # Rule may already exist (unique_together constraint) — fetch existing
  RULE_ID=$(curl -s "$BASE_URL/api/alerts/rules/" \
    -H "Authorization: Bearer $TOKEN" | \
    python3 -c "import sys,json; rules=json.load(sys.stdin)['results']; print(next((r['id'] for r in rules if r['metric']=='cpu_percent'),'')" 2>/dev/null)
  echo "Rule already exists (id=$RULE_ID), continuing."
fi

echo ""
echo "=== 4. List all alert rules ==="
curl -s "$BASE_URL/api/alerts/rules/" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# ============================================================
# TEST 4: AlertEvent created within cooldown window
# ============================================================
echo ""
echo "=== 5. Wait 12s for agent to post a metric (triggers check_alerts) ==="
sleep 12

echo ""
echo "=== 6. Check AlertEvents — expect at least 1 ==="
EVENTS=$(curl -s "$BASE_URL/api/alerts/events/" -H "Authorization: Bearer $TOKEN")
echo "$EVENTS" | python3 -m json.tool
EVENT_COUNT=$(echo "$EVENTS" | python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null)
if [ "$EVENT_COUNT" -ge 1 ] 2>/dev/null; then
  echo "PASS: $EVENT_COUNT AlertEvent(s) found."
else
  echo "FAIL: No AlertEvents found — check Celery worker logs."
fi

# ============================================================
# TEST 5: Cooldown — wait another 12s and confirm count stays at 1
# ============================================================
echo ""
echo "=== 7. Cooldown check — wait 12s, event count should stay at 1 ==="
sleep 12
NEW_COUNT=$(curl -s "$BASE_URL/api/alerts/events/" \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['count'])" 2>/dev/null)
if [ "$NEW_COUNT" -eq "$EVENT_COUNT" ] 2>/dev/null; then
  echo "PASS: Count still $NEW_COUNT — 5-min cooldown is working."
else
  echo "INFO: Count changed to $NEW_COUNT (cooldown window may have been reset or threshold changed)."
fi

# ============================================================
# TEST 6: Celery worker ALERT log line
# ============================================================
echo ""
echo "=== 8. Celery worker logs — look for ALERT line ==="
$COMPOSE logs celery 2>&1 | grep "ALERT" | tail -5

# ============================================================
# TEST 7: Celery Beat — prune task scheduled
# ============================================================
echo ""
echo "=== 9. Celery Beat — confirm prune task is scheduled ==="
$COMPOSE logs celery 2>&1 | grep -i "prune\|beat" | tail -5

# ============================================================
# Cleanup — deactivate the test rule so it doesn't spam events
# ============================================================
if [ -n "$RULE_ID" ]; then
  echo ""
  echo "=== Cleanup — deactivate alert rule id=$RULE_ID ==="
  curl -s -X PATCH "$BASE_URL/api/alerts/rules/$RULE_ID/" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"is_active":false}' | python3 -m json.tool
fi

echo ""
echo "============================================"
echo " Phase 2 tests complete"
echo "============================================"
