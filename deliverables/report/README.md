# Current technical report

- `main.tex`: latest user-supplied IEEE source, with the generated project name replaced by formal wording. No abstract; literature survey, methodology, results, conclusion and clickable references are included.
- `image.png`, `image2.png`, `image3.png`, `image4.png`: main k=1/2/3 results, classifier confusion matrices, exploratory sensitivity and all-four-capture benign starts.
- `wokwi.png`: retained successful-run simulation screenshot. Later screenshot-session evidence is under `../../docs/evidence/report_demo/`.
- `plots.ipynb`: runnable Kaggle/Jupyter cells; display only, default Matplotlib styling, no image saving.
- `tables.tex` and `architecture_figures.tex`: reusable snippets extracted from the latest source.
- `FINAL_REPORT_BRIEF.md`: full numerical evidence and claim boundaries. `REPORT_CONTENT.md` remains an earlier narrative draft.

All five figure filenames used by the LaTeX source are included. TeX environment nesting, citation keys and image references were checked. PDF compilation/pagination remains unverified because the built-in compiler could not download its required bundle. The supplied source's other formatting and labels are preserved.

Main capture-1 results: k=1/2/3 benign starts 66/3/4; benign seconds 164/32/26; observed runs 84/84,83/84,81/84; conditional mean delays 1.068/3.172/5.091 seconds. Capture-4 benign starts are zero for all three settings; coverage and delay costs remain reported.
