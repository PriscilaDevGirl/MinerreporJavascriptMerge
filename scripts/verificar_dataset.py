"""Confere integridade, escopo e contagens da publicacao, sem minerar projetos."""
from pathlib import Path
import csv
import hashlib
import json

root = Path(__file__).resolve().parents[1]


def rows(path, delimiter=','):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream, delimiter=delimiter))


manifest = rows(root / 'MANIFESTO_SHA256.csv')
for entry in manifest:
    file = root / entry['arquivo']
    if root.resolve() not in file.resolve().parents:
        raise ValueError('Caminho fora do repositorio')
    if hashlib.sha256(file.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Arquivo divergente: ' + entry['arquivo'])

projects = rows(root / 'dataset/projetos.csv')
names = {r['projeto'] for r in projects}
assert len(projects) == len(names) == 43
assert {p.name for p in (root / 'projetos').iterdir() if p.is_dir()} == names
samples = rows(root / 'dataset/project_cases.csv')
assert len(samples) == 10162
assert len({(r['project'],r['merge commit'],r['file path']) for r in samples}) == 10162
assert len({r['merge commit'] for r in samples}) == 3532
assert len({r['project'] for r in samples}) == 34
assert {r['project'] for r in samples} <= names
assert sum(int(r['amostras_validadas']) for r in projects) == 10162
assert sum(int(r['pares_brutos']) for r in projects) == 15952
assert sum(int(r['pares_excluidos']) for r in projects) == 5790
assert len(rows(root / 'dataset/exclusoes.csv')) == 5790
assert len(rows(root / 'dataset/selecao_projetos_processados.csv')) == 43
assert len(rows(root / 'dataset/projetos_com_amostras.csv')) == 34
summary = json.loads((root / 'dataset/resumo_coleta.json').read_text(encoding='utf-8'))
assert summary['processados'] == 43 and summary['nao_minerados'] == 25
assert summary['analise_OA_executada'] is False
assert summary['analise_dataflow_executada'] is False
print(f'OK: {len(manifest)} arquivos integros; somente os 43 projetos processados publicados.')
print('OK: 10.162 amostras unicas; 3.532 merges; 34 projetos com amostras; 9 sem amostras.')
