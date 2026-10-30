# Inspiração no artigo e diferenças do recorte

Referência: MORAES, Amanda; BORBA, Paulo; DA SILVA, Léuson. *Semantic conflict detection via dynamic analysis*. SBLP, 2024. [DOI 10.5753/sblp.2024.3471](https://doi.org/10.5753/sblp.2024.3471).

A seção 4.2.1 e a Figura 4 orientaram o fluxo de coleta: lista de projetos, extração de cenários com MiningFramework, seleção de arquivos alterados pelas duas contribuições e preparação de metadados para a análise dinâmica posterior.

## Comparação dos recortes

| Aspecto | Estudo de Amanda e colaboradores | Coleta deste grupo |
|---|---|---|
| Origem dos candidatos | Lista anterior de Tavares e colaboradores | Consulta GraphQL e critérios próprios |
| Projetos | 50 projetos de origem | 100 selecionados, 68 clonados, 43 processados |
| Critérios de seleção | Popularidade, atividade e preferência por ECMAScript 5 | Mais de 1.000 estrelas, pelo menos 500 commits na branch padrão, cinco usuários mencionáveis, sem forks e templates na consulta |
| Restrição temporal | Filtro cronológico com 2015 como limite superior, para favorecer compatibilidade com Jalangi2 | Sem filtro temporal |
| Ferramenta de coleta | MiningFramework | Filtros e coletores oficiais do MiningFramework, com configuração para clones locais |
| Unidade de amostra | Arquivo associado a cenário de merge | Par projeto–merge–arquivo |
| Amostras coletadas | 452 | 15.952 pares brutos; 10.162 após auditoria estrutural |
| Merges únicos nas amostras | Total não explicitado no artigo | 3.532 |
| Projetos que efetivamente fornecem amostras | Não equiparar automaticamente à lista de 50 | 34 dos 43 processados |
| Análise dinâmica | 159 amostras executadas e 293 com erro de execução | Não executada nesta etapa |
| Encerramento | Conjunto e avaliação descritos no artigo | Restrição de disco e decisão de manter os 43 processados |

## O que foi aproveitado

- Uso de histórico Git e de cenários com duas contribuições.
- Coleta por meio do MiningFramework.
- Seleção de arquivos modificados nas duas contribuições em relação ao ancestral.
- Registro de projeto, arquivo, merge, pais e base para rastreabilidade.

## O que ainda não foi reproduzido

O mapeamento das linhas de cada contribuição na versão integrada, a preparação das dependências históricas e a execução com SCAz.js/Jalangi2 pertencem à próxima etapa. Os números de linha do CSV bruto não foram automaticamente convertidos em linhas do merge. Não há resultados de OA, dataflow, cobertura, precisão ou recall nesta publicação.

Esta coleta deve ser descrita como **adaptação do procedimento de mineração**, não como reprodução exata do experimento do artigo. Quantidade maior de amostras não demonstra melhor qualidade ou maior capacidade de detectar conflitos.
