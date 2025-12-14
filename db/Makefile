.PHONY: db-up db-down db-reset db-logs db-shell

db-up:
	docker compose up -d db

db-down:
	docker compose down

db-reset:
	docker compose down -v
	docker compose up -d db

db-logs:
	docker compose logs -f db

db-shell:
	docker compose exec db psql -U saxs -d saxs