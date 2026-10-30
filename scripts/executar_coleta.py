"""Run upstream MiningFramework collectors on local shared disposable clones.

No date filter. Freeze HEAD and supply all exactly-two-parent ancestors explicitly.
Only the injected project processor configuration differs from the upstream JS module.
"""
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RUNTIME = Path(os.environ.get('MINING_RUNTIME', r'C:\Mineraai\mining-runtime'))
FRAMEWORK = RUNTIME / 'miningframework'


def now():
    return datetime.now(timezone.utc).isoformat()


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def git(repo, *args, check=True):
    result = subprocess.run(['git', '-C', str(repo), *args], capture_output=True)
    if check and result.returncode:
        raise RuntimeError(result.stderr.decode('utf-8', 'replace')[:2000])
    return result


def csv_write(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def save_status(out, states):
    write_json(out / 'andamento.json', {'updated_utc': now(), 'projects': states})
    csv_write(out / 'andamento.csv', ['project', 'state', 'head', 'merges_input',
        'file_merge_pairs', 'elapsed_seconds', 'error'], states)


def audit(repo, directory, head, origin):
    raw = directory / 'saida_oficial/data/results.csv'
    records = list(csv.DictReader(raw.open(encoding='utf-8-sig'), delimiter=';')) if raw.exists() else []
    accepted, excluded, cache = [], [], {}
    for row in records:
        sha, file = row['merge commit'], row['file path']
        if sha not in cache:
            parents = git(repo, 'rev-list', '--parents', '-n', '1', sha).stdout.decode().split()[1:]
            bases = git(repo, 'merge-base', '--all', *parents).stdout.decode().split()
            cache[sha] = parents, bases
        parents, bases = cache[sha]
        reasons = []
        if len(parents) != 2:
            reasons.append('not_two_parents')
        if len(bases) != 1 or bases[0] in parents:
            reasons.append('nonunique_or_degenerate_base')
        if not reasons:
            base = bases[0]
            for side, parent in zip(['left', 'right'], parents):
                diff = git(repo, 'diff-tree', '--no-commit-id', '--name-status', '-r',
                           base, parent, '--', file).stdout.decode('utf-8', 'replace').splitlines()
                if len(diff) != 1 or diff[0].split('\t', 1)[0] != 'M':
                    reasons.append(side + '_status_not_M')
            if not file.endswith('.js'):
                reasons.append('not_javascript')
            for name, ref in zip(['base', 'left', 'right', 'merge'], [base, *parents, sha]):
                if git(repo, 'cat-file', '-e', f'{ref}:{file}', check=False).returncode:
                    reasons.append(name + '_file_missing')
        if reasons:
            excluded.append({'merge': sha, 'file': file, 'reason': '|'.join(reasons)})
        else:
            accepted.append({'project': repo.name, 'merge commit': sha,
                'ancestor commit': bases[0], 'left parent commit': parents[0],
                'right parent commit': parents[1], 'file path': file, 'repo url': origin})
    fields = ['project', 'merge commit', 'ancestor commit', 'left parent commit',
              'right parent commit', 'file path', 'repo url']
    csv_write(directory / 'project_cases.csv', fields, accepted)
    csv_write(directory / 'exclusoes.csv', ['merge', 'file', 'reason'], excluded)
    return {'raw_pairs': len(records), 'validated_pairs': len(accepted),
            'validated_merges': len({r['merge commit'] for r in accepted}),
            'excluded_pairs': len(excluded), 'frozen_head': head}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--run-name', required=True)
    ap.add_argument('--repo-root', type=Path, default=Path(r'C:\Mineraai\repositorios'))
    ap.add_argument('--project', help='Folder name, e.g. expressjs__express; omitted means all folders')
    ap.add_argument('--limit-merges', type=int, default=2147483647,
                    help='Pilot limit only; default exceeds any input size')
    args = ap.parse_args()
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', args.run_name):
        raise ValueError('Invalid run name')
    out = ROOT / 'resultados_locais' / args.run_name
    out.mkdir(parents=True, exist_ok=False)
    scratch = RUNTIME / ('coleta-' + args.run_name)
    scratch.mkdir(exist_ok=False)
    # Only a new configuration file is installed. Official filter/collectors are unchanged.
    injector_source = ROOT / 'ferramenta/LocalDynamicAnalysisJsModule.groovy'
    injector_target = FRAMEWORK / 'src/main/injectors/LocalDynamicAnalysisJsModule.groovy'
    if injector_target.exists() and injector_target.read_bytes() != injector_source.read_bytes():
        raise RuntimeError('Existing different local injector; refusing overwrite')
    if not injector_target.exists():
        shutil.copy2(injector_source, injector_target)
    env = os.environ.copy()
    env['GRADLE_USER_HOME'] = str(RUNTIME / 'gradle-cache')
    env['JAVA_HOME'] = os.environ.get('JAVA_HOME', r'C:\Program Files\Eclipse Adoptium\jdk-21.0.8.9-hotspot')
    env['TEMP'] = env['TMP'] = str(RUNTIME / 'tmp')
    env['JAVA_OPTS'] = '-Djava.io.tmpdir=' + str(RUNTIME / 'tmp').replace('\\', '/')
    env['PATH'] = r'C:\Program Files\Git\usr\bin;' + env['PATH']
    env['GIT_TERMINAL_PROMPT'] = '0'
    # All input objects must already exist. No remote credentials are needed.
    repos = sorted(p for p in args.repo_root.iterdir() if p.is_dir())
    if args.project:
        repos = [p for p in repos if p.name == args.project]
    if not repos:
        raise ValueError('No repository selected')
    # Begin with the previously checked Express, then process remaining names in order.
    repos.sort(key=lambda p: (p.name != 'expressjs__express', p.name.lower()))
    write_json(out / 'protocolo.json', {'started_utc': now(), 'date_filter': None,
        'history_scope': 'ancestors of frozen local HEAD, exactly two parents',
        'source_repositories': [str(p) for p in repos], 'random_seed': 1,
        'max_eligible_merges_per_project': args.limit_merges,
        'framework_commit': git(FRAMEWORK, 'rev-parse', 'HEAD').stdout.decode().strip(),
        'injector': 'injectors.LocalDynamicAnalysisJsModule',
        'configuration_change': 'omit remote GitHub existence processor for existing local clones',
        'official_filter': 'MutuallyModifiedFilesCommitFilter',
        'official_collectors': ['ModifiedFilesLinesPerFileCollector', 'StatisticsCollector'],
        'injector_sha256': hashlib.sha256(injector_source.read_bytes()).hexdigest(),
        'outputs': 'raw upstream CSV plus audited project_cases.csv; no OA execution',
        'scratch_directory': str(scratch)})
    # Preserve the exact runtime build adjustments and source status.
    (out / 'framework-build.patch').write_bytes(git(FRAMEWORK, 'diff', '--', 'build.gradle').stdout)
    states = []
    try:
        for repo in repos:
            started = time.monotonic()
            row = dict(project=repo.name, state='running', head='', merges_input=0,
                       file_merge_pairs=0, elapsed_seconds=0, error='')
            states.append(row)
            directory = out / repo.name
            directory.mkdir()
            work = scratch / repo.name
            work.mkdir()
            clone = work / 'clone'
            print('START ' + repo.name, flush=True)
            save_status(out, states)
            try:
                if shutil.disk_usage(args.repo_root).free < 4 * 1024**3:
                    raise RuntimeError('Less than 4 GiB free: collection stopped for disk space')
                head = git(repo, 'rev-parse', '--verify', 'HEAD').stdout.decode().strip()
                row['head'] = head
                origin = git(repo, 'remote', 'get-url', 'origin').stdout.decode().strip()
                # Do not save embedded credentials from a remote URL.
                origin = re.sub(r'(?<=://)[^/@]+@', '', origin)
                merge_lines = git(repo, 'log', '--min-parents=2', '--max-parents=2',
                                  '--format=%H %P', head).stdout.decode().splitlines()
                inputs = [dict(project=repo.name, merge=t[0], left=t[1], right=t[2])
                          for line in merge_lines if len(t := line.split()) == 3]
                row['merges_input'] = len(inputs)
                csv_write(directory / 'commits.csv', ['project', 'merge', 'left', 'right'], inputs)
                write_json(directory / 'origem.json', {'path': str(repo), 'head': head,
                    'repo_url': origin, 'date_filter': None, 'merges_input': len(inputs)})
                if not inputs:
                    row['state'] = 'no_two_parent_merges'
                    continue
                # Shared objects avoid another full download. Only this disposable clone
                # can be reset/checked out by MiningWorker; originals are never passed to it.
                result = subprocess.run(['git', 'clone', '--shared', '--no-checkout',
                    str(repo), str(clone)], capture_output=True)
                if result.returncode:
                    raise RuntimeError(result.stderr.decode('utf-8', 'replace'))
                git(clone, 'update-ref', 'refs/heads/mining-frozen', head)
                git(clone, 'symbolic-ref', 'HEAD', 'refs/heads/mining-frozen')
                csv_write(work / 'projects.csv', ['path', 'name'],
                          [dict(path=clone.as_posix(), name=repo.name)])
                shutil.copy2(directory / 'commits.csv', work / 'commits.csv')
                fw_args = ('--injector injectors.LocalDynamicAnalysisJsModule --extension .js '
                    '--keep-projects --threads 1 --random-seed 1 '
                    f'--max-commits-per-project {args.limit_merges} '
                    f'--project-commit-hashes-file {work.as_posix()}/commits.csv '
                    f'{work.as_posix()}/projects.csv {work.as_posix()}/output')
                command = [str(RUNTIME / 'gradle-runtime/bin/gradle.bat'), '--offline',
                    '--no-daemon', '--console=plain',
                    '-Dorg.gradle.jvmargs=-Xmx512m -Djava.io.tmpdir=' + (RUNTIME / 'tmp').as_posix(),
                    'run', '--args=' + fw_args]
                write_json(directory / 'comando.json', {'cwd': str(FRAMEWORK), 'argv': command})
                with (directory / 'framework.log').open('wb') as log:
                    proc = subprocess.run(command, cwd=FRAMEWORK, env=env,
                                          stdout=log, stderr=subprocess.STDOUT)
                if (work / 'output').exists():
                    shutil.copytree(work / 'output', directory / 'saida_oficial')
                log_text = (directory / 'framework.log').read_text(encoding='utf-8', errors='replace')
                if proc.returncode or '#### MINING FINISHED ####' not in log_text:
                    raise RuntimeError(f'Framework did not finish successfully; exit={proc.returncode}; see framework.log')
                summary = audit(repo, directory, head, origin)
                summary['framework_error_lines'] = log_text.count(' - ERROR')
                write_json(directory / 'resumo.json', summary)
                row['file_merge_pairs'] = summary['validated_pairs']
                row['state'] = 'done' if not summary['framework_error_lines'] else 'done_with_errors'
                # Verify original HEAD was not changed by the collection.
                if git(repo, 'rev-parse', 'HEAD').stdout.decode().strip() != head:
                    raise RuntimeError('Original HEAD changed externally during collection')
            except Exception as error:
                row['state'] = 'failed'
                row['error'] = str(error)[:2000]
                print('ERROR ' + repo.name + ': ' + str(error)[:300], flush=True)
            finally:
                row['elapsed_seconds'] = round(time.monotonic() - started, 2)
                save_status(out, states)
                # Delete only our disposable clone, after validating absolute boundaries.
                # Shared Git objects belong to the original and are never traversed here.
                if clone.exists() and row['state'] in ('done', 'done_with_errors'):
                    resolved = clone.resolve()
                    allowed = scratch.resolve()
                    if (resolved.name != 'clone' or resolved.parent != work.resolve()
                            or allowed not in resolved.parents or clone.is_symlink()):
                        raise RuntimeError('Unsafe scratch cleanup target')
                    def remove_readonly(func, path, exc):
                        import stat
                        os.chmod(path, stat.S_IWRITE)
                        func(path)
                    shutil.rmtree(resolved, onerror=remove_readonly)
                print('END ' + repo.name + ' ' + row['state'] +
                      ' pairs=' + str(row['file_merge_pairs']), flush=True)
            if row['state'] == 'failed':
                print('Stopping at first failed project; fix before continuing.', flush=True)
                break
    finally:
        write_json(out / 'resumo_lote.json', {'finished_utc': now(),
            'requested_projects': len(repos), 'processed_projects': len(states),
            'done_projects': sum(s['state'] in ('done', 'no_two_parent_merges') for s in states),
            'failed_projects': sum(s['state'] == 'failed' for s in states),
            'validated_file_merge_pairs': sum(s['file_merge_pairs'] for s in states),
            'date_filter': None, 'analysis_OA_run': False})
        print('OUTPUT ' + str(out), flush=True)


if __name__ == '__main__':
    main()
