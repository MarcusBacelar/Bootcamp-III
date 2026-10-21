# sdd-task-analyzer

Módulo **TaskAnalyzer** de análise de tarefas e produtividade, desenvolvido como projeto cumulativo do Bootcamp III.

Calcula o tempo médio de conclusão, a taxa de atraso e os indicadores por prioridade. É uma biblioteca pura, sem interface e sem persistência.

## Estrutura

```
sdd-task-analyzer/
├── .github/workflows/ci.yml   # CI: testes automatizados no GitHub Actions
├── Dockerfile                 # Imagem python:3.11-slim
├── docker-compose.yml         # Execução da suíte em um único comando
├── CONTEXT_RULES.md           # Governança de IA
├── specs/task_analyzer_spec.md
├── requirements.txt
├── src/task_analyzer.py
├── tests/test_harness.py
└── README.md
```

## Como executar

### Localmente (Python 3.11+)

```bash
pip install -r requirements.txt
pytest tests/test_harness.py -v
pytest --cov=src --cov-report=term-missing
```

### Com Docker

```bash
docker compose run --rm tests
```

Ou, sem o Compose:

```bash
docker build -t sdd-task-analyzer .
docker run --rm sdd-task-analyzer
```

## Integração contínua

O workflow `.github/workflows/ci.yml` roda a suíte em `ubuntu-latest` com Python 3.11. Ele é disparado por push e Pull Request nas branches `main` e `develop`, e exige cobertura mínima de 90%.

## Documentação

- Especificação: [specs/task_analyzer_spec.md](specs/task_analyzer_spec.md)
- Regras para IA: [CONTEXT_RULES.md](CONTEXT_RULES.md)

## Versionamento

Git Flow simplificado: `main`, `develop` e `feature/*`. Commits no padrão Conventional Commits. Merge somente por Pull Request revisado.
