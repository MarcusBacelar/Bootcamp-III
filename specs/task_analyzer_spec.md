# Especificação SDD — TaskAnalyzer

## 1. Visão geral e contrato de negócio

**Propósito:** módulo de análise de tarefas e produtividade. É uma biblioteca pura, sem interface gráfica e sem persistência. Calcula:

- tempo médio de conclusão, em horas;
- taxa de atraso, em percentual;
- indicadores por prioridade.

### 1.1 Entrada: registro de tarefa

| Campo | Tipo | Obrigatório | Regra |
|---|---|---|---|
| `id_tarefa` | texto (UUID) | sim | não vazio |
| `titulo` | texto | sim | não vazio |
| `prioridade` | enum | sim | `baixa`, `media` ou `alta` |
| `data_criacao` | datetime ISO 8601 | sim | em UTC |
| `data_conclusao` | datetime ISO 8601 | não | posterior a `data_criacao`; obrigatória se `status` for `concluida` |
| `prazo_estimado` | datetime ISO 8601 | não | em UTC |
| `status` | enum | sim | `pendente`, `em_andamento`, `concluida` ou `cancelada` |

### 1.2 Saída: `ResultadoAnalise`

| Campo | Tipo | Descrição |
|---|---|---|
| `quantidade_tarefas_total` | int | tarefas, sem as canceladas |
| `tempo_medio_conclusao_horas` | float | média das tarefas concluídas |
| `taxa_atraso_percentual` | float (0–100) | concluídas após o prazo, entre as que têm prazo |
| `indicadores_por_prioridade` | dict[str, IndicadorPrioridade] | uma entrada por prioridade presente |
| `gerado_em` | datetime UTC | momento da geração |

Cada `IndicadorPrioridade` contém `quantidade_tarefas`, `tempo_medio_conclusao_horas` e `taxa_atraso_percentual`, com o mesmo significado acima, restrito ao grupo.

### 1.3 Regras de negócio

1. Só tarefas `concluida` entram no tempo médio.
2. Tarefas `cancelada` são excluídas de todas as métricas.
3. `data_conclusao` deve ser posterior a `data_criacao`. Caso contrário, `DataInvalidaError`.
4. Todas as datas são UTC. Datas sem fuso são rejeitadas.
5. Lista vazia produz métricas zeradas, sem exceção.
6. Campo obrigatório ausente gera `CampoObrigatorioAusenteError`. Valor inválido gera `ValorInvalidoError`.
7. A função pública não tem efeitos colaterais.

### 1.4 Premissas registradas

Estes pontos não estavam detalhados no contrato original. Foram definidos aqui e precisam de confirmação antes da Fase 2:

- **Atraso:** uma tarefa concluída está atrasada quando `data_conclusao > prazo_estimado`. A taxa considera só as concluídas que têm `prazo_estimado`.
- **Tarefa concluída sem `data_conclusao`:** é tratada como campo obrigatório ausente.
- **`IndicadorPrioridade`:** a estrutura interna foi definida com os três campos listados acima.
- **`gerado_em`:** é opcional na função. Se omitido, usa o horário atual em UTC.

## 2. Cenários de aceite

1. **Sucesso:** conjunto válido com várias prioridades produz as métricas corretas.
2. **Exceção:** `data_conclusao` anterior a `data_criacao` lança `DataInvalidaError`.
3. **Borda:** lista vazia produz métricas zeradas, sem exceção.
4. **Exceção:** campo `prioridade` ausente lança `CampoObrigatorioAusenteError`.
5. **Sucesso:** `indicadores_por_prioridade` tem uma entrada por prioridade presente.
6. **Exceção:** prioridade fora do domínio (ex.: `urgente`) lança `ValorInvalidoError`.

Os cenários são imutáveis na Fase 2. Eles estão em `tests/test_harness.py`.

## 3. Critério de homologação

- Cobertura mínima de 90% em `src/task_analyzer.py`.
- 100% dos testes passando.
- Execução: `pytest --cov=src --cov-report=term-missing`.
