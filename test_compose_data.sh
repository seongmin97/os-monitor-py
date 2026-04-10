#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE="docker compose -f \"$ROOT_DIR/docker-compose.yml\""
SERVICES=(postgres redis)

POSTGRES_DB="${POSTGRES_DB:-sysdash}"
POSTGRES_USER="${POSTGRES_USER:-sysdash_user}"

cleanup() {
  echo ""
  echo "=== docker compose down (postgres, redis) ==="
  eval "$COMPOSE down"
}

trap cleanup EXIT

echo "=== docker compose up -d postgres redis ==="
eval "$COMPOSE up -d ${SERVICES[*]}"

echo ""
echo "=== wait for postgres to be ready ==="
for _ in {1..30}; do
  if eval "$COMPOSE exec -T postgres pg_isready -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\"" >/dev/null 2>&1; then
    echo "Postgres is ready."
    break
  fi
  sleep 1
done

echo ""
echo "=== wait for redis to be ready ==="
for _ in {1..30}; do
  if eval "$COMPOSE exec -T redis redis-cli ping" | grep -q PONG; then
    echo "Redis is ready."
    break
  fi
  sleep 1
done

echo ""
echo "=== check Postgres alert table ==="
eval "$COMPOSE exec -T postgres psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -c \"\\dt alerts_*\""

table_name="alerts_alert"
table_exists="$(
  eval "$COMPOSE exec -T postgres psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -t -A -c \"SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema='public' AND table_name='${table_name}');\""
)"

if [[ "$table_exists" == "t" ]]; then
  echo ""
  echo "--- schema: ${table_name} ---"
  eval "$COMPOSE exec -T postgres psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -c \"\\d ${table_name}\""

  echo ""
  echo "--- first 10 rows: ${table_name} ---"
  eval "$COMPOSE exec -T postgres psql -U \"$POSTGRES_USER\" -d \"$POSTGRES_DB\" -c \"SELECT * FROM ${table_name} ORDER BY id DESC LIMIT 10;\""
else
  echo ""
  echo "--- schema: ${table_name} ---"
  echo "Table does not exist yet. Run Django migrations first."
fi

echo ""
echo "=== add sample data to Redis ==="
redis_test_key="compose:test:$(date +%s)"
redis_test_value="added-by-test_compose_data.sh"
redis_set_result="$(eval "$COMPOSE exec -T redis redis-cli SET \"$redis_test_key\" \"$redis_test_value\"")"
echo "Redis write result: $redis_set_result"
echo "Added key '$redis_test_key' with value '$redis_test_value'"

echo ""
echo "=== check Redis keys and values ==="
redis_keys="$(eval "$COMPOSE exec -T redis redis-cli --scan")"

if [[ -z "$redis_keys" ]]; then
  echo "No keys in Redis."
else
  while IFS= read -r key; do
    [[ -z "$key" ]] && continue
    key_type="$(eval "$COMPOSE exec -T redis redis-cli TYPE \"$key\"")"
    case "$key_type" in
      string)
        value="$(eval "$COMPOSE exec -T redis redis-cli GET \"$key\"")"
        ;;
      list)
        value="$(eval "$COMPOSE exec -T redis redis-cli LRANGE \"$key\" 0 -1")"
        ;;
      set)
        value="$(eval "$COMPOSE exec -T redis redis-cli SMEMBERS \"$key\"")"
        ;;
      zset)
        value="$(eval "$COMPOSE exec -T redis redis-cli ZRANGE \"$key\" 0 -1 WITHSCORES")"
        ;;
      hash)
        value="$(eval "$COMPOSE exec -T redis redis-cli HGETALL \"$key\"")"
        ;;
      *)
        value="(type: $key_type, value not displayed)"
        ;;
    esac

    echo "Key: $key"
    echo "Type: $key_type"
    echo "Value:"
    echo "$value"
    echo "---"
  done <<< "$redis_keys"
fi
