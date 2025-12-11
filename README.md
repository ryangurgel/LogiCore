# LogiCore

LogiCore é um motor simbólico "brutal" em Python que trabalha sobre um grafo de fatos (S, P, O, T, L, C) carregados de um `banco.json`. Ele executa dedução, abdução e um planejamento causal simples para responder perguntas e montar explicações consistentes, usando beam search e um conjunto de operadores interpretados diretamente em memória. O objetivo é explorar rapidamente ideias de raciocínio simbólico sem depender de infraestruturas pesadas ou de modelos estatísticos.

## Visão geral do motor
- **Representação única**: tudo é conceito; fatos ligam sujeito (`S`), predicado (`P`), objeto (`O`), opcionalmente tempo (`T`), localização (`L`), contexto (`C`) e peso (`w`).
- **Consultas com curingas e variáveis**: `None` atua como coringa e strings iniciando com `?` viram variáveis unificáveis entre metas.
- **Operadores embutidos**: transitividade de `é`, causalidade via `faz`/`pode_fazer`/`causa`, abdução (`explica` + `sintoma_de`), analogia (`similar_a`), leis com vigência/revogação/conflitos/exceções, e regras declarativas de cabeça/corpo.
- **Tratamento de tempo e numérico**: metas podem incluir janelas temporais e comparações numéricas (`">120"`, `"<=3.5"`, etc.).
- **Busca explicável**: cada solução traz bindings de variáveis, fatos usados e trace textual de como o motor chegou lá.
- **Controle de custo**: memorização de estados, penalidade por complexidade e limitação por operador ajudam a manter a busca sob controle.

## Estrutura do repositório
- `main.py`: implementação completa do motor (KnowledgeBase + BrutalEngine), exemplos de consulta e CLI mínima.
- `banco.json`: **não incluído no repositório**. Crie o seu seguindo o formato descrito abaixo.

## Formato esperado do `banco.json`
Cada entrada é um objeto com os campos:

```json
{
  "S": "macaco",
  "P": "é",
  "O": "mamifero",
  "T": [2000, null],
  "L": "brasil",
  "C": "fonte_x",
  "w": 1.0
}
```

- Campos `T`, `L`, `C` e `w` são opcionais. `T` pode ser um escalar (ano) ou um intervalo `[inicio, fim]` onde `fim` pode ser `null`.
- Regras declarativas usam `{"rule": {"head": {...}, "body": [{...}, {...}]}}` seguindo o mesmo esquema de S/P/O/T/L/C.
- Valores numéricos podem ser comparados com strings condicionais nas metas (`">120"`).

## Como executar
1. Crie um `banco.json` ao lado de `main.py` com seus fatos e regras.
2. Execute:
   ```bash
   python main.py
   ```
3. O `main()` roda quatro consultas de exemplo (dedução, planejamento, uso de variável, e escolha de lei) e imprime as soluções com bindings, fatos usados e um trace da busca.
4. Ajuste ou crie novas metas diretamente no `main()` ou invoque `engine.explain(goal)` em outro script para integrar a engine em pipelines próprios.

## O que já funciona bem
- Dedução transitiva com `é` e herança de propriedades.
- Planejamento causal simples com encadeamento de ações (`faz`/`pode_fazer`/`causa`).
- Abdução baseada em sintomas, retornando hipóteses plausíveis.
- Suporte a vigência de leis, conflitos e exceções para seleção de normas aplicáveis.
- Comparações numéricas e restrições temporais na mesma estrutura de meta.
- Analogia simbólica suave usando vizinhança de `similar_a` como pista adicional.

## Onde errei e pontos a melhorar
- **Monolítico**: toda a lógica vive em um único arquivo; isso dificulta testes e extensibilidade.
- **Ausência de testes automatizados**: não há suite de unit/integração garantindo regressões quando novas regras são adicionadas.
- **Dependência de dados externos**: sem um `banco.json` de exemplo o onboarding é mais lento; deveria haver fixtures mínimas.
- **Configuração dura no código**: limites de beam e pesos de operadores estão hardcoded; poderia haver um arquivo de configuração.
- **Tracing verboso mas pouco estruturado**: a saída de debug é textual; formatos estruturados (JSON) facilitariam inspeção programática.

## Aprendizados durante o desenvolvimento
- Um modelo S/P/O/T/L/C simples já cobre casos de dedução, causalidade e analogia quando os operadores são bem escolhidos.
- Beam search com poda por operador evita explosão combinatória sem perder completude nas consultas pequenas.
- Normalizar tempo e numérico cedo simplifica muito a unificação e reduz casos especiais espalhados.
- Manter uma representação de bindings por estado torna o trace das soluções mais claro do que espalhar substituições pelo código.

## Próximos passos recomendados
- Quebrar o `main.py` em módulos (`knowledge_base.py`, `engine.py`, `operators.py`, `cli.py`) para facilitar manutenção.
- Adicionar um `banco.json` de demonstração e fixtures de teste cobrindo cada operador.
- Expor uma interface de linha de comando mais amigável (argumentos para metas em JSON/arquivo) e um modo servidor (FastAPI/Flask).
- Implementar persistência/armazenamento incremental de fatos para não depender apenas de carga inicial completa.
- Suporte opcional a pesos probabilísticos e métricas de confiança na saída das explicações.

## Roteiro rápido para criar novos experimentos
1. Modele o domínio em fatos S/P/O (ex.: "alimento", "nutre", "humano").
2. Acrescente relações de causalidade (`faz`/`pode_fazer`/`causa`) e analogia (`similar_a`) para enriquecer a busca.
3. Se precisar de leis ou regras, use campos `T`/`L` para vigência e `rule` para cabeças/corpos declarativos.
4. Monte metas pequenas e interprete a saída: revise pesos `w` e campos `C` quando a complexidade penalizar soluções desejadas.
5. Itere adicionando exceções ou negações (`nao_é`, `nao_aplica_a`) para calibrar contradições detectadas pelo motor.

## Limitações conhecidas
- Não há persistência; tudo vive em memória durante a execução.
- Comparações numéricas e temporais são intencionais, mas não cobrem todas as unidades ou granularidades possíveis.
- Negações e default reasoning são simplificados; casos reais podem exigir lógica não-monotônica mais robusta.
- Ausência de benchmark de desempenho; em grafos grandes será preciso instrumentar métricas de tempo e de memória.

