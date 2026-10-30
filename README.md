# Dataset de cenários de merge em JavaScript

Metadados e resultados de mineração de arquivos JavaScript alterados pelas duas contribuições de um merge. A coleta foi realizada em 29 e 30 de outubro de 2026 com o **MiningFramework**, inspirada no procedimento de Amanda Moraes, Paulo Borba e Léuson Da Silva em *Semantic conflict detection via dynamic analysis* (SBLP 2024).

O escopo deste repositório é **mineração e validação estrutural**. Não foram executadas análises de overriding assignments (OA), dataflow ou classificação de conflitos semânticos.

## Autoria e apoio acadêmico

**Autora do dataset: Priscila Almeida.** A autoria registrada refere-se à construção, seleção, organização e documentação deste conjunto de pesquisa, respeitados os direitos sobre os materiais de origem.

A mineração foi realizada para estudos de **análise dinâmica e fluxo de dados (dataflow)**, inspirada no artigo de **Amanda Moraes, Paulo Borba e Léuson Da Silva**, com **apoio acadêmico do professor Paulo Borba**.

A atribuição de autoria, os agradecimentos e o alcance dos direitos estão detalhados em [AUTORIA.md](AUTORIA.md) e [DIREITOS_E_LICENCAS.md](DIREITOS_E_LICENCAS.md).

## Conjunto publicado

| Indicador | Quantidade |
|---|---:|
| Projetos processados | 43 |
| Projetos com amostras válidas | 34 |
| Projetos processados sem amostras válidas | 9 |
| Pares arquivo–merge coletados antes da auditoria | 15.952 |
| Pares excluídos na auditoria | 5.790 |
| Amostras válidas e únicas | 10.162 |
| Merges distintos com amostras válidas | 3.532 |

Uma amostra corresponde a **um arquivo em um cenário de merge**, identificado por projeto, SHA do merge e caminho do arquivo. Um mesmo merge pode fornecer várias amostras; esses números não representam conflitos detectados.

Somente os 43 projetos processados estão publicados. Um deles não tinha merges de dois pais e foi encerrado antes da chamada ao framework; os outros 42 foram submetidos à ferramenta. As nove ocorrências sem amostras também estão registradas, para não ocultar resultados nulos da coleta.

## Construção do dataset

1. Uma consulta GraphQL examinou 116 resultados e selecionou 100 projetos por critérios explícitos.
2. Foram clonados e verificados 68 históricos Git sem corte de profundidade.
3. Foram processados 43 projetos, considerando os merges de dois pais alcançáveis do HEAD registrado em cada um, **sem filtro de data**.
4. O MiningFramework coletou os pares arquivo–merge e as alterações de cada contribuição.
5. Uma auditoria verificou ancestral comum, status de alteração e presença do arquivo nas quatro versões.
6. O lote foi interrompido por espaço livre abaixo de 4 GiB. Os 25 clones restantes não foram minerados. O conjunto foi posteriormente encerrado nos 43 projetos processados.

Os 32 candidatos não clonados pertencem à etapa anterior. As listas individuais dos candidatos não processados não integram esta publicação; suas quantidades são mantidas como contexto metodológico.

## Onde começar

- [`dataset/project_cases.csv`](dataset/project_cases.csv): as 10.162 amostras validadas.
- [`dataset/projetos.csv`](dataset/projetos.csv): os 43 projetos, SHAs congelados, contagens e tempos.
- [`dataset/projetos_com_amostras.csv`](dataset/projetos_com_amostras.csv): os 34 que forneceram amostras.
- [`dataset/exclusoes.csv`](dataset/exclusoes.csv): os 5.790 pares excluídos e seus motivos.
- [`dataset/manifesto_amostras.csv`](dataset/manifesto_amostras.csv): identificador estável por amostra.
- [`projetos/`](projetos): entradas, comandos normalizados e saídas oficiais por projeto.

## Documentação

- [Metodologia da construção](docs/METODOLOGIA.md)
- [Ferramentas e adaptações](docs/FERRAMENTAS.md)
- [Execução pelo PowerShell](docs/EXECUCAO.md)
- [Inspiração no artigo e diferenças do recorte](docs/ARTIGO_E_DIFERENCAS.md)
- [Limitações e encerramento por disco](docs/LIMITACOES.md)
- [Esquema dos arquivos e integridade](docs/FORMATO_DOS_DADOS.md)

## Verificação da entrega

Com Python 3 disponível, na raiz do repositório:

```powershell
python .\scripts\verificar_dataset.py
```

O verificador confere os hashes dos arquivos publicados e as contagens do dataset. Não executa mineração ou código dos projetos.

## Recuperação dos arquivos

O dataset publica metadados, não cópias completas dos históricos Git nem uma exportação em massa das quatro versões. Para recuperar uma amostra dos clones locais:

```powershell
python .\scripts\extrair_versoes.py --csv .\dataset\project_cases.csv --repositorios C:\Mineraai\repositorios --saida C:\Mineraai\amostras_extraidas --projeto expressjs__express --limite 1
```

O script exporta `base.js`, `left.js`, `right.js`, `merge.js` e metadados, preservando os bytes originais. Esse comando não executa JavaScript nem gera o mapa das contribuições para OA.

## Referência

Para citar este dataset:

> ALMEIDA, Priscila. **Dataset de cenários de merge em JavaScript**. Versão 1.0.0. 2026. Dataset. Disponível em: https://github.com/PriscilaDevGirl/MinerreporJavascriptMerge.

Os metadados de citação estão em [CITATION.cff](CITATION.cff), e a entrada BibTeX está em [CITATION.bib](CITATION.bib).

### Artigo que inspirou a mineração

MORAES, Amanda; BORBA, Paulo; DA SILVA, Léuson. **Semantic conflict detection via dynamic analysis**. SBLP, 2024. [DOI 10.5753/sblp.2024.3471](https://doi.org/10.5753/sblp.2024.3471). O procedimento de coleta está na seção 4.2.1 e na Figura 4.

Ferramenta de mineração: [spgroup/miningframework](https://github.com/spgroup/miningframework), commit `7a9503f0e3af110fb0028fb02753d4c4a627266e`. A licença da ferramenta está preservada em [`ferramenta/LICENSE-MiningFramework`](ferramenta/LICENSE-MiningFramework).

Os dados de origem continuam vinculados aos respectivos projetos. Antes de redistribuir snapshots de código, deve-se conferir a licença de cada projeto e revisão.
