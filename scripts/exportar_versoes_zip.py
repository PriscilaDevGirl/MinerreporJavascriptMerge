"""Exporta quatro blobs Git por amostra diretamente para ZIPs, sem executar JS.

O modo de planejamento mede os bytes antes da exportacao. Os ZIPs sao divididos
por projeto e tamanho descompactado, sem criar uma copia solta dos arquivos.
"""
import argparse
import collections
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import time
import zipfile

VERSIONS = [('base','ancestor commit'),('left','left parent commit'),
            ('right','right parent commit'),('merge','merge commit')]
LICENSE_NAMES = ['LICENSE','LICENSE.md','LICENSE.txt','LICENCE','LICENCE.md',
                 'LICENCE.txt','COPYING','COPYING.md','COPYING.txt','LICENSE-MIT',
                 'LICENSE-MIT.txt','UNLICENSE']


def csv_rows(path):
    with path.open(encoding='utf-8-sig',newline='') as stream:
        return list(csv.DictReader(stream))


def save_csv(path,fields,rows):
    with path.open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=fields,lineterminator='\n')
        writer.writeheader();writer.writerows(rows)


def batch_info(repo,refs):
    if any('\n' in ref or '\r' in ref for ref in refs):
        raise ValueError('Referencia com quebra de linha nao suportada')
    proc=subprocess.run(['git','-C',str(repo),'cat-file',
        '--batch-check=%(objectname) %(objecttype) %(objectsize)'],
        input=('\n'.join(refs)+'\n').encode('utf-8'),capture_output=True)
    if proc.returncode:raise RuntimeError(proc.stderr.decode('utf-8','replace'))
    lines=proc.stdout.decode('utf-8','replace').splitlines()
    if len(lines)!=len(refs):raise ValueError('Quantidade inesperada na resposta Git')
    result={}
    for ref,line in zip(refs,lines):
        parts=line.rsplit(' ',2)
        if len(parts)==3 and parts[1]=='blob':
            result[ref]={'blob':parts[0],'bytes':int(parts[2])}
        else:result[ref]=None
    return result


class BlobReader:
    def __init__(self,repo):
        self.proc=subprocess.Popen(['git','-C',str(repo),'cat-file','--batch'],
            stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL)

    def copy(self,ref,destination):
        self.proc.stdin.write((ref+'\n').encode('utf-8'));self.proc.stdin.flush()
        header=self.proc.stdout.readline().decode('utf-8','replace').strip().split()
        if len(header)!=3 or header[1]!='blob':raise ValueError('Blob indisponivel: '+ref)
        size=int(header[2]);remaining=size;sha256=hashlib.sha256()
        while remaining:
            chunk=self.proc.stdout.read(min(1024*1024,remaining))
            if not chunk:raise EOFError('Git encerrou antes de fornecer o blob inteiro')
            destination.write(chunk);sha256.update(chunk);remaining-=len(chunk)
        if self.proc.stdout.read(1)!=b'\n':raise ValueError('Delimitador Git inesperado')
        return {'blob':header[0],'bytes':size,'sha256':sha256.hexdigest()}

    def bytes(self,ref):
        destination=io.BytesIO();metadata=self.copy(ref,destination)
        return destination.getvalue(),metadata

    def close(self):
        self.proc.stdin.close();self.proc.stdout.close()
        if self.proc.wait(timeout=20):raise RuntimeError('Leitor Git terminou com erro')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--csv',type=Path,required=True)
    parser.add_argument('--repositorios',type=Path,required=True)
    parser.add_argument('--saida',type=Path,required=True)
    parser.add_argument('--planejar',action='store_true')
    parser.add_argument('--parte-mib',type=int,default=32)
    parser.add_argument('--minimo-livre-gib',type=float,default=2)
    args=parser.parse_args()
    if args.parte_mib<1:raise ValueError('Tamanho de parte invalido')
    args.saida.mkdir(parents=True,exist_ok=True)
    cases=csv_rows(args.csv)
    groups=collections.defaultdict(list)
    for case in cases:groups[case['project']].append(case)
    plan=[];details={};total_bytes=0
    for project,rows in sorted(groups.items()):
        if '/' in project or '\\' in project or project in ('.','..'):
            raise ValueError('Identificador de projeto invalido')
        refs=list(dict.fromkeys(f'{row[field]}:{row["file path"]}' for row in rows for _,field in VERSIONS))
        info=batch_info(args.repositorios/project,refs)
        if any(v is None for v in info.values()):raise ValueError('Versao ausente: '+project)
        sizes=[sum(info[f'{row[field]}:{row["file path"]}']['bytes'] for _,field in VERSIONS) for row in rows]
        size=sum(sizes);total_bytes+=size;details[project]=info
        plan.append({'project':project,'amostras':len(rows),'arquivos_versoes':4*len(rows),
                     'bytes_sem_compressao':size,'maior_amostra_bytes':max(sizes)})
        print(f'PLANO {project} amostras={len(rows)} MiB={size/1024**2:.2f}',flush=True)
    save_csv(args.saida/'PLANO_EXPORTACAO.csv',list(plan[0]),plan)
    total={'amostras':len(cases),'arquivos_versoes':len(cases)*4,'projetos_com_amostras':len(groups),
           'bytes_sem_compressao':total_bytes,'maior_amostra_bytes':max(r['maior_amostra_bytes'] for r in plan),
           'filtro_temporal':None,'codigo_javascript_executado':False}
    (args.saida/'PLANO_EXPORTACAO.json').write_text(json.dumps(total,indent=2),encoding='utf-8')
    print('TOTAL '+json.dumps(total),flush=True)
    if args.planejar:return
    if list(args.saida.glob('*.zip')):raise FileExistsError('Ja existem ZIPs no destino')
    if total['maior_amostra_bytes']>80*1024**2:
        raise ValueError('Uma amostra excede 80 MiB; revisar tamanho antes de exportar')
    archives=[];global_manifest=[];license_map=[];completed=0;started=time.monotonic()
    for project,rows in sorted(groups.items()):
        repo=args.repositorios/project
        reader=BlobReader(repo);part=None;part_path=None;part_number=0;part_bytes=0;part_samples=0
        def close_part():
            nonlocal part
            if part is None:return
            part.close()
            archives.append({'arquivo':part_path.name,'project':project,'amostras':part_samples,
                'bytes_zip':part_path.stat().st_size,
                'sha256':hashlib.sha256(part_path.read_bytes()).hexdigest()})
            part=None
        try:
            # Preserve root license files at every revision represented in the cases.
            revisions=sorted({row[field] for row in rows for _,field in VERSIONS})
            license_refs=[f'{sha}:{name}' for sha in revisions for name in LICENSE_NAMES]
            license_info=batch_info(repo,license_refs)
            license_blobs={}
            for ref,info in license_info.items():
                if info is None:continue
                sha,name=ref.split(':',1)
                license_blobs.setdefault((info['blob'],name),ref)
                license_map.append({'project':project,'revisao':sha,'arquivo_original':name,
                    'blob':info['blob'],'caminho_no_zip':'licencas/'+info['blob']+'/'+name})
            missing=[sha for sha in revisions if not any(license_info[f'{sha}:{name}'] is not None for name in LICENSE_NAMES)]
            license_payload={}
            for (blob,name),ref in license_blobs.items():
                data,_=reader.bytes(ref);license_payload['licencas/'+blob+'/'+name]=data
            project_license_map=[r for r in license_map if r['project']==project]
            license_json=json.dumps({'project':project,'revisoes':project_license_map,
                'revisoes_sem_licenca_encontrada_na_raiz':missing,
                'observacao':'Busca por nomes usuais na raiz; nao e parecer de licenciamento. Direitos dos projetos de origem preservados.'},ensure_ascii=False,indent=2).encode('utf-8')
            for row in rows:
                free=shutil.disk_usage(args.saida).free
                if free<args.minimo_livre_gib*1024**3:raise OSError('Limiar de espaco livre atingido; exportacao interrompida')
                size=sum(details[project][f'{row[field]}:{row["file path"]}']['bytes'] for _,field in VERSIONS)
                if part is None or (part_samples and part_bytes+size>args.parte_mib*1024**2):
                    close_part();part_number+=1;part_bytes=0;part_samples=0
                    part_path=args.saida/f'{project}_parte{part_number:03d}.zip'
                    part=zipfile.ZipFile(part_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True)
                    part.writestr('LICENCAS_POR_REVISAO.json',license_json)
                    for name,data in license_payload.items():part.writestr(name,data)
                sample_id=hashlib.sha256('\0'.join([project,row['merge commit'],row['file path']]).encode('utf-8')).hexdigest()
                metadata=dict(row,sample_id=sample_id,sha256_versoes={},blobs_git={},arquivo_zip=part_path.name)
                for version,field in VERSIONS:
                    ref=f'{row[field]}:{row["file path"]}';name=f'{sample_id}/{version}.js'
                    with part.open(name,'w') as destination:record=reader.copy(ref,destination)
                    assert record['blob']==details[project][ref]['blob']
                    assert record['bytes']==details[project][ref]['bytes']
                    metadata['sha256_versoes'][version]=record['sha256'];metadata['blobs_git'][version]=record['blob']
                    global_manifest.append({'project':project,'sample_id':sample_id,'versao':version,
                        'arquivo_zip':part_path.name,'caminho_no_zip':name,**record})
                part.writestr(f'{sample_id}/metadados.json',json.dumps(metadata,ensure_ascii=False,indent=2).encode('utf-8'))
                part_samples+=1;part_bytes+=size;completed+=1
                if completed%250==0:print(f'EXPORTADAS {completed}/{len(cases)}',flush=True)
            close_part()
            print(f'CONCLUIDO {project} amostras={len(rows)} partes={part_number} revisoes_sem_licenca_raiz={len(missing)}',flush=True)
        finally:
            if part is not None:part.close()
            reader.close()
    assert completed==len(cases) and len(global_manifest)==4*len(cases)
    save_csv(args.saida/'ARQUIVOS_DAS_VERSOES.csv',list(global_manifest[0]),global_manifest)
    save_csv(args.saida/'PACOTES.csv',list(archives[0]),archives)
    save_csv(args.saida/'LICENCAS_POR_REVISAO.csv',['project','revisao','arquivo_original','blob','caminho_no_zip'],license_map)
    total.update({'zip_files':len(archives),'bytes_zip':sum(r['bytes_zip'] for r in archives),
        'segundos_exportacao':round(time.monotonic()-started,2),'situacao':'exportado_aguarda_verificacao_integral'})
    (args.saida/'RESUMO_EXPORTACAO.json').write_text(json.dumps(total,indent=2),encoding='utf-8')
    print('FINAL '+json.dumps(total),flush=True)


if __name__=='__main__':main()
