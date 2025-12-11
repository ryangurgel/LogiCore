# Visão para um motor de raciocínio estruturado

Este documento reúne ideias para evoluir o motor lógico, priorizando representações 100% estruturadas (JSON), rastreabilidade e capacidade de explicar como cada resposta foi alcançada, sem dependência de NLP. O foco é empurrar o sistema ao limite técnico com arquiteturas simples, porém sólidas.

## Princípios de design
- **Dados primeiro**: todo fato, regra, justificativa e metadado em JSON validado por schema.
- **Explicabilidade total**: cada inferência deve carregar a cadeia de fatos/regra que a produziu, com tempos e pesos.
- **Determinismo controlado**: mesmos dados e parâmetros produzem a mesma resposta; aleatoriedade opcional, sempre registrada.
- **Observabilidade de raciocínio**: logs estruturados com eventos de expansão, pruning, scoring e contradições.
- **Modularidade**: camadas bem separadas para armazenamento, indexação, inferência, scoring e exposição (CLI/API/UI).
- **Escalabilidade pragmática**: índices em memória + persistência JSON (ou JSONL) com caminhos para sharding simples.

## Modelo de dados (JSON)
### Entidades básicas
- `fact`: `{ "S": str, "P": str, "O": any, "T": number|[number,number]|null, "L": str|null, "src": str, "weight": float, "tags": [str] }`
- `rule`: `{ "if": [condition], "then": fact|[fact], "priority": float, "name": str, "explain": str }`
- `condition` (variável-friendly): `{ "S": str|var, "P": str|var, "O": any|range|var, "T": time_expr, "L": str|var, "filters": [filter] }`
- `filter` (ex.: comparação numérica): `{ "type": "compare", "op": ">=", "value": number, "path": ["O"] }`

### Schema e validação
- Criar `schema/knowledge.schema.json` para facts e rules.
- Validar em ingestão e em CI (ex.: `python -m jsonschema`).
- Suportar migrações de versão com campo `schema_version` no banco.

### Índices sugeridos
- `by_s`: dict `S -> [fact]`
- `by_p`: dict `P -> [fact]`
- `by_sp`: dict `(S,P) -> [fact]`
- `by_tag`: dict `tag -> [fact]`
- `by_time`: estruturas de intervalo (ex.: segment tree) para consultas com janelas temporais.

## Motor de inferência (BrutalEngine++)
- **Unificação estruturada**: manter substituições em mapa e reutilizar `_apply_bindings_to_goal` como núcleo.
- **Beam search configurável**: preservar `beam_width` e `max_expansions_per_operator` no JSON de parâmetros da execução.
- **Operators plugáveis**: cada operador declara nome, custo estimado e métricas; fácil ativar/desativar por config.
- **Detecção de contradição**: tabela de predicados antônimos e regras de exclusão temporal.
- **Scoring multifatorial**:
  - Peso do fato (`weight`), prioridade da regra, frescor temporal (decay), confiabilidade da fonte (`src`), e ajuste geográfico (`L`).
  - Penalização de caminhos longos ou com muitas variáveis livres.
- **Explicação rica**: cada estado leva `trace` com passos `[ {goal, operator, fact|rule, bindings, score_delta, time_ms} ]`.
- **Paralelização**: expandir beam por batches, mantendo determinismo via ordenação estável.

## Banco e persistência
- Arquivo principal `banco.jsonl` (um JSON por linha) para streams grandes; `banco.json` para pequenos.
- Ingestão incremental: append-idempotente com hash do fato, evitando duplicatas.
- Snapshots versionados: `data/snapshots/YYYYMMDD/` com manifest de hashes.
- Compactação opcional com Zstandard mantendo leitura por streaming.

## API e interfaces
- **CLI**: comandos `load`, `validate`, `query`, `explain`, `trace` com flags para limites e beam.
- **REST/JSON-RPC**: endpoint `/explain` recebendo goal + parâmetros; resposta com soluções e trace.
- **UI opcional**: árvore de raciocínio colapsável, filtros por peso, tempo e operador.

## Estratégia para domínios desafiadores
- **Leis**: normalizar referências (`lei_id`, artigos, incisos) como objetos; regras de aplicabilidade por jurisdição e vigência.
- **Nutrição**: fatos sobre nutrientes, restrições, contexto clínico; regras de incompatibilidade (ex.: `alérgico a X -> evitar Y`).
- **Planejamento pessoal**: metas decomponíveis (`faz -> submeta`), com estimativas de duração e pré-condições.

## Plano de métricas
- **Cobertura de provas**: % de metas com ao menos uma explicação.
- **Profundidade média de solução**: mede complexidade.
- **Tempo médio por expansão** e **expansões por solução**.
- **Índice de contradição**: quantas hipóteses descartadas por conflito.
- **Drift de conhecimento**: dif entre snapshot anterior e atual (fatos novos/removidos).

## Pipeline de desenvolvimento
1. Definir schemas em `schema/` e configurar validação em `pre-commit`/CI.
2. Converter `banco.json` atual para `banco.jsonl` com `schema_version`.
3. Reforçar `BrutalEngine` com tracing estruturado e scoring configurável.
4. Implementar CLI de validação e consulta básica.
5. Adicionar API REST e benchmarks sintéticos (leis, nutrição, planejamento).
6. Medir, ajustar índices e beam, iterando em dados reais.

## Ideias de extensões
- **Aprendizado simbólico**: indução de regras a partir de fatos positivos/negativos (FOIL-like) para sugerir novas regras.
- **Verificação formal**: exportar subprovas para SMT (Z3) para checar consistência de constraints numéricas/temporais.
- **Cache de provas**: memoização de metas frequentes com chave (goal, versão do banco, params de beam).
- **Explicação contrastiva**: gerar "por que não" ao comparar trace de falha vs sucesso parcial.
- **Ferramentas de curadoria**: diff visual entre snapshots e sugerir merges ou remoções de fatos fracos.

## Checklist de qualidade
- Schema e validação automatizada.
- Logs estruturados por execução com seeds e parâmetros.
- Scripts de benchmark e dashboards mínimos.
- Conjunto de casos de teste cobrindo variáveis, ranges numéricos e intervalos de tempo.
- Documentação de dados: proveniência, licenças, atualizações.

## Objetivos de curto prazo (4–6 semanas)
- Garantir ingestão validada e sem duplicatas.
- Introduzir traces ricos no engine e na saída do CLI.
- Construir casos de teste para leis e nutrição cobrindo intervalos temporais.
- Disponibilizar snapshots versionados e script de diff.

## Objetivos de médio prazo (2–3 meses)
- API REST estável com throttling e autenticação básica.
- UI mínima para exploração de provas e tuning de parâmetros.
- Benchmark público reproduzível com métricas semanais.
- Integração opcional com solver SMT para checks numéricos/temporais.

## Objetivos de longo prazo (6–12 meses)
- Motor híbrido com cache de provas, paralelização e sharding por domínio.
- Ferramentas de indução de regras e curadoria assistida.
- Certificação de trilhas de decisão (logs assinados e verificáveis).
- Catálogo de domínios (leis, nutrição, planejamento) com pacotes de fatos e regras prontos.
