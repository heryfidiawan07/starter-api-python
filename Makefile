install:
	pip install -r requirements.txt

run:
	uvicorn main:app --host 0.0.0.0 --port 8000 --reload

dev:
	uvicorn main:app --reload

start:
	python main.py

.PHONY: install run dev start
