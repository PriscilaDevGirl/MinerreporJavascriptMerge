# Quatro versões prontas para a próxima etapa

A exportação inclui **10.162 amostras**, provenientes de **34 projetos**, com **40.648 arquivos JavaScript históricos**. Os nove projetos processados sem amostras permanecem documentados nas tabelas; não geram pacotes de versões.

## Baixar e abrir

Os **61 ZIPs** em [`versoes/`](../versoes) são pacotes independentes, separados por projeto e parte. Não é preciso clonar os 34 projetos de origem para abrir esses arquivos. Baixe todos os pacotes para a entrega completa, ou apenas os do projeto desejado. O arquivo [`PACOTES.csv`](../versoes/PACOTES.csv) relaciona nomes, contagens, tamanhos e SHA-256.

No GitHub, abra o ZIP desejado e use **Download raw**. Para obter o dataset inteiro, use **Code → Download ZIP** na página principal e extraia o download. Os ZIPs internos ainda precisam ser descompactados.

Com uma cópia deste dataset no computador, abra o PowerShell na raiz e execute, por exemplo, para Express:

```powershell
Expand-Archive -LiteralPath .\versoes\expressjs__express_parte001.zip -DestinationPath .\amostras_extraidas\expressjs__express
```

Para descompactar todos os pacotes, preservando a organização por parte:

```powershell
Get-ChildItem -LiteralPath .\versoes -Filter '*.zip' | ForEach-Object {
    $destino = Join-Path '.\amostras_extraidas' $_.BaseName
    Expand-Archive -LiteralPath $_.FullName -DestinationPath $destino
}
```

Escolha uma pasta de destino nova. A extração completa precisa de mais de 1,19 GiB para o conteúdo JavaScript, além dos metadados, licenças e espaço alocado pelo sistema de arquivos. Os ZIPs somam **321,45 MiB**; mantê-los junto dos arquivos extraídos exige espaço adicional.

## Dentro de cada amostra

```text
<identificador-estavel-da-amostra>/
  base.js
  left.js
  right.js
  merge.js
  metadados.json
```

São as quatro revisões históricas do mesmo caminho: ancestral comum, primeiro pai, segundo pai e merge registrado. O conteúdo foi copiado dos blobs Git, sem executar JavaScript, converter codificação ou mudar as quebras de linha. Algumas revisões podem ter bytes iguais; isso não invalida a origem histórica.

`metadados.json` informa projeto, URL, caminho original, quatro commits, identificador da amostra, blobs Git e SHA-256 de cada versão. O identificador é o mesmo de `dataset/manifesto_amostras.csv`. O índice global [`ARQUIVOS_DAS_VERSOES.csv`](../versoes/ARQUIVOS_DAS_VERSOES.csv) permite localizar cada arquivo dentro de seu pacote.

## Construção e verificação

Depois da mineração e auditoria, a exportação usou `git cat-file --batch-check` para medir e validar os objetos e `git cat-file --batch` para ler seus bytes. O script escreve diretamente em ZIPs, divididos por projeto com orçamento de 32 MiB de conteúdo JavaScript por parte, sem separar as quatro versões de uma amostra. Foi mantida uma checagem preventiva de pelo menos 2 GiB livres nesta etapa de exportação. Ela não altera o limiar de 4 GiB usado na mineração original.

Com os clones já existentes, a execução foi:

```powershell
python .\scripts\exportar_versoes_zip.py --csv .\dataset\project_cases.csv --repositorios C:\Mineraai\repositorios --saida .\versoes
```

O destino deve ser novo e não conter ZIPs de uma execução anterior. Para apenas medir os bytes, acrescente `--planejar`. Não é necessário executar novamente para usar os pacotes entregues.

A conferência integral pode ser reproduzida com Python 3, sem Git nem históricos locais:

```powershell
python .\scripts\verificar_versoes_zip.py --pasta .\versoes --csv .\dataset\project_cases.csv
```

Ela lê todos os arquivos exportados e confere CRC do ZIP, SHA-256, identificador do blob Git, metadados e presença das quatro versões em cada amostra. O resultado está em [`VERIFICACAO_INTEGRAL.json`](../versoes/VERIFICACAO_INTEGRAL.json).

## Direitos dos projetos e limites da entrega

Os arquivos mantêm seu conteúdo e avisos originais. Cada pacote inclui os arquivos de licença encontrados por nomes usuais na raiz das revisões correspondentes, deduplicados por blob e nome, e `LICENCAS_POR_REVISAO.json`. O índice consolidado é `LICENCAS_POR_REVISAO.csv`. A busca na raiz não cobre todas as formas de licenciamento; revisões sem arquivo encontrado são registradas explicitamente e não significam domínio público ou concessão de nova licença. Os direitos dos projetos de origem permanecem preservados.

As quatro versões facilitam a entrada da próxima etapa. A análise OA e dataflow ainda precisa configurar a ferramenta, produzir o mapa das contribuições quando exigido, preparar dependências e entradas e avaliar compatibilidade com a sintaxe de cada amostra. Estes pacotes não contêm resultados de conflitos semânticos nem ambientes completos dos projetos.
