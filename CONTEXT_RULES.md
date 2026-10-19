# CONTEXT_RULES — Governança de IA

> **RASCUNHO.** Reconstruído a partir do enunciado. Substitua pelas regras
> definidas na Fase 1 antes de entregar.

## Regras para o assistente de IA

1. **Linguagem:** Python 3.11 ou superior.
2. **Tipagem:** type hints em 100% das funções e parâmetros.
3. **Erros:** usar exceções específicas (`TaskValidationError`). Nunca usar `except` genérico que silencie erros.
4. **Divisão por zero:** toda divisão deve ter guarda explícita.
5. **Escopo:** implementar apenas o que está em `specs/task_analyzer_spec.md`. Não criar funções, endpoints ou dependências fora do contrato.
6. **Dependências:** usar apenas as listadas em `requirements.txt`.
7. **Testes:** cada cenário de aceite deve ter um teste correspondente em `tests/test_harness.py`.
8. **Nomes:** nomes de funções, campos e chaves de saída seguem exatamente a especificação.

## Validação humana

Antes de aceitar código gerado pela IA, o desenvolvedor deve:

- Ler o código e confirmar que cada função corresponde à especificação.
- Executar `pytest` e confirmar 100% de aprovação.
- Verificar se nenhuma regra acima foi violada.
- Registrar no Pull Request qualquer correção feita manualmente sobre o código gerado.
