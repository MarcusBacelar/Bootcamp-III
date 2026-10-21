# CONTEXT_RULES — Governança de IA do TaskAnalyzer

Regras que todo agente de IA (ou pessoa) deve seguir ao gerar ou alterar código neste repositório. A especificação de negócio está em `specs/task_analyzer_spec.md`.

## Diretrizes obrigatórias

- Python 3.11+, com type hints em todas as funções e atributos.
- SRP e PEP 8.
- Docstrings no estilo Google.
- `dataclasses` para `Tarefa`, `IndicadorPrioridade` e `ResultadoAnalise`.
- Exceções específicas do módulo (`CampoObrigatorioAusenteError`, `ValorInvalidoError`, `DataInvalidaError`), todas herdadas de `TaskAnalyzerError`.
- Logging padrão com `logging`. Não usar `print`.
- Nomes descritivos em português, alinhados ao contrato da especificação.
- Datas sempre em UTC.

## Proibições explícitas

- Não usar bibliotecas externas além da stdlib, `pytest` e `pytest-cov`.
- Não alterar os cenários de aceite (`test_cenario_1` a `test_cenario_6`).
- Não mudar a estrutura de pastas do repositório.
- Não persistir dados: sem arquivos, banco ou rede.
- Não alterar a assinatura de funções públicas sem autorização humana.
- Não gerar código sem testes correspondentes.
- Não duplicar código.
- Não assumir comportamento que não esteja especificado. Quando houver dúvida, parar e registrar a pergunta.

## Comportamentos especificados que o código deve respeitar

- Só tarefas `concluida` entram no tempo médio de conclusão.
- Tarefas `cancelada` ficam fora de todas as métricas.
- `data_conclusao`, quando informada, deve ser posterior a `data_criacao`. Caso contrário, `DataInvalidaError`.
- Lista vazia resulta em métricas zeradas, sem exceção.
- Campo obrigatório ausente gera `CampoObrigatorioAusenteError`. Valor fora do domínio gera `ValorInvalidoError`.
- A função pública não tem efeitos colaterais.

## Homologação humana (Critical-in-the-Loop)

Nenhum código é incorporado sem passar pela sequência abaixo:

1. Rodar a suíte automatizada. Deve haver 100% de testes passando.
2. Revisar a conformidade com o contrato da especificação e com este documento.
3. Revisar a qualidade do código.
4. Fazer testes manuais de borda.
5. Só então fazer o commit e abrir o Pull Request.

## Rastreabilidade

- Todo código gerado por IA deve registrar o prompt ou a referência ao prompt usado, no PR ou no relatório de governança.
- Alucinações identificadas (lógica fora do contrato ou biblioteca não autorizada) devem ser registradas e corrigidas antes da homologação.
