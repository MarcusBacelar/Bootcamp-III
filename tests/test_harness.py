"""Test Harness do TaskAnalyzer (pytest).

Traduz os cenários de aceite da especificação:
    Cenário 1 - cálculos de sucesso.
    Cenário 2 - datas inconsistentes disparam TaskValidationError.
    Casos de borda - lista vazia e apenas tarefas pendentes.
"""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from task_analyzer import Task, TaskValidationError, analyze_tasks  # noqa: E402


def dt(dia: int, hora: int = 0) -> datetime:
    return datetime(2026, 10, dia, hora, 0)


# --- Cenário 1: cálculos de sucesso -------------------------------------------

def test_cenario_1_metricas_de_sucesso() -> None:
    tarefas = [
        # Alta: 12h, dentro do prazo
        Task("A", "alta", dt(1, 8), dt(1, 20), dt(2)),
        # Alta: 48h, concluída após o prazo
        Task("B", "alta", dt(1, 8), dt(3, 8), dt(2)),
        # Baixa: 6h, dentro do prazo
        Task("C", "baixa", dt(5, 0), dt(5, 6), dt(6)),
        # Pendente
        Task("D", "baixa", dt(5, 0)),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_tarefas"] == 4
    assert resultado["total_concluidas"] == 3
    assert resultado["total_pendentes"] == 1
    assert resultado["tempo_medio_conclusao_horas"] == 22.0
    assert resultado["tempo_medio_por_prioridade"] == {"alta": 30.0, "baixa": 6.0}
    assert resultado["taxa_atraso_percentual"] == pytest.approx(33.33)


# --- Cenário 2: exceção por datas inconsistentes ------------------------------

def test_cenario_2_conclusao_anterior_a_criacao_dispara_erro() -> None:
    tarefas = [Task("X", "alta", dt(10, 12), dt(10, 8))]

    with pytest.raises(TaskValidationError):
        analyze_tasks(tarefas)


def test_cenario_2_erro_nao_e_silenciado_em_meio_a_lote_valido() -> None:
    tarefas = [
        Task("OK", "alta", dt(1, 8), dt(1, 9)),
        Task("INVALIDA", "baixa", dt(2, 8), dt(1, 8)),
    ]

    with pytest.raises(TaskValidationError):
        analyze_tasks(tarefas)


# --- Casos de borda -----------------------------------------------------------

def test_borda_lista_vazia_retorna_zeros_sem_excecao() -> None:
    resultado = analyze_tasks([])

    assert resultado == {
        "total_tarefas": 0,
        "total_concluidas": 0,
        "total_pendentes": 0,
        "tempo_medio_conclusao_horas": 0.0,
        "tempo_medio_por_prioridade": {},
        "taxa_atraso_percentual": 0.0,
    }


def test_borda_apenas_pendentes_retorna_medias_zero() -> None:
    tarefas = [
        Task("P1", "alta", dt(1)),
        Task("P2", "baixa", dt(2)),
    ]

    resultado = analyze_tasks(tarefas)

    assert resultado["total_tarefas"] == 2
    assert resultado["total_concluidas"] == 0
    assert resultado["total_pendentes"] == 2
    assert resultado["tempo_medio_conclusao_horas"] == 0.0
    assert resultado["tempo_medio_por_prioridade"] == {}
    assert resultado["taxa_atraso_percentual"] == 0.0


def test_borda_concluidas_sem_prazo_nao_geram_taxa_de_atraso() -> None:
    tarefas = [Task("S", "media", dt(1, 8), dt(1, 10))]

    resultado = analyze_tasks(tarefas)

    assert resultado["tempo_medio_conclusao_horas"] == 2.0
    assert resultado["taxa_atraso_percentual"] == 0.0
