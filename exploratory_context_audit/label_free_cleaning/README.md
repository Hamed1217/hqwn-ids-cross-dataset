# Label-free cleaning check (exploratory)

The cleaning rule of the paper removes every feature vector that appears with more than one label,
which uses target labels. This check keeps one copy (the first in file order) of every feature vector
and removes nothing because of a label conflict. Exploratory; run after the confirmatory test.

Steps (see step*_log.txt):
1. python prep_unsw_labelfree.py --csv <CICFlowMeter_out.csv> --out unsw_sample_v1_labelfree.npz
2. python harmonize_unsw.py --inp unsw_sample_v1_labelfree.npz --out unsw_sample_v1h_labelfree.npz
3. python ctx_clean_run.py --variants base --seeds 10 --cache unsw_sample_v1h_labelfree.npz --out_dir ctx_labelfree_unsw10

Sample: 252,398 flows (original rule: 252,028). sha256 raw cache 4d108be85e1cc425, harmonised cache 845253e90d83a2e0.
Code fingerprint: hybrid_v3.py 30721b06ba80, qkernel.py aa1423c82892 (locked code, unchanged).

Result (ten seeds, recall at nominal FPR 1%, V3-MAX / V3-SUP / TREE):
- all types:        0.157 / 0.023 / 0.026   (original rule 0.163 / 0.023 / 0.027)
- held-out types:   0.347 / 0.018 / 0.021   (original rule 0.388 / 0.018 / 0.021)
V3-MAX > V3-SUP in 10/10 seeds. Reconnaissance (V3-MAX): 0.598 (original 0.698).
Reported as Table S17 of the manuscript.
