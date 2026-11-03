# Exploratory input audit of the novelty channel (post-hoc)

Run after the confirmatory test of 25 October 2026. Not part of it. The locked `hybrid_v3.py` is called unchanged.

- `load_only_run.py` refits the benign-reference novelty channel with (i) the full input, (ii) the six load-summary numbers only, (iii) the flow features only. Decision rules were written in the file header before the run (3 November 2026). Ten seeds on CIC-UNSW-NB15.
  `python load_only_run.py --seeds 10 --out_dir <dir>`
- `load_only_report.txt` is the report of the ten-seed run (manuscript Section 4.5 and Table S19).
- `no_recon.py` recomputes the macro recall without Reconnaissance from the saved `v3_results.csv` (no model is rerun; manuscript Table S18).
  `python no_recon.py --csv <path>/v3_results.csv --out_dir no_recon_out`
