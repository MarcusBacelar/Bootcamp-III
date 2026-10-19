"""Analisador de tarefas: calcula métricas de conclusão e atraso.

Implementa o contrato definido em specs/task_analyzer_spec.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Iterable


class TaskValidationError(ValueError):
    """Levantada quando os dados de uma tarefa são inconsistentes."""


@dataclass(frozen=True)
class Task:
    """Uma tarefa com datas de criação, conclusão opcional e prazo opcional."""

    titulo: str
    prioridade: str
    data_criacao: datetime
    data_conclusao: datetime | None = None
    prazo: datetime | None = None

    @property
    def concluida(self) -> bool:
        return self.data_conclusao is not None


def _validar(task: Task) -> None:
    """Garante que a data de conclusão não é anterior à criação."""
    if task.data_conclusao is not None and task.data_conclusao < task.data_criacao:
        raise TaskValidationError(
            f"Tarefa '{task.titulo}': data_conclusao ({task.data_conclusao}) "
            f"é anterior a data_criacao ({task.data_criacao})."
        )


def _duracao_horas(task: Task) -> float:
    """Tempo entre criação e conclusão, em horas. Só para tarefas concluídas."""
    if task.data_conclusao is None:
        raise TaskValidationError(f"Tarefa '{task.titulo}' não está concluída.")
    return (task.data_conclusao - task.data_criacao).total_seconds() / 3600.0


def _media(valores: list[float]) -> float:
    """Média aritmética; retorna 0.0 para lista vazia (evita divisão por zero)."""
    if not valores:
        return 0.0
    return sum(valores) / len(valores)


def _percentual(parte: int, total: int) -> float:
    """Percentual de parte sobre total; retorna 0.0 se total for zero."""
    if total == 0:
        return 0.0
    return parte / total * 100.0


def analyze_tasks(tasks: Iterable[Task]) -> dict[str, Any]:
    """Calcula as métricas agregadas de uma coleção de tarefas.

    Retorna um dicionário com:
        total_tarefas: quantidade total de tarefas.
        total_concluidas: quantidade de tarefas com data_conclusao.
        total_pendentes: quantidade de tarefas sem data_conclusao.
        tempo_medio_conclusao_horas: média geral de horas até a conclusão.
        tempo_medio_por_prioridade: média de horas por prioridade.
        taxa_atraso_percentual: percentual de tarefas concluídas com prazo
            que foram concluídas após o prazo.

    Raises:
        TaskValidationError: se alguma tarefa tiver data_conclusao anterior
            a data_criacao.
    """
    lista: list[Task] = list(tasks)
    for task in lista:
        _validar(task)

    concluidas = [t for t in lista if t.concluida]
    duracoes = [_duracao_horas(t) for t in concluidas]

    por_prioridade: dict[str, list[float]] = {}
    for task in concluidas:
        por_prioridade.setdefault(task.prioridade, []).append(_duracao_horas(task))

    com_prazo = [t for t in concluidas if t.prazo is not None]
    atrasadas = [t for t in com_prazo if t.data_conclusao is not None and t.prazo is not None
                 and t.data_conclusao > t.prazo]

    return {
        "total_tarefas": len(lista),
        "total_concluidas": len(concluidas),
        "total_pendentes": len(lista) - len(concluidas),
        "tempo_medio_conclusao_horas": round(_media(duracoes), 2),
        "tempo_medio_por_prioridade": {
            prioridade: round(_media(valores), 2)
            for prioridade, valores in por_prioridade.items()
        },
        "taxa_atraso_percentual": round(_percentual(len(atrasadas), len(com_prazo)), 2),
    }
