# Appendix tables (generated 2026-10-30 14:29 by make_appendix_tables.py)

### A1 Run registry

| folder | script | protocol | target | scenarios | seeds | seed_range | configs | types | rows | hybrid_v3 | qkernel | max_train | scores_saved | analysis_files | date |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cross_out | cross_dataset | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | HistGB,IsolationForest,XGBoost | 14 | 210 |  |  |  |  |  | 2026-10-23 12:10 |
| cross_out2 | cross_dataset | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | HistGB,IF-local2018,IsolationForest,XGBoost | 14 | 576 |  |  |  |  |  | 2026-10-23 13:03 |
| cross_out3 | cross_dataset | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | FUSE-HistGB,FUSE-XGBoost,FUSE-all,HistGB,IF-local2018,XGBoost | 14 | 936 |  |  |  |  |  | 2026-10-23 16:12 |
| hybrid_out | hybrid_v2 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | FLOW-MLP,FULL,FULL-SHUF,SEQ-GRU | 14 | 312 |  |  |  |  |  | 2026-10-23 17:52 |
| hybrid21_ablation | hybrid_v2 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | H21-FULL,H21-QD,H21-noA,H21-noQ,H21-noS,H21-noW | 14 | 468 |  |  |  |  |  | 2026-10-23 22:12 |
| hybrid21_controls | hybrid_v2 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | H21-FLOW,H21-GRU,H21-SHUF,TREE | 14 | 312 |  |  |  |  |  | 2026-10-23 23:44 |
| v3_out | hybrid_v3 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | Q-IQP,Q-RBF,TREE,V3-DENSE,V3-FULL,V3-SUP | 14 | 468 | 6ea9187ec0fc | aa1423c82892 | 30,000 |  |  | 2026-10-24 09:26 |
| v31_max | hybrid_v3 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | TREE,V3-MAX,V3-MAX-RBF,V3-SUP | 14 | 312 | c7cccb69f8f7 | aa1423c82892 | 30,000 |  |  | 2026-10-24 10:43 |
| v31_ablation | hybrid_v3 | cross | CSE-CIC-IDS2018 | known | 3 | 0-2 | TREE,V3-SUP,V3-SUP-DENSE,V3-SUP-NOA,V3-SUP-NOALIGN,V3-SUP-NOW,V3-SUP-SHUF | 14 | 294 | c7cccb69f8f7 | aa1423c82892 | 30,000 |  |  | 2026-10-24 11:08 |
| v32_max2 | hybrid_v3 | cross | CSE-CIC-IDS2018 | known+loo | 3 | 0-2 | TREE,V3-MAX2,V3-MAX2-RBF,V3-SUP | 14 | 312 | 125fa7b7ec1f | aa1423c82892 | 30,000 |  |  | 2026-10-24 13:08 |
| v32_tt | hybrid_v3 | cross | CSE-CIC-IDS2018 | known | 3 | 0-2 | TREE,V3-SUP,V3-SUP-LR,V3-SUP-TT | 14 | 168 | 125fa7b7ec1f | aa1423c82892 | 30,000 |  |  | 2026-10-24 13:31 |
| v31_ablation10 | hybrid_v3 | cross | CSE-CIC-IDS2018 | known | 10 | 0-9 | TREE,V3-SUP,V3-SUP-LR,V3-SUP-NOA,V3-SUP-NOALIGN,V3-SUP-NOW,V3-SUP-SHUF,V3-SUP-TT | 14 | 1,120 | 125fa7b7ec1f | aa1423c82892 | 30,000 |  |  | 2026-10-24 15:59 |
| v33_ens | hybrid_v3 | cross | CSE-CIC-IDS2018 | known | 10 | 0-9 | TREE,TREE-ENS5,V3-SUP,V3-SUP-ENS5 | 14 | 560 | 1dc8da5fe57d | aa1423c82892 | 30,000 |  |  | 2026-10-24 21:06 |
| v31_within | hybrid_v3 | within | CIC-IDS2017 | known+loo | 3 | 0-2 | TREE,V3-MAX,V3-MAX-RBF,V3-SUP,V3-SUP-DENSE,V3-SUP-TT | 14 | 432 | 30721b06ba80 | aa1423c82892 | 30,000 |  | metrics_overall.csv | 2026-10-25 00:06 |
| v33_within10 | hybrid_v3 | within | CIC-IDS2017 | loo | 10 | 0-9 | TREE,V3-MAX,V3-MAX-RBF,V3-SUP,V3-SUP-DENSE | 10 | 500 | 30721b06ba80 | aa1423c82892 | 30,000 |  | metrics_overall.csv | 2026-10-25 04:19 |
| v33_cross10 | hybrid_v3 | cross | CSE-CIC-IDS2018 | known+loo | 10 | 0-9 | TREE,V3-MAX,V3-MAX-RBF,V3-SUP,V3-SUP-DENSE | 14 | 1,300 | 30721b06ba80 | aa1423c82892 | 30,000 |  | metrics_overall.csv | 2026-10-25 14:24 |
| scores_known | dump_scores | cross | CSE-CIC-IDS2018 | known | 10 | 0-9 | TREE,V3-SUP | 14 | 280 |  |  |  | yes | matched_fpr_per_type.csv | 2026-10-25 18:56 |
| unsw_primary | dump_scores | cross | CIC-UNSW-NB15 | known+loo | 10 | 0-9 | TREE,V3-MAX,V3-MAX-RBF,V3-SUP,V3-SUP-DENSE,V3-SUP-NOA | 9 | 660 |  |  |  | yes | matched_fpr_per_type.csv,metrics_overall.csv,event_report.txt,family_metrics.csv | 2026-10-25 21:07 |
| unsw_raw | dump_scores | cross | CIC-UNSW-NB15 | known+loo | 10 | 0-9 | TREE,V3-SUP | 9 | 220 |  |  |  | yes |  | 2026-10-25 22:00 |
| scores_cross | dump_scores | cross | CSE-CIC-IDS2018 | known+loo | 10 | 0-9 | TREE,V3-SUP | 14 | 520 |  |  |  | yes | event_report.txt,family_metrics.csv | 2026-10-26 01:43 |
| scores_within | dump_scores | within | CIC-IDS2017 | known | 10 | 0-9 | TREE,V3-SUP | 14 | 280 |  |  |  | yes | family_metrics.csv | 2026-10-26 08:04 |
| sens_smoke\base | benign_sensitivity (base) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:51 |
| sens_smoke\size25 | benign_sensitivity (size25) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:52 |
| sens_smoke\time | benign_sensitivity (time) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:52 |
| sens_smoke\size10 | benign_sensitivity (size10) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:52 |
| sens_smoke\contam5 | benign_sensitivity (contam5) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:53 |
| sens_smoke\contam1 | benign_sensitivity (contam1) | cross | CSE-CIC-IDS2018 | known+loo | 1 | 0-0 | TREE,V3-MAX,V3-SUP | 4 | 21 |  |  |  |  |  | 2026-10-26 14:53 |
| sens_unsw\base | benign_sensitivity (base) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 15:23 |
| sens_unsw\time | benign_sensitivity (time) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 15:51 |
| sens_unsw\size25 | benign_sensitivity (size25) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 16:18 |
| sens_unsw\size10 | benign_sensitivity (size10) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 16:45 |
| sens_unsw\contam1 | benign_sensitivity (contam1) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 17:13 |
| sens_unsw\contam5 | benign_sensitivity (contam5) | cross | CIC-UNSW-NB15 | known+loo | 5 | 0-4 | TREE,V3-MAX,V3-SUP | 9 | 165 |  |  |  |  |  | 2026-10-26 17:41 |

### A2 CIC-IDS2017 per label and split

| label | raw | after_cleaning | train | validation | test | held_out_in_L2 | tiny_in_test |
|---|---|---|---|---|---|---|---|
| BENIGN | 2,273,097 | 1,896,807 | 1,138,596 | 375,920 | 382,291 |  |  |
| DoS Hulk | 231,073 | 172,713 | 107,647 | 36,901 | 28,165 | yes |  |
| DDoS | 128,027 | 128,011 | 80,176 | 20,501 | 27,334 | yes |  |
| DoS GoldenEye | 10,293 | 10,286 | 6,012 | 1,453 | 2,821 | yes |  |
| FTP-Patator | 7,938 | 5,931 | 3,444 | 1,210 | 1,277 | yes |  |
| DoS slowloris | 5,796 | 5,383 | 3,348 | 1,109 | 926 | yes |  |
| DoS Slowhttptest | 5,499 | 5,228 | 2,155 | 692 | 2,381 | yes |  |
| SSH-Patator | 5,897 | 3,219 | 1,895 | 653 | 671 | yes |  |
| PortScan | 158,930 | 1,850 | 1,211 | 457 | 182 | yes |  |
| Web Attack - Brute Force | 1,507 | 1,470 | 915 | 246 | 309 | yes |  |
| Bot | 1,966 | 1,412 | 825 | 241 | 346 | yes |  |
| Web Attack - XSS | 652 | 652 | 401 | 134 | 117 |  |  |
| Infiltration | 36 | 36 | 19 | 8 | 9 |  | yes |
| Web Attack - Sql Injection | 21 | 21 | 8 | 8 | 5 |  | yes |
| Heartbleed | 11 | 11 | 7 | 2 | 2 |  | yes |
| TOTAL | 2,830,743 | 2,233,030 | 1,346,659 | 439,535 | 446,836 |  |  |

### A3 CSE-CIC-IDS2018 sample (benign thirds 86,893 / 86,893 / 86,895)

| type | raw_dataset | cleaned_sample | counterpart_2017_(L4) | tiny |
|---|---|---|---|---|
| Benign | 13,484,708 | 260,681 | benign |  |
| DoS attacks-GoldenEye | 41,508 | 20,014 | DoS GoldenEye |  |
| DDoS attacks-LOIC-HTTP | 576,191 | 19,875 | DDoS |  |
| DoS attacks-Hulk | 461,912 | 15,343 | DoS Hulk |  |
| Infilteration | 161,934 | 14,659 | Infiltration |  |
| DDOS attack-HOIC | 686,012 | 14,441 | none (L3 only) |  |
| Bot | 286,191 | 10,677 | Bot |  |
| SSH-Bruteforce | 187,589 | 10,194 | SSH-Patator |  |
| DoS attacks-Slowloris | 10,990 | 9,866 | DoS slowloris |  |
| DDOS attack-LOIC-UDP | 1,730 | 1,730 | none (L3 only) |  |
| Brute Force -Web | 611 | 550 | Web Attack - Brute Force |  |
| Brute Force -XSS | 230 | 227 | Web Attack - XSS |  |
| SQL Injection | 87 | 77 | Web Attack - Sql Injection |  |
| DoS attacks-SlowHTTPTest | 139,890 | 36 | DoS Slowhttptest | yes |
| FTP-BruteForce | 193,360 | 31 | FTP-Patator | yes |
| TOTAL | 16,232,943 | 378,401 |  |  |

### A4 CIC-UNSW-NB15 sample (benign thirds 63,633 / 63,633 / 63,635)

| type | raw_dataset | cleaned_sample | counterpart_2017_(L4) | tiny |
|---|---|---|---|---|
| Benign | 3,450,658 | 190,901 | benign |  |
| Exploits | 30,951 | 19,924 | none (L3 only) |  |
| Fuzzers | 29,613 | 17,713 | none (L3 only) |  |
| Reconnaissance | 16,735 | 11,993 | PortScan |  |
| Generic | 4,632 | 4,401 | none (L3 only) |  |
| DoS | 4,467 | 4,323 | DoS Hulk + DoS GoldenEye + DoS slowloris + DoS Slowhttptest + DDoS |  |
| Shellcode | 2,102 | 1,700 | none (L3 only) |  |
| Backdoor | 452 | 452 | none (L3 only) |  |
| Analysis | 385 | 385 | none (L3 only) |  |
| Worms | 246 | 236 | none (L3 only) |  |
| TOTAL | 3,540,241 | 252,028 |  |  |

### A5 Analysis outputs

| folder | file | date |
|---|---|---|
| efficiency_v3 | energy_memory_sensitivity.csv | 2026-10-26 08:22 |
| efficiency_v3 | latency_end_to_end.csv | 2026-10-26 08:22 |
| curves | learning_curves.csv | 2026-10-26 09:21 |
| unsw | qnoise_report.txt | 2026-10-26 10:13 |
| ci | ci_pairs.csv | 2026-10-26 13:42 |
| sens_smoke | sensitivity_report.txt | 2026-10-26 14:53 |
| sens_unsw | sensitivity_report.txt | 2026-10-26 17:41 |
