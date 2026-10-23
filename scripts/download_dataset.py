"""Download official unscaled MQTTEEB-D files and verify publisher SHA-256 hashes."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def fetch(url, destination):
    subprocess.run(["curl", "-L", "--fail", "--retry", "2", "--max-time", "180",
                    "--silent", "--show-error", url, "-o", str(destination)], check=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=Path('data/raw'))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    url = 'https://data.mendeley.com/public-api/datasets/jfttfjn6tr'
    metadata_path = args.output / "publisher_metadata.json"
    fetch(url, metadata_path)
    metadata = json.loads(metadata_path.read_text())
    if metadata['version'] != 2:
        raise SystemExit('Publisher version changed; review metadata before downloading.')
    selected = []
    for item in metadata['files']:
        name = item['filename']
        if not (name == 'MQTTEEB-D_cleaned_data.csv' or '_dataset_loop_' in name
                or name.endswith('.json') or name == 'README.txt'):
            continue
        if Path(name).name != name:
            raise ValueError('Unsafe publisher filename')
        # Readmes share names across folders; retain all with stable publisher IDs.
        local_name = f"README_{item['id']}.txt" if name == 'README.txt' else name
        destination = args.output / local_name
        details = item['content_details']
        expected = details['sha256_hash']
        if not destination.exists() or hashlib.sha256(destination.read_bytes()).hexdigest() != expected:
            temporary = destination.with_suffix(destination.suffix + '.part')
            fetch(details['download_url'], temporary)
            if hashlib.sha256(temporary.read_bytes()).hexdigest() != expected:
                raise ValueError(f'Checksum mismatch: {name}; partial file retained')
            temporary.replace(destination)
        print(f'Verified {local_name} ({destination.stat().st_size:,} bytes)', flush=True)
        selected.append({'filename': local_name, 'publisher_filename': name,
                         'id': item['id'], 'sha256': expected,
                         'bytes': destination.stat().st_size, 'url': details['download_url']})
    manifest = {'dataset': metadata['name'], 'version': metadata['version'],
                'doi': '10.17632/jfttfjn6tr.2',
                'source': 'https://data.mendeley.com/datasets/jfttfjn6tr/2',
                'license': metadata['data_licence'], 'files': selected}
    (args.output / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
