# Autocrítica brutal (só o motor simbólico cru importa)

## Onde errei feio
- **Virei DBA**: gastei tempo com page cache e WAL; isso não gera fatos novos nem prova melhor. Morreu.
- **DSL engomada**: querer gramática rígida mata iteração. Regras precisam ser texto simples que dá para editar e testar em minutos.
- **Forward-chaining corporativo**: agenda pesada, retração e dependências me transformaram em motor BPM. O alvo é derivar rápido em memória, não orquestrar processos.
- **Catalogação e schemas**: obrigar schema antes de experimentar bloqueia o fluxo. Só precisamos saber se um fato bate com o predicado e papéis básicos.
- **Provas burocráticas**: ficar registrando em SQL tira transparência. Prova boa é JSON legível que dá para reexecutar com `cat provas.log | motor`.

## O que fica de pé (e sem frescura)
- **Modelo único: predicado + roles nomeados** (SPO é caso especial). Forma única de representar n-ário sem virar grafão verboso.
- **Fatos em JSONL append-only**: arquivos que qualquer editor lê; índices em memória regenerados a partir do log.
- **Loop determinístico simples**: varre regras em ordem fixa; se emitir fato novo, recomeça da primeira. Para quando não sair fato novo em duas passadas.
- **Prova como evento JSON**: toda aplicação de regra gera `{rule, bindings, novos_fatos}`. Isso já é replay, auditoria e debug.
- **Hot reload de regras**: trocar arquivo de regras reinicia o loop com os mesmos fatos. Iteração vale mais que arquitetura perfeita.

## O que cortar sem dó
- **Banco pesado e versionamento ULID**: só atrapalham. O log JSONL já é histórico; se precisar limpar, reingere.
- **Retração automática**: custa caro e trava o loop. Para corrigir, reprocessa do zero a partir do log.
- **Métricas de BI**: basta `fatos_lidos`, `fatos_emitidos`, `regras_disparadas`, `tempo_ms` no stdout.

## Esqueleto para entregar algo útil em horas
1. **Formato de fato**
   ```json
   {
     "predicate": "transferiu",
     "roles": {"agente": "joao", "origem": "conta_A", "destino": "conta_B", "valor": 300, "tempo": 2024},
     "context": ["brasil", "financeiro"],
     "weight": 1.0
   }
   ```
   - Qualquer SPO cabe como `{predicate: P, roles: {s: S, o: O}}`. Nada de cinco campos obrigatórios.
2. **Armazenamento**
   - `facts.log.jsonl` append-only; cada linha é um fato ou prova.
   - Índice em memória: `by_predicate[predicate] -> [fact_ids]` e `by_role[predicate][role][value] -> [fact_ids]` para match rápido.
3. **Regra mínima**
   ```json
   {
     "id": "rota",
     "when": [
       {"predicate": "liga", "roles": {"de": "?a", "para": "?b"}},
       {"predicate": "liga", "roles": {"de": "?b", "para": "?c"}}
     ],
     "then": [
       {"predicate": "liga", "roles": {"de": "?a", "para": "?c"}}
     ]
   }
   ```
   - Bindings por string `?x`. Sem schema extra, sem catálogo.
4. **Inferência**
   - Loop: para cada regra, tenta casar `when` usando índices por `predicate` e `role`. Ao emitir novo fato, grava no log e reinicia.
   - Detector de ciclo: se nenhuma regra emitir nada em duas passagens completas, para.
5. **Prova e replay**
   - Cada disparo escreve `{rule, bindings, emitted}` em `proofs.log.jsonl`. 
   - Replay = ler `facts.log.jsonl` + `proofs.log.jsonl` e reemitir na mesma ordem para validar determinismo.
6. **Observabilidade crua**
   - A cada N fatos: imprime contadores e tempo total. Nada de painéis.

## Próximos passos (trabalho sujo, 12h)
- Implementar loader de fatos JSONL com índices por `predicate` e `role`.
- Escrever executor de regras com bindings via placeholder `?x` e detecção de novas emissões.
- Emitir provas e fatos em dois arquivos JSONL e fornecer comando `replay`.
- Testar em 3 domínios (parentesco, rotas, inventário) e medir somente `fatos emitidos` e `tempo total`.
- Ajustar layout de fatos se algum domínio exigir papel novo; sem mudar o motor.
