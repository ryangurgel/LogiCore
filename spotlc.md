# SPO(TLC) vs. Modelo de Predicado + Roles Nomeados

## Por que trocar o discurso
- SPO puro era bom para começar, mas o mundo não cabe em 3 campos fixos + TLC opcional.
- A forma mais expressiva e pragmática que continua simples é **Predicado + Roles Nomeados**.
- SPO vira um caso especial com `{predicate: P, roles: {s: S, o: O}}`. Não perde nada, só ganha poder.

## O modelo campeão (n-ário, simples de escrever)
```json
{
  "type": "fact",
  "predicate": "transferiu",
  "roles": {
    "agente": "joao",
    "origem": "conta_A",
    "destino": "conta_B",
    "valor": 300,
    "tempo": 2024
  },
  "context": ["brasil", "financeiro"],
  "weight": 1.0
}
```
- Sintaxe direta, igual a escrever SPO.
- Permite predicados n-ários sem gambiarra de múltiplos fatos.
- Contexto e peso opcionais para sinal/afinidade; não são burocracia.

## Como SPO cai dentro dele
```json
{
  "predicate": "ama",
  "roles": {"s": "alice", "o": "bob"}
}
```
- Zero perda de compatibilidade. Quem só quer triples continua produzindo o mesmo formato.

## Vantagens práticas
- **Menos predicados gordos**: em vez de `transferiu_de_para_valor_tempo`, basta um predicado e papéis nomeados.
- **Match eficiente**: índices por `predicate` e `role` cobrem consultas comuns (`?s transferiu ?o`, `transferiu destino=conta_B`).
- **Expressividade sob controle**: dá para modelar tempo, local, agente, instrumento, evidência, etc., sem multiplicar predicados.
- **Debug fácil**: JSON legível; roles contam a história sem precisar de documentação paralela.

## Quando SPO(TLC) ainda é suficiente
- Domínios de relacionamentos binários puros com pouco contexto.
- Protótipos rápidos onde cada fato só precisa de `s` e `o`.

## Quando migrar para Predicado + Roles Nomeados
- Relações com 3+ argumentos frequentes (financeiro, supply chain, logs de eventos).
- Quando predicados compostos proliferam para carregar papéis que não cabem em `S,O`.
- Quando provas ficam obscuras porque falta nome de papel explícito.

## Próximos passos (objetivo: Charizard do SPO)
- Refatorar ingestão para aceitar fatos n-ários com roles dinâmicos e validar apenas tipos primitivos.
- Atualizar exemplos e datasets sintéticos usando roles nomeados para testar joins reais.
- Ajustar motor de regras para bindar por nome de role, não por posição.
- Manter compatibilidade total: fatos SPO continuam válidos e são apenas um subconjunto.
