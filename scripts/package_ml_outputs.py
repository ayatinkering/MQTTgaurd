"""Package one generated ML/firmware handoff with source and artifact provenance."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]


def package(output):
    required = [
        'requirements.lock', 'scripts/train_pipeline.py',
        'reports/experiment/model.joblib', 'reports/experiment/primary_RF.npz',
        'docs/results/manifest.json', 'docs/results/classification_metrics.csv',
        'docs/results/persistence_metrics.csv', 'docs/results/classification_metrics.png',
        'firmware/wokwi/sketch.ino', 'firmware/wokwi/build.json',
    ]
    for relative in required:
        if not (ROOT / relative).is_file():
            raise FileNotFoundError(f'Run training, publishing and bundling first: {relative}')
    selected = set()
    for folder, suffixes in [
        ('firmware', {'.h', '.ino', '.json', '.txt'}),
        ('docs/results', {'.json', '.csv', '.md', '.png'}),
        ('docs/research', {'.json', '.csv', '.md', '.png'}),
        ('deliverables/report', {'.md', '.tex', '.png'}),
        ('scripts', {'.py'}),
        ('notebooks', {'.ipynb'}),
        ('reports/experiment', {'.joblib', '.npz', '.csv', '.json'}),
    ]:
        selected.update(p for p in (ROOT / folder).rglob('*')
                        if p.is_file() and p.suffix in suffixes
                        and '__pycache__' not in p.parts)
    for name in ['requirements.lock', 'README.md', 'docs/COLAB.md',
                 'docs/METHODOLOGY.md', 'docs/IMPLEMENTATION.md',
                 'docs/DATASET_REVIEW.md', 'docs/REPORT_REFERENCES.md',
                 'docs/RESEARCH_FINDINGS.md', 'docs/EXTENDED_PROTOCOL.md',
                 'docs/EXTERNAL_PROTOCOL_AMENDMENT.md',
                 'docs/evidence/benign_workloads.pcap.gz',
                 'docs/evidence/benign_workload_sessions.json']:
        selected.add(ROOT / name)
    selected = sorted(selected)
    # Snapshot bytes once: archive and hashes describe exactly the same content.
    contents = {str(p.relative_to(ROOT)): p.read_bytes() for p in selected}
    experiment = json.loads(contents['docs/results/manifest.json'])
    metadata = {
        'source_commit': subprocess.check_output(
            ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
        'working_tree_status': subprocess.check_output(
            ['git', 'status', '--porcelain'], cwd=ROOT, text=True).splitlines(),
        'dataset_sha256': experiment['dataset_sha256'],
        'training_python': experiment['python'],
        'training_sklearn': experiment['sklearn'],
        'firmware_build': json.loads(contents['firmware/wokwi/build.json']),
        'artifact_sha256': {name: hashlib.sha256(data).hexdigest()
                            for name, data in contents.items()},
        'notes': [
            'Source commit identifies the checkout; generated artifacts may differ from that commit.',
            'Working-tree status and per-file hashes preserve those differences.',
            'Hashes cover every archive member except this manifest itself.',
            'Bundling does not deploy or verify changed firmware in online Wokwi.',
        ],
    }
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, 'w', ZIP_DEFLATED) as archive:
        for name, data in contents.items():
            archive.writestr(name, data)
        archive.writestr('handoff_manifest.json', json.dumps(metadata, indent=2) + '\n')
    print(f'Packaged {len(contents)} artifacts: {output}')
    print(f'Source commit: {metadata["source_commit"]}')
    return output


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path,
                        default=ROOT / 'reports/MQTTGuard_ML_outputs.zip')
    package(parser.parse_args().output)
