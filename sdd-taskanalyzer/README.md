# sdd-taskanalyzer

Sistema TaskAnalyzer desenvolvido com Spec-Driven Development (SDD) e assistentes de IA, com Test Harness em pytest.

**Status do build:** testes locais executados, ver seção *Execução*.

## Estrutura

```
sdd-taskanalyzer/
├── README.md
├── CONTEXT_RULES.md          # regras de governança para a IA
├── .gitignore
├── requirements.txt
├── specs/
│   └── task_analyzer_spec.md # contrato SDD
├── tests/
│   └── test_harness.py       # cenários de aceite 1 e 2 + casos de borda
└── src/
    └── task_analyzer.py      # função analyze_tasks e TaskValidationError
```

## Requisitos

- Python 3.11+

## Instalação

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Execução dos testes

```bash
pytest -v
```

## Uso

```python
from datetime import datetime
from src.task_analyzer import Task, analyze_tasks

tarefas = [
    Task("Relatório", "alta", datetime(2026, 10, 1, 8), datetime(2026, 10, 1, 20), datetime(2026, 10, 2)),
    Task("Revisão", "baixa", datetime(2026, 10, 5)),
]
print(analyze_tasks(tarefas))
```

## Fluxo de contribuição

- `main` é a branch estável.
- Funcionalidades são desenvolvidas em `feature/*` e integradas via Pull Request.
