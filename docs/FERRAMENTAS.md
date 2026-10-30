# Ferramentas e adaptações do ambiente

| Componente | Versão ou uso registrado |
|---|---|
| Git | 2.55.0.windows.5 |
| Node.js | 24.14.1 |
| `@octokit/graphql` | 9.0.5 no lockfile |
| Python | 3.12.14, organização das chamadas e auditoria |
| Java | Eclipse Temurin 21.0.8 |
| Gradle | 8.13 |
| Groovy | 3.0.23 |
| GNU diff | Comparação textual utilizada pelo coletor |
| PowerShell | Shell de execução dos comandos e scripts |

## MiningFramework

Origem: https://github.com/spgroup/miningframework

Commit fixado: `7a9503f0e3af110fb0028fb02753d4c4a627266e`.

O repositório utiliza um framework configurável. A configuração publicada em `ferramenta/LocalDynamicAnalysisJsModule.groovy` mantém as classes oficiais:

- `MutuallyModifiedFilesCommitFilter`;
- `ModifiedFilesLinesPerFileCollector`;
- `StatisticsCollector`.

A diferença para `DynamicAnalysisJsModifiedLinesDetectionModule` é a omissão do processador de verificação de projetos remotos, que rejeita caminhos locais. Não houve reimplementação dos filtros e coletores.

## Ajustes registrados

1. `compatibilidade-build.patch`: atualização da declaração de `mainClass` e uso do Java 21 disponível em lugar do toolchain Java 17 exigido no build original.
2. Caminho curto de execução e de temporários, para evitar falhas de carregamento de JAR e comunicação local do Gradle no ambiente da coleta.
3. `finalizacao-git.patch`: consumo do fluxo de saída de reset e checkout, com `--quiet`, para impedir bloqueio na finalização de cópias temporárias. A alteração passou a valer a partir do projeto seguinte ao Gatsby.

No Gatsby, o comando Git de finalização ficou parado após a coleta. Foram conferidos o processo e sua vinculação à cópia temporária antes de encerrar apenas o filho bloqueado. Os dados coletados foram preservados e a auditoria consultou o clone original. Essa ocorrência é uma limitação de execução do ambiente e foi separada dos erros de coleta por merge.

O heap de 512 MiB configurado na chamada é o da JVM do Gradle; não deve ser descrito como limite total de memória de todos os processos filhos. A execução sequencial reduz a concorrência, sem estabelecer uma medição completa de recursos.

## Scripts deste repositório

- `selecionar_projetos.mjs`: consulta e filtros da seleção inicial; credenciais são lidas do ambiente.
- `executar_coleta.py`: prepara entradas, aciona os coletores oficiais e audita as amostras.
- `clonar_projetos_processados.ps1`: recupera os históricos dos 43 projetos publicados, sem checkout inicial e sem histórico raso.
- `extrair_versoes.py`: recupera os bytes das quatro versões e seus hashes, sem executar JavaScript.
- `verificar_dataset.py`: confere integridade e contagens da publicação.

Os scripts de reprodução têm caminhos configuráveis. O manifesto de dependências da seleção foi reconstituído com base no lockfile preservado. As mensagens de console e os caminhos locais foram normalizados sem modificar os filtros.

## Análise posterior

O artigo utiliza Jalangi2 e SCAz.js para a análise dinâmica de OA. Esses analisadores não foram executados neste dataset. A mineração não depende de executar o JavaScript dos projetos, e seu sucesso não comprova a compatibilidade desses arquivos com a instrumentação posterior.
