"""Export the editable report prose and measured tables from its LaTeX source."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'deliverables/report'


def main():
    source = (OUT / 'main.tex').read_text()
    keys = re.findall(r'\\bibitem\{([^}]+)\}', source)
    numbers = {key: str(i + 1) for i, key in enumerate(keys)}
    text = source.split(r'\maketitle', 1)[1].split(r'\end{document}', 1)[0]
    text = re.sub(r'\\begin\{abstract\}', '## Abstract\n', text)
    text = text.replace(r'\end{abstract}', '')
    text = text.replace(r'\begin{IEEEkeywords}', '**Keywords:** ').replace(r'\end{IEEEkeywords}', '')
    text = re.sub(r'\\section\{([^}]+)\}', r'## \1', text)
    text = re.sub(r'\\subsection\{([^}]+)\}', r'### \1', text)
    text = re.sub(r'\\cite\{([^}]+)\}', lambda m: '[' + ', '.join(numbers[k] for k in m[1].split(',')) + ']', text)
    # Labels are replaced by readable captions rather than stale LaTeX numbering.
    labels = {}
    for block in re.findall(r'\\begin\{table\*?\}.*?\\end\{table\*?\}', text, re.S):
        caption = re.search(r'\\caption\{([^}]+)\}', block)[1]
        label = re.search(r'\\label\{([^}]+)\}', block)
        if label:
            labels[label[1]] = caption.split('.')[0]
        body = block.split(r'\toprule', 1)[1].split(r'\bottomrule', 1)[0]
        body = body.replace(r'\midrule', '')
        rows = [row.strip() for row in body.split('\\\\') if row.strip()]
        lines = ['**' + caption + '**', '']
        for i, row in enumerate(rows):
            cells = [cell.strip() for cell in row.split('&')]
            lines.append('| ' + ' | '.join(cells) + ' |')
            if i == 0:
                lines.append('| ' + ' | '.join(['---'] * len(cells)) + ' |')
        text = text.replace(block, '\n'.join(lines) + '\n')
    for block in re.findall(r'\\begin\{figure\*?\}.*?\\end\{figure\*?\}', text, re.S):
        caption = re.search(r'\\caption\{([^}]+)\}', block)[1]
        label = re.search(r'\\label\{([^}]+)\}', block)
        if label:
            labels[label[1]] = caption.split('.')[0]
        image = re.search(r'\\includegraphics\[[^]]+\]\{([^}]+)\}', block)
        if image:
            replacement = f'![{caption}](../../docs/research/{image[1]})\n\n{caption}'
        else:
            replacement = ('**System flow:** original captures → host feature extraction and RF training '
                           '→ validation-only confirmation selection → verified C++ export → Wokwi ESP32 '
                           'inference and confirmation → LEDs/buzzer and independent MQTT subscriber.\n\n' + caption)
        text = text.replace(block, replacement)
    text = re.sub(r'\\ref\{([^}]+)\}', lambda m: labels.get(m[1], m[1]), text)
    text = re.sub(r'\\label\{[^}]+\}', '', text)
    text = text.replace(r'\begin{equation}', '\n$$\n').replace(r'\end{equation}', '\n$$\n')
    text = re.sub(r'\\begin\{thebibliography\}\{[^}]+\}', '## References\n', text)
    text = text.replace(r'\end{thebibliography}', '')
    text = re.sub(r'\\bibitem\{([^}]+)\}', lambda m: numbers[m[1]] + '.', text)
    for cmd, mark in [('emph', '*'), ('textbf', '**'), ('texttt', '`')]:
        text = re.sub(r'\\' + cmd + r'\{([^}]+)\}', lambda m: mark + m[1] + mark, text)
    text = re.sub(r'\\url\{([^}]+)\}', r'<\1>', text)
    text = text.replace('~', ' ').replace(r'\%', '%').replace(r'\_', '_').replace(r'\&', '&')
    # Keep Markdown table delimiters and mathematical minus signs intact.
    text = text.replace('``', '“').replace("''", '”')
    text = re.sub(r'(?<!-)--(?!-)', '–', text)
    # Make reference DOIs directly usable without changing their literal identifiers.
    text = re.sub(r'doi:([^\s]+)', lambda m: '[doi:' + m[1].rstrip('.') + '](https://doi.org/' + m[1].rstrip('.') + ')' + ('.' if m[1].endswith('.') else ''), text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()
    text = re.sub(r'Table [A-Z][^.\n]+? (summarizes|gives|compares)', r'The table below \1', text)
    text = text.replace('Table Exploratory SlowITe F1 by feature set and window duration and Fig. Complete prespecified sensitivity grid retain', 'The sensitivity table and figure below retain')
    title = re.search(r'\\title\{([^}]+)\}', source)[1]
    preface = ('# ' + title + '\n\n'
               '*Editable report content. Adapt the wording, author details and section lengths to your course template. '
               'Results below come from the completed repository experiments; numerical limitations are retained.*\n\n'
               'Authors: Ayati Rauthan, Ireshi Rawat and Pranav Tawakley.\n\n')
    appendix = ('\n\n## Supporting reproducible results\n\n'
               '[Complete measured tables](../../docs/research/RESULTS.md) · '
               '[Alarm audit CSV](../../docs/research/alarm_audit.csv) · '
               '[All selected policy parameters and run misses](../../docs/research/comparisons.json) · '
               '[External compatibility and results](../../docs/research/external_results.json) · '
               '[Recorded benign workload results](../../docs/research/benign_stress_results.json).\n\n'
               'The alarm audit also retains median and 95th-percentile conditional delay, benign exposure, '
               'new-onset coverage, excluded starts and all tested fold results. Use those saved values if '
               'expanding the tables; do not reconstruct missing values from rounded means.\n')
    (OUT / 'REPORT_CONTENT.md').write_text('\n'.join(line.rstrip() for line in (preface + text + appendix).splitlines()) + '\n')
    print('Exported:', OUT / 'REPORT_CONTENT.md')


if __name__ == '__main__':
    main()
