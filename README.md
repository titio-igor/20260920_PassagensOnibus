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
Pensando na estrutura Medallion, podemos dizer que dados_passagens_raw.csv é a nossa camada bronze que consiste nos dados brutos carregados dentro do sistema para tratamento e análise.
