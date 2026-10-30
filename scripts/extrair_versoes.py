"""Recupera as quatro versoes das amostras de clones Git locais, sem executar JS."""
import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv', type=Path, required=True)
    parser.add_argument('--repositorios', type=Path, required=True)
    parser.add_argument('--saida', type=Path, required=True)
    parser.add_argument('--projeto', help='Identificador da pasta, por exemplo expressjs__express')
    parser.add_argument('--limite', type=int, help='Quantidade maxima a extrair nesta chamada')
    args = parser.parse_args()
    rows = list(csv.DictReader(args.csv.open(encoding='utf-8-sig')))
    if args.projeto:
        rows = [r for r in rows if r['project'] == args.projeto]
    if args.limite is not None:
        rows = rows[:args.limite]
    args.saida.mkdir(parents=True, exist_ok=True)
    results = []
    for row in rows:
        project = row['project']
        if '/' in project or '\\' in project or project in ('.', '..'):
            raise ValueError('Identificador de projeto invalido')
        source = args.repositorios / project
        identity = '\0'.join([project, row['merge commit'], row['file path']])
        identifier = hashlib.sha256(identity.encode()).hexdigest()
        target = args.saida / identifier
        if target.exists():
            raise FileExistsError(f'Destino ja existe: {target}; escolha outra pasta de saida')
        # Retrieve all four byte sequences before writing this sample.
        contents = {}
        for name, field in [('base', 'ancestor commit'), ('left', 'left parent commit'),
                            ('right', 'right parent commit'), ('merge', 'merge commit')]:
            ref = row[field]
            if len(ref) != 40 or any(c not in '0123456789abcdef' for c in ref):
                raise ValueError('SHA invalido')
            result = subprocess.run(['git', '-C', str(source), 'cat-file', 'blob',
                f'{ref}:{row["file path"]}'], capture_output=True)
            if result.returncode:
                raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
            contents[name] = result.stdout
        target.mkdir()
        metadata = dict(row, sample_id=identifier, original_name=PurePosixPath(row['file path']).name)
        metadata['sha256_versoes'] = {}
        for name, data in contents.items():
            (target / f'{name}.js').write_bytes(data)
            metadata['sha256_versoes'][name] = hashlib.sha256(data).hexdigest()
        (target / 'metadados.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
        results.append(metadata)
        print(f'Extraida {identifier[:12]} {project} {row["file path"]}', flush=True)
    print(f'Concluido: {len(results)} amostras. Nenhum codigo JavaScript foi executado.')


if __name__ == '__main__':
    main()
