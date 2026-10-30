# Recuperar Base Left Right e Merge em outro computador

## Não é necessário acessar o computador da autora

O dataset pode ser usado por outro integrante da pesquisa em seu próprio computador. Não é necessário acesso remoto ao notebook da autora, à sua conta do sistema ou aos seus arquivos pessoais.

O que é necessário:

- uma cópia deste repositório do dataset;
- Git e Python 3 disponíveis no computador;
- acesso à internet para obter os históricos públicos dos projetos;
- espaço em disco para os históricos e as versões que serão extraídas.

As versões foram verificadas nos clones existentes no momento da coleta. Sua recuperação em outra máquina depende da disponibilidade dos objetos Git nos projetos de origem ou de uma cópia preservada desses históricos. O CSV não contém os bytes dos arquivos JavaScript.

## O que o dataset entrega

Cada linha de `dataset/project_cases.csv` registra o projeto, a URL, o caminho do arquivo e os quatro commits necessários:

| Versão | Significado | Coluna |
|---|---|---|
| Base | Arquivo no ancestral comum | `ancestor commit` |
| Left | Arquivo no primeiro pai | `left parent commit` |
| Right | Arquivo no segundo pai | `right parent commit` |
| Merge | Arquivo na integração histórica | `merge commit` |

São quatro revisões do mesmo caminho de arquivo, não quatro nomes que precisem ser adivinhados. A extração usa os SHAs congelados, e não a versão mais recente do arquivo.

### Exemplo real com links para as quatro versões

Projeto: `expressjs/express`. Caminho original: `examples/downloads/app.js`. Os links abaixo abrem as revisões históricas no GitHub do projeto de origem, sem acessar o computador da autora.

| Versão | Commit | Arquivo no projeto de origem |
|---|---|---|
| Base | `c0aab3618780` | [Abrir arquivo](https://github.com/expressjs/express/blob/c0aab3618780058ffde5373daa712ae746fabaaa/examples/downloads/app.js) |
| Left | `9605cbda452a` | [Abrir arquivo](https://github.com/expressjs/express/blob/9605cbda452ad5dcfb4bbb9e105af5965fddb185/examples/downloads/app.js) |
| Right | `a8930b161e38` | [Abrir arquivo](https://github.com/expressjs/express/blob/a8930b161e38ba27b68743a1dafe5a67a3617866/examples/downloads/app.js) |
| Merge | `04ce039ba4ef` | [Abrir arquivo](https://github.com/expressjs/express/blob/04ce039ba4effc7df680e8dbe06ae56d6a987abe/examples/downloads/app.js) |

Esse é um exemplo de recuperação. As quatro versões também podem ser iguais em partes do conteúdo; os links não representam um alerta de OA. Para as demais amostras, combine a URL do projeto, o SHA da coluna correspondente e o caminho do arquivo.

## 1 Baixar o dataset

No PowerShell do computador que fará a recuperação:

```powershell
git clone --branch main https://github.com/PriscilaDevGirl/MinerreporJavascriptMerge.git dataset-mineracao
Set-Location dataset-mineracao
git --version
python --version
python .\scripts\verificar_dataset.py
```

Este guia usa os scripts atualizados da branch `main`. O conjunto de dados continua sendo a versão 1.0.0; os novos comandos não alteram suas amostras. Se já houver uma cópia do dataset, atualize-a com o fluxo Git adequado ao trabalho local.

Se `python` não estiver disponível por esse nome, utilize o comando correspondente à instalação do computador, por exemplo `py -3` no Windows ou `python3` no Linux.

## 2 Obter primeiro um único histórico

```powershell
$repositorios = Join-Path (Get-Location) 'repositorios'
$amostras = Join-Path (Get-Location) 'amostras_extraidas'

.\scripts\clonar_projetos_processados.ps1 -Destino $repositorios -Projeto expressjs__express
```

`$repositorios` e `$amostras` são diretórios criados no computador que está executando os comandos. Não dependem de `C:\Mineraai` nem do computador da autora.

O script baixa o histórico sem `--depth`, evita o checkout inicial da árvore de trabalho e confere a disponibilidade do HEAD registrado. Ele não executa código JavaScript. Uma pasta de clone já existente precisa conter um repositório Git válido; em caso de clone incompleto, corrija-o antes de prosseguir.

Se o PowerShell bloquear scripts locais, siga a política do ambiente ou use o comando Git equivalente, sem precisar desativar a política de segurança:

```powershell
New-Item -ItemType Directory -Path $repositorios -Force
git clone --no-checkout https://github.com/expressjs/express "$repositorios\expressjs__express"
```

Esse comando alternativo também pode ser adaptado a outro sistema operacional com Git.

## 3 Extrair uma amostra

```powershell
python .\scripts\extrair_versoes.py --csv .\dataset\project_cases.csv --repositorios $repositorios --saida $amostras --projeto expressjs__express --limite 1
```

A estrutura produzida é:

```text
amostras_extraidas/
  identificador_SHA256_da_amostra/
    base.js
    left.js
    right.js
    merge.js
    metadados.json
```

O identificador é o mesmo `sample_id` calculado no manifesto. `metadados.json` conserva o caminho original, os SHAs, a URL e os hashes SHA256 dos quatro arquivos exportados. Os nomes de saída são padronizados; o conteúdo original é preservado em bytes.

O extrator não sobrescreve uma amostra que já exista na pasta de destino. Para repetir o teste, escolha outra pasta em `--saida` ou gerencie conscientemente a extração anterior.

## 4 Ampliar a recuperação

Para obter somente os 34 projetos que forneceram amostras:

```powershell
.\scripts\clonar_projetos_processados.ps1 -Destino $repositorios -SomenteComAmostras
```

Para extrair todas as amostras do Express, use uma pasta de saída nova e omita o limite:

```powershell
$saidaExpress = Join-Path (Get-Location) 'extracao_express'
python .\scripts\extrair_versoes.py --csv .\dataset\project_cases.csv --repositorios $repositorios --saida $saidaExpress --projeto expressjs__express
```

Para todos os projetos com amostras, omita também `--projeto`, somente depois de conferir o espaço disponível. Não é preciso minerar novamente os 43 projetos para extrair os registros já publicados.

## O que falta para executar OA

A recuperação das quatro versões prepara os arquivos históricos. Ela não executa o analisador, não instala as dependências dos projetos e não produz o mapa das contribuições na versão integrada.

O responsável pela análise precisa confirmar o acesso à versão do SCAz.js/Jalangi2 utilizada, preparar o ambiente e gerar ou conferir o mapa Left/Right exigido pelo fluxo da ferramenta. Na abordagem do artigo, a análise dinâmica observa a versão Merge com esse mapa. As outras versões sustentam a identificação das contribuições e a rastreabilidade.

O README do SCAz.js informa testes em Ubuntu e suporte garantido até ECMAScript 5.1. Como a coleta atual não tem corte temporal, a compatibilidade dos arquivos deve ser avaliada. Falhas de preparação e execução devem ser registradas separadamente de resultados sem alerta.

Recuperação bem-sucedida das quatro versões não demonstra a existência de OA nem garante sucesso de execução. A etapa seguinte deve começar por um piloto pequeno, com suas entradas e resultados documentados.

## Verificação do caminho de recuperação

Em 30/10/2026, o procedimento foi testado com um clone novo do Express, obtido diretamente do GitHub e sem objetos compartilhados com os clones anteriores. Uma amostra de `examples/downloads/app.js` foi recuperada, com as quatro versões e seus hashes conferidos. O teste ocorreu na máquina de preparação usando um histórico independente; não é um teste de OA nem valida a execução de todas as amostras ou de todos os sistemas operacionais. Os identificadores, tamanhos e hashes estão em [VERIFICACAO_RECUPERACAO.json](VERIFICACAO_RECUPERACAO.json).
