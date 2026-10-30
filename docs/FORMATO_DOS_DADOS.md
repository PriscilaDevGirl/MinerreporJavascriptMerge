# Formato dos dados

## Amostras validadas

`dataset/project_cases.csv` é um CSV UTF-8 com separador vírgula e as seguintes colunas:

| Coluna | Significado |
|---|---|
| `project` | Identificador da pasta do projeto, no padrão proprietário e repositório separados por `__` |
| `merge commit` | SHA da integração histórica |
| `ancestor commit` | SHA do ancestral comum |
| `left parent commit` | SHA do primeiro pai |
| `right parent commit` | SHA do segundo pai |
| `file path` | Caminho original do arquivo no repositório |
| `repo url` | URL do projeto de origem |

As sete colunas correspondem ao esquema descrito no README do SCAz.js. O formato e o separador precisam ser conferidos na integração com a versão do analisador escolhida. A publicação não afirma que as amostras já foram executadas nessa ferramenta.

`manifesto_amostras.csv` acrescenta `sample_id`, calculado como SHA256 dos valores projeto, SHA do merge e caminho, separados pelo byte nulo. A chave lógica continua sendo projeto–merge–arquivo.

## Organização por projeto

Cada diretório de `projetos/` pode conter:

- `commits.csv`: lista dos merges de entrada e seus dois pais;
- `origem.json`: clone, HEAD congelado e URL, com caminhos normalizados;
- `comando.json`: argumentos da chamada ao framework;
- `saida_oficial/data/results.csv`: CSV original do coletor, separado por ponto e vírgula;
- `saida_oficial/statistics/results.csv`: estatísticas produzidas pela ferramenta;
- `project_cases.csv`: amostras validadas daquele projeto;
- `exclusoes.csv`: registros reprovados na auditoria;
- `resumo.json`: contagens do processamento.

O projeto sem merges de dois pais não possui chamada ao framework nem saída oficial correspondente. Os arquivos ausentes nessa situação não devem ser interpretados como perda de resultados.

## Motivos de exclusão

Os motivos são registrados como códigos combináveis com `|`:

- `nonunique_or_degenerate_base`: ancestral não único ou igual a um dos pais;
- `left_status_not_M` / `right_status_not_M`: comparação daquele lado não apresenta o status exigido;
- `base_file_missing`, `left_file_missing`, `right_file_missing`, `merge_file_missing`: versão não recuperável para o caminho.

Os números de linha nas saídas oficiais pertencem às comparações realizadas pelo coletor. Não são um mapa pronto de Left e Right na versão integrada.

## Integridade

`MANIFESTO_SHA256.csv` registra caminho, tamanho e SHA256 de cada arquivo da publicação, exceto o próprio manifesto. O verificador também confere as contagens e a ausência de chaves duplicadas. O manifesto de amostras e o manifesto de arquivos têm finalidades diferentes.

Os CSVs oficiais foram copiados sem alteração de seus registros. Os metadados consolidados e as exclusões são produtos da auditoria posterior, separados das saídas oficiais.
