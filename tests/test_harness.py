"""Test harness do TaskAnalyzer.

Os seis primeiros testes (cenario_1 a cenario_6) correspondem aos cenários de
aceite da especificação e não devem ser alterados na Fase 2.
Os demais testes cobrem regras de borda e validações adicionais.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.task_analyzer import (  # noqa: E402
    CampoObrigatorioAusenteError,
    DataInvalidaError,
    ResultadoAnalise,
    ValorInvalidoError,
    analisar_tarefas,
    criar_tarefa,
)


def _registro(**campos):
    """Monta um registro de tarefa válido, sobrescrevendo os campos informados."""
    base = {
        "id_tarefa": "11111111-1111-1111-1111-111111111111",
        "titulo": "Tarefa de teste",
        "prioridade": "media",
        "data_criacao": "2026-10-01T08:00:00+00:00",
        "status": "pendente",
    }
    base.update(campos)
    return base


@pytest.fixture
def conjunto_multiprioridade():
    """Conjunto válido com todas as prioridades e um registro cancelado."""
    return [
        _registro(
            id_tarefa="t1",
            prioridade="alta",
            data_criacao="2026-10-01T08:00:00+00:00",
            data_conclusao="2026-10-01T12:00:00+00:00",
            prazo_estimado="2026-10-01T10:00:00+00:00",
            status="concluida",
        ),
        _registro(
            id_tarefa="t2",
            prioridade="alta",
            data_criacao="2026-10-02T08:00:00+00:00",
            data_conclusao="2026-10-02T10:00:00+00:00",
            prazo_estimado="2026-10-02T12:00:00+00:00",
            status="concluida",
        ),
        _registro(
            id_tarefa="t3",
            prioridade="baixa",
            data_criacao="2026-10-03T08:00:00+00:00",
            data_conclusao="2026-10-03T14:00:00+00:00",
            prazo_estimado="2026-10-03T12:00:00+00:00",
            status="concluida",
        ),
        _registro(id_tarefa="t4", prioridade="media", status="pendente"),
        _registro(id_tarefa="t5", prioridade="media", status="cancelada"),
    ]


@pytest.fixture
def conjunto_apenas_alta_e_baixa():
    """Conjunto sem tarefas de prioridade média."""
    return [
        _registro(
            id_tarefa="a1",
            prioridade="alta",
            data_conclusao="2026-10-01T09:00:00+00:00",
            status="concluida",
        ),
        _registro(id_tarefa="b1", prioridade="baixa", status="em_andamento"),
    ]


# --- Cenários de aceite -----------------------------------------------------


def test_cenario_1_sucesso_conjunto_multiprioridade_calcula_metricas_corretas(
    conjunto_multiprioridade,
):
    """Sucesso: conjunto válido multi-prioridade produz as métricas esperadas."""
    resultado = analisar_tarefas(conjunto_multiprioridade)

    assert resultado.quantidade_tarefas_total == 4
    assert resultado.tempo_medio_conclusao_horas == pytest.approx(4.0)
    assert resultado.taxa_atraso_percentual == pytest.approx(200 / 3)


def test_cenario_2_excecao_data_conclusao_anterior_a_criacao_gera_erro():
    """Exceção: data_conclusao anterior a data_criacao lança DataInvalidaError."""
    registro = _registro(
        data_criacao="2026-10-05T08:00:00+00:00",
        data_conclusao="2026-10-04T08:00:00+00:00",
        status="concluida",
    )
    with pytest.raises(DataInvalidaError):
        analisar_tarefas([registro])


def test_cenario_3_borda_lista_vazia_retorna_metricas_zeradas():
    """Borda: lista vazia produz métricas zeradas sem exceção."""
    resultado = analisar_tarefas([])

    assert isinstance(resultado, ResultadoAnalise)
    assert resultado.quantidade_tarefas_total == 0
    assert resultado.tempo_medio_conclusao_horas == 0.0
    assert resultado.taxa_atraso_percentual == 0.0
    assert resultado.indicadores_por_prioridade == {}


def test_cenario_4_excecao_prioridade_ausente_gera_campo_obrigatorio_ausente():
    """Exceção: campo prioridade ausente lança CampoObrigatorioAusenteError."""
    registro = _registro()
    del registro["prioridade"]
    with pytest.raises(CampoObrigatorioAusenteError, match="prioridade"):
        analisar_tarefas([registro])


def test_cenario_5_sucesso_indicadores_tem_uma_entrada_por_prioridade_presente(
    conjunto_multiprioridade,
):
    """Sucesso: indicadores_por_prioridade contém uma entrada por prioridade presente."""
    resultado = analisar_tarefas(conjunto_multiprioridade)

    assert set(resultado.indicadores_por_prioridade) == {"alta", "media", "baixa"}
    assert resultado.indicadores_por_prioridade["alta"].quantidade_tarefas == 2
    assert resultado.indicadores_por_prioridade["alta"].tempo_medio_conclusao_horas == pytest.approx(3.0)
    assert resultado.indicadores_por_prioridade["alta"].taxa_atraso_percentual == pytest.approx(50.0)
    assert resultado.indicadores_por_prioridade["baixa"].taxa_atraso_percentual == pytest.approx(100.0)
    assert resultado.indicadores_por_prioridade["media"].tempo_medio_conclusao_horas == 0.0


def test_cenario_6_excecao_prioridade_fora_do_dominio_gera_valor_invalido():
    """Exceção: prioridade fora do domínio (ex.: 'urgente') lança ValorInvalidoError."""
    with pytest.raises(ValorInvalidoError, match="urgente"):
        analisar_tarefas([_registro(prioridade="urgente")])


# --- Regras de borda e validações adicionais --------------------------------


def test_regra_apenas_prioridades_presentes_aparecem_nos_indicadores(conjunto_apenas_alta_e_baixa):
    """Prioridades sem tarefas não geram indicador."""
    resultado = analisar_tarefas(conjunto_apenas_alta_e_baixa)

    assert set(resultado.indicadores_por_prioridade) == {"alta", "baixa"}


def test_regra_tarefas_canceladas_ficam_fora_de_todas_as_metricas(conjunto_multiprioridade):
    """Canceladas não contam no total nem em nenhum indicador."""
    resultado = analisar_tarefas(conjunto_multiprioridade)

    assert resultado.quantidade_tarefas_total == 4
    assert resultado.indicadores_por_prioridade["media"].quantidade_tarefas == 1


def test_regra_conjunto_so_com_canceladas_retorna_metricas_zeradas():
    """Se todas as tarefas forem canceladas, o resultado é zerado."""
    resultado = analisar_tarefas([_registro(status="cancelada")])

    assert resultado.quantidade_tarefas_total == 0
    assert resultado.indicadores_por_prioridade == {}


def test_regra_concluida_sem_data_conclusao_gera_campo_obrigatorio_ausente():
    """Tarefa concluída exige data_conclusao."""
    with pytest.raises(CampoObrigatorioAusenteError, match="data_conclusao"):
        analisar_tarefas([_registro(status="concluida")])


def test_regra_taxa_atraso_ignora_concluidas_sem_prazo():
    """Concluídas sem prazo_estimado não entram na taxa de atraso."""
    registro = _registro(
        data_conclusao="2026-10-01T12:00:00+00:00",
        status="concluida",
    )
    resultado = analisar_tarefas([registro])

    assert resultado.taxa_atraso_percentual == 0.0


def test_regra_data_conclusao_igual_a_criacao_gera_data_invalida():
    """Conclusão no mesmo instante da criação não é posterior e deve falhar."""
    registro = _registro(
        data_criacao="2026-10-01T08:00:00+00:00",
        data_conclusao="2026-10-01T08:00:00+00:00",
        status="concluida",
    )
    with pytest.raises(DataInvalidaError):
        analisar_tarefas([registro])


def test_regra_datas_com_fuso_diferente_sao_normalizadas_para_utc():
    """Datas com outro fuso são convertidas para UTC antes do cálculo."""
    tarefa = criar_tarefa(
        _registro(data_criacao="2026-10-01T05:00:00-03:00", status="pendente")
    )

    assert tarefa.data_criacao == datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)


def test_regra_aceita_datetime_ja_construido():
    """Datetime nativo com fuso é aceito no lugar de texto ISO."""
    criacao = datetime(2026, 10, 1, 8, 0, tzinfo=timezone.utc)
    tarefa = criar_tarefa(_registro(data_criacao=criacao))

    assert tarefa.data_criacao == criacao


def test_regra_gerado_em_usa_horario_atual_em_utc_quando_omitido():
    """Sem gerado_em explícito, o resultado recebe o horário atual em UTC."""
    resultado = analisar_tarefas([])

    assert resultado.gerado_em.tzinfo is not None
    assert resultado.gerado_em.utcoffset().total_seconds() == 0


def test_regra_gerado_em_informado_e_preservado():
    """gerado_em informado é devolvido sem alteração (função determinística)."""
    momento = datetime(2026, 10, 21, 12, 0, tzinfo=timezone.utc)
    resultado = analisar_tarefas([], gerado_em=momento)

    assert resultado.gerado_em == momento


def test_regra_entrada_nao_e_alterada_pela_analise(conjunto_multiprioridade):
    """A função é pura: os registros de entrada permanecem iguais."""
    copia = [dict(r) for r in conjunto_multiprioridade]
    analisar_tarefas(conjunto_multiprioridade)

    assert conjunto_multiprioridade == copia


@pytest.mark.parametrize("campo", ["id_tarefa", "titulo"])
def test_validacao_texto_vazio_gera_valor_invalido(campo):
    """id_tarefa e titulo não podem ser vazios."""
    with pytest.raises(ValorInvalidoError, match=campo):
        analisar_tarefas([_registro(**{campo: "   "})])


def test_validacao_status_fora_do_dominio_gera_valor_invalido():
    """Status fora do domínio lança ValorInvalidoError."""
    with pytest.raises(ValorInvalidoError, match="Status"):
        analisar_tarefas([_registro(status="arquivada")])


def test_validacao_data_em_formato_invalido_gera_valor_invalido():
    """Texto que não é ISO 8601 lança ValorInvalidoError."""
    with pytest.raises(ValorInvalidoError, match="ISO 8601"):
        analisar_tarefas([_registro(data_criacao="01/10/2026")])


def test_validacao_data_sem_fuso_gera_valor_invalido():
    """Datas sem fuso horário são rejeitadas, pois o contrato exige UTC."""
    with pytest.raises(ValorInvalidoError, match="fuso"):
        analisar_tarefas([_registro(data_criacao="2026-10-01T08:00:00")])


def test_validacao_tipo_de_data_invalido_gera_valor_invalido():
    """Tipos diferentes de datetime ou texto são rejeitados."""
    with pytest.raises(ValorInvalidoError, match="datetime"):
        analisar_tarefas([_registro(data_criacao=1727769600)])


def test_validacao_id_tarefa_nao_textual_gera_valor_invalido():
    """id_tarefa precisa ser texto."""
    with pytest.raises(ValorInvalidoError, match="id_tarefa"):
        analisar_tarefas([_registro(id_tarefa=123)])
