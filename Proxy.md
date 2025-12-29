Otimização de Proxy: quando medir vira meta e o sistema começa a “jogar contra você”
Introdução

Quase toda organização precisa de métricas para coordenar pessoas, priorizar trabalho e avaliar progresso. O problema começa quando aquilo que importa de verdade — qualidade, valor entregue ao cliente, sustentabilidade do negócio — é difícil de observar diretamente. Para lidar com isso, criamos proxies: medidas substitutas que aproximam o objetivo real.

O ponto crítico é que sistemas humanos reagem às métricas. Quando uma proxy passa a determinar bônus, punições, status ou sobrevivência, ela deixa de ser apenas um termômetro e vira um volante: altera decisões e comportamento. Por isso, em ambientes com agentes adaptativos, vale a máxima: quando uma medida vira meta, ela deixa de medir bem.

Este artigo explica por que isso acontece, quais são os efeitos mais comuns (e previsíveis), e como desenhar métricas e incentivos de modo correto e poderoso — não no sentido de “perfeito”, mas no sentido de alto desempenho com estabilidade, evitando que a empresa “ganhe hoje e quebre amanhã”.

1) O que é proxy e o que significa otimizá-la

Proxy é uma medida usada como substituta do objetivo real. Exemplos:

Objetivo real: “Clientes satisfeitos e fidelizados”
Proxy: “Número de vendas”

Objetivo real: “Software confiável”
Proxy: “Bugs fechados por semana”

Objetivo real: “Equipe eficiente”
Proxy: “Horas trabalhadas” ou “features entregues”

Otimizar a proxy é orientar decisões para maximizar o número — e isso pode ser útil. O problema surge quando a organização passa a recompensar o número mais do que o resultado real. A proxy vira um alvo. E, como pessoas são adaptativas, elas encontram caminhos para bater o alvo mesmo que isso prejudique o objetivo real.

2) Por que métricas “quebram” coisas: efeitos típicos

Abaixo estão efeitos recorrentes quando proxies viram metas rígidas.

2.1 “Gaming”: bater a métrica sem entregar valor

Quando o indicador vira uma “regra do jogo”, surge a criatividade para vencer o jogo — não necessariamente para melhorar o sistema.

Exemplo (vendas de sapatos):

Métrica: “Vender mais”

Efeito: vendedores empurram venda para qualquer pessoa (pai, mãe, quem não precisa), gerando troca, estorno, reclamação, perda de confiança.

Trocar para “venda líquida (venda – troca – estorno)” melhora um pouco, mas pode gerar outro gaming:

Mentiras mais sofisticadas

Promessas vagas

Manipulação de canal (ex.: empurrar para marketplace, triangulações, “jeitos” de registrar)
Tudo para preservar o número.

2.2 Otimização local que prejudica o todo

A empresa é um sistema acoplado. Melhorar um ponto pode piorar o restante.

Exemplo (software):

Meta: “fechar mais bugs”

Efeito: correções rápidas geram regressões, dívida técnica, fragilizam arquitetura. O número sobe, mas o produto fica mais instável.

2.3 Substituição do objetivo real por um simulacro

Com o tempo, as pessoas passam a “pensar na métrica”, não no propósito. O valor real vira secundário porque não é recompensado.

2.4 Pressão e risco ampliam o comportamento adversarial

Quanto maior a dependência de remuneração variável e punição por número, maior a chance de:

esconder problemas

“empurrar para o próximo período”

transferir risco ao cliente

queimar reputação para ganhar curto prazo

3) Um ponto-chave: não existe métrica perfeita em sistemas humanos

Em sistemas com pessoas (agentes adaptativos), não há função objetivo única e estável que capture toda a realidade sem gerar distorção quando vira alvo. O que existe é engenharia de incentivos e métricas para reduzir dano, acelerar correção e manter desempenho.

A pergunta madura não é “como evitar efeitos colaterais?”, mas:

quais efeitos colaterais aceitamos, por quanto tempo,

quais são inaceitáveis (guardrails),

e como detectamos cedo quando o sistema começa a degradar.

4) Um complemento necessário: além de métricas, identidade, autoria e reputação

Discussões sobre proxies costumam focar apenas em indicadores e fórmulas. Isso é insuficiente. Em muitos contextos, o regulador mais forte do comportamento humano não é a métrica, mas um conjunto de forças sociais e psicológicas: identidade profissional, autoria, reputação acumulativa e “memória longa” do trabalho.

Quando o output é durável e observável, e quando decisões têm autoria clara, errar não significa apenas “perder bônus”; significa manchar a própria história profissional. Nesses regimes, incentivos monetários marginais podem perder força, enquanto custo reputacional, vergonha, orgulho e legado passam a dominar. Após um certo ponto de suficiência material, dinheiro deixa de ser o driver principal e a preocupação com reputação e consistência interna ganha enorme peso.

Esse regime, porém, não é universal e não pode ser “decretado” apenas com cultura. Ele depende de propriedades estruturais do trabalho:

Visibilidade do output (o cliente ou o time consegue ver qualidade/impacto)

Rastreabilidade da autoria (dá para saber quem decidiu o quê)

Memória longa (erros e acertos persistem e são lembrados)

Reputação acumulativa (o histórico importa de verdade)

Horizonte temporal longo (não se zera tudo a cada trimestre)

Onde essas condições não existem — trabalho fragmentado, impacto difuso, anonimato, alta rotatividade, ciclos curtos — identidade e reputação não conseguem “segurar” o comportamento sozinhas. Nesses casos, métricas e estruturas formais tornam-se ainda mais necessárias (e mais arriscadas).

O ponto central é: o erro não é usar métricas. O erro é exigir que métricas façam o papel de identidade e reputação quando estas não podem operar — e ignorar identidade e reputação quando elas poderiam reduzir drasticamente a dependência de controle formal. Organizações resilientes reconhecem a diferença: usam métricas para coordenar e aprender, mas constroem, sempre que possível, condições de suficiência, autoria e reputação que tornam o sistema menos vulnerável à otimização adversarial.

5) Identidade com estrutura mínima: o modelo mais estável quando métricas podem ser rebaixadas

Quando um time opera em um regime de autoria, reputação e memória longa, a tentação é “jogar métricas fora” e confiar apenas em boa vontade. Isso quase sempre falha. O modelo mais estável não é substituir métricas por identidade, mas proteger a identidade com estrutura mínima.

Na prática, isso preserva:

autonomia

espaço para curiosidade

ausência de micro-métricas

Mas adiciona três ancoragens leves que tornam o sistema sustentável.

5.1 Ancoragem 1 — Autoria explícita e visível

Mesmo sem KPI, precisa ficar claro:

quem mantém o quê

quem decide o quê

quem responde quando quebra (no sentido de assumir e resolver, não de punir)

Exemplo (software): cada serviço ou módulo tem um “dono” visível (responsável por decisões e evolução), e incidentes viram aprendizado com dono e plano de correção.
Exemplo (varejo): cada loja tem uma pessoa responsável por resolver causas recorrentes de devolução (tamanho, estoque, promessa de entrega), em vez de tratar tudo como “culpa do vendedor”.

Isso protege:

o sistema (responsabilidades não viram “terra de ninguém”)

o profissional (clareza evita culpa difusa)

a empresa (reduz risco operacional)

5.2 Ancoragem 2 — Expectativa qualitativa clara

Não é “faz o que quiser”. É algo como:

“Esperamos que você deixe o sistema melhor do que encontrou.”

Esse critério inclui, por exemplo:

reduzir complexidade desnecessária

documentar decisões relevantes

melhorar confiabilidade e observabilidade

eliminar fontes recorrentes de retrabalho

Exemplo (engenharia): “sair do trimestre com menos pontos cegos” (logs, alertas, testes) e menos risco oculto, mesmo que isso não apareça em uma contagem de features.
Exemplo (operações): “reduzir trabalho repetitivo” (automatizar conciliação, padronizar rotina de fechamento), mesmo sem KPI de ‘tarefas concluídas’.

Não há número, mas há padrão, linguagem comum e critério compartilhado.

5.3 Ancoragem 3 — Revisão humana periódica

Não é avaliação de meta. É conversa estruturada:

O que você melhorou?

O que ficou mais simples?

O que ficou mais seguro?

O que você evitaria fazer de novo?

Isso cria:

memória institucional

reconhecimento real (não só numérico)

justiça percebida (decisões ficam explicáveis)

Importante: esse modelo funciona melhor onde o trabalho é observável e a autoria é rastreável. Onde o trabalho é anônimo, altamente rotativo ou de impacto difuso, essas ancoragens não substituem guardrails e métricas — elas apenas complementam.

6) Confiança, julgamento humano e o limite definitivo das métricas

Existe um limite que todo sistema de métricas encontra: nenhum conjunto de números substitui julgamento humano. Métricas ajudam a iluminar a realidade, mas não tomam decisões por si. Promoções, aumentos, reconhecimento, confiança e até alocação de responsabilidade são, inevitavelmente, atos humanos.

É comum tentar usar números como “proteção” contra decisões difíceis. Mas, quando surge desconfiança — por exemplo, diante de favoritismo, relações pessoais, conflitos de interesse ou jogos políticos — o problema raramente é “falta de métrica”. Métricas não resolvem captura de julgamento, assimetria de poder ou questões éticas. Tentar “corrigir” esses casos com mais números costuma piorar a situação: transforma métricas em álibi, incentiva o gaming e corrói ainda mais a confiança.

Exemplo (promoções): se uma promoção parece injusta, adicionar um score numérico raramente resolve. As pessoas passam a otimizar o score (visibilidade, tarefas fáceis, trabalho “contável”) e o sentimento de injustiça permanece — agora com uma camada de “objetividade” artificial.
Exemplo (vendas): se um gerente favorece sua “turma”, o time entende que o jogo não é atender bem o cliente, é agradar o gerente. Colocar mais KPIs vira combustível para disputa de narrativa e manipulação de registro.

Empresas que funcionam bem aceitam essa limitação explicitamente. Elas:

usam métricas como evidência, não como árbitro final;

tornam julgamentos explícitos (critérios escritos, exemplos do que “bom” significa);

criam governança para pontos onde confiança individual não opera sozinha.

Na prática, isso costuma incluir:

separar quem avalia de quem decide em casos de conflito de interesse (comitês, segunda opinião, calibragem);

registrar decisões e racional (para aprender e reduzir arbitrariedade);

distribuir responsabilidade em vez de escondê-la atrás de indicadores (“o KPI mandou”).

Em última instância, liderança é decidir com informação incompleta. Métricas reduzem o escuro, mas não eliminam a necessidade de confiar em pessoas — nem a obrigação de proteger essa confiança com regras claras. Organizações duráveis não tentam substituir confiança por números; elas desenham sistemas onde métricas informam, pessoas decidem e a estrutura existe para quando a confiança precisa de apoio.

7) Como fazer corretamente — com alta performance e estabilidade

A seguir, um conjunto prático de princípios que, combinados, costuma gerar os melhores resultados em organizações reais.

7.1 Trate métricas como sensores, não como sentença

Métrica boa é sinal para investigação, não gatilho automático de punição/bonificação irrestrita.

“Aumentou troca?” → investigar causa, treinamento, produto, promessa, qualidade do atendimento

“Caiu bug fechado?” → checar gargalo, complexidade, prioridade, qualidade do backlog

Isso reduz gaming e aumenta aprendizagem do sistema.

7.2 Use poucos indicadores e defina “guardrails” (limites de segurança)

Para desempenho máximo, você quer foco. Para estabilidade, você quer freios.

Uma forma poderosa é combinar:

métrica de tração (empurra desempenho)

métrica de segurança (impede colapso)

métrica de saúde (detecta degradação)

Exemplo (vendas de sapatos):

Tração: vendas válidas

Segurança (gate): venda só conta se não virar troca/estorno dentro de X dias

Saúde: reclamações / NPS pós-compra / reincidência de devoluções por vendedor (para diagnóstico, não para caça às bruxas)

O detalhe importante: guardrail como “portão” (gate) é melhor que “penalidade matemática”.
Se a venda virou troca, não conta. Não entra em fórmula para “compensar com mais volume”.

7.3 Evite incentivos que dependam de decisões que você não quer delegar

Se o vendedor ganha por volume, ele decide “para quem vender” e “como prometer”.
Se isso é crítico, o incentivo precisa ser desenhado para não premiar decisões ruins.

Uma regra prática:

Incentive o que a pessoa controla sem prejudicar o cliente.

Transforme o que ameaça o cliente em restrição operacional (não em jogo numérico).

7.4 Limite o upside da variável (cap) e pague fixo suficiente

Comissão “infinita” e salário baixo favorecem comportamento extremo.
Um pacote mais robusto costuma ser:

fixo suficiente para reduzir desespero e trapaça

variável com teto e curva que achata (evita “qualquer coisa por mais 1%”)

parte coletiva (loja/time) para reduzir individualismo predatório

Isso normalmente não maximiza o pico de curto prazo, mas maximiza o resultado sustentável.

7.5 Separe direção (gestão) de avaliação (recompensa)

Uma métrica pode ser ótima para guiar o sistema, mas péssima para pagar pessoas.

Use números para operar (melhorar processo).

Use avaliação humana com evidências para promover e reconhecer (qualidade, ética, aprendizado, colaboração).

Quanto mais complexo e interdependente o trabalho, mais essa separação evita que o time “vire advogado do próprio número”.

7.6 Faça métricas temporárias e revisáveis

Métrica eterna vira jogo eterno.

Prática forte:

escolher foco por ciclos (ex.: 6–8 semanas)

revisar: “o que melhorou?” “o que quebrou?” “o que virou teatro?”

substituir sem medo

Isso impede overfitting organizacional (a empresa se adaptando à métrica, não ao mercado).

7.7 (Opcional, mas potente) Reduza a dependência de incentivos artificiais

Quando possível, fortaleça condições que tornam o sistema menos vulnerável a gaming:

aumentar visibilidade do trabalho (feedback de cliente, qualidade observável)

tornar autoria e decisões rastreáveis (sem caça às bruxas; com aprendizagem)

criar memória longa (retrospectivas reais, pós-mortem sem culpa, registro de decisões)

dar estabilidade e suficiência (reduz “sobrevivência” como driver)

reforçar reputação interna (histórico importa, mas com justiça e contexto)

Isso não substitui métricas, mas rebaixa o papel delas, deixando-as mais seguras.

8) Um desenho “poderoso” de incentivo para seu caso de vendas (modelo-base)

Um esquema geralmente robusto (ajuste ao seu contexto):

Fixo competitivo (reduz comportamento adversarial)

Variável por vendas válidas (com janela de confirmação: 7–30 dias, depende do ciclo de trocas)

Gate de qualidade: venda que vira troca/estorno não conta

Cap de variável + prêmio incremental pequeno para evitar extremos

Componente coletivo (loja/time) baseado em saúde do negócio (ex.: taxa de devolução da loja, satisfação do cliente, conformidade)

Auditoria leve e real (amostragem): impede estratégias “criativas” de canal/registro

Treinamento e script de promessa: reduz assimetria e padroniza ética

Consequências claras para fraude (poucas, firmes, consistentes)

Isso entrega performance porque:

foca em tração (vendas)

preserva futuro (validade + qualidade)

reduz incentivo a “vender errado”

limita exploração do sistema

Conclusão

Otimização de proxy não é um “defeito de caráter” do time. É uma consequência previsível de sistemas que recompensam números. Se você quer alta performance sem colapso, não basta escolher uma métrica melhor; você precisa desenhar um conjunto pequeno de sinais com guardrails, separar operação de recompensa quando necessário, limitar o upside da variável e criar mecanismos de correção rápida.

Ao mesmo tempo, há um complemento essencial: métricas não são o único regulador do comportamento. Onde autoria, reputação e memória longa operam, a empresa pode depender menos de incentivos artificiais e mais de identidade e responsabilidade — desde que essa identidade seja protegida por estrutura mínima e por governança que preserve confiança. Onde essas condições não existem, métricas e estrutura continuam necessárias — mas devem ser tratadas como instrumentos de coordenação e aprendizagem, não como substitutos do julgamento.

A empresa que não quebra com o tempo não é a que mede tudo. É a que mede pouco, reage cedo, aprende rápido — e impede que “bater meta” vire desculpa para destruir o valor real.

Se você quiser, eu adapto esse artigo para o seu caso real com um “template” pronto: (a) métricas do time, (b) fórmula de comissão, (c) gates e janelas, (d) regras anti-gaming, tudo em uma página.
