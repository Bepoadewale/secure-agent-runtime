.PHONY: install test lint audit run demo demo-security build-sandbox bootstrap-local smoke demo-agent-task demo-api demo-containment demo-security-real demo-recovery observability-up observability-down demo-observability verify clean-local destroy-local helm-lint dashboards
PYTHON ?= python3.12
VENV := .venv
PY := $(VENV)/bin/python

install:
	command -v $(PYTHON) >/dev/null || { echo "Python 3.12 is required"; exit 1; }
	@if [ -x "$(PY)" ] && ! $(PY) -c 'import sys; assert sys.version_info[:2] == (3, 12)' >/dev/null 2>&1; then \
		echo "Recreating project-local virtual environment with Python 3.12"; rm -rf $(VENV); \
	fi
	$(PYTHON) -m venv $(VENV)
	$(PY) -m pip install --upgrade pip
	$(PY) -m pip install -e '.[dev]'
test:
	PYTHONPATH=control-plane/src $(PY) -m pytest -q
lint:
	$(PY) -m ruff check control-plane/src control-plane/tests scripts
audit:
	$(PY) -m pip_audit
run:
	PYTHONPATH=control-plane/src $(VENV)/bin/uvicorn agent_runtime.api.main:app --port 8000 --reload
demo:
	PYTHONPATH=control-plane/src $(PY) examples/demo.py
demo-security:
	PYTHONPATH=control-plane/src $(PY) examples/security_demo.py
build-sandbox:
	docker build -t agent-runtime-sandbox:local -f sandbox/images/Dockerfile .
bootstrap-local:
	$(MAKE) build-sandbox
	./scripts/bootstrap-local.sh
smoke:
	./scripts/smoke.sh
demo-agent-task:
	PYTHONPATH=control-plane/src $(PY) scripts/demo-agent-task.py
demo-api:
	PYTHONPATH=control-plane/src $(PY) scripts/demo-api.py
demo-containment:
	PYTHONPATH=control-plane/src $(PY) scripts/demo-containment.py
demo-security-real:
	PYTHONPATH=control-plane/src $(PY) scripts/demo-security-real.py
demo-recovery:
	PYTHONPATH=control-plane/src $(PY) scripts/demo-recovery.py
observability-up:
	docker compose -f docker-compose.observability.yml up -d
observability-down:
	docker compose -f docker-compose.observability.yml down -v --remove-orphans
demo-observability: observability-up
	PYTHONPATH=control-plane/src $(PY) scripts/demo-observability.py
verify:
	$(MAKE) lint
	$(MAKE) test
	$(MAKE) audit
	docker build -t agent-runtime-sandbox:local -f sandbox/images/Dockerfile .
clean-local:
	./scripts/clean-local.sh
destroy-local:
	kind delete cluster --name secure-agent-runtime-local
helm-lint:
	helm lint platform/helm/agent-runtime
dashboards:
	@echo 'Import dashboards/runtime.json into local Grafana after Prometheus is installed.'
