# Hybrid Quantum–Wavelet–Neuromorphic IDS under Cross-Dataset Shift

Code, analysis plan and saved outputs for the article:

> H. Kamel. *A Hybrid Quantum–Wavelet–Neuromorphic Deep Learning Intrusion Detection System under Cross-Dataset Shift: A Pre-Specified Evaluation of What Transfers.* Manuscript under review, 2026.

Archived at Zenodo: https://doi.org/10.5281/zenodo.23842133 (all versions). Code release v1.0.1: https://doi.org/10.5281/zenodo.23842134. Per-seed scores (v2): https://doi.org/10.5281/zenodo.23842225.

## What is here

| Folder | Content |
|---|---|
| `code/` | All scripts in one folder, because they import each other. Model: `hybrid_v3.py` (the evaluated model, code fingerprint `30721b06ba80`) and `qkernel.py` (simulated 8-qubit IQP kernel). Preprocessing: `stage1_cicids2017_pipeline.py`, `ids2018.py`, `ts_2018.py`, `prep_unsw.py`, `harmonize_unsw.py`, `count_manifest.py`. Analysis: score extraction, metrics, event-level metrics, bootstrap intervals, seed-level Wilcoxon/Holm tests, audits, latency, and the scripts that build the result tables and figures (`make_results_tables.py`, `make_appendix_tables.py`, `make_figures.py`, `make_paper_figures.py`, `make_schematics.py`). `hybrid_v2.py` is the earlier model version described in Supplementary S3 |
| `analysis_plan/` | Analysis plan of the confirmatory test on CIC-UNSW-NB15, fixed on 25 October 2026 before the single confirmatory run |
| `results/` | All saved outputs as CSV/TXT/JSON (and rendered figures). Per-seed score files (`*.npz`) are in the Zenodo archive only |

## Reproducing the tables without retraining

The per-seed score files in the Zenodo archive (`per_seed_scores.zip`) contain the model scores of every test flow. Unzip them into the repository root so that `scores_within/`, `scores_cross/`, `scores_known/`, `unsw_primary/` and `unsw_raw/` sit next to `code/`. Run the scripts from inside `code/`. The analysis scripts then rebuild the tables from the saved scores. Run each script with `--help` to see its arguments.

| Article item | Saved output | Script |
|---|---|---|
| Table 4 (four-level ladder), Fig. 4 | `results/results_tables/` | `make_results_tables.py` |
| Table 5 (confirmatory tests) | `results/seed_stats/` | `seed_level_stats.py` |
| 95% intervals | `results/ci/` | `bootstrap_ci.py` |
| Table 7 (ablation) | `results/v31_ablation10/` | `hybrid_v3.py` |
| Table 8 (latency), energy | `results/efficiency_v3/` | `measure_v3.py`, `fast_novelty.py` |
| Fig. 6, Table S4 (event level) | `results/scores_cross/`, `results/unsw_primary/` (`event_*`) | `event_metrics.py` |
| Table S5 (benign reference sensitivity) | `results/sens_unsw/` | `benign_sensitivity.py` |
| Table S6 (attack-family naming) | `family_*` files | `family_stage2.py` |
| Table S7 (threshold metrics) | `results/results_tables/R12_*` | `derive_metrics.py`, `make_results_tables.py` |
| S6 (shift diagnostic), Fig. 7 | `results/diagnose/` | `diagnose_shift.py` |
| S7 (audits) | `results/audit_target/`, `results/manifest/audit/` | `target_audit.py`, `portscan_audit.py` |
| Tables S8–S11 | `results/manifest/appendix/` | `count_manifest.py`, `make_appendix_tables.py` |

Note: the confirmatory test on CIC-UNSW-NB15 was run once, with the code and plan above. Running the scripts again reproduces that analysis; it is not a new confirmatory test.

## Re-running the full pipeline

1. Download the three datasets (see `DATA.md`) and check their SHA256 hashes.
2. Install the environment: `pip install -r requirements.txt` (Python 3.13).
3. Run the preprocessing scripts, then `hybrid_v3.py` for each level and seed, then the analysis scripts.

Raw and preprocessed data are not redistributed here.

## Environment

Python 3.13 on Windows. CPU, memory and package details of the reported runs are in `results/efficiency_v3/environment.csv`. `qiskit-ibm-runtime` is needed only for the optional hardware-noise check (`qnoise_check.py`), which requires your own IBM Quantum account; no credentials are stored in this repository.

## License

Code: MIT (see `LICENSE`). Saved results: CC BY 4.0.

## Citation

See `CITATION.cff`. Please cite the article and the Zenodo archive.

## Note on paths

Scripts and logs refer to `D:/revised model`, the folder used on the author's machine. Pass your own locations with the command-line arguments (for example `--s17_dir`, `--target_cache`, `--out_dir`).

## Contact

Hamed Kamel, Islamic Azad University, North Tehran Branch — ORCID [0009-0007-6096-1574](https://orcid.org/0009-0007-6096-1574)

## Exploratory context audit (run after the confirmatory test)

The folder exploratory_context_audit/ holds the scripts and the report of an exploratory test that rebuilds the service-load context without attack traffic (ten seeds). The locked hybrid_v3.py is called unchanged. This analysis is not part of the confirmatory test.
