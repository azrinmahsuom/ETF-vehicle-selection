# notebooks/

Exploration and scratch work. Name notebooks `NN-short-description.ipynb` (e.g. `01-explore-prices.ipynb`).

Rules:
- Import from `src/analysis` rather than redefining functions.
- If a cell's logic is needed twice, move it into `src/analysis/` and add a test.
- Clear outputs of large dataframes before committing.
- Final results belong in `reports/`, not in a notebook.

Start JupyterLab with: `uv run jupyter lab`
