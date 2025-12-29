O engenheiro que você acha que está contratando

E por que a engenharia de software vive quebrando quando o sistema premia “não-engenheiros”

A engenharia de software tem um problema antigo que a IA só deixou mais visível: hoje dá para produzir aparência de resultado em escala. Quando “entregar” vira a métrica suprema, surge um tipo de profissional que sabe vencer o jogo das métricas — e não necessariamente construir sistemas que sobrevivem ao tempo.

Isso não é um texto sobre “gente boa vs gente ruim”. É um texto sobre sistemas de incentivo. O mesmo mecanismo que transforma vendas em teatro transforma software em castelo de cartas: otimização de proxy. Quando medir vira meta, o sistema começa a jogar contra você.

A tese é simples:

Engenharia é a disciplina de sustentar consequências.
Software quebra quando a organização recompensa quem só sustenta números.

1) O que é engenharia (o que deveria ser)

Engenharia não é uma coleção de técnicas, frameworks ou certificados. É uma postura diante do mundo:

modelar um problema real com restrições reais

assumir trade-offs explicitamente

validar com método (testes, evidências, limites)

operar e manter o que foi construído

responder pelas consequências (mesmo quando ninguém está olhando)

O engenheiro não é “quem escreve”. É “quem garante”. Não no sentido de perfeição — no sentido de processo: ele prefere errar cedo e barato do que errar tarde e caro.

Em engenharia civil, elétrica e mecânica isso sempre foi óbvio porque o mundo físico cobra. Em software, por décadas, deu para fingir: sempre existiu a tentação de tratar o sistema como um texto — algo que “parece certo”, compila, roda, dá demo.

Só que software não é texto: software é sistema em operação.

2) Como a engenharia de software se desviou (e por que isso foi “racional”)

A indústria de software cresceu rápido demais. Para escalar, ela precisou simplificar:

simplificar avaliação (“quantas features?”, “quantos tickets?”, “quantos PRs?”)

simplificar ensino (“faça CRUD”, “siga tutorial”, “resolva lista”)

simplificar contratação (tarefas padronizadas, entrevistas com sinais fáceis)

Isso funcionou por um tempo porque “produção de código” era cara. Mas ao transformar engenharia em produção, criamos uma confusão: passamos a chamar de “engenheiro” alguém excelente em entregar sem sustentar.

E aí nasce o padrão que destrói organizações:

o profissional que sabe parecer competente sob métricas fracas
vence o profissional que constrói competência real com erro, verificação e manutenção.

Quem entende de verdade experimenta, testa, erra, refatora. Quem joga o jogo evita errar publicamente e “fecha” o trabalho com o que está visível.

A IA amplifica isso, porque torna “entregar algo plausível” muito mais fácil.

3) O problema real: otimização de proxy na engenharia

A sua organização não consegue medir “qualidade real” diretamente. Então ela cria proxies:

“bugs fechados por semana” como proxy de confiabilidade

“features entregues” como proxy de valor

“PRs/commits” como proxy de produtividade

“tempo de entrega” como proxy de eficiência

“uptime” como proxy de robustez

Até aqui, normal. O problema surge quando essas proxies viram metas que determinam status, promoção, bônus ou sobrevivência. Aí acontece o inevitável: quando uma medida vira meta, ela deixa de medir bem.

3.1 Gaming: bater a métrica sem sustentar o objetivo

fecha bug fácil, ignora bug estrutural

entrega feature sem observabilidade, sem testes, sem rollback

“cumpre” prazo empurrando risco para produção

divide ticket para aumentar contagem

trabalha na superfície do problema para parecer movimento

3.2 Otimização local que destrói o todo

correção rápida gera regressão

aceleração de entrega gera dívida técnica

“entregar” hoje aumenta custo de mudança amanhã

“arquitetura mínima” vira arquitetura impossível

3.3 Substituição do objetivo real pelo simulacro

Com o tempo, as pessoas passam a pensar na métrica, não no sistema. E software pune isso com atraso: ele funciona… até não funcionar.

O resultado é previsível: você tem um time que “entrega” e um produto que envelhece mal. Quando a quebra chega, chega caro.

4) “Não-engenheiros” em engenharia: quem são?

Aqui é importante ser formal: “não-engenheiro” não significa “sem diploma” ou “pessoa ruim”. Significa alguém que atua com uma lógica diferente:

curto prazo: parecer bom agora

visibilidade: otimizar o que aparece, não o que sustenta

transferência de risco: empurrar custo para depois, para outro time, para o cliente

narrativa: convencer, não verificar

Esse perfil pode ser inteligente, articulado e produtivo — e ainda assim perigoso para sistemas críticos. Porque ele mede sucesso como “métrica atingida”, não como “sistema estável no tempo”.

Aqui entra um ponto que costuma ser mal entendido. Não é moralismo e não é polícia da vida alheia. É compatibilidade entre função e risco: quem sustenta sistemas tende a carregar um conjunto de hábitos mentais difíceis de falsificar por muito tempo.

O sinal não é “o que a pessoa faz no tempo livre”; é o que ela valoriza quando ninguém está olhando:

ela pensa em confiabilidade ou em aplauso?

em evidência ou em narrativa?

em manter o sistema daqui a um ano ou em fechar a sprint?

Você está entregando o coração operacional do negócio para alguém. Se esse alguém otimiza visibilidade e evita responsabilidade, o custo não aparece hoje. Aparece no dia em que você menos pode pagar.

5) “Mas engenharia não precisa de ameaça para funcionar”

Concordo. Não é sobre punição, medo, assinatura em papel, “arma na cabeça”. Esse argumento é infantil.

O que faz engenharia funcionar é:

cultura (orgulho técnico, clareza de responsabilidade)

processo (checagem, revisão, evidência)

guardrails (limites que impedem colapso)

feedback rápido (detectar degradação cedo)

Você não precisa colocar terror. Você precisa parar de recompensar teatro.

6) Por que isso às vezes gerou coisas incríveis (e como)

A história não é só tragédia. O mesmo mundo que produz “gente que entrega” também produziu software excelente. Por quê?

Porque algumas equipes alinharam o essencial:

métricas como sensores, não como sentença

qualidade como gate, não como “penalidade”

validação como parte do trabalho, não como burocracia

autonomia técnica com responsabilidade real (operar o que constrói)

autoria e memória longa (decisões registradas, aprendizado acumulado)

O que gera software ótimo não é “gênio”. É um sistema onde:

ninguém ganha por empurrar risco

incidentes viram aprendizado, não caça às bruxas

decisões ficam registradas (“por que fizemos assim?”)

custo futuro é visível hoje

Isso é engenharia.

7) Como distinguir um engenheiro de verdade (sem virar polícia)

O ponto não é vigiar a vida pessoal de ninguém. O ponto é: existem sinais de orientação profissional que são difíceis de falsificar no longo prazo.

Você não captura um engenheiro só pelos acertos. Você captura por como ele lida com erro e o que ele faz quando ninguém está cobrando.

7.1 Relação com erro

erra cedo e documenta

cria teste quando encontra bug

procura causa raiz, não culpado

transforma falha em guardrail

7.2 Relação com evidência

gosta de reproduzir, medir, isolar variável

escreve “como validar” junto com “como fazer”

não confunde “rodou na minha máquina” com verdade

7.3 Relação com o tempo

pensa em manutenção e reversão (rollback)

projeta observabilidade antes de precisar dela

pergunta “o que isso vira em 6 meses?”

7.4 Relação com responsabilidade

prefere dizer “não sei ainda” e investigar

assume trade-off explicitamente

evita prometer sem plano de verificação

Isso é “estilo de vida” no sentido correto: um conjunto de hábitos mentais. Não é sobre feed — é sobre orientação: curto prazo versus consequência.

8) O que está quebrando a engenharia de software hoje (e sempre)

A síntese é:

métricas ruins premiaram o profissional errado.
a IA só tornou isso mais fácil e mais rápido.

Quando o sistema paga por “entrega aparente”, ele seleciona:

quem minimiza risco visível

quem maximiza narrativa

quem terceiriza custo futuro

E depois a organização se surpreende quando precisa contratar alguém para apagar incêndio. Isso não é romantizar “amor ao ofício”. É reconhecer um fato: corrigir sistemas quebrados exige tolerância ao desconforto, paciência para causa raiz e compromisso com evidência — coisas que não aparecem em métricas rasas.

9) Como consertar sem utopia: métricas e guardrails que não incentivam teatro
9.1 Métricas como sensores, não como sentença

Número serve para investigar, não para pagar automaticamente.

9.2 Guardrails como “gates”

Exemplos:

feature só “conta” se tiver testes mínimos + observabilidade + plano de rollback

mudança só “conta” se não gerar regressão dentro de X dias

performance só “conta” se não aumentar custo de infra acima de limite

entrega só “conta” se não elevar taxa de incidentes

Gate é melhor que “penalidade matemática” porque reduz gaming: se não passou, não passou.

9.3 Separar direção (operar) de recompensa (avaliar)

Você usa métricas para guiar. Mas promoção e reconhecimento precisam de avaliação humana com evidência: qualidade, aprendizado, segurança, colaboração, responsabilidade.

9.4 Feedback rápido e pós-mortem sem espetáculo

Incidente vira instrumento de engenharia, não tribunal.

Conclusão: a IA está forçando o retorno do engenheiro real

A IA está barateando produção. Isso revela o que sempre foi verdade:

resposta bonita é fácil

“funcionar hoje” é fácil

o difícil é funcionar no tempo, sob pressão, com mudanças

Engenharia de software vai se reorganizar em torno do que nunca deveria ter perdido: verificação, consequência e responsabilidade.
