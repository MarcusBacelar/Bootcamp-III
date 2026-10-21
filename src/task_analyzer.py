"""Módulo de análise de tarefas e produtividade (TaskAnalyzer).

Biblioteca pura: sem interface gráfica, sem persistência e sem efeitos
colaterais. Calcula o tempo médio de conclusão, a taxa de atraso e os
indicadores agrupados por prioridade.

Ver specs/task_analyzer_spec.md para o contrato de negócio completo.
"""

import logging
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)

PRIORIDADES_VALIDAS: tuple[str, ...] = ("baixa", "media", "alta")
STATUS_VALIDOS: tuple[str, ...] = ("pendente", "em_andamento", "concluida", "cancelada")
CAMPOS_OBRIGATORIOS: tuple[str, ...] = (
    "id_tarefa",
    "titulo",
    "prioridade",
    "data_criacao",
    "status",
)


class TaskAnalyzerError(Exception):
    """Erro base de todas as exceções do módulo."""


class CampoObrigatorioAusenteError(TaskAnalyzerError):
    """Um campo obrigatório não foi informado no registro da tarefa."""


class ValorInvalidoError(TaskAnalyzerError):
    """Um campo foi informado com valor fora do domínio permitido."""


class DataInvalidaError(TaskAnalyzerError):
    """As datas da tarefa são inconsistentes entre si."""


@dataclass(frozen=True)
class Tarefa:
    """Representação validada de uma tarefa.

    Attributes:
        id_tarefa: Identificador único (UUID em texto).
        titulo: Descrição curta da tarefa.
        prioridade: Um de PRIORIDADES_VALIDAS.
        data_criacao: Momento de criação, em UTC.
        status: Um de STATUS_VALIDOS.
        data_conclusao: Momento de conclusão, em UTC, quando houver.
        prazo_estimado: Prazo previsto para conclusão, em UTC, quando houver.
    """

    id_tarefa: str
    titulo: str
    prioridade: str
    data_criacao: datetime
    status: str
    data_conclusao: Optional[datetime] = None
    prazo_estimado: Optional[datetime] = None


@dataclass(frozen=True)
class IndicadorPrioridade:
    """Indicadores calculados para um grupo de tarefas de mesma prioridade.

    Attributes:
        quantidade_tarefas: Número de tarefas do grupo, sem as canceladas.
        tempo_medio_conclusao_horas: Média, em horas, das tarefas concluídas.
        taxa_atraso_percentual: Percentual de tarefas concluídas após o prazo.
    """

    quantidade_tarefas: int
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float


@dataclass(frozen=True)
class ResultadoAnalise:
    """Resultado consolidado da análise.

    Attributes:
        quantidade_tarefas_total: Total de tarefas, sem as canceladas.
        tempo_medio_conclusao_horas: Média, em horas, das tarefas concluídas.
        taxa_atraso_percentual: Percentual de 0 a 100 de tarefas concluídas
            após o prazo estimado.
        indicadores_por_prioridade: Um indicador por prioridade presente.
        gerado_em: Momento da geração do resultado, em UTC.
    """

    quantidade_tarefas_total: int
    tempo_medio_conclusao_horas: float
    taxa_atraso_percentual: float
    indicadores_por_prioridade: dict[str, IndicadorPrioridade]
    gerado_em: datetime


def analisar_tarefas(
    registros: Iterable[Mapping[str, Any]],
    gerado_em: Optional[datetime] = None,
) -> ResultadoAnalise:
    """Calcula as métricas de produtividade de um conjunto de tarefas.

    A função não altera os registros recebidos e não grava nada. Tarefas
    canceladas são validadas, mas ficam fora de todas as métricas.

    Args:
        registros: Registros de tarefa com os campos do contrato de entrada.
        gerado_em: Momento a registrar no resultado. Se omitido, usa o
            horário atual em UTC.

    Returns:
        O ResultadoAnalise com as métricas calculadas. Uma lista vazia
        resulta em métricas zeradas.

    Raises:
        CampoObrigatorioAusenteError: Se um campo obrigatório estiver ausente.
        ValorInvalidoError: Se um campo tiver valor fora do domínio.
        DataInvalidaError: Se data_conclusao não for posterior a data_criacao.
    """
    tarefas = [criar_tarefa(registro) for registro in registros]
    ativas = [tarefa for tarefa in tarefas if tarefa.status != "cancelada"]

    indicadores: dict[str, IndicadorPrioridade] = {}
    for prioridade in PRIORIDADES_VALIDAS:
        grupo = [tarefa for tarefa in ativas if tarefa.prioridade == prioridade]
        if grupo:
            indicadores[prioridade] = IndicadorPrioridade(
                quantidade_tarefas=len(grupo),
                tempo_medio_conclusao_horas=_tempo_medio_horas(grupo),
                taxa_atraso_percentual=_taxa_atraso(grupo),
            )

    resultado = ResultadoAnalise(
        quantidade_tarefas_total=len(ativas),
        tempo_medio_conclusao_horas=_tempo_medio_horas(ativas),
        taxa_atraso_percentual=_taxa_atraso(ativas),
        indicadores_por_prioridade=indicadores,
        gerado_em=gerado_em or datetime.now(timezone.utc),
    )
    logger.debug("Análise concluída: %d tarefas ativas", resultado.quantidade_tarefas_total)
    return resultado


def criar_tarefa(registro: Mapping[str, Any]) -> Tarefa:
    """Valida um registro bruto e o converte em Tarefa.

    Args:
        registro: Mapeamento com os campos de entrada da tarefa.

    Returns:
        Uma Tarefa validada, com datas normalizadas para UTC.

    Raises:
        CampoObrigatorioAusenteError: Se um campo obrigatório estiver ausente,
            ou se uma tarefa concluída não tiver data_conclusao.
        ValorInvalidoError: Se algum campo tiver valor inválido.
        DataInvalidaError: Se data_conclusao não for posterior a data_criacao.
    """
    for campo in CAMPOS_OBRIGATORIOS:
        if registro.get(campo) is None:
            raise CampoObrigatorioAusenteError(f"Campo obrigatório ausente: '{campo}'")

    id_tarefa = _texto_nao_vazio(registro["id_tarefa"], "id_tarefa")
    titulo = _texto_nao_vazio(registro["titulo"], "titulo")

    prioridade = registro["prioridade"]
    if prioridade not in PRIORIDADES_VALIDAS:
        raise ValorInvalidoError(
            f"Prioridade inválida: {prioridade!r}. Valores aceitos: {PRIORIDADES_VALIDAS}"
        )

    status = registro["status"]
    if status not in STATUS_VALIDOS:
        raise ValorInvalidoError(
            f"Status inválido: {status!r}. Valores aceitos: {STATUS_VALIDOS}"
        )

    data_criacao = _converter_data(registro["data_criacao"], "data_criacao")
    data_conclusao = _converter_data_opcional(registro.get("data_conclusao"), "data_conclusao")
    prazo_estimado = _converter_data_opcional(registro.get("prazo_estimado"), "prazo_estimado")

    if status == "concluida" and data_conclusao is None:
        raise CampoObrigatorioAusenteError(
            "Campo obrigatório ausente: 'data_conclusao' (exigido para tarefas concluídas)"
        )
    if data_conclusao is not None and data_conclusao <= data_criacao:
        raise DataInvalidaError(
            "data_conclusao deve ser posterior a data_criacao "
            f"({data_conclusao.isoformat()} <= {data_criacao.isoformat()})"
        )

    return Tarefa(
        id_tarefa=id_tarefa,
        titulo=titulo,
        prioridade=prioridade,
        data_criacao=data_criacao,
        status=status,
        data_conclusao=data_conclusao,
        prazo_estimado=prazo_estimado,
    )


def _texto_nao_vazio(valor: Any, campo: str) -> str:
    """Garante que o valor seja texto não vazio."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValorInvalidoError(f"'{campo}' deve ser um texto não vazio")
    return valor


def _converter_data_opcional(valor: Any, campo: str) -> Optional[datetime]:
    """Converte a data quando informada; devolve None quando ausente."""
    if valor is None:
        return None
    return _converter_data(valor, campo)


def _converter_data(valor: Any, campo: str) -> datetime:
    """Converte datetime ou texto ISO 8601 com fuso em datetime UTC."""
    if isinstance(valor, datetime):
        data = valor
    elif isinstance(valor, str):
        try:
            data = datetime.fromisoformat(valor)
        except ValueError as erro:
            raise ValorInvalidoError(f"'{campo}' não está em ISO 8601: {valor!r}") from erro
    else:
        raise ValorInvalidoError(f"'{campo}' deve ser datetime ou texto ISO 8601")

    if data.tzinfo is None:
        raise ValorInvalidoError(f"'{campo}' precisa informar fuso horário (UTC)")
    return data.astimezone(timezone.utc)


def _tempo_medio_horas(tarefas: list[Tarefa]) -> float:
    """Média, em horas, do tempo entre criação e conclusão das tarefas concluídas."""
    concluidas = [t for t in tarefas if t.status == "concluida"]
    if not concluidas:
        return 0.0
    segundos = sum((t.data_conclusao - t.data_criacao).total_seconds() for t in concluidas)
    return segundos / 3600 / len(concluidas)


def _taxa_atraso(tarefas: list[Tarefa]) -> float:
    """Percentual de tarefas concluídas depois do prazo estimado.

    Só entram no cálculo as tarefas concluídas que possuem prazo_estimado.
    """
    elegiveis = [t for t in tarefas if t.status == "concluida" and t.prazo_estimado is not None]
    if not elegiveis:
        return 0.0
    atrasadas = sum(1 for t in elegiveis if t.data_conclusao > t.prazo_estimado)
    return atrasadas / len(elegiveis) * 100
