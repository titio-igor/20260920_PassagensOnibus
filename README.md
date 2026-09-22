# 20260920_PassagensOnibus
Desafio de Ciência de Dados envolvendo dataset simulado, análise exploratória, limpeza e insights. A linguagem escolhida para o desafio é python.

# 0. Considerações preliminares
## 0.1. Primeiro arquivo simulado
Foi pedido ao Claude que gerasse dataset bruto dados_passagens_raw.csv com as regras de negócio definidas, porém o resultado não foi muito satisfatório:
- Foi pedido 500 linhas com as premissas listadas em DesafioPassagensOnibus.docx
- Os assentos variavam de 1A a 45D, ou seja, eram considerados ônibus com até 180 lugares únicos, o que não é razoável
- Dos 500 registros gerados, haviam 480 viagens, o que também não é razoável, pois o ideal éramos identificar vários assentos em uma mesma viagem (várias compras dentro de um mesmo ônibus, por exemplo)

## 0.2. Segundo arquivo simulado
Foi feita uma nova tentativa no Claude, orientando a limitar o número de assentos no ônibus em 42 lugares (1A até 21B) e também incluindo propositalmente erros de tipagem, digitação, duplicatas e dados faltando (conforme briefing do desafio).
Também foi solicitado que fosse gerado um script duplicador do csv, exatamente com os mesmos dados para futuras ingestões e o resultado dessa vez foi positivo.
Arquivos gerado nessa etapa:
- gerar_passagens_seed.py (script duplicador)
- dados_passagens_raw.csv (dataset bruto)

### Observação:
Pensando na estrutura Medallion, podemos dizer que dados_passagens_raw.csv é a nossa **camada bronze** que consiste nos dados brutos carregados dentro do sistema para tratamento e análise.

# 1. Análise GPT
Submeti o dados_passagens_raw.csv para uma análise mais geral pelo chat GPT. Essa análise pode ser acompanhada no 00_analise_gpt.pdf. Basicamente o GPT identificou dados ausentes e duplicatas bem facilmente e, o que ele não percebeu, mas eu sim, foram dados incoerentes de valor (valores discrepantes, negativos ou nulos).
Via gráfico de pontos, identifiquei facilmente os valores discrepantes e, como o dataset simulado não previu variabilidade nos valores dentro de uma mesma viagem (mesmo destino e mesmo horário) podemos facilmente fazer o inferência que o valor discrepante, deve ser igual aos demais valores.
<img width="3221" height="1598" alt="image" src="https://github.com/user-attachments/assets/d3abbc22-17e0-47a5-a0ad-fc949bfd2bd7" />

# 2. Limpeza dos dados
Pensando no nosso arquivo simulado e na análise prévia do GPT, percebi de imediato que muitas linhas não tinham dados completos, mas, tinham algumas colunas preenchidas.
A heurística dividiu-se em algumas partes:
- Erros de digitação: Corrigir a grafia das cidades destino, com especial atenção ao uso correto de letras maiúsculas, espaços e parêntese.
- Destinos NaN: Foram preenchidos após a constatação de que destinos iguais em um mesmo dia ocorriam em horários iguais e, consequentemente, horários diferentes corresponderiam a destinos diferentes. Com base nessa lógica, foi possível preencher alguns destinos ausentes.
- Exceções/particularidades: foi observado um caso de erro de digitação na data, que foi facilmente identificado e outro caso em que quase todas as colunas estavam vazias, portanto, será dropado.
- A mesma estratégia foi feita para preenchimento dos preços unitários (já que o dataset simulado não previu variação no preço das passagens dentro de uma mesma viagem).
- No caso do preço, houve alguns valores discrepantes identificados pelo gráfico de pontos que foram corrigidos considerando o mesmo destino e a mesma data/hora da viagem.
- Em seguida, foi feito o tratamento dos horários, inclusive convertendo a variável para o formato datetime.
- Após esses tratamentos, decidi **manter** os dados em que não foi indicado a posição do assento, pois todas as demais informações estavam preenchidas e, para fins da análise (receita, datas/épocas/horários de maiores vendas, correlação de preço e número de passagens etc.) são relevantes. E corrigi 3 casos em que eram indicados 0 assentos, mas na verdade, havia 1 posição de assento em cada linha.
- Finalmente, se houvessem linhas exatamente iguais, as duplicadas foram dropadas e a nova coluna receita foi criada.

O resultado dessa limpeza foi dados_passagens_limpo.csv.

### Observação:
Pensando na estrutura Medallion, podemos dizer que dados_passagens_limpo.csv é a nossa **camada silver** que consiste nos dados limpos e tratados que servem de consumo para diferentes POs, BIs, Agentes de IA dentro de um ecossistema de dados de uma empresa real.

# 3. EDA e Insights
Observamos inicialmente, as Receitas por mês e por destino. A partir dessa análise inicial podemos responder as questões:
## Q01. Qual mês teve a maior receita? E a menor?
### R01. Maior receita ocorreu em Maio e, a menor, em Setembro.

## Q02. Qual destino gerou a maior receita?
### R02. Fortaleza (CE).

Em seguida, foram carregadas as bibliotecas gráficas e estatísticas afim de construir algumas representações e construir alguns indicadores mais elaborados. Pessoalmente prefiro o seaborn por trazer aspectos visuais melhores do que matplot.

As visualizações escolhidas foram:
## Gráfico de linha: Receita ao longo do ano (R$)
<img width="1184" height="584" alt="image" src="https://github.com/user-attachments/assets/27625df8-b601-4dfc-bf33-667c3fcf9cbf" />
### Comentário: Maior receita em Maio e menor em Setembro.

## Gráfico de barras: Receita por Dia da Semana (R$)
<img width="984" height="584" alt="image" src="https://github.com/user-attachments/assets/8456525a-f767-488e-bb2a-70015725c483" />
### Comentário: Terça-feira e Sexta-feira dias com menor receita e Quarta-feira com maior receita. Esse fato é contraintuitivo e, por ser um dataset simulado, dificilmente seria observado em um cenário real (finais de semana concentram mais viagens de ônibus do que o meio da semana).

## Gráfico de barras: Quantidade de viagens por Dia da Semana (R$)
<img width="984" height="584" alt="image" src="https://github.com/user-attachments/assets/406cd32f-d1e1-452d-8780-ae63159fdb87" />
### Comentário: Esse gráfico tem o mesmo comportamento do gráfico de receita, portanto, pode ser um forte indício de correlação entre as variáveis.

## Gráfico de barras: Quantidade de viagens por Horário/Turno
<img width="884" height="484" alt="image" src="https://github.com/user-attachments/assets/182c43eb-0a3c-4e4a-aa4b-2a1e36c60692" />
### Comentário: Foi observado uma quantidade bem baixa de viagens de Madrugada. Nos demais horários do dia, a quantidade de viagens não flutua tanto.

## Tabelas de Preço Médio
<img width="364" height="888" alt="image" src="https://github.com/user-attachments/assets/a423b132-fea7-4f77-89be-a4ca4f11f8ee" />
### Comentário: Construí essas tabelas para verificar se o preço maior ou menor gera um aumento significativo no número de bilhetes vendidos ou na receita. Não observei esse efeito, a receita pareceu-me proporcional à quantidade de vendas.

## Teste de correlação entre Quantidade de viagens e Receita por Dia da Semana
<img width="509" height="84" alt="image" src="https://github.com/user-attachments/assets/3a274f7f-b9f6-47bf-88b7-d2d2c25cc2a7" />
### Comentário: O valor encontrado foi muito próximo de 1, portanto, quanto mais bilhetes vendidos mais receita gerada (o que não é nenhuma novidade, é o comportamtneo natural)

## Gráfico de regressão: Preço unitário vs. Quantidade de passagens
<img width="884" height="484" alt="image" src="https://github.com/user-attachments/assets/1e74137b-8973-4fea-8d47-7ee538a033c6" />
### Comentário: O valor encontrado foi muito próximo de 0, portanto, não podemos inferir correlação entre as variáveis e o preço (mais barato, por exemplo) não influencia nem gera demanda por uma quantidade maior de vendas.

## Mapa de calor¹ dos assentos mais escolhidos
<img width="1278" height="761" alt="image" src="https://github.com/user-attachments/assets/545a77a4-081b-41e0-b114-2829a6fef7ae" />
### Comentário, apesar de haver alguns assentos mais buscados, não é relevante para motivar uma promoção ou política de vendas. Talvez em uma análise futura, pode-se propor um dataset real que tenha diferença de valores por assento (assentos premium, leito etc) ou ainda, com variação de preço (assentos reservados, assentos com acessibilidade, acentos próximos à TV ou banheiros).
(1.) Mapa de calor construído com GPT.

# 4. Ampliações e insights futuros
Gerar um novo dataset inicial com diferenciação no layout do ônibus, com assentos mais caros e mais baratos por defaut podem gerar maiores possibilidades de investigação. Aumento da demanda aos finais de semana, em feriados ou meses de férias, também tornariam o desafio mais real.
Considerando o dataset simulado, a única evidência observada é a sazonalidade com grande número de viagens em Maio e poucas em Setembro, podendo gerar ações de aumento do valor dos bilhetes em Maio (visando um aumento na Receita) e ações de marketing ou tickets promocionais em Setembro (visando uma maior demanda).
