# Limitações e encerramento

## Espaço em disco

A disponibilidade de armazenamento limitou duas etapas diferentes:

1. A clonagem inicial ficou restrita a 68 dos 100 projetos selecionados.
2. A mineração encerrou após 43 projetos processados, quando a checagem preventiva detectou menos de 4 GiB livres antes de iniciar o próximo projeto. Assim, 25 clones não foram minerados.

O projeto impedido pela checagem não chegou a executar o coletor; não se trata de falha de análise de seus arquivos. Após a interrupção, decidiu-se manter o conjunto e não retomar o lote.

Uma medição durante a coleta indicou aproximadamente 21,1 GiB nos 68 clones e 1,13 GiB em ferramenta, dependências, cache e temporários. São leituras pontuais, sem medição de pico. O espaço livre variou durante a sessão; a leitura posterior às 05h05 de 30/10 indicou 4,96 GiB. O valor exato imediatamente abaixo do limiar não foi registrado.

O lote decorreu de 15h32 de 29/10 até 00h25 de 30/10/2026, no fuso de Brasília: aproximadamente 8h53. Esse tempo inclui coleta, validação, preparação e a ocorrência de finalização do Gatsby, não apenas processamento do coletor.

## Viés de seleção e processamento

A busca não é um censo e não oferece amostragem aleatória. O universo foi limitado pela consulta e por sua ordem de retorno. O processamento colocou Express primeiro e depois seguiu a ordenação pelos nomes das pastas; a interrupção por recursos afeta o subconjunto publicado. Os 43 não devem ser apresentados como os melhores ou mais representativos projetos do GitHub.

Não houve classificação manual prévia que excluísse listas, tutoriais e documentação. Usuários mencionáveis não são colaboradores efetivos. O recorte por linguagem da consulta não comprova uma proporção mínima de JavaScript em cada projeto.

## Histórico e arquivos

O histórico é definido pelos ancestrais alcançáveis do HEAD registrado. Não inclui necessariamente todas as branches ou referências remotas. Somente merges de dois pais foram enumerados.

Não houve exclusão específica de testes, arquivos gerados ou minificados. O dataset admite arquivos modernos por não ter limite temporal. Isso pode dificultar sua execução na versão de instrumentação usada no artigo de referência.

## Limites da validação

A aprovação estrutural verifica relações Git e presença das quatro versões. Não comprova que um arquivo execute isoladamente, que suas dependências sejam recuperáveis ou que uma entrada alcance as contribuições relevantes. Projetos sem amostras não demonstram ausência de conflitos.

O dataset inclui 5.790 exclusões e 21 merges ignorados pelo framework, com motivos registrados separadamente. Uma falha de execução futura não deve ser contada como resultado negativo de conflito.

## Publicação e continuidade

As pastas e tabelas desta publicação incluem somente os 43 projetos processados. Os números dos candidatos não processados aparecem apenas como contexto da redução da coleta.

Após o encerramento da mineração, as quatro versões das 10.162 amostras foram exportadas diretamente dos objetos Git para 61 ZIPs, sem criar todos os arquivos soltos no disco. A exportação ocupa 337.066.328 bytes compactados; os arquivos JavaScript representam 1.279.920.984 bytes descompactados. Esta etapa não amplia a amostra nem retoma a mineração. Os históricos Git completos e as dependências dos projetos não integram os pacotes. Para reconstruir o ambiente completo de execução, pode ser necessário obter o projeto de origem.

Os comandos de consulta foram normalizados quanto a caminhos locais. Identificadores e caminhos reais dentro dos projetos foram mantidos. Nenhuma análise OA ou dataflow foi realizada nesta fase.
