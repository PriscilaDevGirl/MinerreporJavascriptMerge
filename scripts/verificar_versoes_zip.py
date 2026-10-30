"""Verifica todos os bytes exportados e sua correspondencia com as amostras."""
import argparse
import collections
import csv
import hashlib
import json
from pathlib import Path
import zipfile

def rows(path):
    with path.open(encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pasta',type=Path,required=True)
    parser.add_argument('--csv',type=Path,required=True)
    args=parser.parse_args()
    cases=rows(args.csv)
    expected={hashlib.sha256('\0'.join([r['project'],r['merge commit'],r['file path']]).encode()).hexdigest():r for r in cases}
    assert len(expected)==len(cases)
    manifest=rows(args.pasta/'ARQUIVOS_DAS_VERSOES.csv')
    packages=rows(args.pasta/'PACOTES.csv')
    groups=collections.defaultdict(list)
    for row in manifest:groups[row['arquivo_zip']].append(row)
    seen=collections.defaultdict(set)
    total_bytes=0
    for package in packages:
        path=args.pasta/package['arquivo']
        assert path.stat().st_size==int(package['bytes_zip'])
        assert hashlib.sha256(path.read_bytes()).hexdigest()==package['sha256']
        with zipfile.ZipFile(path) as archive:
            names=archive.namelist()
            assert len(names)==len(set(names))
            license_info=json.loads(archive.read('LICENCAS_POR_REVISAO.json'))
            for entry in license_info['revisoes']:
                data=archive.read(entry['caminho_no_zip'])
                assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['blob']
            for row in groups[path.name]:
                sid=row['sample_id'];version=row['versao']
                assert sid in expected and version not in seen[sid]
                assert version in {'base','left','right','merge'}
                assert row['project']==expected[sid]['project']
                assert row['caminho_no_zip']==sid+'/'+version+'.js'
                data=archive.read(row['caminho_no_zip'])
                assert len(data)==int(row['bytes'])
                assert hashlib.sha256(data).hexdigest()==row['sha256']
                assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==row['blob']
                metadata=json.loads(archive.read(sid+'/metadados.json'))
                for key,value in expected[sid].items():assert metadata[key]==value
                assert metadata['sha256_versoes'][version]==row['sha256']
                assert metadata['blobs_git'][version]==row['blob']
                seen[sid].add(version);total_bytes+=len(data)
        print('VERIFICADO '+path.name,flush=True)
    assert set(seen)==set(expected)
    assert all(versions=={'base','left','right','merge'} for versions in seen.values())
    assert len(manifest)==4*len(cases)
    report={'situacao':'verificacao_integral_aprovada','amostras':len(cases),
            'arquivos_versoes':len(manifest),'pacotes':len(packages),
            'bytes_versoes_verificados':total_bytes,'verificacoes':['SHA256 dos pacotes',
            'CRC durante leitura ZIP','SHA256 e blob Git de cada versao','metadados e quatro versoes por amostra',
            'blobs das licencas incluidas'],'analise_OA_executada':False}
    (args.pasta/'VERIFICACAO_INTEGRAL.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False),flush=True)

if __name__=='__main__':main()
