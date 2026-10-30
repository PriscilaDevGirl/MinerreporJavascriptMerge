# Construção do dataset

## Objetivo e unidade de análise

Selecionar projetos JavaScript e coletar arquivos alterados nas duas contribuições de um cenário de merge, preparando metadados rastreáveis para uma etapa posterior de análise dinâmica. A chave de uma amostra é a combinação `(project, merge commit, file path)`.

A mineração não executou o JavaScript dos projetos, não identificou conflitos e não avaliou cobertura das alterações. O termo “validada” significa aprovação nos critérios estruturais abaixo.

## Seleção inicial

Foi executado um script JavaScript usando a API GraphQL do GitHub por meio de `@octokit/graphql`. A consulta foi:

```text
language:JavaScript stars:>1000 fork:false template:false
```

Os resultados foram obtidos em páginas de 30. O script reteve repositórios com pelo menos 500 commits na branch padrão e cinco usuários mencionáveis, ignorando nomes completos já visitados. A busca terminou ao atingir 100 selecionados; a saída da execução registrou 116 resultados examinados.

Não houve ordenação explícita por `sort` na consulta. Os números de estrelas e commits são os retornados no momento da seleção. O horário exato dessa consulta não foi registrado em arquivo próprio. Sua repetição pode fornecer outros projetos; os metadados dos 43 publicados estão em `dataset/selecao_projetos_processados.csv`.

`mentionableUsers` não representa uma contagem exata de colaboradores. O filtro de linguagem também não foi seguido por medição independente da proporção de JavaScript. Não houve exclusão manual prévia de documentação, tutoriais ou listas.

## Clonagem e validação

A clonagem utilizou `git clone URL PASTA`, sem `--depth`. Os diretórios foram nomeados pelo padrão `proprietario__repositorio`. Por limitação de disco, a clonagem foi interrompida com 68 clones disponíveis; os 32 candidatos restantes não foram clonados.

Cada clone disponível foi verificado com:

```powershell
git -C CAMINHO_DO_CLONE rev-parse --verify HEAD
git -C CAMINHO_DO_CLONE rev-parse --is-shallow-repository
git -C CAMINHO_DO_CLONE fsck --connectivity-only --no-dangling
```

Os 68 apresentaram HEAD válido, histórico não superficial e conectividade dos objetos. Essas verificações não são uma auditoria de segurança nem uma prova de recuperação de todas as referências remotas.

## Congelamento das entradas

No início do processamento de cada projeto, registrou-se o HEAD local. O universo de merges corresponde aos ancestrais alcançáveis desse SHA com exatamente dois pais:

```powershell
git -C CAMINHO_DO_CLONE log --min-parents=2 --max-parents=2 --format="%H %P" SHA_CONGELADO
```

Não foram aplicadas datas mínima ou máxima. Branches não integradas ao HEAD registrado não compõem essa definição de histórico. Left corresponde ao primeiro pai e Right ao segundo. Os 43 projetos processados forneceram 27.422 merges de entrada, que não devem ser confundidos com merges elegíveis ou com amostras válidas.

Cada pasta em `projetos/` preserva `commits.csv` e, quando aplicável, `origem.json` e `comando.json`. O projeto sem merges de dois pais foi encerrado antes de chamar o framework.

## Coleta com o MiningFramework

O executor Python organiza a chamada ao MiningFramework pelo PowerShell. O framework utiliza seu filtro oficial `MutuallyModifiedFilesCommitFilter` e seus coletores oficiais `ModifiedFilesLinesPerFileCollector` e `StatisticsCollector`.

Uma configuração local omite apenas o processador que exige a existência remota no GitHub, pois a execução utiliza clones locais. Os algoritmos dos filtros e coletores não foram reimplementados.

Foram usados clones temporários com objetos compartilhados, uma thread e semente 1. Os clones originais não foram passados ao worker para reset ou checkout. A opção `--project-commit-hashes-file` forneceu explicitamente os merges de entrada; o limite de 2147483647 excede as entradas. A semente determinou a ordem de processamento, sem reduzir o lote a uma amostra de merges.

Um piloto do Express validou previamente o fluxo em cinco merges elegíveis, com 15 pares brutos e 14 válidos. O piloto não foi somado ao dataset final. Os números publicados provêm exclusivamente do lote completo, sem duplicação de chaves.

## Auditoria por arquivo

Após a coleta oficial, cada par foi submetido aos seguintes critérios:

1. Merge de dois pais.
2. Ancestral comum único e distinto dos pais.
3. Caminho terminado em `.js`.
4. Status `M` nas comparações base–Left e base–Right.
5. Arquivo recuperável nas quatro revisões Base, Left, Right e Merge.

O filtro do framework aceita um merge ao encontrar algum arquivo JavaScript mutuamente modificado. O coletor então enumera uma interseção de arquivos alterados com uma regra mais ampla. A auditoria por arquivo resolve essa diferença e preserva os motivos das exclusões.

Dos 15.952 pares brutos, 5.790 foram excluídos e 10.162 foram validados. Entre as exclusões, 5.005 foram marcadas como ancestral não único ou degenerado; os demais 785 apresentaram combinações de arquivo ausente e status diferente de `M`.

Os 21 merges ignorados pelo framework por dificuldade de obtenção do ancestral são uma ocorrência separada. Não são 21 amostras, nem resultados negativos de OA.

## Encerramento e publicação

A execução iniciou em 29/10/2026 às 15h32 e encerrou em 30/10/2026 às 00h25, no fuso de Brasília, por espaço abaixo do limiar preventivo de 4 GiB. O próximo projeto não chegou a executar a mineração e outros 24 aguardavam. Por decisão de encerramento, os 25 não foram retomados.

Os 43 processados incluem 34 projetos com amostras e nove sem amostras. Quarenta e dois foram submetidos ao framework; o restante não tinha merges de dois pais. O dataset reúne 10.162 amostras de 3.532 merges distintos.

Só os 43 projetos processados integram os arquivos publicados. Credenciais e caminhos específicos da máquina foram removidos dos comandos de consulta. As identificações dos projetos, os caminhos originais dos arquivos, os SHAs e os CSVs oficiais foram preservados. Nomes que pertençam ao código dos projetos de origem não foram renomeados.
