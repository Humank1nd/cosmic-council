.PHONY: up down logs migrate seed curl fmt lint test

up:
	docker compose -f infra/docker/docker-compose.yml up -d --build
	sleep 3

down:
	docker compose -f infra/docker/docker-compose.yml down -v

logs:
	docker compose -f infra/docker/docker-compose.yml logs -f

migrate:
	psql postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$${POSTGRES_HOST}:$${POSTGRES_PORT}/$${POSTGRES_DB} -f migrations/001_init.sql
	psql postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$${POSTGRES_HOST}:$${POSTGRES_PORT}/$${POSTGRES_DB} -f migrations/002_enterprise_architecture.sql
	psql postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$${POSTGRES_HOST}:$${POSTGRES_PORT}/$${POSTGRES_DB} -f migrations/003_production_hardening.sql

seed:
	psql postgres://$${POSTGRES_USER}:$${POSTGRES_PASSWORD}@$${POSTGRES_HOST}:$${POSTGRES_PORT}/$${POSTGRES_DB} -f scripts/dev_seed.sql

curl:
	curl -s localhost:8080/v1/evaluate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"11111111-1111-1111-1111-111111111111","enterprise":"red","squad":"data_miner"},"resource":{"service":"raw_intel_feed","action":"read"},"context":{"risk":0.12}}' | jq .

curl-autonomous:
	curl -s localhost:8080/v1/autonomous-cycle -X POST -H 'Content-Type: application/json' \
	  -d '{"problem":"How can we optimize our AI agent collaboration for better decision making?","complexity":"high","urgency":"medium"}' | jq .

curl-enterprises:
	curl -s localhost:8080/v1/enterprises | jq .

# Test matrix scenarios
test-risk-block:
	curl -s localhost:8080/v1/evaluate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"11111111-1111-1111-1111-111111111111","enterprise":"red","squad":"data_miner"},"resource":{"service":"raw_intel_feed","action":"read"},"context":{"risk":0.9}}' | jq .

test-brand-safety:
	curl -s localhost:8080/v1/evaluate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"22222222-2222-2222-2222-222222222222","enterprise":"blue","squad":"publisher"},"resource":{"service":"comms_publish","action":"send"},"context":{"brand_safety":{"flags":["hate_speech"]}}}' | jq .

test-budget-cap:
	curl -s localhost:8080/v1/evaluate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"33333333-3333-3333-3333-333333333333","enterprise":"yellow","squad":"prototype"},"resource":{"service":"compute_job","action":"run"},"context":{"estimated_cost":120,"budget_cap":100}}' | jq .

test-simulate:
	curl -s localhost:8080/v1/simulate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"11111111-1111-1111-1111-111111111111","enterprise":"red","squad":"data_miner"},"resource":{"service":"raw_intel_feed","action":"read"},"context":{"risk":0.12},"perturbation":{"risk":"+0.2"}}' | jq .

test-caps:
	curl -s localhost:8080/v1/caps | jq .

test-openapi:
	curl -s localhost:8080/v1/openapi.json | jq '.info'

test-provenance:
	@echo "Testing provenance tracking..."
	@response=$$(curl -s localhost:8080/v1/evaluate -X POST -H 'Content-Type: application/json' \
	  -d '{"agent":{"id":"11111111-1111-1111-1111-111111111111","enterprise":"red","squad":"data_miner"},"resource":{"service":"raw_intel_feed","action":"read"},"context":{"risk":0.12,"provenance":{"source":"pilot_corpus_v1","hash":"abc123"}}}'); \
	decision_id=$$(echo "$$response" | jq -r '.decision_id'); \
	echo "Decision ID: $$decision_id"; \
	curl -s localhost:8080/v1/explain/$$decision_id | jq .

test-all:
	@echo "Running complete test matrix..."
	@echo "1. Access happy-path:"
	@make curl
	@echo "\n2. Risk block:"
	@make test-risk-block
	@echo "\n3. Brand safety block:"
	@make test-brand-safety
	@echo "\n4. Budget cap:"
	@make test-budget-cap
	@echo "\n5. Simulation test:"
	@make test-simulate
	@echo "\n6. Budget caps endpoint:"
	@make test-caps
	@echo "\n7. OpenAPI endpoint:"
	@make test-openapi
	@echo "\n8. Provenance tracking:"
	@make test-provenance

fmt:
	docker compose -f infra/docker/docker-compose.yml exec gateway black /app/app || true

lint:
	docker compose -f infra/docker/docker-compose.yml exec gateway ruff /app/app || true

test:
	docker compose -f infra/docker/docker-compose.yml exec gateway pytest -q || true
