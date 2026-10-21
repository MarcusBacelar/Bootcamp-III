# Imagem base leve e fixa: garante o mesmo ambiente em qualquer máquina.
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Dependências primeiro, para aproveitar o cache de camadas do Docker.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código, testes e especificação.
COPY src/ ./src/
COPY tests/ ./tests/
COPY specs/ ./specs/

# Comando padrão: executa a suíte de testes inteira.
CMD ["pytest", "tests/test_harness.py", "-v"]
