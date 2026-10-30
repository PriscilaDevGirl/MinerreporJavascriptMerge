param(
    [string]$Destino = '.\repositorios',
    [string]$Projeto,
    [switch]$SomenteComAmostras
)
$ErrorActionPreference = 'Stop'
$taskInput = Join-Path (Split-Path -Parent $PSScriptRoot) 'dataset\projetos.csv'
$taskRows = @(Import-Csv -LiteralPath $taskInput)
if ($Projeto) { $taskRows = @($taskRows | Where-Object { $_.projeto -eq $Projeto }) }
if ($SomenteComAmostras) { $taskRows = @($taskRows | Where-Object { [int]$_.amostras_validadas -gt 0 }) }
if ($taskRows.Count -eq 0) { throw 'Nenhum projeto corresponde aos filtros. Consulte dataset/projetos.csv.' }
New-Item -ItemType Directory -Path $Destino -Force | Out-Null
$taskRoot = (Resolve-Path -LiteralPath $Destino).Path
foreach ($taskRow in $taskRows) {
    if ($taskRow.projeto -notmatch '^[A-Za-z0-9_.-]+__[A-Za-z0-9_.-]+$') { throw 'Nome de projeto invalido' }
    if ($taskRow.url -notmatch '^https://github.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$') { throw 'URL invalida' }
    if ($taskRow.head -notmatch '^[a-f0-9]{40}$') { throw 'SHA invalido' }
    $taskTarget = Join-Path $taskRoot $taskRow.projeto
    if (!(Test-Path -LiteralPath $taskTarget)) {
        & git clone --no-checkout $taskRow.url $taskTarget
        if ($LASTEXITCODE -ne 0) { throw "Falha de clonagem: $($taskRow.projeto)" }
    }
    & git -C $taskTarget cat-file -e "$($taskRow.head)^{commit}"
    if ($LASTEXITCODE -ne 0) {
        & git -C $taskTarget fetch origin $taskRow.head
        if ($LASTEXITCODE -ne 0) { throw "Historico registrado nao recuperado: $($taskRow.projeto)" }
    }
    Write-Host "Historico disponivel: $($taskRow.projeto)"
}
Write-Host 'Concluido. Os clones dos projetos processados estao sem checkout para economizar espaco; nenhum JavaScript foi executado.'
