# Decisões de arquitetura e trade-offs

Este documento descreve a arquitetura escolhida para o motor de raciocínio estruturado, os motivos das decisões, os trade-offs
considerados e possíveis melhorias. O foco permanece em dados 100% estruturados (JSON) e em trilhas de explicação completas,
com modelos baseados em proposições, entidades e grafos orientados a SPO(TLC).

## Visão geral da arquitetura
- **Modelo SPO(TLC)**: cada fato é uma tupla `Sujeito-Predicado-Objeto-(Tempo)-(Local)-(Contexto)` armazenada como JSON. Isso
  preserva estrutura simples para buscas e facilita extensões temporais/espaciais sem abandonar o formato plano.
- **Camada de índices**: dicionários em memória por `S`, `P`, `(S,P)`, tags e intervalos de tempo. Trade-off: simplicidade e
  velocidade de leitura vs. consumo de RAM; mitigado com carregamento lazy e compressão leve.
- **Motor de inferência**: beam search configurável com unificação estruturada, operadores plugáveis e pontuação multifatorial
  (peso do fato, prioridade da regra, frescor temporal, fonte e localização). Escolhido pela previsibilidade e por ser
  explicável passo a passo. Trade-off: pode perder soluções ótimas se o beam for estreito; amenizado com ajustes dinâmicos e
  retraçoamento parcial.
- **Persistência JSON/JSONL**: banco em `banco.jsonl` para streams e snapshots versionados. Trade-off: leitura linear mais lenta
  que um banco relacional, mas ganha em transparência, auditabilidade e portabilidade.
- **API/CLI**: exposição via CLI e endpoints JSON-RPC/REST para consultas e explicações. Permite rastreabilidade e testes
  automatizados; evita dependência em UI, mas deixa espaço para dashboards opcionais.

## Por que SPO(TLC) + grafo
- **Uniformidade**: qualquer domínio (leis, nutrição, planejamento) cabe no mesmo molde de proposições com variantes temporais e
  geográficas.
- **Compatibilidade com grafos**: o modelo cria naturalmente um grafo dirigido (S -> P -> O), permitindo algoritmos de busca,
  verificação de caminhos e detecção de contradições por antônimos.
- **Explicabilidade**: cada aresta/fato carrega metadados (`src`, `weight`, `tags`, `trace`), possibilitando reconstruir provas
  e contrastes ("por que não").
- **Simplicidade operacional**: JSON+índices é mais fácil de versionar e auditar do que pipelines NLP ou bases não-estruturadas.

## Decisões tomadas
- **Schema validado**: facts e rules seguem schemas explícitos; ingestão recusa entradas inválidas para evitar deriva semântica.
- **Beam search determinístico**: parâmetros (`beam_width`, `max_expansions`) são salvos junto da execução para reprodutibilidade.
- **Operadores plugáveis**: cada operador anuncia custo/heurística; a pilha permite desligar operadores caros sem alterar o
  núcleo do motor.
- **Traces ricos**: cada passo leva bindings, regra/fato aplicado, delta de score e tempo de execução, permitindo depuração.
- **Snapshots versionados**: toda alteração no banco pode ser congelada em `data/snapshots/YYYYMMDD/` com manifest de hashes.
- **Contradição explícita**: tabela de predicados antônimos e regras de exclusão temporal reduzem respostas incoerentes.

## Trade-offs e alternativas
- **Beam search vs. busca exaustiva**: beam é mais rápido e controlável, mas pode podar soluções válidas. Alternativa: usar A*
  com heurísticas admissíveis para metas críticas ou aumentar o beam adaptativamente em caso de baixa cobertura.
- **JSONL vs. banco relacional**: JSONL é simples e versionável; porém, queries complexas podem ser lentas. Alternativa: manter
  um índice secundário em SQLite/DuckDB apenas para leitura analítica, preservando JSON como verdade-fonte.
- **Índices em memória vs. cache on-demand**: manter tudo em RAM acelera, mas consome memória. Alternativa: cache LRU por
  predicado ou sharding por domínio para reduzir pegada.
- **Modelo SPO(TLC) vs. ontologias mais ricas**: SPO(TLC) é simples e direto; ontologias OWL trazem inferências automáticas, mas
  aumentam complexidade e custo computacional. Mantemos SPO(TLC) e adicionamos camadas opcionais de tipos e restrições via
  validadores.
- **Explicação detalhada vs. tamanho do log**: logs completos facilitam auditoria, mas geram volume. Solução: níveis de log
  configuráveis e compactação de traces arquivados.

## Sugestões de melhorias
- **Refinar o grafo temporal**: adicionar estruturas como interval trees ou segment trees para queries com janelas e vigência,
  mantendo compatibilidade com o modelo SPO(TLC).
- **Heurísticas adaptativas**: ajustar o beam dinamicamente com base em densidade de soluções ou custo médio por operador.
- **Memória persistente eficiente**: explorar Zstandard com dicionários treinados no vocabulário do domínio para reduzir IO.
- **Validação incremental**: hashes de bloco no JSONL para validar integridade sem reprocessar tudo.
- **Cache de provas**: memoização por `(goal, versão do banco, parâmetros)` para evitar recomputar caminhos frequentes.
- **Ferramentas de curadoria**: diff visual de fatos e regras, com sugestão de merge/remover fatos fracos.
- **SMT opcional**: exportar subproblemas numéricos/temporais para Z3 quando a checagem booleana não bastar.
- **Tipagem leve de entidades**: campos `type` e constraints simples para distinguir pessoa/lei/produto/nutriente sem exigir
  ontologias pesadas.
- **Testes de regressão**: suites para leis, nutrição e planejamento com metas, casos positivos/negativos e faixas temporais.

## Recomendações práticas
- Mantenha schemas e exemplos próximos do código de validação para reduzir drift.
- Documente cada operador com custo esperado e casos de uso; desative o que não for crítico em produção.
- Guarde seeds, parâmetros e hashes de banco em cada execução para garantir reprodutibilidade.
- Implemente CLI de inspeção de traces para permitir auditorias rápidas.
- Defina limites de profundidade e tempo por domínio (leis vs. nutrição) para equilibrar custo e completude.

## Próximos passos sugeridos
1. Publicar schemas em `schema/` e ativar validação automática na ingestão.
2. Implementar índice temporal eficiente e hooks de cache de provas.
3. Criar benchmarks específicos por domínio e dashboards mínimos de métricas (tempo, expansões, contradições).
4. Adicionar modo A* opcional para metas críticas com heurísticas por domínio.
5. Integrar exportação para SMT em casos numéricos/temporais e medir custo/benefício.
