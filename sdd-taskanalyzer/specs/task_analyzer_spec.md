# Especificação SDD — TaskAnalyzer

> **RASCUNHO.** Este arquivo foi reconstruído a partir do enunciado da Fase 2.
> Substitua pelo conteúdo do seu documento da Fase 1 (Google Docs) antes de
> entregar. Se houver divergência, a especificação da Fase 1 vale.

## 1. Objetivo

Calcular métricas agregadas sobre uma lista de tarefas.

## 2. Entrada

Lista de objetos `Task` com os campos:

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| titulo | str | sim | Identificação da tarefa |
| prioridade | str | sim | Ex.: "alta", "media", "baixa" |
| data_criacao | datetime | sim | Momento de criação |
| data_conclusao | datetime \| None | não | Momento de conclusão; ausente = pendente |
| prazo | datetime \| None | não | Data limite para conclusão |

## 3. Saída

Dicionário com:

- `total_tarefas`: número total de tarefas.
- `total_concluidas`: tarefas com `data_conclusao`.
- `total_pendentes`: tarefas sem `data_conclusao`.
- `tempo_medio_conclusao_horas`: média, em horas, de `data_conclusao - data_criacao` entre as concluídas. Arredondado em 2 casas.
- `tempo_medio_por_prioridade`: mesma média, agrupada por `prioridade`.
- `taxa_atraso_percentual`: `atrasadas / concluidas_com_prazo * 100`, onde atrasada = `data_conclusao > prazo`. Arredondado em 2 casas.

## 4. Regras

- R1: Se `data_conclusao < data_criacao`, levantar `TaskValidationError`.
- R2: Médias sem elementos retornam `0.0`. Nunca lançar exceção por divisão por zero.
- R3: Tarefas pendentes não entram em médias de tempo.

## 5. Cenários de aceite (Dado-Quando-Então)

**Cenário 1 — Sucesso**
- Dado 4 tarefas: 3 concluídas (12h, 48h e 6h; a de 48h após o prazo) e 1 pendente
- Quando `analyze_tasks` é chamada
- Então total = 4, concluídas = 3, pendentes = 1, tempo médio geral = 22.0, média alta = 30.0, média baixa = 6.0, taxa de atraso = 33.33

**Cenário 2 — Erro**
- Dado uma tarefa com `data_conclusao` anterior a `data_criacao`
- Quando `analyze_tasks` é chamada
- Então é levantada `TaskValidationError`

**Casos de borda**
- Lista vazia → todos os zeros, sem exceção.
- Apenas pendentes → médias zero, taxa de atraso zero.
