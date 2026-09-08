lint:
	pre-commit run --all-files

start:
	python -m uvicorn run:app --host 0.0.0.0 --port 5000

test:
	pytest tests -q
