+64
-0

# LogiCore

LogiCore é um motor simbólico autocontido pensado para explorar até o limite o que se consegue extrair de um banco de conhecimento estruturado em JSON, sem recorrer a NLP. A proposta é chegar o mais próximo possível de responder perguntas complexas (leis, nutrição, planejamento, diagnósticos) apenas com lógica demonstrável, rastreando cada passo das inferências.

## Ideia central

O sistema trabalha sobre um **grafo de fatos e regras** armazenado em `banco.json`. Cada fato segue o modelo "predicado + roles nomeados" (`predicate` + `roles`), permitindo flexibilidade para representar sujeito/objeto, tempo, localização e contexto como papéis explícitos. Há compatibilidade com o formato legado `S/P/O`, convertendo automaticamente para o esquema moderno. O objetivo é maximizar a estruturação dos dados para permitir explicações claras e verificáveis.【F:main.py†L5-L114】

## Como funciona

1. **Carregamento do conhecimento**: `KnowledgeBase` normaliza fatos vindos do JSON, mantém índices por sujeito, predicado e objeto e armazena regras declarativas head/body. Assim, o motor consegue localizar rapidamente evidências relevantes e aplicar regras customizadas.【F:main.py†L52-L120】
2. **Motor de explicação único**: `BrutalEngine.explain(goal)` recebe um objetivo (`S/P/O/T/L/C` ou roles equivalentes), considera `None` como curinga e variáveis prefixadas com `?` para unificação. Todo o processo é uma busca de explicações guiada por score, com memoização de estados e penalidade de complexidade para controlar o espaço de busca.【F:main.py†L200-L263】
3. **Operadores simbólicos**: O motor combina correspondência direta de fatos, transitividade de `é`, planejamento com `faz/pode_fazer/causa`, cadeias causais, abdução via `explica`, heurísticas de leis (`melhor_para_argumentar`), regras declarativas, negação por falha (`nao_provavel`) e analogia simbólica. Cada operador tem peso próprio e limites de expansão para equilibrar profundidade e cobertura.【F:main.py†L205-L261】
4. **Recursos auxiliares**: Suporte a variáveis lógicas, comparações numéricas simples (ex.: `">120"`), intervalos temporais, detecção de contradições entre predicados (`é` vs `nao_é`, `aplica_a` vs `nao_aplica_a`) e atribuição de IDs/trace para cada fato derivado, mantendo explicações auditáveis.【F:main.py†L200-L263】

## O que tem de bom

- **Rastreabilidade**: Cada fato derivado recebe `id`, `derived_by` e referências de suporte, facilitando reconstruir o caminho até a resposta.
- **Flexibilidade de domínio**: A modelagem por papéis nomeados permite representar leis, diagnósticos, planos e analogias no mesmo grafo simbólico.
- **Controle de busca**: Beam limitado por operador e penalização de complexidade evitam explosões combinatórias sem perder transparência.
- **Compatibilidade suave**: Dados antigos em formato `S/P/O` continuam válidos; basta fornecer `banco.json` ao lado do script.【F:main.py†L5-L114】

## Escolhas de arquitetura e pensamentos

- **Modelo "predicado + roles"** como núcleo: privilegia clareza semântica sobre free text e reduz ambiguidade.
- **Operadores modulados por peso**: diferenciar força de dedução, abdução, analogia e regras permite calibrar o motor para domínios específicos (ex.: leis mais fortes que analogias).
- **Atenção simbólica limitada**: limites de expansões por operador funcionam como uma atenção simbólica, focando nas pistas mais promissoras em vez de explorar cegamente o grafo.
- **Negação como falha simplificada**: o operador `nao_provavel` oferece defaults fracos sem exigir modelagem explícita de todas as negações, mantendo o sistema ágil.
- **Analogia simbólica leve**: o uso de `similar_a` fornece criatividade controlada, útil para cenários onde não há evidência direta mas existem vizinhos semânticos no grafo.

## O que estou fazendo agora

- Refinando os pesos e limites de operadores para equilibrar profundidade de explicação e tempo de resposta.
- Expandindo o esquema de `roles` para capturar nuances (tempo, localização, contexto) sem inflar a complexidade do motor.
- Testando como o motor lida com casos jurídicos e diagnósticos de saúde, aproveitando as heurísticas de leis e a abdução por sintomas.

## Ideias futuras e objetivos

- **Banco JSON enriquecido**: adicionar ontologias de domínio e taxonomias para fortalecer a transitividade de `é` e melhorar analogias.
- **Interface de trace**: gerar relatórios legíveis das explicações, com trilhas de fatos base e regras aplicadas.
- **Planejamento simbólico mais profundo**: explorar heurísticas de custo e recursos para o operador `faz/pode_fazer/causa` aproximar-se de planners clássicos.
- **Gestão de contradições**: ampliar a lista de predicados conflitantes e estratégias de resolução (prioridade por fonte, tempo ou peso).
- **Ferramentas de curadoria**: validar automaticamente `banco.json`, detectar regras órfãs e sugerir novos fatos com base em lacunas de explicação.
- **Benchmarking multi-domínio**: medir desempenho em cenários de leis, nutrição e troubleshooting técnico para guiar ajustes de pesos e limites.

## Como começar

1. Coloque um `banco.json` ao lado de `main.py` seguindo o esquema descrito.
2. Importe e instancie o motor:

```python
from main import KnowledgeBase, BrutalEngine

kb = KnowledgeBase()
kb.load_json("banco.json")
engine = BrutalEngine(kb)

resultado = engine.explain({"S": "alice", "P": "é", "O": "cientista"})
print(resultado)
```

3. Ajuste pesos, limites e dados no JSON para experimentar diferentes estratégias de inferência.

LogiCore é um convite para ir até o limite técnico do raciocínio simbólico com dados estruturados, mantendo cada resposta demonstrável passo a passo.
