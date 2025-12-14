#!/bin/bash
set -e

DATA_DIR="$1"
CONTAINER="saxs-db"

echo "Loading CSV files from $DATA_DIR"

count=0
for f in "$DATA_DIR"/*.csv; do
    docker cp "$f" "$CONTAINER:/tmp/data.csv"
    docker exec "$CONTAINER" psql -U postgres -d saxs -c "\COPY saxs_data(q, intensity, error) FROM '/tmp/data.csv' WITH CSV" > /dev/null
    count=$((count + 1))
done

echo "Loaded $count files"
docker exec "$CONTAINER" psql -U postgres -d saxs -c "SELECT COUNT(*) as total_rows FROM saxs_data;"