# Other one-class detectors in the novelty channel (post-hoc)

Run after the confirmatory test of 25 October 2026. Not part of it. The locked `hybrid_v3.py` and `qkernel.py` are called unchanged (code fingerprint printed at start: hybrid_v3.py 30721b06ba80, qkernel.py aa1423c82892).

- `novelty_baselines_run.py` replaces the quantum kernel one-class SVM in the novelty channel with an RBF kernel one-class SVM, an isolation forest, a local outlier factor, a Mahalanobis distance and an autoencoder. All use the same benign reference flows, quantile transform, PCA and standardization. Decision rules are in the file header (written before the run). Ten seeds on CIC-UNSW-NB15. Copy the file next to `hybrid_v3.py` in `code/`.
  `python novelty_baselines_run.py --selftest`
  `python novelty_baselines_run.py --seeds 10 --out_dir <dir>`
- `novelty_baselines_report.txt` is the report of the ten-seed run (manuscript Section 4 and Table S22). Rule 1 was met: V3-MAX reproduced 0.163 (all types) and 0.388 (held-out types).
