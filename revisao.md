# Revisão técnica madura — crítica e recomendações (versão oficial)

> Documento técnico pronto para publicar no GitHub.  
> Objetivo: explicar claramente **o que é problema**, **o que é escolha de design**, **onde o sistema já acerta**, **onde precisa melhorar**, e **ações priorizadas** para evolução.  
> Não cita pessoas — fala apenas sobre o motor e decisões técnicas.

---

## TL;DR (resumo executivo)

O motor é um protótipo sólido e raro: combina dedução, abdução, causalidade, analogia e regras num único motor explicável.  
Muitos dos pontos apontados como “riscos” são reais (escala, NAF, heurísticas estáticas), mas a maior parte pode ser abordada com ajustes pragmáticos (hashing de estado, propagação de bindings, NAF como fallback, heurísticas adaptativas).  
Abaixo seguem diagnóstico, distinção entre bug vs escolha de design, e um roteiro priorizado de melhorias.

---

# 1. Onde o motor acerta (forças)

- **Arquitetura explicável**: cada fato/derivação tem `id`, `derived_by` e trace — excelente para auditoria.  
- **Operadores heterogêneos**: dedução (transitividade), causalidade/planejamento, abdução, regras e analogia convivem no mesmo ciclo de busca. Isso é raro e valioso.  
- **Modelo de dados pragmático**: `predicate + roles` (compatível com S/P/O) dá flexibilidade sem depender de NLP.  
- **Controlo pragmático da busca**: beam por operador + penalidade de complexidade é uma defesa prática contra explosões iniciais.  
- **Design modularizável (implícito)**: operadores são listados e parametrizáveis via dicionários — base para modularização futura.

---

# 2. Problemas reais (técnicos, necessitam correção)

1. **Memoização insuficiente / hashing fraco de estados**  
   - `seen_states` baseia-se em representações frágeis; estados estruturalmente equivalentes podem ser reexplorados.  
2. **Bindings não são totalmente re-propagados**  
   - fatos derivados podem manter bindings antigos; ao finalizar uma solução, bindings finais devem normalizar toda a prova.  
3. **NAF (negação como falha) aplicado cedo**  
   - `nao_provavel` pode produzir negações indevidas quando derivação indireta seria possível.  
4. **Beam e custo de operadores não adaptativos**  
   - operadores “barulhentos” (analogia, abdução) podem gerar branching desnecessário; falta um cost model para priorizar.  
5. **Analogias sem controle de distância**  
   - limiar fixo e ausência de decaimento por distância no grafo geram muitos candidatos irrelevantes.  
6. **Regras recursivas e loops possíveis**  
   - depth + seen_states mitigam mas não eliminam riscos de looping; falta assinatura de estado mais rica e limites por cadeia.  
7. **Monolito dificulta testes e ablações**  
   - `BrutalEngine` concentra matching, search, scoring e trace — torna difícil testes unitários e substituição incremental.

---

# 3. Escolhas de design (intenções válidas — não bugs)

- **NAF minimalista** — escolha pragmática para prototipagem; funciona como default fraco quando ausência é aceitável.  
- **Penalidade de complexidade e limites por operador** — forma prática de "atenção simbólica" com custo de implementação baixo.  
- **Formato S/P/O → roles nomeados** — decisão de engenharia para clareza e compatibilidade (bom trade-off).  
- **Monolito inicial** — facilita experimentar o conceito completo antes de modularizar.

Essas escolhas são legítimas no estágio inicial; só exigem reavaliação a medida que o projeto escala.

---

# 4. Recomendação priorizada — o que fazer agora (ordem: imediato → curto → médio → longo)

## Imediato (alto impacto, baixo esforço)
- **Normalizar bindings ao final de cada solução**  
  - Ao gerar uma solução, aplicar substituições finais a todos os fatos derivados (propagar bindings) para consistência.
- **Melhorar hashing de estado (`seen_states`)**  
  - Usar assinatura composta: `hash(frozenset(repr(unsat))), hash(tuple(sorted(bindings.items())))` e incluir aspectos do `expl`. Evita revisitas inúteis.
- **NAF como fallback**  
  - Executar `nao_provavel` somente se nenhum outro operador produzir expansão viável para o mesmo goal (ou após X iterações).
- **Top-K por score local em vez de corte arbitrário**  
  - Ao limitar expansões, escolher os K melhores por score do operador (não por ordem gerada).

## Curto prazo (1–2 semanas)
- **Threshold adaptativo para analogia**  
  - Sim_threshold aumenta com profundidade; penalizar analogia por distância de grafo (BFS 1–2 níveis).  
- **Propagar limite de ramificação por operador baseado em score e custo**  
  - Converter limites estáticos em políticas baseadas em `operator_strength * score_local / estimated_cost`.
- **Instrumentar métricas por operador**  
  - Medir expansões, tempo/operação, taxa de sucesso — imprescindível para tuning.

## Médio prazo (1–3 meses)
- **Modo A\*** opcional para metas críticas  
  - Heurística baseada em: número de metas pendentes, soma de pesos esperados, custo estimado por operador.  
- **ATMS-lite / justificações mínimas**  
  - Em cada `wrap_fact`, manter um set de justificativas (IDs) e possibilitar `nogood` básico para abort early em contradições indiretas.  
- **Modularizar operators / extrair interface**  
  - Extrair `operators/`, `search/`, `kb/`, `scoring/`, `trace/` para testes e swaps rápidos.

## Longo prazo (3–6+ meses)
- **Meta-operador de síntese (chunking)**  
  - Detectar sequências repetidas de operadores bem-sucedidas e encapsular em novo operador (aprender operadores).  
- **Aprendizado simbólico incremental**  
  - Promover soluções confiáveis a fatos permanentes (com peso ajustado) e induzir regras por compressão.  
- **Exportador SMT (Z3) para subproblemas críticos**  
  - Checagem formal para constraints temporais/númericas complexas.

---

# 5. Checklist técnico (tarefas rápidas para PRs)

- [ ] Normalizar bindings em cada solução final.  
- [ ] Substituir `seen_states` por hash mais robusto.  
- [ ] Fazer NAF ser fallback* (aplicado somente se nada mais).  
- [ ] Implementar top-K por score local em operadores.  
- [ ] Sim_threshold adaptativo e penalidade por distância para analogia.  
- [ ] Instrumentar métricas por operador (expansões/sucesso/tempo).  
- [ ] Extrair interface de operador `match/expand/score`.  
- [ ] Implementar modo A* opcional com heurística simples.  

\*Aplicar NAF como fallback reduz falsos-positivos de negação por ausência.

---

# 6. Sugestões de redação para README (frases técnicas a usar)

- “Limita crescimento combinatório em muitos cenários via beam, penalidade e limites — melhorias são necessárias para grafos muito densos.”  
- “Trace estruturado facilita futuro aprendizado simbólico; atualmente o trace não é reaproveitado automaticamente.”  
- “Índices S/P/O aceleram matching; reduzir branching requer heurísticas de busca complementares (A*/heurísticas adaptativas).”

---

# 7. Observações finais — posição técnica

- **O motor não é apenas um 'motorzinho'**: é uma prova de arquitetura simbólica híbrida com ingredientes raros (ops plugáveis, trace, scoring integrado).  
- **Os riscos apontados são reais**, mas **mitigáveis** com intervenções de engenharia e tuning.  
- **Prioridade prática**: corrigir hashing de estados e propagação de bindings agora, instrumentar métricas, depois ajustar NAF/analogia e evoluir para modularidade e A*.

---

## Próximos artefatos que posso fornecer (pronto para PR)
1. Patch: hashing de estado + normalização de bindings (PR-ready).  
2. Pseudo-código/implementação: modo A* com heurística recomendada.  
3. Test-cases mínimos e script de benchmarking (pequenos domínios: parentesco, causalidade, leis).

---


---
