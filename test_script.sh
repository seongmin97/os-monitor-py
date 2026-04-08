#!/bin/bash
# SysDash Phase 1 API Test Script
# Usage: bash test_script.sh

BASE_URL="http://localhost:8000"

echo "============================================"
echo " SysDash Phase 1 — API Tests"
echo "============================================"

# 1. Register
echo ""
echo "=== 1. Register new user (POST /api/auth/register/) ==="
curl -s -X POST "$BASE_URL/api/auth/register/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","email":"demo@sysdash.io","password":"Demo1234!","password2":"Demo1234!"}' \
  | python3 -m json.tool

# 2. Login
echo ""
echo "=== 2. Login and get JWT (POST /api/auth/token/) ==="
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/api/auth/token/" \
  -H "Content-Type: application/json" \
  -d '{"username":"demouser","password":"Demo1234!"}')
echo "$LOGIN_RESPONSE" | python3 -m json.tool | head -6
TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin)['access'])")

# 3. Latest metric
echo ""
echo "=== 3. Latest metric snapshot (GET /api/metrics/latest/?server=1) ==="
curl -s "$BASE_URL/api/metrics/latest/?server=1" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# 4. Paginated history
echo ""
echo "=== 4. Metric history — paginated (GET /api/metrics/history/?server=1) ==="
curl -s "$BASE_URL/api/metrics/history/?server=1" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -c "
import sys, json
d = json.load(sys.stdin)
print(f'total count  : {d[\"count\"]}')
print(f'results len  : {len(d[\"results\"])}')
print(f'next page    : {d[\"next\"]}')
print(f'prev page    : {d[\"previous\"]}')
print(f'first item   : cpu={d[\"results\"][0][\"cpu_percent\"]}%  mem={d[\"results\"][0][\"memory_percent\"]}%')
"

# 5. Server list
echo ""
echo "=== 5. Server list (GET /api/servers/) ==="
curl -s "$BASE_URL/api/servers/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# 6. Alert rules (empty)
echo ""
echo "=== 6. Alert rules (GET /api/alerts/rules/) ==="
curl -s "$BASE_URL/api/alerts/rules/" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool

# 7. Auth protection check
echo ""
echo "=== 7. Unauthenticated request — expect 401 (GET /api/metrics/latest/) ==="
curl -s "$BASE_URL/api/metrics/latest/" \
  | python3 -m json.tool

echo ""
echo "============================================"
echo " All tests complete"
echo "============================================"
