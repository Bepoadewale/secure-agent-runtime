.PHONY: install test lint run demo demo-security bootstrap-local destroy-local helm-lint dashboards
install:
	python3 -m pip install -e '.[dev]'
test:
	PYTHONPATH=control-plane/src python3 -m pytest -q
lint:
	python3 -m ruff check control-plane/src control-plane/tests
run:
	PYTHONPATH=control-plane/src uvicorn agent_runtime.api.main:app --port 8000 --reload
demo:
	PYTHONPATH=control-plane/src python3 examples/demo.py
demo-security:
	PYTHONPATH=control-plane/src python3 examples/security_demo.py
bootstrap-local:
	./scripts/bootstrap-local.sh
destroy-local:
	kind delete cluster --name secure-agent-runtime-local
helm-lint:
	helm lint platform/helm/agent-runtime
dashboards:
	@echo 'Import dashboards/runtime.json into local Grafana after Prometheus is installed.'
