# Makefile para automação de tarefas

.PHONY: install run test lint format clean help

help:
	@echo "Comandos disponíveis:"
	@echo "  make install    - Instala as dependências"
	@echo "  make run        - Executa a aplicação"
	@echo "  make test       - Executa os testes"
	@echo "  make test-cov   - Executa testes com cobertura"
	@echo "  make lint       - Verifica o código (flake8)"
	@echo "  make format     - Formata o código (black, isort)"
	@echo "  make clean      - Remove arquivos temporários"
	@echo "  make db-create  - Cria as tabelas do banco de dados"

install:
	pip install -r requirements.txt

run:
	python run.py

test:
	pytest

test-cov:
	pytest --cov=app --cov-report=html

lint:
	flake8 app tests

format:
	black app tests
	isort app tests

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".pytest_cache" -exec rm -rf {} +
	find . -type f -name ".coverage" -delete
	find . -type d -name "htmlcov" -exec rm -rf {} +

db-create:
	python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine); print('Database tables created successfully')"
