# Execução da coleta pelo PowerShell

Este documento descreve o fluxo usado e apresenta comandos de reprodução. Os exemplos usam um diretório de runtime padronizado; os caminhos da máquina original foram normalizados. Os argumentos preservados por projeto estão em `projetos/PROJETO/comando.json`.

Uma nova execução precisa usar nomes de saída novos. O dataset publicado permanece fechado nos 43 projetos processados.

## 1 Seleção inicial

O comando da seleção original foi `node .\minerador.js`. A cópia de reprodução está em `scripts/selecionar_projetos.mjs`, com os mesmos filtros e paginação. Para uma nova consulta:

```powershell
npm.cmd ci --prefix .\scripts
node .\scripts\selecionar_projetos.mjs
```

Defina `GITHUB_TOKEN` no ambiente por um meio seguro antes da consulta. Não inclua o token em arquivos ou transcrições de terminal. A busca gera candidatos; não extrai cenários de merge. Sua repetição não garante os mesmos 100 projetos, porque o GitHub muda.

Os resultados dos 43 projetos publicados estão congelados em `dataset/selecao_projetos_processados.csv`. As listas dos candidatos não processados não são distribuídas nesta publicação.

## 2 Clonagem dos projetos publicados

Na coleta original foi usado `git clone URL PASTA`, sem histórico raso, em um laço sequencial. Para recuperar apenas os históricos dos 43 projetos publicados, em uma máquina com espaço disponível:

```powershell
powershell -File .\scripts\clonar_projetos_processados.ps1 -Destino C:\Mineraai\repositorios
```

O script de reprodução usa `--no-checkout` para economizar espaço de arquivos da árvore de trabalho, sem aplicar `--depth`. Ele verifica se o HEAD registrado está disponível e tenta obtê-lo da origem quando necessário. Não executa JavaScript.

Verificações efetuadas na coleta:

```powershell
git -C CAMINHO_DO_CLONE rev-parse --verify HEAD
git -C CAMINHO_DO_CLONE rev-parse --is-shallow-repository
git -C CAMINHO_DO_CLONE fsck --connectivity-only --no-dangling
```

## 3 Preparação do MiningFramework

Requisitos: JDK 21, Git e GNU diff no PATH; Gradle 8.13; Python 3.12. O programa precisa de um caminho de execução e de temporários compatível com o ambiente local.

Na raiz deste repositório:

```powershell
$raizEstudo = (Get-Location).Path
$runtimeMineracao = 'C:\Mineraai\mining-runtime'

New-Item -ItemType Directory -Path $runtimeMineracao -Force
git clone https://github.com/spgroup/miningframework.git "$runtimeMineracao\miningframework"
git -C "$runtimeMineracao\miningframework" checkout 7a9503f0e3af110fb0028fb02753d4c4a627266e

git -C "$runtimeMineracao\miningframework" apply "$raizEstudo\ferramenta\compatibilidade-build.patch"
git -C "$runtimeMineracao\miningframework" apply "$raizEstudo\ferramenta\finalizacao-git.patch"
```

Instale a distribuição Gradle 8.13 em `C:\Mineraai\mining-runtime\gradle-runtime`, de modo que exista `gradle-runtime\bin\gradle.bat`. Não confunda a distribuição do Gradle com o repositório do framework.

Configure o ambiente e obtenha as dependências antes de usar a execução offline:

```powershell
$env:MINING_RUNTIME = $runtimeMineracao
$env:JAVA_HOME = 'C:\Program Files\Eclipse Adoptium\jdk-21.0.8.9-hotspot'
$env:GRADLE_USER_HOME = "$runtimeMineracao\gradle-cache"
$env:TEMP = "$runtimeMineracao\tmp"
$env:TMP = $env:TEMP
$env:PATH = "C:\Program Files\Git\usr\bin;" + $env:PATH

New-Item -ItemType Directory -Path $env:TEMP -Force
New-Item -ItemType Directory -Path $env:GRADLE_USER_HOME -Force

Push-Location "$runtimeMineracao\miningframework"
& "$runtimeMineracao\gradle-runtime\bin\gradle.bat" --no-daemon --console=plain "-Dorg.gradle.jvmargs=-Xmx512m -Djava.io.tmpdir=C:/Mineraai/mining-runtime/tmp" classes
Pop-Location
```

Adapte `JAVA_HOME` e o diretório de GNU diff à instalação da máquina. A primeira compilação requer acesso aos repositórios de dependências. A execução registrada usou cache provisionado e `--offline`; essa opção não instala dependências ausentes.

## 4 Execução organizada pelo script

Para uma nova coleta apenas do Express:

```powershell
python .\scripts\executar_coleta.py --run-name reproducao-express --repo-root C:\Mineraai\repositorios --project expressjs__express
```

Para uma nova coleta dos históricos encontrados no diretório informado:

```powershell
python .\scripts\executar_coleta.py --run-name reproducao-projetos --repo-root C:\Mineraai\repositorios
```

O segundo comando processa todos os subdiretórios detectados. Para repetir apenas o escopo publicado, use um diretório que contenha somente os 43 projetos listados. O script recusa sobrescrever uma execução de mesmo nome e salva resultados em `resultados_locais/NOME`.

O executor registra o HEAD, enumera seus merges de dois pais, prepara `commits.csv` e `projects.csv`, cria uma cópia temporária com objetos compartilhados e chama o Gradle. A configuração local é copiada de `ferramenta/LocalDynamicAnalysisJsModule.groovy`.

## 5 Chamada da ferramenta de mineração

O núcleo da chamada é:

```powershell
$argumentosColeta = '--injector injectors.LocalDynamicAnalysisJsModule --extension .js --keep-projects --threads 1 --random-seed 1 --max-commits-per-project 2147483647 --project-commit-hashes-file CAMINHO/commits.csv CAMINHO/projects.csv CAMINHO/output'

& "$runtimeMineracao\gradle-runtime\bin\gradle.bat" --offline --no-daemon --console=plain "-Dorg.gradle.jvmargs=-Xmx512m -Djava.io.tmpdir=C:/Mineraai/mining-runtime/tmp" run "--args=$argumentosColeta"
```

O comando deve ser executado na raiz do MiningFramework com as entradas preparadas. Os três caminhos são parâmetros de reprodução, não nomes literais de arquivos já existentes. O script evita ter de montá-los manualmente e registra os argumentos utilizados por projeto.

`--project-commit-hashes-file` fixa os merges fornecidos; `.js` restringe a extensão; uma thread mantém a execução sequencial; a semente 1 controla a ordem. Não há `--since` ou `--until`. O limite operacional informado não reduz o conjunto de entrada a uma amostra.

## 6 Preservação e auditoria

O executor preserva as saídas oficiais, verifica cada par e gera as amostras consolidadas. Após salvar os resultados e conferir o HEAD original, remove somente a cópia temporária. A checagem de disco antes de cada projeto impede novas execuções com menos de 4 GiB livres.

A interpretação das saídas e os critérios da auditoria estão em [METODOLOGIA.md](METODOLOGIA.md). Os ajustes de ambiente estão em [FERRAMENTAS.md](FERRAMENTAS.md). Não houve análise OA ou dataflow nesta execução.
