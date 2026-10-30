import { graphql } from "@octokit/graphql";

const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

if (!GITHUB_TOKEN) {
  console.error("Defina GITHUB_TOKEN no ambiente antes de executar.");
  process.exit(1);
}

const graphqlWithAuth = graphql.defaults({
  headers: {
    authorization: `Bearer ${GITHUB_TOKEN}`,
  },
});

const QUERY = `
  query SearchJSRepositories($cursor: String) {
    search(
      query: "language:JavaScript stars:>1000 fork:false template:false"
      type: REPOSITORY
      first: 30
      after: $cursor
    ) {
      pageInfo {
        endCursor
        hasNextPage
      }
      edges {
        node {
          ... on Repository {
            nameWithOwner
            url
            stargazerCount
            defaultBranchRef {
              target {
                ... on Commit {
                  history {
                    totalCount
                  }
                }
              }
            }
            mentionableUsers {
              totalCount
            }
          }
        }
      }
    }
  }
`;

async function minerarRepositorios() {
  const repositoriosValidados = [];
  const repositoriosVisitados = new Set();

  let hasNextPage = true;
  let cursor = null;

  console.log("Buscando repositórios JavaScript...");

  try {
    while (hasNextPage && repositoriosValidados.length < 100) {
      const response = await graphqlWithAuth(QUERY, { cursor });
      const search = response.search;

      for (const edge of search.edges ?? []) {
        const repo = edge?.node;

        if (!repo?.nameWithOwner) continue;
        if (repositoriosVisitados.has(repo.nameWithOwner)) continue;

        repositoriosVisitados.add(repo.nameWithOwner);

        const commits =
          repo.defaultBranchRef?.target?.history?.totalCount ?? 0;

        const usuariosMencionaveis =
          repo.mentionableUsers?.totalCount ?? 0;

        if (commits >= 500 && usuariosMencionaveis >= 5) {
          repositoriosValidados.push({
            nome: repo.nameWithOwner,
            url: repo.url,
            estrelas: repo.stargazerCount,
            totalCommits: commits,
            usuariosMencionaveis,
          });
        }

        if (repositoriosValidados.length >= 100) break;
      }

      console.log(
        `Analisados: ${repositoriosVisitados.size} | ` +
        `Selecionados: ${repositoriosValidados.length}`
      );

      hasNextPage = search.pageInfo.hasNextPage;

      const proximoCursor = search.pageInfo.endCursor;

      if (!proximoCursor || proximoCursor === cursor) break;

      cursor = proximoCursor;
    }

    console.log(
      `\nBusca concluída: ${repositoriosValidados.length} repositórios encontrados.`
    );

    console.table(repositoriosValidados);
  } catch (error) {
    console.error("Erro na API do GitHub:", error.message);
    process.exitCode = 1;
  }
}

await minerarRepositorios();