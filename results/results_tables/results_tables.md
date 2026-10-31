# Results tables (built from saved files under D:/revised model; nothing re-run)

## R1. Four-level ladder and confirmatory test: macro recall at threshold B

recall1 / recall01 = recall at threshold B for nominal FPR 1% / 0.1% (macro over attack types, mean over seeds); recall1_sd = sd over seeds; ci = two-way bootstrap 95% interval; fpr_test1 = observed FPR on the test benign part; pauc1 = McClish-standardised partial AUC up to 1% FPR.

| level | model | seeds | recall1 | recall1_sd | ci_lo | ci_hi | recall1_nontiny | fpr_test1 | recall01 | pauc1 |
|---|---|---|---|---|---|---|---|---|---|---|
| easy (L1) | TREE | 10 | 0.906 | 0.053 | 0.788 | 0.983 | 0.983 | 0.010 | 0.779 | 0.926 |
| easy (L1) | V3-SUP | 10 | 0.888 | 0.050 | 0.746 | 0.980 | 0.982 | 0.009 | 0.780 | 0.924 |
| medium (L2) | TREE | 10 | 0.524 | 0.026 | 0.296 | 0.742 |  | 0.010 | 0.375 | 0.733 |
| medium (L2) | V3-SUP | 10 | 0.524 | 0.027 | 0.289 | 0.749 |  | 0.009 | 0.395 | 0.735 |
| medium (L2) | V3-SUP-DENSE | 10 | 0.516 | 0.029 | 0.294 | 0.733 |  | 0.010 | 0.376 | 0.730 |
| medium (L2) | V3-MAX | 10 | 0.565 | 0.027 | 0.318 | 0.804 |  | 0.011 | 0.377 | 0.740 |
| medium (L2) | V3-MAX-RBF | 10 | 0.561 | 0.024 | 0.310 | 0.799 |  | 0.011 | 0.376 | 0.739 |
| hard (L3) | TREE | 10 | 0.312 | 0.135 | 0.137 | 0.505 | 0.230 | 0.005 | 0.193 | 0.627 |
| hard (L3) | V3-SUP | 10 | 0.340 | 0.123 | 0.165 | 0.540 | 0.251 | 0.010 | 0.195 | 0.635 |
| hard (L3) | V3-SUP-DENSE | 10 | 0.241 | 0.139 | 0.090 | 0.433 | 0.179 | 0.010 | 0.133 | 0.599 |
| hard (L3) | V3-MAX | 10 | 0.311 | 0.105 | 0.141 | 0.507 | 0.223 | 0.009 | 0.132 | 0.616 |
| hard (L3) | V3-MAX-RBF | 10 | 0.315 | 0.096 | 0.142 | 0.508 | 0.223 | 0.009 | 0.131 | 0.619 |
| hardest (L4) | TREE | 10 | 0.274 | 0.042 | 0.084 | 0.498 | 0.156 | 0.008 | 0.147 | 0.612 |
| hardest (L4) | V3-SUP | 10 | 0.273 | 0.043 | 0.083 | 0.499 | 0.150 | 0.010 | 0.151 | 0.614 |
| hardest (L4) | V3-SUP-DENSE | 10 | 0.254 | 0.053 | 0.072 | 0.481 | 0.136 | 0.010 | 0.138 | 0.605 |
| hardest (L4) | V3-MAX | 10 | 0.272 | 0.038 | 0.090 | 0.488 | 0.151 | 0.009 | 0.102 | 0.602 |
| hardest (L4) | V3-MAX-RBF | 10 | 0.279 | 0.031 | 0.093 | 0.503 | 0.152 | 0.009 | 0.099 | 0.606 |
| UNSW known (L3) | TREE | 10 | 0.027 | 0.050 | 0.005 | 0.064 |  | 0.007 | 0.010 | 0.506 |
| UNSW known (L3) | V3-SUP | 10 | 0.023 | 0.051 | 0.003 | 0.063 |  | 0.010 | 0.008 | 0.505 |
| UNSW known (L3) | V3-SUP-DENSE | 10 | 0.023 | 0.051 | 0.002 | 0.063 |  | 0.010 | 0.008 | 0.505 |
| UNSW known (L3) | V3-SUP-NOA | 10 | 0.016 | 0.033 | 0.002 | 0.043 |  | 0.010 | 0.006 | 0.503 |
| UNSW known (L3) | V3-MAX | 10 | 0.163 | 0.019 | 0.060 | 0.315 |  | 0.010 | 0.014 | 0.544 |
| UNSW known (L3) | V3-MAX-RBF | 10 | 0.161 | 0.021 | 0.059 | 0.306 |  | 0.010 | 0.018 | 0.543 |
| UNSW held-out (L4) | TREE | 10 | 0.021 | 0.017 | 0.0007 | 0.048 |  | 0.008 | 0.006 | 0.504 |
| UNSW held-out (L4) | V3-SUP | 10 | 0.018 | 0.015 | 0.0008 | 0.045 |  | 0.010 | 0.005 | 0.503 |
| UNSW held-out (L4) | V3-SUP-DENSE | 10 | 0.018 | 0.016 | 0.0004 | 0.048 |  | 0.010 | 0.005 | 0.503 |
| UNSW held-out (L4) | V3-SUP-NOA | 10 | 0.018 | 0.019 | 0.0004 | 0.051 |  | 0.010 | 0.005 | 0.503 |
| UNSW held-out (L4) | V3-MAX | 10 | 0.388 | 0.006 | 0.079 | 0.692 |  | 0.010 | 0.005 | 0.600 |
| UNSW held-out (L4) | V3-MAX-RBF | 10 | 0.377 | 0.036 | 0.081 | 0.689 |  | 0.010 | 0.007 | 0.583 |

## R2. Confirmatory hypotheses on CIC-UNSW-NB15 (calibrated recall at nominal FPR 1%, all nine types)

p_seed = one-sided Wilcoxon on the ten seed-level differences (inference); p_seed_holm = Holm over the eight tests; p_cell_descriptive = pre-specified seed x type form, descriptive. For non-inferiority (U2, U4) the test is of (A - B + 0.02) > 0.

| hypothesis | level | A | B | kind | mean_diff | ci_lo | ci_hi | seed_wins | n_seeds | p_seed | p_seed_holm | p_cell_descriptive | seed_level_decision | holm_decision | pre_specified_decision |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| U1 | unsw_known | V3-SUP | TREE | superiority | -0.004 | -0.011 | 0.0009 | 5 | 10 | 0.839 | 1.000 | 0.966 | not met | not met | not met |
| U2 | unsw_known | V3-SUP | V3-SUP-DENSE | non-inferiority | 0.0003 | -0.002 | 0.002 | 10 | 10 | 0.0010 | 0.008 | 0.0000 | met | met | met |
| U3 known | unsw_known | V3-MAX | V3-SUP | superiority | 0.140 | 0.038 | 0.287 | 10 | 10 | 0.0010 | 0.008 | 0.0000 | met | met | met |
| U3 loo | unsw_loo | V3-MAX | V3-SUP | superiority | 0.370 | 0.043 | 0.691 | 10 | 10 | 0.0010 | 0.008 | 0.0000 | met | met | met |
| U3 quantum known | unsw_known | V3-MAX | V3-MAX-RBF | superiority | 0.002 | -0.002 | 0.015 | 2 | 10 | 0.812 | 1.000 | 0.455 | not met | not met | not met |
| U3 quantum loo | unsw_loo | V3-MAX | V3-MAX-RBF | superiority | 0.011 | -0.003 | 0.044 | 6 | 10 | 0.385 | 1.000 | 0.195 | not met | not met | not met |
| U4 | unsw_known | V3-SUP-NOA | V3-SUP | non-inferiority | -0.007 |  |  | 9 | 10 | 0.042 | 0.210 | 0.0000 | met | not met | met |
| U5 | unsw_loo | V3-SUP | TREE | superiority | -0.004 | -0.014 | 0.002 | 4 | 10 | 0.688 | 1.000 | 0.623 | not met | not met | not met |

## R3. Paired comparisons per level (seed level; all attack types)

stable = two-way bootstrap interval excludes zero (interval available for recall1 and pauc1 of the levels that bootstrap_ci.py was run on).

| level | metric | kind | A | B | mean_diff | ci_lo | ci_hi | ci_excludes_0 | seed_wins | n_seeds | p_seed | p_cell_descriptive | point_rule_met |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| easy | pauc1 | superiority | V3-SUP | TREE | -0.002 | -0.009 | 0.004 | False | 4 | 10 | 0.862 | 0.182 |  |
| easy | recall1 | superiority | V3-SUP | TREE | -0.018 | -0.057 | -0.0005 | True | 2 | 10 | 0.990 | 0.998 |  |
| medium | pauc1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.006 | -0.005 | 0.017 | False | 10 | 10 | 0.0010 | 0.0000 | True |
| medium | pauc1 | superiority | V3-SUP | TREE | 0.002 | -0.007 | 0.011 | False | 7 | 10 | 0.161 | 0.118 |  |
| medium | pauc1 | superiority | V3-MAX | V3-SUP | 0.005 | -0.026 | 0.053 | False | 7 | 10 | 0.042 | 1.000 |  |
| medium | pauc1 | superiority | V3-MAX | TREE | 0.007 | -0.028 | 0.060 | False | 6 | 10 | 0.116 | 0.996 |  |
| medium | pauc1 | superiority | V3-MAX | V3-MAX-RBF | 0.001 | -0.004 | 0.007 | False | 5 | 10 | 0.312 | 0.251 |  |
| medium | pauc1 | superiority | V3-SUP | V3-SUP-DENSE | 0.006 | -0.005 | 0.017 | False | 7 | 10 | 0.080 | 0.001 |  |
| medium | recall1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.009 | -0.025 | 0.040 | False | 8 | 10 | 0.005 | 0.0000 | True |
| medium | recall1 | superiority | V3-SUP | TREE | -0.0001 | -0.036 | 0.032 | False | 7 | 10 | 0.278 | 0.641 |  |
| medium | recall1 | superiority | V3-MAX | V3-SUP | 0.040 | -0.039 | 0.166 | False | 10 | 10 | 0.0010 | 0.968 |  |
| medium | recall1 | superiority | V3-MAX | TREE | 0.040 | -0.066 | 0.184 | False | 9 | 10 | 0.003 | 0.920 |  |
| medium | recall1 | superiority | V3-MAX | V3-MAX-RBF | 0.004 | -0.003 | 0.019 | False | 7 | 10 | 0.097 | 0.211 |  |
| medium | recall1 | superiority | V3-SUP | V3-SUP-DENSE | 0.009 | -0.025 | 0.040 | False | 8 | 10 | 0.161 | 0.020 |  |
| hard | pauc1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.036 | 0.010 | 0.073 | True | 10 | 10 | 0.0010 | 0.0000 | True |
| hard | pauc1 | superiority | V3-SUP | TREE | 0.008 | -0.009 | 0.027 | False | 8 | 10 | 0.116 | 0.033 |  |
| hard | pauc1 | superiority | V3-MAX | V3-SUP | -0.018 | -0.033 | -0.006 | True | 1 | 10 | 0.999 | 1.000 |  |
| hard | pauc1 | superiority | V3-MAX | TREE | -0.011 | -0.029 | 0.004 | False | 2 | 10 | 0.947 | 0.999 |  |
| hard | pauc1 | superiority | V3-MAX | V3-MAX-RBF | -0.003 | -0.008 | 0.0003 | False | 1 | 10 | 0.990 | 0.845 |  |
| hard | pauc1 | superiority | V3-SUP | V3-SUP-DENSE | 0.036 | 0.010 | 0.073 | True | 9 | 10 | 0.005 | 0.0000 |  |
| hard | recall1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.098 | 0.025 | 0.194 | True | 8 | 10 | 0.005 | 0.0000 | True |
| hard | recall1 | superiority | V3-SUP | TREE | 0.027 | -0.028 | 0.089 | False | 7 | 10 | 0.080 | 0.002 |  |
| hard | recall1 | superiority | V3-MAX | V3-SUP | -0.029 | -0.075 | 0.019 | False | 2 | 10 | 0.993 | 0.996 |  |
| hard | recall1 | superiority | V3-MAX | TREE | -0.001 | -0.070 | 0.058 | False | 5 | 10 | 0.539 | 0.076 |  |
| hard | recall1 | superiority | V3-MAX | V3-MAX-RBF | -0.004 | -0.019 | 0.003 | False | 5 | 10 | 0.812 | 0.406 |  |
| hard | recall1 | superiority | V3-SUP | V3-SUP-DENSE | 0.098 | 0.025 | 0.194 | True | 8 | 10 | 0.007 | 0.0000 |  |
| hardest | pauc1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.008 | -0.003 | 0.028 | False | 9 | 10 | 0.002 | 0.0000 | True |
| hardest | pauc1 | superiority | V3-SUP | TREE | 0.002 | -0.015 | 0.021 | False | 6 | 10 | 0.278 | 0.638 |  |
| hardest | pauc1 | superiority | V3-MAX | V3-SUP | -0.012 | -0.026 | 0.0009 | False | 0 | 10 | 1.000 | 1.000 |  |
| hardest | pauc1 | superiority | V3-MAX | TREE | -0.010 | -0.033 | 0.007 | False | 4 | 10 | 0.935 | 0.993 |  |
| hardest | pauc1 | superiority | V3-MAX | V3-MAX-RBF | -0.004 | -0.011 | 0.0003 | False | 1 | 10 | 0.998 | 0.998 |  |
| hardest | pauc1 | superiority | V3-SUP | V3-SUP-DENSE | 0.008 | -0.003 | 0.028 | False | 8 | 10 | 0.032 | 0.004 |  |
| hardest | recall1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.019 | -0.012 | 0.062 | False | 9 | 10 | 0.005 | 0.0000 | True |
| hardest | recall1 | superiority | V3-SUP | TREE | -0.001 | -0.039 | 0.042 | False | 6 | 10 | 0.539 | 0.699 |  |
| hardest | recall1 | superiority | V3-MAX | V3-SUP | -0.0008 | -0.033 | 0.039 | False | 5 | 10 | 0.652 | 0.899 |  |
| hardest | recall1 | superiority | V3-MAX | TREE | -0.002 | -0.051 | 0.051 | False | 6 | 10 | 0.539 | 0.568 |  |
| hardest | recall1 | superiority | V3-MAX | V3-MAX-RBF | -0.007 | -0.028 | 0.002 | False | 2 | 10 | 0.968 | 0.790 |  |
| hardest | recall1 | superiority | V3-SUP | V3-SUP-DENSE | 0.019 | -0.012 | 0.062 | False | 9 | 10 | 0.024 | 0.018 |  |
| unsw_known | pauc1 | non-inferiority | V3-SUP | V3-SUP-DENSE | -0.0000 | -0.001 | 0.0008 | False | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_known | pauc1 | non-inferiority | V3-SUP-NOA | V3-SUP | -0.001 |  |  |  | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_known | pauc1 | superiority | V3-SUP | TREE | -0.001 | -0.004 | 0.0002 | False | 3 | 10 | 0.935 | 0.995 |  |
| unsw_known | pauc1 | superiority | V3-MAX | V3-SUP | 0.039 | 0.011 | 0.076 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_known | pauc1 | superiority | V3-MAX | TREE | 0.038 | 0.010 | 0.075 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_known | pauc1 | superiority | V3-MAX | V3-MAX-RBF | 0.0010 | -0.006 | 0.012 | False | 6 | 10 | 0.138 | 0.999 |  |
| unsw_known | pauc1 | superiority | V3-SUP | V3-SUP-DENSE | -0.0000 | -0.001 | 0.0008 | False | 4 | 10 | 0.461 | 0.261 |  |
| unsw_known | pauc1 | superiority | V3-SUP | V3-SUP-NOA | 0.001 | -0.0002 | 0.005 | False | 7 | 10 | 0.065 | 0.002 |  |
| unsw_known | recall1 | non-inferiority | V3-SUP | V3-SUP-DENSE | 0.0003 | -0.002 | 0.002 | False | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_known | recall1 | non-inferiority | V3-SUP-NOA | V3-SUP | -0.007 |  |  |  | 9 | 10 | 0.042 | 0.0000 | True |
| unsw_known | recall1 | superiority | V3-SUP | TREE | -0.004 | -0.011 | 0.0009 | False | 5 | 10 | 0.839 | 0.966 |  |
| unsw_known | recall1 | superiority | V3-MAX | V3-SUP | 0.140 | 0.038 | 0.287 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_known | recall1 | superiority | V3-MAX | TREE | 0.137 | 0.036 | 0.282 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_known | recall1 | superiority | V3-MAX | V3-MAX-RBF | 0.002 | -0.002 | 0.015 | False | 2 | 10 | 0.812 | 0.455 |  |
| unsw_known | recall1 | superiority | V3-SUP | V3-SUP-DENSE | 0.0003 | -0.002 | 0.002 | False | 4 | 10 | 0.461 | 0.075 |  |
| unsw_known | recall1 | superiority | V3-SUP | V3-SUP-NOA | 0.007 | -0.0001 | 0.021 | False | 7 | 10 | 0.053 | 0.0000 |  |
| unsw_loo | pauc1 | non-inferiority | V3-SUP | V3-SUP-DENSE | -0.0003 | -0.001 | 0.0004 | False | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_loo | pauc1 | non-inferiority | V3-SUP-NOA | V3-SUP | 0.0003 |  |  |  | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_loo | pauc1 | superiority | V3-SUP | TREE | -0.001 | -0.004 | 0.0003 | False | 5 | 10 | 0.754 | 0.752 |  |
| unsw_loo | pauc1 | superiority | V3-MAX | V3-SUP | 0.097 | 0.009 | 0.189 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_loo | pauc1 | superiority | V3-MAX | TREE | 0.096 | 0.007 | 0.187 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_loo | pauc1 | superiority | V3-MAX | V3-MAX-RBF | 0.017 | -0.003 | 0.044 | False | 10 | 10 | 0.0010 | 0.032 |  |
| unsw_loo | pauc1 | superiority | V3-SUP | V3-SUP-DENSE | -0.0003 | -0.001 | 0.0004 | False | 4 | 10 | 0.722 | 0.587 |  |
| unsw_loo | pauc1 | superiority | V3-SUP | V3-SUP-NOA | -0.0003 | -0.002 | 0.001 | False | 4 | 10 | 0.715 | 0.658 |  |
| unsw_loo | recall1 | non-inferiority | V3-SUP | V3-SUP-DENSE | -0.0001 | -0.003 | 0.002 | False | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_loo | recall1 | non-inferiority | V3-SUP-NOA | V3-SUP | 0.0005 |  |  |  | 10 | 10 | 0.0010 | 0.0000 | True |
| unsw_loo | recall1 | superiority | V3-SUP | TREE | -0.004 | -0.014 | 0.002 | False | 4 | 10 | 0.688 | 0.623 |  |
| unsw_loo | recall1 | superiority | V3-MAX | V3-SUP | 0.370 | 0.043 | 0.691 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_loo | recall1 | superiority | V3-MAX | TREE | 0.366 | 0.038 | 0.691 | True | 10 | 10 | 0.0010 | 0.0000 |  |
| unsw_loo | recall1 | superiority | V3-MAX | V3-MAX-RBF | 0.011 | -0.003 | 0.044 | False | 6 | 10 | 0.385 | 0.195 |  |
| unsw_loo | recall1 | superiority | V3-SUP | V3-SUP-DENSE | -0.0001 | -0.003 | 0.002 | False | 4 | 10 | 0.422 | 0.361 |  |
| unsw_loo | recall1 | superiority | V3-SUP | V3-SUP-NOA | -0.0005 | -0.007 | 0.003 | False | 4 | 10 | 0.633 | 0.407 |  |

## R4a. L3 ablation (CSE-CIC-IDS2018, ten seeds, v3.2 code before the lock): model means

| model | recall1_mean | recall1_sd |
|---|---|---|
| TREE | 0.312 | 0.135 |
| V3-SUP | 0.340 | 0.123 |
| V3-SUP-NOA | 0.330 | 0.129 |
| V3-SUP-NOALIGN | 0.319 | 0.122 |
| V3-SUP-NOW | 0.307 | 0.108 |
| V3-SUP-SHUF | 0.316 | 0.119 |
| V3-SUP-TT | 0.320 | 0.126 |
| V3-SUP-LR | 0.328 | 0.106 |

## R4b. L3 ablation: seed-level paired tests (recall at B, 1%)

| types | kind | A | B | mean_diff | seed_wins | n_seeds | p_seed | p_cell_descriptive | point_rule_met |
|---|---|---|---|---|---|---|---|---|---|
| all types | superiority | V3-SUP | TREE | 0.027 | 7 | 10 | 0.080 | 0.002 |  |
| all types | superiority | V3-SUP | V3-SUP-NOA | 0.010 | 7 | 10 | 0.348 | 0.301 |  |
| all types | superiority | V3-SUP | V3-SUP-NOALIGN | 0.021 | 7 | 10 | 0.116 | 0.001 |  |
| all types | superiority | V3-SUP | V3-SUP-SHUF | 0.024 | 9 | 10 | 0.005 | 0.0004 |  |
| all types | superiority | V3-SUP | V3-SUP-NOW | 0.032 | 7 | 10 | 0.042 | 0.060 |  |
| all types | superiority | V3-SUP-TT | V3-SUP-LR | -0.008 | 7 | 10 | 0.278 | 0.067 |  |
| all types | non-inferiority | V3-SUP-NOA | V3-SUP | -0.010 | 4 | 10 | 0.461 | 0.0000 | True |
| all types | non-inferiority | V3-SUP-TT | V3-SUP | -0.020 | 5 | 10 | 0.539 | 0.0002 | True |
| non-tiny types | superiority | V3-SUP | TREE | 0.022 | 7 | 10 | 0.097 | 0.014 |  |
| non-tiny types | superiority | V3-SUP | V3-SUP-NOA | 0.001 | 7 | 10 | 0.423 | 0.386 |  |
| non-tiny types | superiority | V3-SUP | V3-SUP-NOALIGN | 0.028 | 8 | 10 | 0.080 | 0.0005 |  |
| non-tiny types | superiority | V3-SUP | V3-SUP-SHUF | 0.026 | 9 | 10 | 0.007 | 0.0003 |  |
| non-tiny types | superiority | V3-SUP | V3-SUP-NOW | 0.028 | 7 | 10 | 0.053 | 0.110 |  |
| non-tiny types | superiority | V3-SUP-TT | V3-SUP-LR | -0.002 | 7 | 10 | 0.278 | 0.042 |  |
| non-tiny types | non-inferiority | V3-SUP-NOA | V3-SUP | -0.001 | 4 | 10 | 0.385 | 0.0000 | True |
| non-tiny types | non-inferiority | V3-SUP-TT | V3-SUP | -0.008 | 4 | 10 | 0.539 | 0.0000 | True |

## R5. CIC-UNSW-NB15 (known scenario): recall at B per attack type, mean over ten seeds

| type | group | flows | TREE | V3-SUP | V3-SUP-DENSE | V3-SUP-NOA | V3-MAX | V3-MAX-RBF |
|---|---|---|---|---|---|---|---|---|
| DoS | counterpart | 4323.000 | 0.040 | 0.033 | 0.034 | 0.027 | 0.090 | 0.092 |
| Reconnaissance | counterpart | 11993.000 | 0.040 | 0.042 | 0.040 | 0.036 | 0.698 | 0.674 |
| Analysis | new | 385.000 | 0.0003 | 0.0005 | 0.0003 | 0.000 | 0.0005 | 0.0005 |
| Backdoor | new | 452.000 | 0.024 | 0.025 | 0.023 | 0.012 | 0.038 | 0.037 |
| Exploits | new | 19924.000 | 0.037 | 0.031 | 0.032 | 0.024 | 0.041 | 0.041 |
| Fuzzers | new | 17713.000 | 0.024 | 0.020 | 0.020 | 0.019 | 0.102 | 0.100 |
| Generic | new | 4401.000 | 0.027 | 0.013 | 0.015 | 0.012 | 0.210 | 0.216 |
| Shellcode | new | 1700.000 | 0.029 | 0.023 | 0.023 | 0.010 | 0.225 | 0.225 |
| Worms | new | 236.000 | 0.020 | 0.019 | 0.018 | 0.007 | 0.065 | 0.064 |
| counterpart | mean |  | 0.040 | 0.038 | 0.037 | 0.032 | 0.394 | 0.383 |
| new | mean |  | 0.023 | 0.019 | 0.019 | 0.012 | 0.097 | 0.098 |

## R6. CIC-UNSW-NB15: calibrated recall, ROC-interpolated recall (test FPR 1% / 0.1%) and average precision

| scenario | model | recall_B | fpr_B | recall_at1 | recall_at01 | pr_auc |
|---|---|---|---|---|---|---|
| known | TREE | 0.027 | 0.007 | 0.028 | 0.010 | 0.160 |
| known | V3-SUP | 0.023 | 0.010 | 0.024 | 0.008 | 0.138 |
| known | V3-SUP-DENSE | 0.023 | 0.010 | 0.024 | 0.008 | 0.166 |
| known | V3-SUP-NOA | 0.016 | 0.010 | 0.017 | 0.005 | 0.134 |
| known | V3-MAX | 0.163 | 0.010 | 0.163 | 0.013 | 0.276 |
| known | V3-MAX-RBF | 0.161 | 0.010 | 0.161 | 0.018 | 0.271 |
| loo | TREE | 0.021 | 0.008 | 0.022 | 0.006 | 0.226 |
| loo | V3-SUP | 0.018 | 0.010 | 0.018 | 0.005 | 0.189 |
| loo | V3-SUP-DENSE | 0.018 | 0.010 | 0.018 | 0.005 | 0.215 |
| loo | V3-SUP-NOA | 0.018 | 0.010 | 0.018 | 0.005 | 0.184 |
| loo | V3-MAX | 0.388 | 0.010 | 0.388 | 0.005 | 0.497 |
| loo | V3-MAX-RBF | 0.377 | 0.010 | 0.378 | 0.007 | 0.484 |

## R7_unsw_primary. Event-level metric, CIC-UNSW-NB15 (mean over attack types, then over seeds)

| scenario | fpr | k | model | n_flows | flow_recall | n_episodes | episode_recall | minute_recall | median_ttd_s | share_detected_60s | flow_fpr | n_benign_minutes | fa_minute_rate | fa_minutes_per_hour | hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 0.001 | 1 | TREE | 6791.889 | 0.010 | 16.667 | 0.331 | 0.079 | 1136.103 | 0.023 | 0.0009 | 1459.000 | 0.037 | 2.192 | 24.684 |
| known | 0.001 | 1 | V3-SUP | 6791.889 | 0.008 | 16.667 | 0.273 | 0.061 | 2615.270 | 0.021 | 0.001 | 1459.000 | 0.039 | 2.297 | 24.684 |
| known | 0.001 | 1 | V3-SUP-DENSE | 6791.889 | 0.008 | 16.667 | 0.311 | 0.065 | 1835.088 | 0.018 | 0.001 | 1459.000 | 0.043 | 2.516 | 24.684 |
| known | 0.001 | 1 | V3-SUP-NOA | 6791.889 | 0.006 | 16.667 | 0.271 | 0.053 | 1529.315 | 0.017 | 0.001 | 1459.000 | 0.040 | 2.362 | 24.684 |
| known | 0.001 | 1 | V3-MAX | 6791.889 | 0.014 | 16.667 | 0.352 | 0.093 | 1204.832 | 0.034 | 0.0010 | 1459.000 | 0.036 | 2.143 | 24.684 |
| known | 0.001 | 1 | V3-MAX-RBF | 6791.889 | 0.018 | 16.667 | 0.466 | 0.113 | 1241.510 | 0.048 | 0.001 | 1459.000 | 0.038 | 2.273 | 24.684 |
| known | 0.001 | 3 | TREE | 6791.889 | 0.010 | 16.667 | 0.151 | 0.010 | 4075.229 | 0.003 | 0.0009 | 1459.000 | 0.0001 | 0.008 | 24.684 |
| known | 0.001 | 3 | V3-SUP | 6791.889 | 0.008 | 16.667 | 0.128 | 0.008 | 1767.859 | 0.003 | 0.001 | 1459.000 | 0.0010 | 0.057 | 24.684 |
| known | 0.001 | 3 | V3-SUP-DENSE | 6791.889 | 0.008 | 16.667 | 0.136 | 0.008 | 2492.052 | 0.003 | 0.001 | 1459.000 | 0.0003 | 0.020 | 24.684 |
| known | 0.001 | 3 | V3-SUP-NOA | 6791.889 | 0.006 | 16.667 | 0.119 | 0.005 | 2386.995 | 0.002 | 0.001 | 1459.000 | 0.0008 | 0.049 | 24.684 |
| known | 0.001 | 3 | V3-MAX | 6791.889 | 0.014 | 16.667 | 0.147 | 0.010 | 2772.845 | 0.010 | 0.0010 | 1459.000 | 0.0010 | 0.057 | 24.684 |
| known | 0.001 | 3 | V3-MAX-RBF | 6791.889 | 0.018 | 16.667 | 0.171 | 0.014 | 3041.182 | 0.019 | 0.001 | 1459.000 | 0.0010 | 0.057 | 24.684 |
| known | 0.010 | 1 | TREE | 6791.889 | 0.027 | 16.667 | 0.384 | 0.130 | 1097.553 | 0.086 | 0.007 | 1459.000 | 0.262 | 15.492 | 24.684 |
| known | 0.010 | 1 | V3-SUP | 6791.889 | 0.023 | 16.667 | 0.348 | 0.104 | 1699.575 | 0.082 | 0.010 | 1459.000 | 0.287 | 16.942 | 24.684 |
| known | 0.010 | 1 | V3-SUP-DENSE | 6791.889 | 0.023 | 16.667 | 0.347 | 0.108 | 1290.173 | 0.069 | 0.010 | 1459.000 | 0.332 | 19.648 | 24.684 |
| known | 0.010 | 1 | V3-SUP-NOA | 6791.889 | 0.016 | 16.667 | 0.296 | 0.088 | 1701.310 | 0.039 | 0.010 | 1459.000 | 0.297 | 17.529 | 24.684 |
| known | 0.010 | 1 | V3-MAX | 6791.889 | 0.163 | 16.667 | 0.672 | 0.413 | 115.933 | 0.441 | 0.010 | 1459.000 | 0.277 | 16.387 | 24.684 |
| known | 0.010 | 1 | V3-MAX-RBF | 6791.889 | 0.161 | 16.667 | 0.673 | 0.416 | 114.931 | 0.427 | 0.010 | 1459.000 | 0.281 | 16.602 | 24.684 |
| known | 0.010 | 3 | TREE | 6791.889 | 0.027 | 16.667 | 0.197 | 0.030 | 3242.944 | 0.031 | 0.007 | 1459.000 | 0.009 | 0.555 | 24.684 |
| known | 0.010 | 3 | V3-SUP | 6791.889 | 0.023 | 16.667 | 0.177 | 0.028 | 2685.083 | 0.028 | 0.010 | 1459.000 | 0.027 | 1.616 | 24.684 |
| known | 0.010 | 3 | V3-SUP-DENSE | 6791.889 | 0.023 | 16.667 | 0.172 | 0.027 | 2257.467 | 0.025 | 0.010 | 1459.000 | 0.017 | 1.001 | 24.684 |
| known | 0.010 | 3 | V3-SUP-NOA | 6791.889 | 0.016 | 16.667 | 0.164 | 0.021 | 1992.792 | 0.011 | 0.010 | 1459.000 | 0.027 | 1.580 | 24.684 |
| known | 0.010 | 3 | V3-MAX | 6791.889 | 0.163 | 16.667 | 0.457 | 0.170 | 1530.642 | 0.153 | 0.010 | 1459.000 | 0.037 | 2.159 | 24.684 |
| known | 0.010 | 3 | V3-MAX-RBF | 6791.889 | 0.161 | 16.667 | 0.457 | 0.169 | 1365.708 | 0.151 | 0.010 | 1459.000 | 0.037 | 2.188 | 24.684 |
| loo | 0.001 | 1 | TREE | 8158.000 | 0.006 | 4.500 | 0.280 | 0.029 | 2811.562 | 0.035 | 0.0009 | 1459.000 | 0.034 | 2.024 | 24.684 |
| loo | 0.001 | 1 | V3-SUP | 8158.000 | 0.005 | 4.500 | 0.295 | 0.023 | 2271.125 | 0.025 | 0.001 | 1459.000 | 0.040 | 2.372 | 24.684 |
| loo | 0.001 | 1 | V3-SUP-DENSE | 8158.000 | 0.005 | 4.500 | 0.280 | 0.024 | 1569.250 | 0.035 | 0.001 | 1459.000 | 0.040 | 2.392 | 24.684 |
| loo | 0.001 | 1 | V3-SUP-NOA | 8158.000 | 0.005 | 4.500 | 0.273 | 0.022 | 5276.625 | 0.025 | 0.001 | 1459.000 | 0.041 | 2.404 | 24.684 |
| loo | 0.001 | 1 | V3-MAX | 8158.000 | 0.005 | 4.500 | 0.412 | 0.028 | 1286.000 | 0.055 | 0.0010 | 1459.000 | 0.037 | 2.161 | 24.684 |
| loo | 0.001 | 1 | V3-MAX-RBF | 8158.000 | 0.007 | 4.500 | 0.750 | 0.043 | 2295.475 | 0.075 | 0.001 | 1459.000 | 0.039 | 2.327 | 24.684 |
| loo | 0.001 | 3 | TREE | 8158.000 | 0.006 | 4.500 | 0.050 | 0.0006 | 4309.000 | 0.000 | 0.0009 | 1459.000 | 0.0001 | 0.008 | 24.684 |
| loo | 0.001 | 3 | V3-SUP | 8158.000 | 0.005 | 4.500 | 0.050 | 0.0006 | 4309.000 | 0.000 | 0.001 | 1459.000 | 0.0006 | 0.034 | 24.684 |
| loo | 0.001 | 3 | V3-SUP-DENSE | 8158.000 | 0.005 | 4.500 | 0.075 | 0.001 | 4755.167 | 0.000 | 0.001 | 1459.000 | 0.0003 | 0.016 | 24.684 |
| loo | 0.001 | 3 | V3-SUP-NOA | 8158.000 | 0.005 | 4.500 | 0.075 | 0.001 | 4754.167 | 0.000 | 0.001 | 1459.000 | 0.0006 | 0.034 | 24.684 |
| loo | 0.001 | 3 | V3-MAX | 8158.000 | 0.005 | 4.500 | 0.080 | 0.0008 | 4063.250 | 0.000 | 0.0010 | 1459.000 | 0.0008 | 0.045 | 24.684 |
| loo | 0.001 | 3 | V3-MAX-RBF | 8158.000 | 0.007 | 4.500 | 0.050 | 0.0006 | 4309.000 | 0.000 | 0.001 | 1459.000 | 0.001 | 0.061 | 24.684 |
| loo | 0.010 | 1 | TREE | 8158.000 | 0.021 | 4.500 | 0.535 | 0.102 | 1621.850 | 0.135 | 0.008 | 1459.000 | 0.275 | 16.241 | 24.684 |
| loo | 0.010 | 1 | V3-SUP | 8158.000 | 0.018 | 4.500 | 0.487 | 0.073 | 1181.694 | 0.082 | 0.010 | 1459.000 | 0.302 | 17.849 | 24.684 |
| loo | 0.010 | 1 | V3-SUP-DENSE | 8158.000 | 0.018 | 4.500 | 0.485 | 0.074 | 1298.450 | 0.115 | 0.010 | 1459.000 | 0.330 | 19.486 | 24.684 |
| loo | 0.010 | 1 | V3-SUP-NOA | 8158.000 | 0.018 | 4.500 | 0.475 | 0.071 | 1072.694 | 0.095 | 0.010 | 1459.000 | 0.303 | 17.904 | 24.684 |
| loo | 0.010 | 1 | V3-MAX | 8158.000 | 0.388 | 4.500 | 1.000 | 0.659 | 78.525 | 0.650 | 0.010 | 1459.000 | 0.284 | 16.790 | 24.684 |
| loo | 0.010 | 1 | V3-MAX-RBF | 8158.000 | 0.377 | 4.500 | 1.000 | 0.662 | 81.700 | 0.600 | 0.010 | 1459.000 | 0.287 | 16.980 | 24.684 |
| loo | 0.010 | 3 | TREE | 8158.000 | 0.021 | 4.500 | 0.237 | 0.011 | 3760.889 | 0.000 | 0.008 | 1459.000 | 0.012 | 0.711 | 24.684 |
| loo | 0.010 | 3 | V3-SUP | 8158.000 | 0.018 | 4.500 | 0.242 | 0.005 | 4025.361 | 0.000 | 0.010 | 1459.000 | 0.024 | 1.416 | 24.684 |
| loo | 0.010 | 3 | V3-SUP-DENSE | 8158.000 | 0.018 | 4.500 | 0.223 | 0.005 | 4343.889 | 0.000 | 0.010 | 1459.000 | 0.017 | 1.015 | 24.684 |
| loo | 0.010 | 3 | V3-SUP-NOA | 8158.000 | 0.018 | 4.500 | 0.253 | 0.007 | 4173.000 | 0.000 | 0.010 | 1459.000 | 0.022 | 1.278 | 24.684 |
| loo | 0.010 | 3 | V3-MAX | 8158.000 | 0.388 | 4.500 | 0.775 | 0.507 | 1444.475 | 0.400 | 0.010 | 1459.000 | 0.035 | 2.050 | 24.684 |
| loo | 0.010 | 3 | V3-MAX-RBF | 8158.000 | 0.377 | 4.500 | 0.775 | 0.503 | 1351.925 | 0.390 | 0.010 | 1459.000 | 0.035 | 2.048 | 24.684 |

## R7_scores_cross. Event-level metric, CSE-CIC-IDS2018 (mean over attack types, then over seeds)

| scenario | fpr | k | model | n_flows | flow_recall | n_episodes | episode_recall | minute_recall | median_ttd_s | share_detected_60s | flow_fpr | n_benign_minutes | fa_minute_rate | fa_minutes_per_hour | hours |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 0.001 | 1 | TREE | 8408.571 | 0.193 | 2.571 | 0.485 | 0.342 | 726.655 | 0.348 | 0.0008 | 4377.000 | 0.015 | 0.561 | 113.707 |
| known | 0.001 | 1 | V3-SUP | 8408.571 | 0.195 | 2.571 | 0.546 | 0.355 | 969.645 | 0.358 | 0.0009 | 4377.000 | 0.017 | 0.643 | 113.707 |
| known | 0.001 | 3 | TREE | 8408.571 | 0.193 | 2.571 | 0.240 | 0.176 | 31.787 | 0.232 | 0.0008 | 4377.000 | 0.0001 | 0.003 | 113.707 |
| known | 0.001 | 3 | V3-SUP | 8408.571 | 0.195 | 2.571 | 0.279 | 0.205 | 100.550 | 0.254 | 0.0009 | 4377.000 | 0.0003 | 0.010 | 113.707 |
| known | 0.010 | 1 | TREE | 8408.571 | 0.312 | 2.571 | 0.657 | 0.532 | 567.195 | 0.475 | 0.005 | 4377.000 | 0.082 | 3.157 | 113.707 |
| known | 0.010 | 1 | V3-SUP | 8408.571 | 0.340 | 2.571 | 0.693 | 0.565 | 385.731 | 0.497 | 0.010 | 4377.000 | 0.137 | 5.257 | 113.707 |
| known | 0.010 | 3 | TREE | 8408.571 | 0.312 | 2.571 | 0.401 | 0.306 | 727.538 | 0.329 | 0.005 | 4377.000 | 0.004 | 0.135 | 113.707 |
| known | 0.010 | 3 | V3-SUP | 8408.571 | 0.340 | 2.571 | 0.440 | 0.320 | 757.112 | 0.341 | 0.010 | 4377.000 | 0.013 | 0.517 | 113.707 |
| loo | 0.001 | 1 | TREE | 8462.417 | 0.147 | 2.833 | 0.480 | 0.285 | 548.096 | 0.364 | 0.0008 | 4377.000 | 0.014 | 0.555 | 113.707 |
| loo | 0.001 | 1 | V3-SUP | 8462.417 | 0.151 | 2.833 | 0.490 | 0.298 | 482.144 | 0.367 | 0.0009 | 4377.000 | 0.016 | 0.626 | 113.707 |
| loo | 0.001 | 3 | TREE | 8462.417 | 0.147 | 2.833 | 0.296 | 0.167 | 278.867 | 0.267 | 0.0008 | 4377.000 | 0.0001 | 0.004 | 113.707 |
| loo | 0.001 | 3 | V3-SUP | 8462.417 | 0.151 | 2.833 | 0.278 | 0.173 | 92.059 | 0.248 | 0.0009 | 4377.000 | 0.0003 | 0.011 | 113.707 |
| loo | 0.010 | 1 | TREE | 8462.417 | 0.274 | 2.833 | 0.719 | 0.491 | 326.430 | 0.530 | 0.008 | 4377.000 | 0.118 | 4.533 | 113.707 |
| loo | 0.010 | 1 | V3-SUP | 8462.417 | 0.273 | 2.833 | 0.724 | 0.478 | 398.103 | 0.520 | 0.010 | 4377.000 | 0.138 | 5.313 | 113.707 |
| loo | 0.010 | 3 | TREE | 8462.417 | 0.274 | 2.833 | 0.465 | 0.270 | 741.670 | 0.356 | 0.008 | 4377.000 | 0.006 | 0.250 | 113.707 |
| loo | 0.010 | 3 | V3-SUP | 8462.417 | 0.273 | 2.833 | 0.460 | 0.270 | 621.900 | 0.356 | 0.010 | 4377.000 | 0.013 | 0.495 | 113.707 |

## R8_latency_end_to_end. End-to-end p95 latency (batch 1) and throughput

| config | end_to_end_p95_ms | flows_per_s |
|---|---|---|
| TREE | 3.424 | 235878.665 |
| V3-SUP | 20.261 | 28864.475 |
| V3-SUP-DENSE | 16.407 | 42250.456 |
| V3-MAX (IQP) | 71.598 | 4162.297 |
| V3-MAX-RBF | 83.374 | 8181.037 |

## R8_latency_parts. Latency of each part

| part | med_1thr | p95_1thr | p99_1thr | med_all | p95_all |
|---|---|---|---|---|---|
| tree (incl. logit) | 3.000 | 3.424 | 4.007 | 3.015 | 3.610 |
| V3-SUP network | 11.800 | 15.086 | 19.304 | 16.407 | 24.044 |
| V3-SUP-DENSE network | 8.073 | 11.232 | 13.114 | 9.168 | 10.511 |
| novelty IQP | 44.665 | 51.337 | 60.064 | 47.712 | 63.825 |
| novelty RBF | 43.235 | 63.113 | 67.573 | 42.278 | 50.730 |
| 16-minute sequence (PortTable) | 1.136 | 1.751 |  |  |  |

## R8_energy_memory_sensitivity. Energy estimate with memory-access sensitivity

| model | mem_pJ_per_read | P_energy_nJ | total_energy_nJ |
|---|---|---|---|
| V3-SUP | 0.000 | 56.081 | 96.855 |
| V3-SUP | 5.000 | 175.570 | 260.665 |
| V3-SUP | 50.000 | 1250.975 | 1734.950 |
| V3-SUP-DENSE | 0.000 | 422.579 | 463.354 |
| V3-SUP-DENSE | 5.000 | 894.259 | 979.354 |
| V3-SUP-DENSE | 50.000 | 5139.379 | 5623.354 |

## R9. CIC-UNSW-NB15: sensitivity to the benign reference (five seeds, exploratory)

| variant | scenario | model | seeds | recall1 | recall1_sd | fpr_test1 |
|---|---|---|---|---|---|---|
| base | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| base | known | V3-SUP | 5 | 0.007 | 0.004 | 0.010 |
| base | known | V3-MAX | 5 | 0.158 | 0.003 | 0.010 |
| size25 | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| size25 | known | V3-SUP | 5 | 0.007 | 0.004 | 0.010 |
| size25 | known | V3-MAX | 5 | 0.156 | 0.004 | 0.010 |
| size10 | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| size10 | known | V3-SUP | 5 | 0.009 | 0.011 | 0.010 |
| size10 | known | V3-MAX | 5 | 0.151 | 0.009 | 0.010 |
| time | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| time | known | V3-SUP | 5 | 0.007 | 0.005 | 0.011 |
| time | known | V3-MAX | 5 | 0.083 | 0.009 | 0.013 |
| contam1 | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| contam1 | known | V3-SUP | 5 | 0.010 | 0.005 | 0.010 |
| contam1 | known | V3-MAX | 5 | 0.103 | 0.006 | 0.009 |
| contam5 | known | TREE | 5 | 0.012 | 0.009 | 0.008 |
| contam5 | known | V3-SUP | 5 | 0.011 | 0.012 | 0.010 |
| contam5 | known | V3-MAX | 5 | 0.073 | 0.006 | 0.007 |
| base | loo | TREE | 5 | 0.029 | 0.022 | 0.008 |
| base | loo | V3-SUP | 5 | 0.021 | 0.021 | 0.010 |
| base | loo | V3-MAX | 5 | 0.389 | 0.008 | 0.010 |
| size25 | loo | TREE | 5 | 0.030 | 0.024 | 0.009 |
| size25 | loo | V3-SUP | 5 | 0.023 | 0.023 | 0.010 |
| size25 | loo | V3-MAX | 5 | 0.387 | 0.014 | 0.010 |
| size10 | loo | TREE | 5 | 0.030 | 0.026 | 0.009 |
| size10 | loo | V3-SUP | 5 | 0.022 | 0.026 | 0.011 |
| size10 | loo | V3-MAX | 5 | 0.366 | 0.054 | 0.011 |
| time | loo | TREE | 5 | 0.031 | 0.025 | 0.010 |
| time | loo | V3-SUP | 5 | 0.022 | 0.025 | 0.011 |
| time | loo | V3-MAX | 5 | 0.071 | 0.050 | 0.013 |
| contam1 | loo | TREE | 5 | 0.028 | 0.021 | 0.008 |
| contam1 | loo | V3-SUP | 5 | 0.022 | 0.024 | 0.010 |
| contam1 | loo | V3-MAX | 5 | 0.171 | 0.033 | 0.009 |
| contam5 | loo | TREE | 5 | 0.022 | 0.011 | 0.008 |
| contam5 | loo | V3-SUP | 5 | 0.017 | 0.015 | 0.010 |
| contam5 | loo | V3-MAX | 5 | 0.035 | 0.006 | 0.007 |

## R10_context_unsw. Share of benign flows with a sampled attack flow in their window (unsw)

| part | n | network | 16 min | network | same minute | service | 16 min | service | same minute |
|---|---|---|---|---|---|
| fit | 31816 | 0.581 | 0.558 | 0.219 | 0.158 |
| ref | 31817 | 0.577 | 0.553 | 0.222 | 0.159 |
| cal | 63633 | 0.584 | 0.561 | 0.223 | 0.160 |
| test | 63635 | 0.581 | 0.557 | 0.220 | 0.157 |
| reference_all | 63633 | 0.579 | 0.555 | 0.220 | 0.159 |

## R10_threshold_clean_unsw. Threshold B from attack-free-window calibration flows (unsw)

| nominal | scenario | model | recall_B | recall_Bclean | fpr_test_B | fpr_cleantest_B | fpr_cleantest_Bclean | fpr_attackwindow_test_B |
|---|---|---|---|---|---|---|---|---|
| 0.010 | known | TREE | 0.027 | 0.030 | 0.007 | 0.007 | 0.007 | 0.007 |
| 0.010 | known | V3-SUP | 0.023 | 0.026 | 0.010 | 0.011 | 0.010 | 0.009 |
| 0.010 | known | V3-SUP-DENSE | 0.023 | 0.026 | 0.010 | 0.010 | 0.010 | 0.010 |
| 0.010 | known | V3-SUP-NOA | 0.016 | 0.018 | 0.010 | 0.010 | 0.010 | 0.010 |
| 0.010 | known | V3-MAX | 0.163 | 0.173 | 0.010 | 0.007 | 0.010 | 0.012 |
| 0.010 | known | V3-MAX-RBF | 0.161 | 0.175 | 0.010 | 0.008 | 0.010 | 0.012 |
| 0.010 | loo | TREE | 0.021 | 0.023 | 0.008 | 0.008 | 0.008 | 0.008 |
| 0.010 | loo | V3-SUP | 0.018 | 0.018 | 0.010 | 0.011 | 0.010 | 0.009 |
| 0.010 | loo | V3-SUP-DENSE | 0.018 | 0.019 | 0.010 | 0.010 | 0.010 | 0.010 |
| 0.010 | loo | V3-SUP-NOA | 0.018 | 0.019 | 0.010 | 0.010 | 0.010 | 0.009 |
| 0.010 | loo | V3-MAX | 0.388 | 0.400 | 0.010 | 0.007 | 0.010 | 0.012 |
| 0.010 | loo | V3-MAX-RBF | 0.377 | 0.398 | 0.010 | 0.007 | 0.010 | 0.012 |
| 0.001 | known | TREE | 0.010 | 0.013 | 0.0009 | 0.0007 | 0.0009 | 0.001 |
| 0.001 | known | V3-SUP | 0.008 | 0.009 | 0.001 | 0.001 | 0.0010 | 0.0009 |
| 0.001 | known | V3-SUP-DENSE | 0.008 | 0.010 | 0.001 | 0.0010 | 0.0010 | 0.001 |
| 0.001 | known | V3-SUP-NOA | 0.006 | 0.007 | 0.001 | 0.0009 | 0.0009 | 0.001 |
| 0.001 | known | V3-MAX | 0.014 | 0.025 | 0.0010 | 0.0006 | 0.0009 | 0.001 |
| 0.001 | known | V3-MAX-RBF | 0.018 | 0.031 | 0.001 | 0.0005 | 0.0010 | 0.001 |
| 0.001 | loo | TREE | 0.006 | 0.006 | 0.0009 | 0.0008 | 0.0009 | 0.0009 |
| 0.001 | loo | V3-SUP | 0.005 | 0.004 | 0.001 | 0.001 | 0.0009 | 0.0010 |
| 0.001 | loo | V3-SUP-DENSE | 0.005 | 0.005 | 0.001 | 0.0010 | 0.0009 | 0.001 |
| 0.001 | loo | V3-SUP-NOA | 0.005 | 0.005 | 0.001 | 0.001 | 0.001 | 0.001 |
| 0.001 | loo | V3-MAX | 0.005 | 0.008 | 0.0010 | 0.0006 | 0.0009 | 0.001 |
| 0.001 | loo | V3-MAX-RBF | 0.007 | 0.009 | 0.001 | 0.0005 | 0.0009 | 0.001 |

## R10_context_ids2018. Share of benign flows with a sampled attack flow in their window (ids2018)

| part | n | network | 16 min | network | same minute |
|---|---|---|---|
| fit | 43446 | 0.323 | 0.251 |
| ref | 43447 | 0.324 | 0.252 |
| cal | 86893 | 0.324 | 0.252 |
| test | 86895 | 0.324 | 0.252 |
| reference_all | 86893 | 0.323 | 0.252 |

## R10_threshold_clean_ids2018. Threshold B from attack-free-window calibration flows (ids2018)

| nominal | scenario | model | recall_B | recall_Bclean | fpr_test_B | fpr_cleantest_B | fpr_cleantest_Bclean | fpr_attackwindow_test_B |
|---|---|---|---|---|---|---|---|---|
| 0.010 | known | TREE | 0.312 | 0.310 | 0.005 | 0.005 | 0.005 | 0.005 |
| 0.010 | known | V3-SUP | 0.340 | 0.331 | 0.010 | 0.011 | 0.010 | 0.008 |
| 0.010 | loo | TREE | 0.274 | 0.269 | 0.008 | 0.008 | 0.007 | 0.007 |
| 0.010 | loo | V3-SUP | 0.273 | 0.271 | 0.010 | 0.011 | 0.010 | 0.008 |
| 0.001 | known | TREE | 0.193 | 0.180 | 0.0008 | 0.0009 | 0.0008 | 0.0005 |
| 0.001 | known | V3-SUP | 0.195 | 0.182 | 0.0009 | 0.001 | 0.0009 | 0.0007 |
| 0.001 | loo | TREE | 0.147 | 0.138 | 0.0008 | 0.0008 | 0.0008 | 0.0007 |
| 0.001 | loo | V3-SUP | 0.151 | 0.149 | 0.0009 | 0.001 | 0.0009 | 0.0007 |

## R10_conflict_bounds. CIC-UNSW-NB15: recall bounds had the conflicting rows been kept

| scenario | model | types | macro_recall | macro_low_none_detected | macro_high_all_detected |
|---|---|---|---|---|---|
| known | TREE | 9 | 0.027 | 0.025 | 0.088 |
| known | V3-SUP | 9 | 0.023 | 0.021 | 0.084 |
| known | V3-SUP-DENSE | 9 | 0.023 | 0.021 | 0.084 |
| known | V3-SUP-NOA | 9 | 0.016 | 0.015 | 0.078 |
| known | V3-MAX | 9 | 0.163 | 0.139 | 0.202 |
| known | V3-MAX-RBF | 9 | 0.161 | 0.137 | 0.200 |
| loo | TREE | 2 | 0.021 | 0.020 | 0.157 |
| loo | V3-SUP | 2 | 0.018 | 0.017 | 0.154 |
| loo | V3-SUP-DENSE | 2 | 0.018 | 0.017 | 0.154 |
| loo | V3-SUP-NOA | 2 | 0.018 | 0.018 | 0.155 |
| loo | V3-MAX | 2 | 0.388 | 0.302 | 0.439 |
| loo | V3-MAX-RBF | 2 | 0.377 | 0.294 | 0.431 |

## R10_conflict_composition. CIC-UNSW-NB15: removed conflicting rows by label and kind

| lab | attack row sharing a vector with another attack type only | attack row sharing a vector with benign | benign row | All |
|---|---|---|---|---|
| Benign | 0 | 0 | 558 | 558 |
| DoS | 110 | 18 | 0 | 128 |
| Exploits | 43 | 4 | 0 | 47 |
| Fuzzers | 242 | 1930 | 0 | 2172 |
| Generic | 123 | 15 | 0 | 138 |
| Reconnaissance | 75 | 3832 | 0 | 3907 |
| Shellcode | 216 | 32 | 0 | 248 |
| Worms | 6 | 0 | 0 | 6 |
| All | 815 | 5831 | 558 | 7204 |

## R11_scores_cross. Attack-family naming, CSE-CIC-IDS2018 (mean over seeds and tasks)

| scenario | tau | families_trained | n_known_flows | n_unknown_flows | cls_n | cls_acc_known | cls_macro_f1_known | cls_macro_f1_with_unknown | cls_unknown_recall | cls_false_unknown | e2e_n | e2e_acc_known | e2e_macro_f1_known | e2e_macro_f1_with_unknown | e2e_unknown_recall | e2e_false_unknown | auroc_new_vs_known | detected_share | false_alarms | false_alarms_called_unknown | recall_cls[Bot] | recall_cls[BruteForce] | recall_cls[DDoS] | recall_cls[DoS] | recall_cls[Infiltration] | recall_cls[Web] | recall_cls[unknown] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 0.961 | 7.000 | 117720.000 | 0.000 | 117720.000 | 0.171 | 0.154 | 0.154 |  | 0.487 | 34981.000 | 0.386 | 0.260 | 0.260 |  | 0.453 |  | 0.297 | 871.700 | 0.469 | 0.009 | 0.210 | 0.000 | 0.379 | 0.040 | 0.218 |  |
| loo | 0.968 | 6.750 | 4694.833 | 3767.583 | 8462.417 | 0.113 | 0.159 | 0.337 | 0.803 | 0.442 | 1554.517 | 0.094 | 0.127 | 0.278 | 0.706 | 0.529 |  | 0.273 | 863.725 | 0.639 |  | 0.0001 |  | 0.179 |  | 0.100 | 0.803 |

## R11_unsw_primary. Attack-family naming, CIC-UNSW-NB15 (mean over seeds and tasks)

| scenario | tau | families_trained | n_known_flows | n_unknown_flows | cls_n | cls_acc_known | cls_macro_f1_known | cls_macro_f1_with_unknown | cls_unknown_recall | cls_false_unknown | cls_dos_lenient_acc | e2e_n | e2e_acc_known | e2e_macro_f1_known | e2e_macro_f1_with_unknown | e2e_unknown_recall | e2e_false_unknown | e2e_dos_lenient_acc | auroc_new_vs_known | detected_share | false_alarms | false_alarms_called_unknown | recall_cls[DoS] | recall_cls[Scan] | recall_cls[unknown] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 0.961 | 7.000 | 16316.000 | 44811.000 | 61127.000 | 0.056 | 0.085 | 0.141 | 0.247 | 0.499 | 0.059 | 1743.900 | 0.013 | 0.027 | 0.096 | 0.123 | 0.183 | 0.020 | 0.330 | 0.029 | 618.500 | 0.256 | 0.058 | 0.055 | 0.247 |
| loo | 0.972 | 5.500 | 0.000 | 8158.000 | 8158.000 |  |  | 0.340 | 0.297 |  |  | 84.450 |  |  | 0.174 | 0.147 |  |  |  | 0.018 | 625.000 | 0.233 |  |  | 0.297 |

## R11_scores_within. Attack-family naming, CIC-IDS2017 (mean over seeds and tasks)

| scenario | tau | families_trained | n_known_flows | n_unknown_flows | cls_n | cls_acc_known | cls_macro_f1_known | cls_macro_f1_with_unknown | cls_unknown_recall | cls_false_unknown | e2e_n | e2e_acc_known | e2e_macro_f1_known | e2e_macro_f1_with_unknown | e2e_unknown_recall | e2e_false_unknown | auroc_new_vs_known | detected_share | false_alarms | false_alarms_called_unknown | recall_cls[Bot] | recall_cls[BruteForce] | recall_cls[DDoS] | recall_cls[DoS] | recall_cls[Infiltration] | recall_cls[Scan] | recall_cls[Web] | recall_cls[unknown] |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| known | 0.961 | 7.000 | 64543.000 | 2.000 | 64545.000 | 0.861 | 0.733 | 0.641 | 0.050 | 0.128 | 64476.100 | 0.862 | 0.760 | 0.733 | 0.000 | 0.128 | 0.098 | 0.999 | 3581.200 | 0.709 | 0.918 | 0.721 | 0.762 | 0.949 | 0.111 | 0.630 | 0.903 | 0.050 |

## R12_unsw_primary. Derived metrics from unsw_primary/metrics_overall.csv

| protocol | scenario | op | seed | model | TP | FN | FP | TN | accuracy | precision | recall | f1 | fpr | specificity | balanced_acc | mcc | prevalence | precision_at_prev1 | macro_recall | macro_recall_nontiny | auc | pauc1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cross | known | 0.1% | 0 | TREE | 284 | 60843 | 67.000 | 63568.000 | 0.512 | 0.809 | 0.005 | 0.009 | 0.001 | 0.999 | 0.502 | 0.034 | 0.490 | 0.043 | 0.003 | 0.003 | 0.541 | 0.506 |
| cross | known | 0.1% | 0 | V3-MAX | 417 | 60710 | 51.000 | 63584.000 | 0.513 | 0.891 | 0.007 | 0.014 | 0.0008 | 0.999 | 0.503 | 0.049 | 0.490 | 0.079 | 0.007 | 0.007 | 0.805 | 0.548 |
| cross | known | 0.1% | 0 | V3-MAX-RBF | 944 | 60183 | 50.000 | 63585.000 | 0.517 | 0.950 | 0.015 | 0.030 | 0.0008 | 0.999 | 0.507 | 0.082 | 0.490 | 0.166 | 0.016 | 0.016 | 0.767 | 0.545 |
| cross | known | 0.1% | 0 | V3-SUP | 58 | 61069 | 55.000 | 63580.000 | 0.510 | 0.513 | 0.0009 | 0.002 | 0.0009 | 0.999 | 0.500 | 0.001 | 0.490 | 0.011 | 0.0004 | 0.0004 | 0.625 | 0.499 |
| cross | known | 0.1% | 0 | V3-SUP-DENSE | 268 | 60859 | 49.000 | 63586.000 | 0.512 | 0.845 | 0.004 | 0.009 | 0.0008 | 0.999 | 0.502 | 0.036 | 0.490 | 0.054 | 0.002 | 0.002 | 0.676 | 0.501 |
| cross | known | 0.1% | 0 | V3-SUP-NOA | 92 | 61035 | 48.000 | 63587.000 | 0.510 | 0.657 | 0.002 | 0.003 | 0.0008 | 0.999 | 0.500 | 0.011 | 0.490 | 0.020 | 0.0006 | 0.0006 | 0.621 | 0.498 |
| cross | known | 0.1% | 1 | TREE | 297 | 60830 | 67.000 | 63568.000 | 0.512 | 0.816 | 0.005 | 0.010 | 0.001 | 0.999 | 0.502 | 0.035 | 0.490 | 0.045 | 0.003 | 0.003 | 0.682 | 0.503 |
| cross | known | 0.1% | 1 | V3-MAX | 583 | 60544 | 66.000 | 63569.000 | 0.514 | 0.898 | 0.010 | 0.019 | 0.001 | 0.999 | 0.504 | 0.059 | 0.490 | 0.085 | 0.010 | 0.010 | 0.795 | 0.554 |
| cross | known | 0.1% | 1 | V3-MAX-RBF | 754 | 60373 | 60.000 | 63575.000 | 0.516 | 0.926 | 0.012 | 0.024 | 0.0009 | 0.999 | 0.506 | 0.071 | 0.490 | 0.117 | 0.013 | 0.013 | 0.778 | 0.550 |
| cross | known | 0.1% | 1 | V3-SUP | 303 | 60824 | 78.000 | 63557.000 | 0.512 | 0.795 | 0.005 | 0.010 | 0.001 | 0.999 | 0.502 | 0.034 | 0.490 | 0.039 | 0.003 | 0.003 | 0.617 | 0.503 |
| cross | known | 0.1% | 1 | V3-SUP-DENSE | 302 | 60825 | 74.000 | 63561.000 | 0.512 | 0.803 | 0.005 | 0.010 | 0.001 | 0.999 | 0.502 | 0.034 | 0.490 | 0.041 | 0.003 | 0.003 | 0.773 | 0.503 |
| cross | known | 0.1% | 1 | V3-SUP-NOA | 297 | 60830 | 83.000 | 63552.000 | 0.512 | 0.782 | 0.005 | 0.010 | 0.001 | 0.999 | 0.502 | 0.032 | 0.490 | 0.036 | 0.003 | 0.003 | 0.627 | 0.503 |
| cross | known | 0.1% | 2 | TREE | 1051 | 60076 | 85.000 | 63550.000 | 0.518 | 0.925 | 0.017 | 0.034 | 0.001 | 0.999 | 0.508 | 0.083 | 0.490 | 0.115 | 0.010 | 0.010 | 0.661 | 0.506 |
| cross | known | 0.1% | 2 | V3-MAX | 1811 | 59316 | 79.000 | 63556.000 | 0.524 | 0.958 | 0.030 | 0.057 | 0.001 | 0.999 | 0.514 | 0.116 | 0.490 | 0.194 | 0.021 | 0.021 | 0.802 | 0.555 |
| cross | known | 0.1% | 2 | V3-MAX-RBF | 1864 | 59263 | 75.000 | 63560.000 | 0.524 | 0.961 | 0.030 | 0.059 | 0.001 | 0.999 | 0.515 | 0.118 | 0.490 | 0.207 | 0.022 | 0.022 | 0.773 | 0.553 |
| cross | known | 0.1% | 2 | V3-SUP | 987 | 60140 | 75.000 | 63560.000 | 0.517 | 0.929 | 0.016 | 0.032 | 0.001 | 0.999 | 0.507 | 0.081 | 0.490 | 0.122 | 0.009 | 0.009 | 0.672 | 0.506 |
| cross | known | 0.1% | 2 | V3-SUP-DENSE | 859 | 60268 | 78.000 | 63557.000 | 0.516 | 0.917 | 0.014 | 0.028 | 0.001 | 0.999 | 0.506 | 0.074 | 0.490 | 0.104 | 0.008 | 0.008 | 0.751 | 0.506 |
| cross | known | 0.1% | 2 | V3-SUP-NOA | 999 | 60128 | 77.000 | 63558.000 | 0.517 | 0.928 | 0.016 | 0.032 | 0.001 | 0.999 | 0.508 | 0.082 | 0.490 | 0.120 | 0.009 | 0.009 | 0.690 | 0.506 |
| cross | known | 0.1% | 3 | TREE | 787 | 60340 | 59.000 | 63576.000 | 0.516 | 0.930 | 0.013 | 0.025 | 0.0009 | 0.999 | 0.506 | 0.073 | 0.490 | 0.123 | 0.008 | 0.008 | 0.741 | 0.504 |
| cross | known | 0.1% | 3 | V3-MAX | 1079 | 60048 | 68.000 | 63567.000 | 0.518 | 0.941 | 0.018 | 0.035 | 0.001 | 0.999 | 0.508 | 0.087 | 0.490 | 0.143 | 0.015 | 0.015 | 0.814 | 0.553 |
| cross | known | 0.1% | 3 | V3-MAX-RBF | 1534 | 59593 | 75.000 | 63560.000 | 0.522 | 0.953 | 0.025 | 0.049 | 0.001 | 0.999 | 0.512 | 0.106 | 0.490 | 0.177 | 0.021 | 0.021 | 0.799 | 0.543 |
| cross | known | 0.1% | 3 | V3-SUP | 740 | 60387 | 64.000 | 63571.000 | 0.515 | 0.920 | 0.012 | 0.024 | 0.001 | 0.999 | 0.506 | 0.069 | 0.490 | 0.108 | 0.008 | 0.008 | 0.702 | 0.504 |
| cross | known | 0.1% | 3 | V3-SUP-DENSE | 648 | 60479 | 63.000 | 63572.000 | 0.515 | 0.911 | 0.011 | 0.021 | 0.0010 | 0.999 | 0.505 | 0.064 | 0.490 | 0.098 | 0.007 | 0.007 | 0.820 | 0.503 |
| cross | known | 0.1% | 3 | V3-SUP-NOA | 809 | 60318 | 65.000 | 63570.000 | 0.516 | 0.926 | 0.013 | 0.026 | 0.001 | 0.999 | 0.506 | 0.073 | 0.490 | 0.116 | 0.008 | 0.008 | 0.756 | 0.504 |
| cross | known | 0.1% | 4 | TREE | 145 | 60982 | 39.000 | 63596.000 | 0.511 | 0.788 | 0.002 | 0.005 | 0.0006 | 0.999 | 0.501 | 0.023 | 0.490 | 0.038 | 0.002 | 0.002 | 0.646 | 0.499 |
| cross | known | 0.1% | 4 | V3-MAX | 505 | 60622 | 67.000 | 63568.000 | 0.514 | 0.883 | 0.008 | 0.016 | 0.001 | 0.999 | 0.504 | 0.053 | 0.490 | 0.073 | 0.009 | 0.009 | 0.810 | 0.549 |
| cross | known | 0.1% | 4 | V3-MAX-RBF | 713 | 60414 | 65.000 | 63570.000 | 0.515 | 0.916 | 0.012 | 0.023 | 0.001 | 0.999 | 0.505 | 0.068 | 0.490 | 0.103 | 0.013 | 0.013 | 0.783 | 0.546 |
| cross | known | 0.1% | 4 | V3-SUP | 13 | 61114 | 83.000 | 63552.000 | 0.509 | 0.135 | 0.0002 | 0.0004 | 0.001 | 0.999 | 0.499 | -0.020 | 0.490 | 0.002 | 0.0001 | 0.0001 | 0.645 | 0.498 |
| cross | known | 0.1% | 4 | V3-SUP-DENSE | 13 | 61114 | 70.000 | 63565.000 | 0.510 | 0.157 | 0.0002 | 0.0004 | 0.001 | 0.999 | 0.500 | -0.017 | 0.490 | 0.002 | 0.0002 | 0.0002 | 0.633 | 0.498 |
| cross | known | 0.1% | 4 | V3-SUP-NOA | 0 | 61127 | 59.000 | 63576.000 | 0.510 | 0.000 | 0.000 | 0.000 | 0.0009 | 0.999 | 0.500 | -0.021 | 0.490 | 0.000 | 0.000 | 0.000 | 0.515 | 0.498 |
| cross | known | 0.1% | 5 | TREE | 1135 | 59992 | 46.000 | 63589.000 | 0.519 | 0.961 | 0.019 | 0.036 | 0.0007 | 0.999 | 0.509 | 0.092 | 0.490 | 0.206 | 0.014 | 0.014 | 0.695 | 0.508 |
| cross | known | 0.1% | 5 | V3-MAX | 666 | 60461 | 50.000 | 63585.000 | 0.515 | 0.930 | 0.011 | 0.022 | 0.0008 | 0.999 | 0.505 | 0.067 | 0.490 | 0.123 | 0.009 | 0.009 | 0.809 | 0.553 |
| cross | known | 0.1% | 5 | V3-MAX-RBF | 837 | 60290 | 53.000 | 63582.000 | 0.516 | 0.940 | 0.014 | 0.027 | 0.0008 | 0.999 | 0.506 | 0.076 | 0.490 | 0.142 | 0.014 | 0.014 | 0.769 | 0.544 |
| cross | known | 0.1% | 5 | V3-SUP | 226 | 60901 | 72.000 | 63563.000 | 0.511 | 0.758 | 0.004 | 0.007 | 0.001 | 0.999 | 0.501 | 0.026 | 0.490 | 0.032 | 0.002 | 0.002 | 0.693 | 0.500 |
| cross | known | 0.1% | 5 | V3-SUP-DENSE | 638 | 60489 | 70.000 | 63565.000 | 0.515 | 0.901 | 0.010 | 0.021 | 0.001 | 0.999 | 0.505 | 0.062 | 0.490 | 0.087 | 0.007 | 0.007 | 0.767 | 0.503 |
| cross | known | 0.1% | 5 | V3-SUP-NOA | 395 | 60732 | 67.000 | 63568.000 | 0.513 | 0.855 | 0.006 | 0.013 | 0.001 | 0.999 | 0.503 | 0.045 | 0.490 | 0.058 | 0.003 | 0.003 | 0.653 | 0.502 |
| cross | known | 0.1% | 6 | TREE | 66 | 61061 | 41.000 | 63594.000 | 0.510 | 0.617 | 0.001 | 0.002 | 0.0006 | 0.999 | 0.500 | 0.007 | 0.490 | 0.017 | 0.0005 | 0.0005 | 0.657 | 0.499 |
| cross | known | 0.1% | 6 | V3-MAX | 241 | 60886 | 46.000 | 63589.000 | 0.512 | 0.840 | 0.004 | 0.008 | 0.0007 | 0.999 | 0.502 | 0.034 | 0.490 | 0.052 | 0.002 | 0.002 | 0.806 | 0.548 |
| cross | known | 0.1% | 6 | V3-MAX-RBF | 668 | 60459 | 63.000 | 63572.000 | 0.515 | 0.914 | 0.011 | 0.022 | 0.0010 | 0.999 | 0.505 | 0.065 | 0.490 | 0.100 | 0.006 | 0.006 | 0.758 | 0.544 |
| cross | known | 0.1% | 6 | V3-SUP | 0 | 61127 | 56.000 | 63579.000 | 0.510 | 0.000 | 0.000 | 0.000 | 0.0009 | 0.999 | 0.500 | -0.021 | 0.490 | 0.000 | 0.000 | 0.000 | 0.583 | 0.498 |
| cross | known | 0.1% | 6 | V3-SUP-DENSE | 37 | 61090 | 81.000 | 63554.000 | 0.510 | 0.314 | 0.0006 | 0.001 | 0.001 | 0.999 | 0.500 | -0.011 | 0.490 | 0.005 | 0.0003 | 0.0003 | 0.719 | 0.498 |
| cross | known | 0.1% | 6 | V3-SUP-NOA | 18 | 61109 | 73.000 | 63562.000 | 0.510 | 0.198 | 0.0003 | 0.0006 | 0.001 | 0.999 | 0.500 | -0.016 | 0.490 | 0.003 | 0.0001 | 0.0001 | 0.644 | 0.498 |
| cross | known | 0.1% | 7 | TREE | 1133 | 59994 | 65.000 | 63570.000 | 0.519 | 0.946 | 0.019 | 0.036 | 0.001 | 0.999 | 0.509 | 0.090 | 0.490 | 0.155 | 0.011 | 0.011 | 0.690 | 0.507 |
| cross | known | 0.1% | 7 | V3-MAX | 1311 | 59816 | 63.000 | 63572.000 | 0.520 | 0.954 | 0.021 | 0.042 | 0.0010 | 0.999 | 0.510 | 0.098 | 0.490 | 0.180 | 0.016 | 0.016 | 0.829 | 0.554 |
| cross | known | 0.1% | 7 | V3-MAX-RBF | 1797 | 59330 | 69.000 | 63566.000 | 0.524 | 0.963 | 0.029 | 0.057 | 0.001 | 0.999 | 0.514 | 0.117 | 0.490 | 0.215 | 0.024 | 0.024 | 0.803 | 0.546 |
| cross | known | 0.1% | 7 | V3-SUP | 924 | 60203 | 63.000 | 63572.000 | 0.517 | 0.936 | 0.015 | 0.030 | 0.0010 | 0.999 | 0.507 | 0.080 | 0.490 | 0.134 | 0.009 | 0.009 | 0.622 | 0.505 |
| cross | known | 0.1% | 7 | V3-SUP-DENSE | 517 | 60610 | 69.000 | 63566.000 | 0.514 | 0.882 | 0.008 | 0.017 | 0.001 | 0.999 | 0.504 | 0.054 | 0.490 | 0.073 | 0.006 | 0.006 | 0.699 | 0.502 |
| cross | known | 0.1% | 7 | V3-SUP-NOA | 510 | 60617 | 60.000 | 63575.000 | 0.514 | 0.895 | 0.008 | 0.017 | 0.0009 | 0.999 | 0.504 | 0.055 | 0.490 | 0.082 | 0.006 | 0.006 | 0.612 | 0.502 |
| cross | known | 0.1% | 8 | TREE | 793 | 60334 | 54.000 | 63581.000 | 0.516 | 0.936 | 0.013 | 0.026 | 0.0008 | 0.999 | 0.506 | 0.074 | 0.490 | 0.134 | 0.008 | 0.008 | 0.663 | 0.505 |
| cross | known | 0.1% | 8 | V3-MAX | 1173 | 59954 | 76.000 | 63559.000 | 0.519 | 0.939 | 0.019 | 0.038 | 0.001 | 0.999 | 0.509 | 0.090 | 0.490 | 0.140 | 0.015 | 0.015 | 0.786 | 0.562 |
| cross | known | 0.1% | 8 | V3-MAX-RBF | 1102 | 60025 | 73.000 | 63562.000 | 0.518 | 0.938 | 0.018 | 0.035 | 0.001 | 0.999 | 0.508 | 0.087 | 0.490 | 0.137 | 0.012 | 0.012 | 0.729 | 0.554 |
| cross | known | 0.1% | 8 | V3-SUP | 539 | 60588 | 61.000 | 63574.000 | 0.514 | 0.898 | 0.009 | 0.017 | 0.0010 | 0.999 | 0.504 | 0.057 | 0.490 | 0.085 | 0.007 | 0.007 | 0.432 | 0.506 |
| cross | known | 0.1% | 8 | V3-SUP-DENSE | 819 | 60308 | 62.000 | 63573.000 | 0.516 | 0.930 | 0.013 | 0.026 | 0.0010 | 0.999 | 0.506 | 0.074 | 0.490 | 0.122 | 0.008 | 0.008 | 0.643 | 0.505 |
| cross | known | 0.1% | 8 | V3-SUP-NOA | 768 | 60359 | 56.000 | 63579.000 | 0.516 | 0.932 | 0.013 | 0.025 | 0.0009 | 0.999 | 0.506 | 0.072 | 0.490 | 0.126 | 0.008 | 0.008 | 0.560 | 0.504 |
| cross | known | 0.1% | 9 | TREE | 2955 | 58172 | 65.000 | 63570.000 | 0.533 | 0.978 | 0.048 | 0.092 | 0.001 | 0.999 | 0.524 | 0.154 | 0.490 | 0.323 | 0.040 | 0.040 | 0.886 | 0.548 |
| cross | known | 0.1% | 9 | V3-MAX | 2451 | 58676 | 69.000 | 63566.000 | 0.529 | 0.973 | 0.040 | 0.077 | 0.001 | 0.999 | 0.520 | 0.139 | 0.490 | 0.272 | 0.035 | 0.035 | 0.890 | 0.580 |
| cross | known | 0.1% | 9 | V3-MAX-RBF | 2966 | 58161 | 85.000 | 63550.000 | 0.533 | 0.972 | 0.049 | 0.092 | 0.001 | 0.999 | 0.524 | 0.153 | 0.490 | 0.268 | 0.042 | 0.042 | 0.875 | 0.579 |
| cross | known | 0.1% | 9 | V3-SUP | 2944 | 58183 | 63.000 | 63572.000 | 0.533 | 0.979 | 0.048 | 0.092 | 0.0010 | 0.999 | 0.524 | 0.154 | 0.490 | 0.329 | 0.039 | 0.039 | 0.824 | 0.548 |
| cross | known | 0.1% | 9 | V3-SUP-DENSE | 2955 | 58172 | 65.000 | 63570.000 | 0.533 | 0.978 | 0.048 | 0.092 | 0.001 | 0.999 | 0.524 | 0.154 | 0.490 | 0.323 | 0.040 | 0.040 | 0.864 | 0.548 |
| cross | known | 0.1% | 9 | V3-SUP-NOA | 1729 | 59398 | 81.000 | 63554.000 | 0.523 | 0.955 | 0.028 | 0.055 | 0.001 | 0.999 | 0.514 | 0.113 | 0.490 | 0.183 | 0.020 | 0.020 | 0.845 | 0.544 |
| cross | known | 1% | 0 | TREE | 1668 | 59459 | 491.000 | 63144.000 | 0.519 | 0.773 | 0.027 | 0.053 | 0.008 | 0.992 | 0.510 | 0.075 | 0.490 | 0.034 | 0.027 | 0.027 | 0.541 | 0.506 |
| cross | known | 1% | 0 | V3-MAX | 11907 | 49220 | 628.000 | 63007.000 | 0.600 | 0.950 | 0.195 | 0.323 | 0.010 | 0.990 | 0.592 | 0.307 | 0.490 | 0.166 | 0.154 | 0.154 | 0.805 | 0.548 |
| cross | known | 1% | 0 | V3-MAX-RBF | 11945 | 49182 | 635.000 | 63000.000 | 0.601 | 0.950 | 0.195 | 0.324 | 0.010 | 0.990 | 0.593 | 0.308 | 0.490 | 0.165 | 0.154 | 0.154 | 0.767 | 0.545 |
| cross | known | 1% | 0 | V3-SUP | 265 | 60862 | 611.000 | 63024.000 | 0.507 | 0.303 | 0.004 | 0.009 | 0.010 | 0.990 | 0.497 | -0.032 | 0.490 | 0.005 | 0.003 | 0.003 | 0.625 | 0.499 |
| cross | known | 1% | 0 | V3-SUP-DENSE | 508 | 60619 | 627.000 | 63008.000 | 0.509 | 0.448 | 0.008 | 0.016 | 0.010 | 0.990 | 0.499 | -0.008 | 0.490 | 0.008 | 0.003 | 0.003 | 0.676 | 0.501 |
| cross | known | 1% | 0 | V3-SUP-NOA | 113 | 61014 | 591.000 | 63044.000 | 0.506 | 0.161 | 0.002 | 0.004 | 0.009 | 0.991 | 0.496 | -0.050 | 0.490 | 0.002 | 0.0007 | 0.0007 | 0.621 | 0.498 |
| cross | known | 1% | 1 | TREE | 798 | 60329 | 319.000 | 63316.000 | 0.514 | 0.714 | 0.013 | 0.026 | 0.005 | 0.995 | 0.504 | 0.043 | 0.490 | 0.026 | 0.010 | 0.010 | 0.682 | 0.503 |
| cross | known | 1% | 1 | V3-MAX | 12431 | 48696 | 633.000 | 63002.000 | 0.605 | 0.952 | 0.203 | 0.335 | 0.010 | 0.990 | 0.597 | 0.316 | 0.490 | 0.171 | 0.158 | 0.158 | 0.795 | 0.554 |
| cross | known | 1% | 1 | V3-MAX-RBF | 12387 | 48740 | 629.000 | 63006.000 | 0.604 | 0.952 | 0.203 | 0.334 | 0.010 | 0.990 | 0.596 | 0.315 | 0.490 | 0.172 | 0.158 | 0.158 | 0.778 | 0.550 |
| cross | known | 1% | 1 | V3-SUP | 814 | 60313 | 610.000 | 63025.000 | 0.512 | 0.572 | 0.013 | 0.026 | 0.010 | 0.990 | 0.502 | 0.018 | 0.490 | 0.014 | 0.010 | 0.010 | 0.617 | 0.503 |
| cross | known | 1% | 1 | V3-SUP-DENSE | 818 | 60309 | 612.000 | 63023.000 | 0.512 | 0.572 | 0.013 | 0.026 | 0.010 | 0.990 | 0.502 | 0.018 | 0.490 | 0.014 | 0.010 | 0.010 | 0.773 | 0.503 |
| cross | known | 1% | 1 | V3-SUP-NOA | 799 | 60328 | 597.000 | 63038.000 | 0.512 | 0.572 | 0.013 | 0.026 | 0.009 | 0.991 | 0.502 | 0.018 | 0.490 | 0.014 | 0.010 | 0.010 | 0.627 | 0.503 |
| cross | known | 1% | 2 | TREE | 1161 | 59966 | 674.000 | 62961.000 | 0.514 | 0.633 | 0.019 | 0.037 | 0.011 | 0.989 | 0.504 | 0.035 | 0.490 | 0.018 | 0.011 | 0.011 | 0.661 | 0.506 |
| cross | known | 1% | 2 | V3-MAX | 12829 | 48298 | 619.000 | 63016.000 | 0.608 | 0.954 | 0.210 | 0.344 | 0.010 | 0.990 | 0.600 | 0.323 | 0.490 | 0.179 | 0.162 | 0.162 | 0.802 | 0.555 |
| cross | known | 1% | 2 | V3-MAX-RBF | 12828 | 48299 | 648.000 | 62987.000 | 0.608 | 0.952 | 0.210 | 0.344 | 0.010 | 0.990 | 0.600 | 0.322 | 0.490 | 0.172 | 0.162 | 0.162 | 0.773 | 0.553 |
| cross | known | 1% | 2 | V3-SUP | 1235 | 59892 | 634.000 | 63001.000 | 0.515 | 0.661 | 0.020 | 0.039 | 0.010 | 0.990 | 0.505 | 0.042 | 0.490 | 0.020 | 0.011 | 0.011 | 0.672 | 0.506 |
| cross | known | 1% | 2 | V3-SUP-DENSE | 1188 | 59939 | 683.000 | 62952.000 | 0.514 | 0.635 | 0.019 | 0.038 | 0.011 | 0.989 | 0.504 | 0.036 | 0.490 | 0.018 | 0.011 | 0.011 | 0.751 | 0.506 |
| cross | known | 1% | 2 | V3-SUP-NOA | 1119 | 60008 | 649.000 | 62986.000 | 0.514 | 0.633 | 0.018 | 0.036 | 0.010 | 0.990 | 0.504 | 0.034 | 0.490 | 0.018 | 0.010 | 0.010 | 0.690 | 0.506 |
| cross | known | 1% | 3 | TREE | 844 | 60283 | 583.000 | 63052.000 | 0.512 | 0.591 | 0.014 | 0.027 | 0.009 | 0.991 | 0.502 | 0.022 | 0.490 | 0.015 | 0.008 | 0.008 | 0.741 | 0.504 |
| cross | known | 1% | 3 | V3-MAX | 12628 | 48499 | 605.000 | 63030.000 | 0.606 | 0.954 | 0.207 | 0.340 | 0.010 | 0.990 | 0.599 | 0.320 | 0.490 | 0.180 | 0.160 | 0.160 | 0.814 | 0.553 |
| cross | known | 1% | 3 | V3-MAX-RBF | 9892 | 51235 | 630.000 | 63005.000 | 0.584 | 0.940 | 0.162 | 0.276 | 0.010 | 0.990 | 0.576 | 0.273 | 0.490 | 0.142 | 0.134 | 0.134 | 0.799 | 0.543 |
| cross | known | 1% | 3 | V3-SUP | 872 | 60255 | 616.000 | 63019.000 | 0.512 | 0.586 | 0.014 | 0.028 | 0.010 | 0.990 | 0.502 | 0.021 | 0.490 | 0.015 | 0.009 | 0.009 | 0.702 | 0.504 |
| cross | known | 1% | 3 | V3-SUP-DENSE | 757 | 60370 | 595.000 | 63040.000 | 0.511 | 0.560 | 0.012 | 0.024 | 0.009 | 0.991 | 0.502 | 0.015 | 0.490 | 0.013 | 0.008 | 0.008 | 0.820 | 0.503 |
| cross | known | 1% | 3 | V3-SUP-NOA | 882 | 60245 | 610.000 | 63025.000 | 0.512 | 0.591 | 0.014 | 0.028 | 0.010 | 0.990 | 0.502 | 0.022 | 0.490 | 0.015 | 0.009 | 0.009 | 0.756 | 0.504 |
| cross | known | 1% | 4 | TREE | 259 | 60868 | 430.000 | 63205.000 | 0.509 | 0.376 | 0.004 | 0.008 | 0.007 | 0.993 | 0.499 | -0.017 | 0.490 | 0.006 | 0.003 | 0.003 | 0.646 | 0.499 |
| cross | known | 1% | 4 | V3-MAX | 12232 | 48895 | 657.000 | 62978.000 | 0.603 | 0.949 | 0.200 | 0.331 | 0.010 | 0.990 | 0.595 | 0.312 | 0.490 | 0.164 | 0.157 | 0.157 | 0.810 | 0.549 |
| cross | known | 1% | 4 | V3-MAX-RBF | 12161 | 48966 | 645.000 | 62990.000 | 0.602 | 0.950 | 0.199 | 0.329 | 0.010 | 0.990 | 0.594 | 0.311 | 0.490 | 0.165 | 0.157 | 0.157 | 0.783 | 0.546 |
| cross | known | 1% | 4 | V3-SUP | 180 | 60947 | 634.000 | 63001.000 | 0.506 | 0.221 | 0.003 | 0.006 | 0.010 | 0.990 | 0.496 | -0.044 | 0.490 | 0.003 | 0.002 | 0.002 | 0.645 | 0.498 |
| cross | known | 1% | 4 | V3-SUP-DENSE | 216 | 60911 | 638.000 | 62997.000 | 0.507 | 0.253 | 0.004 | 0.007 | 0.010 | 0.990 | 0.497 | -0.039 | 0.490 | 0.004 | 0.003 | 0.003 | 0.633 | 0.498 |
| cross | known | 1% | 4 | V3-SUP-NOA | 3 | 61124 | 664.000 | 62971.000 | 0.505 | 0.004 | 0.0000 | 0.0001 | 0.010 | 0.990 | 0.495 | -0.071 | 0.490 | 0.0000 | 0.0000 | 0.0000 | 0.515 | 0.498 |
| cross | known | 1% | 5 | TREE | 1367 | 59760 | 523.000 | 63112.000 | 0.517 | 0.723 | 0.022 | 0.043 | 0.008 | 0.992 | 0.507 | 0.058 | 0.490 | 0.027 | 0.017 | 0.017 | 0.695 | 0.508 |
| cross | known | 1% | 5 | V3-MAX | 12081 | 49046 | 626.000 | 63009.000 | 0.602 | 0.951 | 0.198 | 0.327 | 0.010 | 0.990 | 0.594 | 0.310 | 0.490 | 0.169 | 0.154 | 0.154 | 0.809 | 0.553 |
| cross | known | 1% | 5 | V3-MAX-RBF | 12084 | 49043 | 628.000 | 63007.000 | 0.602 | 0.951 | 0.198 | 0.327 | 0.010 | 0.990 | 0.594 | 0.310 | 0.490 | 0.168 | 0.155 | 0.155 | 0.769 | 0.544 |
| cross | known | 1% | 5 | V3-SUP | 376 | 60751 | 595.000 | 63040.000 | 0.508 | 0.387 | 0.006 | 0.012 | 0.009 | 0.991 | 0.498 | -0.018 | 0.490 | 0.007 | 0.004 | 0.004 | 0.693 | 0.500 |
| cross | known | 1% | 5 | V3-SUP-DENSE | 739 | 60388 | 646.000 | 62989.000 | 0.511 | 0.534 | 0.012 | 0.024 | 0.010 | 0.990 | 0.501 | 0.009 | 0.490 | 0.012 | 0.009 | 0.009 | 0.767 | 0.503 |
| cross | known | 1% | 5 | V3-SUP-NOA | 682 | 60445 | 608.000 | 63027.000 | 0.511 | 0.529 | 0.011 | 0.022 | 0.010 | 0.990 | 0.501 | 0.008 | 0.490 | 0.012 | 0.007 | 0.007 | 0.653 | 0.502 |
| cross | known | 1% | 6 | TREE | 185 | 60942 | 376.000 | 63259.000 | 0.509 | 0.330 | 0.003 | 0.006 | 0.006 | 0.994 | 0.499 | -0.022 | 0.490 | 0.005 | 0.001 | 0.001 | 0.657 | 0.499 |
| cross | known | 1% | 6 | V3-MAX | 11889 | 49238 | 640.000 | 62995.000 | 0.600 | 0.949 | 0.194 | 0.323 | 0.010 | 0.990 | 0.592 | 0.307 | 0.490 | 0.163 | 0.153 | 0.153 | 0.806 | 0.548 |
| cross | known | 1% | 6 | V3-MAX-RBF | 11853 | 49274 | 635.000 | 63000.000 | 0.600 | 0.949 | 0.194 | 0.322 | 0.010 | 0.990 | 0.592 | 0.306 | 0.490 | 0.164 | 0.153 | 0.153 | 0.758 | 0.544 |
| cross | known | 1% | 6 | V3-SUP | 16 | 61111 | 653.000 | 62982.000 | 0.505 | 0.024 | 0.0003 | 0.0005 | 0.010 | 0.990 | 0.495 | -0.068 | 0.490 | 0.0003 | 0.0001 | 0.0001 | 0.583 | 0.498 |
| cross | known | 1% | 6 | V3-SUP-DENSE | 99 | 61028 | 616.000 | 63019.000 | 0.506 | 0.138 | 0.002 | 0.003 | 0.010 | 0.990 | 0.496 | -0.053 | 0.490 | 0.002 | 0.0009 | 0.0009 | 0.719 | 0.498 |
| cross | known | 1% | 6 | V3-SUP-NOA | 35 | 61092 | 647.000 | 62988.000 | 0.505 | 0.051 | 0.0006 | 0.001 | 0.010 | 0.990 | 0.495 | -0.065 | 0.490 | 0.0006 | 0.0003 | 0.0003 | 0.644 | 0.498 |
| cross | known | 1% | 7 | TREE | 1246 | 59881 | 105.000 | 63530.000 | 0.519 | 0.922 | 0.020 | 0.040 | 0.002 | 0.998 | 0.509 | 0.090 | 0.490 | 0.111 | 0.013 | 0.013 | 0.690 | 0.507 |
| cross | known | 1% | 7 | V3-MAX | 12568 | 48559 | 632.000 | 63003.000 | 0.606 | 0.952 | 0.206 | 0.338 | 0.010 | 0.990 | 0.598 | 0.318 | 0.490 | 0.173 | 0.158 | 0.158 | 0.829 | 0.554 |
| cross | known | 1% | 7 | V3-MAX-RBF | 12620 | 48507 | 640.000 | 62995.000 | 0.606 | 0.952 | 0.206 | 0.339 | 0.010 | 0.990 | 0.598 | 0.319 | 0.490 | 0.172 | 0.159 | 0.159 | 0.803 | 0.546 |
| cross | known | 1% | 7 | V3-SUP | 988 | 60139 | 605.000 | 63030.000 | 0.513 | 0.620 | 0.016 | 0.032 | 0.010 | 0.990 | 0.503 | 0.030 | 0.490 | 0.017 | 0.009 | 0.009 | 0.622 | 0.505 |
| cross | known | 1% | 7 | V3-SUP-DENSE | 552 | 60575 | 652.000 | 62983.000 | 0.509 | 0.458 | 0.009 | 0.018 | 0.010 | 0.990 | 0.499 | -0.006 | 0.490 | 0.009 | 0.006 | 0.006 | 0.699 | 0.502 |
| cross | known | 1% | 7 | V3-SUP-NOA | 719 | 60408 | 645.000 | 62990.000 | 0.511 | 0.527 | 0.012 | 0.023 | 0.010 | 0.990 | 0.501 | 0.008 | 0.490 | 0.012 | 0.008 | 0.008 | 0.612 | 0.502 |
| cross | known | 1% | 8 | TREE | 1074 | 60053 | 630.000 | 63005.000 | 0.514 | 0.630 | 0.018 | 0.034 | 0.010 | 0.990 | 0.504 | 0.033 | 0.490 | 0.018 | 0.010 | 0.010 | 0.663 | 0.505 |
| cross | known | 1% | 8 | V3-MAX | 12666 | 48461 | 655.000 | 62980.000 | 0.606 | 0.951 | 0.207 | 0.340 | 0.010 | 0.990 | 0.598 | 0.319 | 0.490 | 0.169 | 0.163 | 0.163 | 0.786 | 0.562 |
| cross | known | 1% | 8 | V3-MAX-RBF | 12694 | 48433 | 660.000 | 62975.000 | 0.607 | 0.951 | 0.208 | 0.341 | 0.010 | 0.990 | 0.599 | 0.319 | 0.490 | 0.168 | 0.164 | 0.164 | 0.729 | 0.554 |
| cross | known | 1% | 8 | V3-SUP | 1365 | 59762 | 636.000 | 62999.000 | 0.516 | 0.682 | 0.022 | 0.043 | 0.010 | 0.990 | 0.506 | 0.049 | 0.490 | 0.022 | 0.016 | 0.016 | 0.432 | 0.506 |
| cross | known | 1% | 8 | V3-SUP-DENSE | 1103 | 60024 | 640.000 | 62995.000 | 0.514 | 0.633 | 0.018 | 0.035 | 0.010 | 0.990 | 0.504 | 0.034 | 0.490 | 0.018 | 0.011 | 0.011 | 0.643 | 0.505 |
| cross | known | 1% | 8 | V3-SUP-NOA | 922 | 60205 | 636.000 | 62999.000 | 0.512 | 0.592 | 0.015 | 0.029 | 0.010 | 0.990 | 0.503 | 0.023 | 0.490 | 0.015 | 0.009 | 0.009 | 0.560 | 0.504 |
| cross | known | 1% | 9 | TREE | 11325 | 49802 | 591.000 | 63044.000 | 0.596 | 0.950 | 0.185 | 0.310 | 0.009 | 0.991 | 0.588 | 0.299 | 0.490 | 0.168 | 0.167 | 0.167 | 0.886 | 0.548 |
| cross | known | 1% | 9 | V3-MAX | 16137 | 44990 | 629.000 | 63006.000 | 0.634 | 0.962 | 0.264 | 0.414 | 0.010 | 0.990 | 0.627 | 0.372 | 0.490 | 0.212 | 0.216 | 0.216 | 0.890 | 0.580 |
| cross | known | 1% | 9 | V3-MAX-RBF | 15941 | 45186 | 621.000 | 63014.000 | 0.633 | 0.963 | 0.261 | 0.410 | 0.010 | 0.990 | 0.626 | 0.370 | 0.490 | 0.213 | 0.215 | 0.215 | 0.875 | 0.579 |
| cross | known | 1% | 9 | V3-SUP | 11328 | 49799 | 591.000 | 63044.000 | 0.596 | 0.950 | 0.185 | 0.310 | 0.009 | 0.991 | 0.588 | 0.299 | 0.490 | 0.168 | 0.167 | 0.167 | 0.824 | 0.548 |
| cross | known | 1% | 9 | V3-SUP-DENSE | 11333 | 49794 | 592.000 | 63043.000 | 0.596 | 0.950 | 0.185 | 0.310 | 0.009 | 0.991 | 0.588 | 0.299 | 0.490 | 0.168 | 0.167 | 0.167 | 0.864 | 0.548 |
| cross | known | 1% | 9 | V3-SUP-NOA | 9230 | 51897 | 598.000 | 63037.000 | 0.579 | 0.939 | 0.151 | 0.260 | 0.009 | 0.991 | 0.571 | 0.263 | 0.490 | 0.140 | 0.110 | 0.110 | 0.845 | 0.544 |
| cross | loo | 0.1% | 0 | TREE | 6 | 16310 | 41.000 | 63594.000 | 0.795 | 0.128 | 0.0004 | 0.0007 | 0.0006 | 0.999 | 0.500 | -0.005 | 0.204 | 0.006 | 0.0003 | 0.0003 | 0.852 | 0.506 |
| cross | loo | 0.1% | 0 | V3-MAX | 5 | 16311 | 57.000 | 63578.000 | 0.795 | 0.081 | 0.0003 | 0.0006 | 0.0009 | 0.999 | 0.500 | -0.009 | 0.204 | 0.003 | 0.0004 | 0.0004 | 0.913 | 0.623 |
| cross | loo | 0.1% | 0 | V3-MAX-RBF | 53 | 16263 | 62.000 | 63573.000 | 0.796 | 0.461 | 0.003 | 0.006 | 0.0010 | 0.999 | 0.501 | 0.024 | 0.204 | 0.033 | 0.004 | 0.004 | 0.903 | 0.598 |
| cross | loo | 0.1% | 0 | V3-SUP | 5 | 16311 | 64.000 | 63571.000 | 0.795 | 0.072 | 0.0003 | 0.0006 | 0.001 | 0.999 | 0.500 | -0.010 | 0.204 | 0.003 | 0.0002 | 0.0002 | 0.806 | 0.504 |
| cross | loo | 0.1% | 0 | V3-SUP-DENSE | 6 | 16310 | 63.500 | 63571.500 | 0.795 | 0.086 | 0.0004 | 0.0007 | 0.0010 | 0.999 | 0.500 | -0.009 | 0.204 | 0.004 | 0.0003 | 0.0003 | 0.780 | 0.506 |
| cross | loo | 0.1% | 0 | V3-SUP-NOA | 3 | 16313 | 59.000 | 63576.000 | 0.795 | 0.048 | 0.0002 | 0.0004 | 0.0009 | 0.999 | 0.500 | -0.011 | 0.204 | 0.002 | 0.0001 | 0.0001 | 0.857 | 0.506 |
| cross | loo | 0.1% | 1 | TREE | 83 | 16233 | 57.000 | 63578.000 | 0.796 | 0.593 | 0.005 | 0.010 | 0.0009 | 0.999 | 0.502 | 0.040 | 0.204 | 0.054 | 0.010 | 0.010 | 0.763 | 0.501 |
| cross | loo | 0.1% | 1 | V3-MAX | 52 | 16264 | 64.500 | 63570.500 | 0.796 | 0.446 | 0.003 | 0.006 | 0.001 | 0.999 | 0.501 | 0.023 | 0.204 | 0.031 | 0.006 | 0.006 | 0.896 | 0.648 |
| cross | loo | 0.1% | 1 | V3-MAX-RBF | 84 | 16232 | 61.500 | 63573.500 | 0.796 | 0.577 | 0.005 | 0.010 | 0.0010 | 0.999 | 0.502 | 0.040 | 0.204 | 0.051 | 0.008 | 0.008 | 0.885 | 0.631 |
| cross | loo | 0.1% | 1 | V3-SUP | 55 | 16261 | 69.500 | 63565.500 | 0.796 | 0.442 | 0.003 | 0.007 | 0.001 | 0.999 | 0.501 | 0.023 | 0.204 | 0.030 | 0.006 | 0.006 | 0.787 | 0.502 |
| cross | loo | 0.1% | 1 | V3-SUP-DENSE | 61 | 16255 | 62.500 | 63572.500 | 0.796 | 0.494 | 0.004 | 0.007 | 0.0010 | 0.999 | 0.501 | 0.028 | 0.204 | 0.037 | 0.007 | 0.007 | 0.808 | 0.501 |
| cross | loo | 0.1% | 1 | V3-SUP-NOA | 5 | 16311 | 66.000 | 63569.000 | 0.795 | 0.070 | 0.0003 | 0.0006 | 0.001 | 0.999 | 0.500 | -0.010 | 0.204 | 0.003 | 0.0006 | 0.0006 | 0.783 | 0.499 |
| cross | loo | 0.1% | 2 | TREE | 79 | 16237 | 58.000 | 63577.000 | 0.796 | 0.577 | 0.005 | 0.010 | 0.0009 | 0.999 | 0.502 | 0.038 | 0.204 | 0.051 | 0.009 | 0.009 | 0.743 | 0.500 |
| cross | loo | 0.1% | 2 | V3-MAX | 71 | 16245 | 70.000 | 63565.000 | 0.796 | 0.504 | 0.004 | 0.009 | 0.001 | 0.999 | 0.502 | 0.031 | 0.204 | 0.038 | 0.008 | 0.008 | 0.893 | 0.637 |
| cross | loo | 0.1% | 2 | V3-MAX-RBF | 91 | 16225 | 70.000 | 63565.000 | 0.796 | 0.565 | 0.006 | 0.011 | 0.001 | 0.999 | 0.502 | 0.040 | 0.204 | 0.049 | 0.009 | 0.009 | 0.884 | 0.619 |
| cross | loo | 0.1% | 2 | V3-SUP | 61 | 16255 | 63.500 | 63571.500 | 0.796 | 0.490 | 0.004 | 0.007 | 0.0010 | 0.999 | 0.501 | 0.028 | 0.204 | 0.036 | 0.007 | 0.007 | 0.635 | 0.500 |
| cross | loo | 0.1% | 2 | V3-SUP-DENSE | 99 | 16217 | 65.000 | 63570.000 | 0.796 | 0.604 | 0.006 | 0.012 | 0.001 | 0.999 | 0.503 | 0.045 | 0.204 | 0.057 | 0.011 | 0.011 | 0.793 | 0.501 |
| cross | loo | 0.1% | 2 | V3-SUP-NOA | 112 | 16204 | 62.000 | 63573.000 | 0.797 | 0.644 | 0.007 | 0.014 | 0.0010 | 0.999 | 0.503 | 0.051 | 0.204 | 0.066 | 0.013 | 0.013 | 0.449 | 0.502 |
| cross | loo | 0.1% | 3 | TREE | 0 | 16316 | 68.500 | 63566.500 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.015 | 0.204 | 0.000 | 0.000 | 0.000 | 0.808 | 0.500 |
| cross | loo | 0.1% | 3 | V3-MAX | 2 | 16314 | 66.000 | 63569.000 | 0.795 | 0.029 | 0.0001 | 0.0002 | 0.001 | 0.999 | 0.500 | -0.013 | 0.204 | 0.001 | 0.0002 | 0.0002 | 0.911 | 0.624 |
| cross | loo | 0.1% | 3 | V3-MAX-RBF | 32 | 16284 | 77.000 | 63558.000 | 0.795 | 0.294 | 0.002 | 0.004 | 0.001 | 0.999 | 0.500 | 0.008 | 0.204 | 0.016 | 0.003 | 0.003 | 0.904 | 0.573 |
| cross | loo | 0.1% | 3 | V3-SUP | 0 | 16316 | 71.000 | 63564.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.015 | 0.204 | 0.000 | 0.000 | 0.000 | 0.671 | 0.500 |
| cross | loo | 0.1% | 3 | V3-SUP-DENSE | 0 | 16316 | 64.000 | 63571.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.014 | 0.204 | 0.000 | 0.000 | 0.000 | 0.775 | 0.500 |
| cross | loo | 0.1% | 3 | V3-SUP-NOA | 1 | 16315 | 72.500 | 63562.500 | 0.795 | 0.014 | 0.0001 | 0.0001 | 0.001 | 0.999 | 0.499 | -0.014 | 0.204 | 0.0005 | 0.0001 | 0.0001 | 0.814 | 0.500 |
| cross | loo | 0.1% | 4 | TREE | 8 | 16308 | 27.500 | 63607.500 | 0.796 | 0.225 | 0.0005 | 0.0010 | 0.0004 | 1.000 | 0.500 | 0.001 | 0.204 | 0.011 | 0.0003 | 0.0003 | 0.774 | 0.511 |
| cross | loo | 0.1% | 4 | V3-MAX | 2 | 16314 | 65.000 | 63570.000 | 0.795 | 0.030 | 0.0001 | 0.0002 | 0.001 | 0.999 | 0.500 | -0.013 | 0.204 | 0.001 | 0.0002 | 0.0002 | 0.918 | 0.636 |
| cross | loo | 0.1% | 4 | V3-MAX-RBF | 54 | 16262 | 67.000 | 63568.000 | 0.796 | 0.446 | 0.003 | 0.007 | 0.001 | 0.999 | 0.501 | 0.023 | 0.204 | 0.031 | 0.004 | 0.004 | 0.914 | 0.621 |
| cross | loo | 0.1% | 4 | V3-SUP | 0 | 16316 | 63.000 | 63572.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.0010 | 0.999 | 0.500 | -0.014 | 0.204 | 0.000 | 0.000 | 0.000 | 0.787 | 0.497 |
| cross | loo | 0.1% | 4 | V3-SUP-DENSE | 12 | 16304 | 65.500 | 63569.500 | 0.795 | 0.155 | 0.0007 | 0.001 | 0.001 | 0.999 | 0.500 | -0.004 | 0.204 | 0.007 | 0.0005 | 0.0005 | 0.828 | 0.498 |
| cross | loo | 0.1% | 4 | V3-SUP-NOA | 0 | 16316 | 69.500 | 63565.500 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.015 | 0.204 | 0.000 | 0.000 | 0.000 | 0.685 | 0.497 |
| cross | loo | 0.1% | 5 | TREE | 78 | 16238 | 66.000 | 63569.000 | 0.796 | 0.542 | 0.005 | 0.009 | 0.001 | 0.999 | 0.502 | 0.036 | 0.204 | 0.044 | 0.009 | 0.009 | 0.717 | 0.500 |
| cross | loo | 0.1% | 5 | V3-MAX | 96 | 16220 | 54.500 | 63580.500 | 0.796 | 0.638 | 0.006 | 0.012 | 0.0009 | 0.999 | 0.503 | 0.047 | 0.204 | 0.065 | 0.010 | 0.010 | 0.904 | 0.649 |
| cross | loo | 0.1% | 5 | V3-MAX-RBF | 114 | 16202 | 58.000 | 63577.000 | 0.797 | 0.663 | 0.007 | 0.014 | 0.0009 | 0.999 | 0.503 | 0.053 | 0.204 | 0.072 | 0.011 | 0.011 | 0.880 | 0.610 |
| cross | loo | 0.1% | 5 | V3-SUP | 77 | 16239 | 67.000 | 63568.000 | 0.796 | 0.535 | 0.005 | 0.009 | 0.001 | 0.999 | 0.502 | 0.035 | 0.204 | 0.043 | 0.009 | 0.009 | 0.656 | 0.500 |
| cross | loo | 0.1% | 5 | V3-SUP-DENSE | 76 | 16240 | 63.000 | 63572.000 | 0.796 | 0.547 | 0.005 | 0.009 | 0.0010 | 0.999 | 0.502 | 0.035 | 0.204 | 0.045 | 0.009 | 0.009 | 0.765 | 0.500 |
| cross | loo | 0.1% | 5 | V3-SUP-NOA | 76 | 16240 | 78.500 | 63556.500 | 0.796 | 0.492 | 0.005 | 0.009 | 0.001 | 0.999 | 0.502 | 0.031 | 0.204 | 0.037 | 0.009 | 0.009 | 0.520 | 0.500 |
| cross | loo | 0.1% | 6 | TREE | 131 | 16185 | 51.000 | 63584.000 | 0.797 | 0.720 | 0.008 | 0.016 | 0.0008 | 0.999 | 0.504 | 0.061 | 0.204 | 0.092 | 0.015 | 0.015 | 0.745 | 0.502 |
| cross | loo | 0.1% | 6 | V3-MAX | 68 | 16248 | 50.500 | 63584.500 | 0.796 | 0.574 | 0.004 | 0.008 | 0.0008 | 0.999 | 0.502 | 0.035 | 0.204 | 0.050 | 0.008 | 0.008 | 0.904 | 0.638 |
| cross | loo | 0.1% | 6 | V3-MAX-RBF | 96 | 16220 | 64.000 | 63571.000 | 0.796 | 0.600 | 0.006 | 0.012 | 0.001 | 0.999 | 0.502 | 0.044 | 0.204 | 0.056 | 0.010 | 0.010 | 0.884 | 0.623 |
| cross | loo | 0.1% | 6 | V3-SUP | 81 | 16235 | 58.000 | 63577.000 | 0.796 | 0.583 | 0.005 | 0.010 | 0.0009 | 0.999 | 0.502 | 0.039 | 0.204 | 0.052 | 0.009 | 0.009 | 0.770 | 0.501 |
| cross | loo | 0.1% | 6 | V3-SUP-DENSE | 74 | 16242 | 64.000 | 63571.000 | 0.796 | 0.536 | 0.005 | 0.009 | 0.001 | 0.999 | 0.502 | 0.034 | 0.204 | 0.044 | 0.009 | 0.009 | 0.770 | 0.500 |
| cross | loo | 0.1% | 6 | V3-SUP-NOA | 128 | 16188 | 64.000 | 63571.000 | 0.797 | 0.667 | 0.008 | 0.016 | 0.001 | 0.999 | 0.503 | 0.056 | 0.204 | 0.073 | 0.015 | 0.015 | 0.349 | 0.502 |
| cross | loo | 0.1% | 7 | TREE | 0 | 16316 | 63.000 | 63572.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.0010 | 0.999 | 0.500 | -0.014 | 0.204 | 0.000 | 0.000 | 0.000 | 0.543 | 0.499 |
| cross | loo | 0.1% | 7 | V3-MAX | 7 | 16309 | 70.000 | 63565.000 | 0.795 | 0.091 | 0.0004 | 0.0009 | 0.001 | 0.999 | 0.500 | -0.009 | 0.204 | 0.004 | 0.0008 | 0.0008 | 0.906 | 0.631 |
| cross | loo | 0.1% | 7 | V3-MAX-RBF | 41 | 16275 | 75.500 | 63559.500 | 0.795 | 0.352 | 0.003 | 0.005 | 0.001 | 0.999 | 0.501 | 0.014 | 0.204 | 0.021 | 0.003 | 0.003 | 0.894 | 0.600 |
| cross | loo | 0.1% | 7 | V3-SUP | 5 | 16311 | 77.000 | 63558.000 | 0.795 | 0.061 | 0.0003 | 0.0006 | 0.001 | 0.999 | 0.500 | -0.011 | 0.204 | 0.003 | 0.0006 | 0.0006 | 0.630 | 0.499 |
| cross | loo | 0.1% | 7 | V3-SUP-DENSE | 0 | 16316 | 71.000 | 63564.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.015 | 0.204 | 0.000 | 0.000 | 0.000 | 0.785 | 0.499 |
| cross | loo | 0.1% | 7 | V3-SUP-NOA | 0 | 16316 | 74.000 | 63561.000 | 0.795 | 0.000 | 0.000 | 0.000 | 0.001 | 0.999 | 0.499 | -0.015 | 0.204 | 0.000 | 0.000 | 0.000 | 0.628 | 0.499 |
| cross | loo | 0.1% | 8 | TREE | 58 | 16258 | 55.000 | 63580.000 | 0.796 | 0.513 | 0.004 | 0.007 | 0.0009 | 0.999 | 0.501 | 0.029 | 0.204 | 0.040 | 0.007 | 0.007 | 0.780 | 0.499 |
| cross | loo | 0.1% | 8 | V3-MAX | 131 | 16185 | 71.500 | 63563.500 | 0.797 | 0.647 | 0.008 | 0.016 | 0.001 | 0.999 | 0.503 | 0.055 | 0.204 | 0.067 | 0.010 | 0.010 | 0.884 | 0.656 |
| cross | loo | 0.1% | 8 | V3-MAX-RBF | 96 | 16220 | 69.000 | 63566.000 | 0.796 | 0.582 | 0.006 | 0.012 | 0.001 | 0.999 | 0.502 | 0.043 | 0.204 | 0.052 | 0.009 | 0.009 | 0.851 | 0.616 |
| cross | loo | 0.1% | 8 | V3-SUP | 48 | 16268 | 61.500 | 63573.500 | 0.796 | 0.438 | 0.003 | 0.006 | 0.0010 | 0.999 | 0.501 | 0.022 | 0.204 | 0.030 | 0.006 | 0.006 | 0.414 | 0.499 |
| cross | loo | 0.1% | 8 | V3-SUP-DENSE | 53 | 16263 | 67.000 | 63568.000 | 0.796 | 0.442 | 0.003 | 0.006 | 0.001 | 0.999 | 0.501 | 0.023 | 0.204 | 0.030 | 0.006 | 0.006 | 0.772 | 0.499 |
| cross | loo | 0.1% | 8 | V3-SUP-NOA | 64 | 16252 | 68.500 | 63566.500 | 0.796 | 0.483 | 0.004 | 0.008 | 0.001 | 0.999 | 0.501 | 0.028 | 0.204 | 0.036 | 0.007 | 0.007 | 0.656 | 0.499 |
| cross | loo | 0.1% | 9 | TREE | 62 | 16254 | 54.000 | 63581.000 | 0.796 | 0.534 | 0.004 | 0.008 | 0.0008 | 0.999 | 0.501 | 0.031 | 0.204 | 0.043 | 0.007 | 0.007 | 0.709 | 0.501 |
| cross | loo | 0.1% | 9 | V3-MAX | 67 | 16249 | 63.000 | 63572.000 | 0.796 | 0.515 | 0.004 | 0.008 | 0.0010 | 0.999 | 0.502 | 0.031 | 0.204 | 0.040 | 0.008 | 0.008 | 0.902 | 0.636 |
| cross | loo | 0.1% | 9 | V3-MAX-RBF | 80 | 16236 | 70.500 | 63564.500 | 0.796 | 0.532 | 0.005 | 0.010 | 0.001 | 0.999 | 0.502 | 0.035 | 0.204 | 0.043 | 0.009 | 0.009 | 0.883 | 0.623 |
| cross | loo | 0.1% | 9 | V3-SUP | 68 | 16248 | 61.500 | 63573.500 | 0.796 | 0.525 | 0.004 | 0.008 | 0.0010 | 0.999 | 0.502 | 0.032 | 0.204 | 0.042 | 0.008 | 0.008 | 0.657 | 0.501 |
| cross | loo | 0.1% | 9 | V3-SUP-DENSE | 68 | 16248 | 60.500 | 63574.500 | 0.796 | 0.529 | 0.004 | 0.008 | 0.0010 | 0.999 | 0.502 | 0.032 | 0.204 | 0.042 | 0.008 | 0.008 | 0.567 | 0.500 |
| cross | loo | 0.1% | 9 | V3-SUP-NOA | 44 | 16272 | 63.000 | 63572.000 | 0.796 | 0.411 | 0.003 | 0.005 | 0.0010 | 0.999 | 0.501 | 0.019 | 0.204 | 0.027 | 0.005 | 0.005 | 0.688 | 0.500 |
| cross | loo | 1% | 0 | TREE | 583 | 15733 | 625.000 | 63010.000 | 0.795 | 0.483 | 0.036 | 0.067 | 0.010 | 0.990 | 0.513 | 0.086 | 0.204 | 0.035 | 0.065 | 0.065 | 0.852 | 0.506 |
| cross | loo | 1% | 0 | V3-MAX | 8792 | 7524 | 638.500 | 62996.500 | 0.898 | 0.932 | 0.539 | 0.683 | 0.010 | 0.990 | 0.764 | 0.661 | 0.204 | 0.352 | 0.403 | 0.403 | 0.913 | 0.623 |
| cross | loo | 1% | 0 | V3-MAX-RBF | 8796 | 7520 | 645.500 | 62989.500 | 0.898 | 0.932 | 0.539 | 0.683 | 0.010 | 0.990 | 0.764 | 0.661 | 0.204 | 0.349 | 0.406 | 0.406 | 0.903 | 0.598 |
| cross | loo | 1% | 0 | V3-SUP | 505 | 15811 | 634.000 | 63001.000 | 0.794 | 0.443 | 0.031 | 0.058 | 0.010 | 0.990 | 0.510 | 0.071 | 0.204 | 0.030 | 0.055 | 0.055 | 0.806 | 0.504 |
| cross | loo | 1% | 0 | V3-SUP-DENSE | 545 | 15771 | 658.000 | 62977.000 | 0.795 | 0.453 | 0.033 | 0.062 | 0.010 | 0.990 | 0.512 | 0.076 | 0.204 | 0.032 | 0.062 | 0.062 | 0.780 | 0.506 |
| cross | loo | 1% | 0 | V3-SUP-NOA | 606 | 15710 | 631.000 | 63004.000 | 0.796 | 0.490 | 0.037 | 0.069 | 0.010 | 0.990 | 0.514 | 0.089 | 0.204 | 0.036 | 0.069 | 0.069 | 0.857 | 0.506 |
| cross | loo | 1% | 1 | TREE | 135 | 16181 | 457.500 | 63177.500 | 0.792 | 0.228 | 0.008 | 0.016 | 0.007 | 0.993 | 0.501 | 0.005 | 0.204 | 0.011 | 0.012 | 0.012 | 0.763 | 0.501 |
| cross | loo | 1% | 1 | V3-MAX | 8665 | 7651 | 622.000 | 63013.000 | 0.897 | 0.933 | 0.531 | 0.677 | 0.010 | 0.990 | 0.761 | 0.656 | 0.204 | 0.354 | 0.388 | 0.388 | 0.896 | 0.648 |
| cross | loo | 1% | 1 | V3-MAX-RBF | 8638 | 7678 | 620.500 | 63014.500 | 0.896 | 0.933 | 0.529 | 0.676 | 0.010 | 0.990 | 0.760 | 0.655 | 0.204 | 0.354 | 0.387 | 0.387 | 0.885 | 0.631 |
| cross | loo | 1% | 1 | V3-SUP | 201 | 16115 | 632.000 | 63003.000 | 0.791 | 0.241 | 0.012 | 0.023 | 0.010 | 0.990 | 0.501 | 0.009 | 0.204 | 0.012 | 0.014 | 0.014 | 0.787 | 0.502 |
| cross | loo | 1% | 1 | V3-SUP-DENSE | 135 | 16181 | 631.500 | 63003.500 | 0.790 | 0.176 | 0.008 | 0.016 | 0.010 | 0.990 | 0.499 | -0.007 | 0.204 | 0.008 | 0.012 | 0.012 | 0.808 | 0.501 |
| cross | loo | 1% | 1 | V3-SUP-NOA | 67 | 16249 | 623.000 | 63012.000 | 0.789 | 0.097 | 0.004 | 0.008 | 0.010 | 0.990 | 0.497 | -0.025 | 0.204 | 0.004 | 0.004 | 0.004 | 0.783 | 0.499 |
| cross | loo | 1% | 2 | TREE | 129 | 16187 | 450.000 | 63185.000 | 0.792 | 0.223 | 0.008 | 0.015 | 0.007 | 0.993 | 0.500 | 0.004 | 0.204 | 0.011 | 0.015 | 0.015 | 0.743 | 0.500 |
| cross | loo | 1% | 2 | V3-MAX | 8634 | 7682 | 627.500 | 63007.500 | 0.896 | 0.932 | 0.529 | 0.675 | 0.010 | 0.990 | 0.760 | 0.654 | 0.204 | 0.352 | 0.386 | 0.386 | 0.893 | 0.637 |
| cross | loo | 1% | 2 | V3-MAX-RBF | 8623 | 7693 | 650.500 | 62984.500 | 0.896 | 0.930 | 0.528 | 0.674 | 0.010 | 0.990 | 0.759 | 0.652 | 0.204 | 0.343 | 0.386 | 0.386 | 0.884 | 0.619 |
| cross | loo | 1% | 2 | V3-SUP | 128 | 16188 | 618.500 | 63016.500 | 0.790 | 0.171 | 0.008 | 0.015 | 0.010 | 0.990 | 0.499 | -0.008 | 0.204 | 0.008 | 0.015 | 0.015 | 0.635 | 0.500 |
| cross | loo | 1% | 2 | V3-SUP-DENSE | 128 | 16188 | 635.000 | 63000.000 | 0.790 | 0.168 | 0.008 | 0.015 | 0.010 | 0.990 | 0.499 | -0.009 | 0.204 | 0.008 | 0.015 | 0.015 | 0.793 | 0.501 |
| cross | loo | 1% | 2 | V3-SUP-NOA | 184 | 16132 | 601.000 | 63034.000 | 0.791 | 0.234 | 0.011 | 0.022 | 0.009 | 0.991 | 0.501 | 0.007 | 0.204 | 0.012 | 0.017 | 0.017 | 0.449 | 0.502 |
| cross | loo | 1% | 3 | TREE | 155 | 16161 | 560.000 | 63075.000 | 0.791 | 0.217 | 0.009 | 0.018 | 0.009 | 0.991 | 0.500 | 0.003 | 0.204 | 0.011 | 0.018 | 0.018 | 0.808 | 0.500 |
| cross | loo | 1% | 3 | V3-MAX | 8610 | 7706 | 628.500 | 63006.500 | 0.896 | 0.932 | 0.528 | 0.674 | 0.010 | 0.990 | 0.759 | 0.653 | 0.204 | 0.351 | 0.383 | 0.383 | 0.911 | 0.624 |
| cross | loo | 1% | 3 | V3-MAX-RBF | 6070 | 10246 | 643.000 | 62992.000 | 0.864 | 0.904 | 0.372 | 0.527 | 0.010 | 0.990 | 0.681 | 0.526 | 0.204 | 0.271 | 0.276 | 0.276 | 0.904 | 0.573 |
| cross | loo | 1% | 3 | V3-SUP | 157 | 16159 | 631.500 | 63003.500 | 0.790 | 0.199 | 0.010 | 0.018 | 0.010 | 0.990 | 0.500 | -0.001 | 0.204 | 0.010 | 0.018 | 0.018 | 0.671 | 0.500 |
| cross | loo | 1% | 3 | V3-SUP-DENSE | 169 | 16147 | 630.500 | 63004.500 | 0.790 | 0.211 | 0.010 | 0.020 | 0.010 | 0.990 | 0.500 | 0.002 | 0.204 | 0.010 | 0.020 | 0.020 | 0.775 | 0.500 |
| cross | loo | 1% | 3 | V3-SUP-NOA | 175 | 16141 | 627.500 | 63007.500 | 0.790 | 0.218 | 0.011 | 0.020 | 0.010 | 0.990 | 0.500 | 0.003 | 0.204 | 0.011 | 0.020 | 0.020 | 0.814 | 0.500 |
| cross | loo | 1% | 4 | TREE | 818 | 15498 | 485.000 | 63150.000 | 0.800 | 0.628 | 0.050 | 0.093 | 0.008 | 0.992 | 0.521 | 0.135 | 0.204 | 0.062 | 0.034 | 0.034 | 0.774 | 0.511 |
| cross | loo | 1% | 4 | V3-MAX | 8662 | 7654 | 643.500 | 62991.500 | 0.896 | 0.931 | 0.531 | 0.676 | 0.010 | 0.990 | 0.760 | 0.654 | 0.204 | 0.347 | 0.386 | 0.386 | 0.918 | 0.636 |
| cross | loo | 1% | 4 | V3-MAX-RBF | 8639 | 7677 | 635.000 | 63000.000 | 0.896 | 0.932 | 0.529 | 0.675 | 0.010 | 0.990 | 0.760 | 0.654 | 0.204 | 0.349 | 0.386 | 0.386 | 0.914 | 0.621 |
| cross | loo | 1% | 4 | V3-SUP | 0 | 16316 | 623.500 | 63011.500 | 0.788 | 0.000 | 0.000 | 0.000 | 0.010 | 0.990 | 0.495 | -0.045 | 0.204 | 0.000 | 0.000 | 0.000 | 0.787 | 0.497 |
| cross | loo | 1% | 4 | V3-SUP-DENSE | 33 | 16283 | 644.500 | 62990.500 | 0.788 | 0.049 | 0.002 | 0.004 | 0.010 | 0.990 | 0.496 | -0.036 | 0.204 | 0.002 | 0.001 | 0.001 | 0.828 | 0.498 |
| cross | loo | 1% | 4 | V3-SUP-NOA | 0 | 16316 | 606.000 | 63029.000 | 0.788 | 0.000 | 0.000 | 0.000 | 0.010 | 0.990 | 0.495 | -0.044 | 0.204 | 0.000 | 0.000 | 0.000 | 0.685 | 0.497 |
| cross | loo | 1% | 5 | TREE | 84 | 16232 | 498.000 | 63137.000 | 0.791 | 0.144 | 0.005 | 0.010 | 0.008 | 0.992 | 0.499 | -0.013 | 0.204 | 0.007 | 0.010 | 0.010 | 0.717 | 0.500 |
| cross | loo | 1% | 5 | V3-MAX | 8632 | 7684 | 638.500 | 62996.500 | 0.896 | 0.931 | 0.529 | 0.675 | 0.010 | 0.990 | 0.760 | 0.653 | 0.204 | 0.348 | 0.386 | 0.386 | 0.904 | 0.649 |
| cross | loo | 1% | 5 | V3-MAX-RBF | 8610 | 7706 | 647.000 | 62988.000 | 0.896 | 0.930 | 0.528 | 0.673 | 0.010 | 0.990 | 0.759 | 0.652 | 0.204 | 0.344 | 0.385 | 0.385 | 0.880 | 0.610 |
| cross | loo | 1% | 5 | V3-SUP | 117 | 16199 | 645.500 | 62989.500 | 0.789 | 0.153 | 0.007 | 0.014 | 0.010 | 0.990 | 0.499 | -0.012 | 0.204 | 0.007 | 0.014 | 0.014 | 0.656 | 0.500 |
| cross | loo | 1% | 5 | V3-SUP-DENSE | 117 | 16199 | 639.000 | 62996.000 | 0.789 | 0.155 | 0.007 | 0.014 | 0.010 | 0.990 | 0.499 | -0.012 | 0.204 | 0.007 | 0.014 | 0.014 | 0.765 | 0.500 |
| cross | loo | 1% | 5 | V3-SUP-NOA | 109 | 16207 | 633.500 | 63001.500 | 0.789 | 0.147 | 0.007 | 0.013 | 0.010 | 0.990 | 0.498 | -0.014 | 0.204 | 0.007 | 0.013 | 0.013 | 0.520 | 0.500 |
| cross | loo | 1% | 6 | TREE | 145 | 16171 | 441.000 | 63194.000 | 0.792 | 0.247 | 0.009 | 0.017 | 0.007 | 0.993 | 0.501 | 0.009 | 0.204 | 0.013 | 0.017 | 0.017 | 0.745 | 0.502 |
| cross | loo | 1% | 6 | V3-MAX | 8673 | 7643 | 608.000 | 63027.000 | 0.897 | 0.934 | 0.532 | 0.678 | 0.010 | 0.990 | 0.761 | 0.657 | 0.204 | 0.360 | 0.390 | 0.390 | 0.904 | 0.638 |
| cross | loo | 1% | 6 | V3-MAX-RBF | 8654 | 7662 | 605.500 | 63029.500 | 0.897 | 0.935 | 0.530 | 0.677 | 0.010 | 0.990 | 0.760 | 0.656 | 0.204 | 0.360 | 0.390 | 0.390 | 0.884 | 0.623 |
| cross | loo | 1% | 6 | V3-SUP | 129 | 16187 | 591.000 | 63044.000 | 0.790 | 0.179 | 0.008 | 0.015 | 0.009 | 0.991 | 0.499 | -0.006 | 0.204 | 0.009 | 0.015 | 0.015 | 0.770 | 0.501 |
| cross | loo | 1% | 6 | V3-SUP-DENSE | 110 | 16206 | 604.000 | 63031.000 | 0.790 | 0.154 | 0.007 | 0.013 | 0.009 | 0.991 | 0.499 | -0.012 | 0.204 | 0.007 | 0.013 | 0.013 | 0.770 | 0.500 |
| cross | loo | 1% | 6 | V3-SUP-NOA | 144 | 16172 | 610.000 | 63025.000 | 0.790 | 0.191 | 0.009 | 0.017 | 0.010 | 0.990 | 0.500 | -0.003 | 0.204 | 0.009 | 0.017 | 0.017 | 0.349 | 0.502 |
| cross | loo | 1% | 7 | TREE | 188 | 16128 | 485.000 | 63150.000 | 0.792 | 0.279 | 0.012 | 0.022 | 0.008 | 0.992 | 0.502 | 0.017 | 0.204 | 0.015 | 0.021 | 0.021 | 0.543 | 0.499 |
| cross | loo | 1% | 7 | V3-MAX | 8592 | 7724 | 654.500 | 62980.500 | 0.895 | 0.929 | 0.527 | 0.672 | 0.010 | 0.990 | 0.758 | 0.651 | 0.204 | 0.341 | 0.380 | 0.380 | 0.906 | 0.631 |
| cross | loo | 1% | 7 | V3-MAX-RBF | 8582 | 7734 | 662.500 | 62972.500 | 0.895 | 0.928 | 0.526 | 0.672 | 0.010 | 0.990 | 0.758 | 0.650 | 0.204 | 0.338 | 0.381 | 0.381 | 0.894 | 0.600 |
| cross | loo | 1% | 7 | V3-SUP | 181 | 16135 | 620.500 | 63014.500 | 0.790 | 0.226 | 0.011 | 0.021 | 0.010 | 0.990 | 0.501 | 0.005 | 0.204 | 0.011 | 0.020 | 0.020 | 0.630 | 0.499 |
| cross | loo | 1% | 7 | V3-SUP-DENSE | 177 | 16139 | 624.500 | 63010.500 | 0.790 | 0.221 | 0.011 | 0.021 | 0.010 | 0.990 | 0.501 | 0.004 | 0.204 | 0.011 | 0.020 | 0.020 | 0.785 | 0.499 |
| cross | loo | 1% | 7 | V3-SUP-NOA | 169 | 16147 | 637.500 | 62997.500 | 0.790 | 0.210 | 0.010 | 0.020 | 0.010 | 0.990 | 0.500 | 0.001 | 0.204 | 0.010 | 0.020 | 0.020 | 0.628 | 0.499 |
| cross | loo | 1% | 8 | TREE | 67 | 16249 | 527.000 | 63108.000 | 0.790 | 0.113 | 0.004 | 0.008 | 0.008 | 0.992 | 0.498 | -0.020 | 0.204 | 0.005 | 0.008 | 0.008 | 0.780 | 0.499 |
| cross | loo | 1% | 8 | V3-MAX | 8618 | 7698 | 627.500 | 63007.500 | 0.896 | 0.932 | 0.528 | 0.674 | 0.010 | 0.990 | 0.759 | 0.653 | 0.204 | 0.351 | 0.385 | 0.385 | 0.884 | 0.656 |
| cross | loo | 1% | 8 | V3-MAX-RBF | 8621 | 7695 | 630.000 | 63005.000 | 0.896 | 0.932 | 0.528 | 0.674 | 0.010 | 0.990 | 0.759 | 0.653 | 0.204 | 0.350 | 0.386 | 0.386 | 0.851 | 0.616 |
| cross | loo | 1% | 8 | V3-SUP | 64 | 16252 | 622.500 | 63012.500 | 0.789 | 0.093 | 0.004 | 0.008 | 0.010 | 0.990 | 0.497 | -0.026 | 0.204 | 0.004 | 0.007 | 0.007 | 0.414 | 0.499 |
| cross | loo | 1% | 8 | V3-SUP-DENSE | 67 | 16249 | 616.000 | 63019.000 | 0.789 | 0.098 | 0.004 | 0.008 | 0.010 | 0.990 | 0.497 | -0.024 | 0.204 | 0.004 | 0.008 | 0.008 | 0.772 | 0.499 |
| cross | loo | 1% | 8 | V3-SUP-NOA | 67 | 16249 | 635.000 | 63000.000 | 0.789 | 0.095 | 0.004 | 0.008 | 0.010 | 0.990 | 0.497 | -0.025 | 0.204 | 0.004 | 0.008 | 0.008 | 0.656 | 0.499 |
| cross | loo | 1% | 9 | TREE | 135 | 16181 | 584.000 | 63051.000 | 0.790 | 0.188 | 0.008 | 0.016 | 0.009 | 0.991 | 0.500 | -0.004 | 0.204 | 0.009 | 0.015 | 0.015 | 0.709 | 0.501 |
| cross | loo | 1% | 9 | V3-MAX | 8697 | 7619 | 630.000 | 63005.000 | 0.897 | 0.932 | 0.533 | 0.678 | 0.010 | 0.990 | 0.762 | 0.657 | 0.204 | 0.352 | 0.391 | 0.391 | 0.902 | 0.636 |
| cross | loo | 1% | 9 | V3-MAX-RBF | 8639 | 7677 | 629.500 | 63005.500 | 0.896 | 0.932 | 0.529 | 0.675 | 0.010 | 0.990 | 0.760 | 0.654 | 0.204 | 0.351 | 0.387 | 0.387 | 0.883 | 0.623 |
| cross | loo | 1% | 9 | V3-SUP | 207 | 16109 | 631.000 | 63004.000 | 0.791 | 0.247 | 0.013 | 0.024 | 0.010 | 0.990 | 0.501 | 0.011 | 0.204 | 0.013 | 0.018 | 0.018 | 0.657 | 0.501 |
| cross | loo | 1% | 9 | V3-SUP-DENSE | 127 | 16189 | 628.000 | 63007.000 | 0.790 | 0.168 | 0.008 | 0.015 | 0.010 | 0.990 | 0.499 | -0.009 | 0.204 | 0.008 | 0.015 | 0.015 | 0.567 | 0.500 |
| cross | loo | 1% | 9 | V3-SUP-NOA | 133 | 16183 | 617.000 | 63018.000 | 0.790 | 0.177 | 0.008 | 0.016 | 0.010 | 0.990 | 0.499 | -0.006 | 0.204 | 0.008 | 0.015 | 0.015 | 0.688 | 0.500 |

## R12_v31_within. Derived metrics from v31_within/metrics_overall.csv

| protocol | scenario | op | seed | model | TP | FN | FP | TN | accuracy | precision | recall | f1 | fpr | specificity | balanced_acc | mcc | prevalence | precision_at_prev1 | macro_recall | macro_recall_nontiny | auc | pauc1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| within | known | 0.1% | 0 | TREE | 64219 | 326 | 396.000 | 381895.000 | 0.998 | 0.994 | 0.995 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.907 | 0.777 | 0.953 | 1.000 | 0.999 |
| within | known | 0.1% | 0 | V3-MAX | 64214 | 331 | 380.000 | 381911.000 | 0.998 | 0.994 | 0.995 | 0.994 | 0.0010 | 0.999 | 0.997 | 0.994 | 0.144 | 0.910 | 0.773 | 0.947 | 1.000 | 0.998 |
| within | known | 0.1% | 0 | V3-MAX-RBF | 64154 | 391 | 425.000 | 381866.000 | 0.998 | 0.993 | 0.994 | 0.994 | 0.001 | 0.999 | 0.996 | 0.993 | 0.144 | 0.900 | 0.771 | 0.945 | 1.000 | 0.998 |
| within | known | 0.1% | 0 | V3-SUP | 64307 | 238 | 404.000 | 381887.000 | 0.999 | 0.994 | 0.996 | 0.995 | 0.001 | 0.999 | 0.998 | 0.994 | 0.144 | 0.905 | 0.793 | 0.955 | 1.000 | 0.999 |
| within | known | 0.1% | 0 | V3-SUP-DENSE | 64212 | 333 | 405.000 | 381886.000 | 0.998 | 0.994 | 0.995 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.905 | 0.775 | 0.950 | 1.000 | 0.998 |
| within | known | 0.1% | 0 | V3-SUP-TT | 64227 | 318 | 396.000 | 381895.000 | 0.998 | 0.994 | 0.995 | 0.994 | 0.001 | 0.999 | 0.997 | 0.994 | 0.144 | 0.907 | 0.777 | 0.952 | 1.000 | 0.999 |
| within | known | 0.1% | 1 | TREE | 64166 | 379 | 413.000 | 381878.000 | 0.998 | 0.994 | 0.994 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.903 | 0.742 | 0.926 | 1.000 | 0.998 |
| within | known | 0.1% | 1 | V3-MAX | 64064 | 481 | 407.000 | 381884.000 | 0.998 | 0.994 | 0.993 | 0.993 | 0.001 | 0.999 | 0.996 | 0.992 | 0.144 | 0.904 | 0.710 | 0.903 | 1.000 | 0.998 |
| within | known | 0.1% | 1 | V3-MAX-RBF | 64054 | 491 | 405.000 | 381886.000 | 0.998 | 0.994 | 0.992 | 0.993 | 0.001 | 0.999 | 0.996 | 0.992 | 0.144 | 0.904 | 0.708 | 0.901 | 1.000 | 0.998 |
| within | known | 0.1% | 1 | V3-SUP | 64212 | 333 | 417.000 | 381874.000 | 0.998 | 0.994 | 0.995 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.902 | 0.732 | 0.931 | 1.000 | 0.998 |
| within | known | 0.1% | 1 | V3-SUP-DENSE | 64151 | 394 | 404.000 | 381887.000 | 0.998 | 0.994 | 0.994 | 0.994 | 0.001 | 0.999 | 0.996 | 0.993 | 0.144 | 0.905 | 0.728 | 0.927 | 1.000 | 0.998 |
| within | known | 0.1% | 1 | V3-SUP-TT | 64274 | 271 | 446.000 | 381845.000 | 0.998 | 0.993 | 0.996 | 0.994 | 0.001 | 0.999 | 0.997 | 0.994 | 0.144 | 0.896 | 0.755 | 0.932 | 1.000 | 0.999 |
| within | known | 0.1% | 2 | TREE | 64188 | 357 | 408.000 | 381883.000 | 0.998 | 0.994 | 0.994 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.904 | 0.807 | 0.932 | 1.000 | 0.998 |
| within | known | 0.1% | 2 | V3-MAX | 64106 | 439 | 403.000 | 381888.000 | 0.998 | 0.994 | 0.993 | 0.993 | 0.001 | 0.999 | 0.996 | 0.992 | 0.144 | 0.905 | 0.769 | 0.922 | 1.000 | 0.997 |
| within | known | 0.1% | 2 | V3-MAX-RBF | 64106 | 439 | 396.000 | 381895.000 | 0.998 | 0.994 | 0.993 | 0.994 | 0.001 | 0.999 | 0.996 | 0.992 | 0.144 | 0.906 | 0.769 | 0.922 | 1.000 | 0.997 |
| within | known | 0.1% | 2 | V3-SUP | 64252 | 293 | 402.000 | 381889.000 | 0.998 | 0.994 | 0.995 | 0.995 | 0.001 | 0.999 | 0.997 | 0.994 | 0.144 | 0.905 | 0.800 | 0.943 | 1.000 | 0.998 |
| within | known | 0.1% | 2 | V3-SUP-DENSE | 64190 | 355 | 419.000 | 381872.000 | 0.998 | 0.994 | 0.994 | 0.994 | 0.001 | 0.999 | 0.997 | 0.993 | 0.144 | 0.902 | 0.808 | 0.933 | 1.000 | 0.998 |
| within | known | 0.1% | 2 | V3-SUP-TT | 64283 | 262 | 421.000 | 381870.000 | 0.998 | 0.993 | 0.996 | 0.995 | 0.001 | 0.999 | 0.997 | 0.994 | 0.144 | 0.901 | 0.818 | 0.946 | 1.000 | 0.999 |
| within | known | 1% | 0 | TREE | 64488 | 57 | 3758.000 | 378533.000 | 0.991 | 0.945 | 0.999 | 0.971 | 0.010 | 0.990 | 0.995 | 0.967 | 0.144 | 0.507 | 0.847 | 0.987 | 1.000 | 0.999 |
| within | known | 1% | 0 | V3-MAX | 64439 | 106 | 3811.000 | 378480.000 | 0.991 | 0.944 | 0.998 | 0.971 | 0.010 | 0.990 | 0.994 | 0.966 | 0.144 | 0.503 | 0.832 | 0.976 | 1.000 | 0.998 |
| within | known | 1% | 0 | V3-MAX-RBF | 64439 | 106 | 3655.000 | 378636.000 | 0.992 | 0.946 | 0.998 | 0.972 | 0.010 | 0.990 | 0.994 | 0.967 | 0.144 | 0.513 | 0.832 | 0.976 | 1.000 | 0.998 |
| within | known | 1% | 0 | V3-SUP | 64465 | 80 | 3267.000 | 379024.000 | 0.993 | 0.952 | 0.999 | 0.975 | 0.009 | 0.991 | 0.995 | 0.971 | 0.144 | 0.541 | 0.844 | 0.983 | 1.000 | 0.999 |
| within | known | 1% | 0 | V3-SUP-DENSE | 64462 | 83 | 3790.000 | 378501.000 | 0.991 | 0.944 | 0.999 | 0.971 | 0.010 | 0.990 | 0.994 | 0.966 | 0.144 | 0.504 | 0.843 | 0.982 | 1.000 | 0.998 |
| within | known | 1% | 0 | V3-SUP-TT | 64457 | 88 | 3708.000 | 378583.000 | 0.992 | 0.946 | 0.999 | 0.971 | 0.010 | 0.990 | 0.994 | 0.967 | 0.144 | 0.510 | 0.841 | 0.980 | 1.000 | 0.999 |
| within | known | 1% | 1 | TREE | 64433 | 112 | 3963.000 | 378328.000 | 0.991 | 0.942 | 0.998 | 0.969 | 0.010 | 0.990 | 0.994 | 0.965 | 0.144 | 0.493 | 0.894 | 0.966 | 1.000 | 0.998 |
| within | known | 1% | 1 | V3-MAX | 64424 | 121 | 4095.000 | 378196.000 | 0.991 | 0.940 | 0.998 | 0.968 | 0.011 | 0.989 | 0.994 | 0.963 | 0.144 | 0.485 | 0.863 | 0.963 | 1.000 | 0.998 |
| within | known | 1% | 1 | V3-MAX-RBF | 64423 | 122 | 4092.000 | 378199.000 | 0.991 | 0.940 | 0.998 | 0.968 | 0.011 | 0.989 | 0.994 | 0.963 | 0.144 | 0.485 | 0.863 | 0.963 | 1.000 | 0.998 |
| within | known | 1% | 1 | V3-SUP | 64445 | 100 | 3600.000 | 378691.000 | 0.992 | 0.947 | 0.998 | 0.972 | 0.009 | 0.991 | 0.995 | 0.968 | 0.144 | 0.517 | 0.881 | 0.968 | 1.000 | 0.998 |
| within | known | 1% | 1 | V3-SUP-DENSE | 64437 | 108 | 3823.000 | 378468.000 | 0.991 | 0.944 | 0.998 | 0.970 | 0.010 | 0.990 | 0.994 | 0.966 | 0.144 | 0.502 | 0.872 | 0.966 | 1.000 | 0.998 |
| within | known | 1% | 1 | V3-SUP-TT | 64459 | 86 | 3586.000 | 378705.000 | 0.992 | 0.947 | 0.999 | 0.972 | 0.009 | 0.991 | 0.995 | 0.968 | 0.144 | 0.518 | 0.896 | 0.969 | 1.000 | 0.999 |
| within | known | 1% | 2 | TREE | 64480 | 65 | 3946.000 | 378345.000 | 0.991 | 0.942 | 0.999 | 0.970 | 0.010 | 0.990 | 0.994 | 0.965 | 0.144 | 0.494 | 0.960 | 0.980 | 1.000 | 0.998 |
| within | known | 1% | 2 | V3-MAX | 64403 | 142 | 4164.000 | 378127.000 | 0.990 | 0.939 | 0.998 | 0.968 | 0.011 | 0.989 | 0.993 | 0.963 | 0.144 | 0.481 | 0.959 | 0.969 | 1.000 | 0.997 |
| within | known | 1% | 2 | V3-MAX-RBF | 64402 | 143 | 3900.000 | 378391.000 | 0.991 | 0.943 | 0.998 | 0.970 | 0.010 | 0.990 | 0.994 | 0.965 | 0.144 | 0.497 | 0.959 | 0.968 | 1.000 | 0.997 |
| within | known | 1% | 2 | V3-SUP | 64463 | 82 | 3608.000 | 378683.000 | 0.992 | 0.947 | 0.999 | 0.972 | 0.009 | 0.991 | 0.995 | 0.968 | 0.144 | 0.517 | 0.967 | 0.978 | 1.000 | 0.998 |
| within | known | 1% | 2 | V3-SUP-DENSE | 64478 | 67 | 3901.000 | 378390.000 | 0.991 | 0.943 | 0.999 | 0.970 | 0.010 | 0.990 | 0.994 | 0.965 | 0.144 | 0.497 | 0.960 | 0.979 | 1.000 | 0.998 |
| within | known | 1% | 2 | V3-SUP-TT | 64478 | 67 | 3846.000 | 378445.000 | 0.991 | 0.944 | 0.999 | 0.971 | 0.010 | 0.990 | 0.994 | 0.966 | 0.144 | 0.501 | 0.961 | 0.980 | 1.000 | 0.999 |
| within | loo | 0.1% | 0 | TREE | 37436 | 26976 | 379.900 | 381911.100 | 0.939 | 0.990 | 0.581 | 0.732 | 0.0010 | 0.999 | 0.790 | 0.732 | 0.144 | 0.855 | 0.401 | 0.401 | 0.935 | 0.832 |
| within | loo | 0.1% | 0 | V3-MAX | 37925 | 26487 | 379.300 | 381911.700 | 0.940 | 0.990 | 0.589 | 0.738 | 0.0010 | 0.999 | 0.794 | 0.737 | 0.144 | 0.857 | 0.418 | 0.418 | 0.953 | 0.825 |
| within | loo | 0.1% | 0 | V3-MAX-RBF | 37244 | 27168 | 417.600 | 381873.400 | 0.938 | 0.989 | 0.578 | 0.730 | 0.001 | 0.999 | 0.789 | 0.730 | 0.144 | 0.842 | 0.390 | 0.390 | 0.953 | 0.827 |
| within | loo | 0.1% | 0 | V3-SUP | 37492 | 26920 | 375.800 | 381915.200 | 0.939 | 0.990 | 0.582 | 0.733 | 0.0010 | 0.999 | 0.791 | 0.733 | 0.144 | 0.857 | 0.402 | 0.402 | 0.954 | 0.841 |
| within | loo | 0.1% | 0 | V3-SUP-DENSE | 37420 | 26992 | 383.300 | 381907.700 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.854 | 0.397 | 0.397 | 0.949 | 0.816 |
| within | loo | 0.1% | 0 | V3-SUP-TT | 37458 | 26954 | 389.100 | 381901.900 | 0.939 | 0.990 | 0.582 | 0.733 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.852 | 0.401 | 0.401 | 0.934 | 0.829 |
| within | loo | 0.1% | 1 | TREE | 37432 | 26980 | 402.200 | 381888.800 | 0.939 | 0.989 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.848 | 0.406 | 0.406 | 0.975 | 0.839 |
| within | loo | 0.1% | 1 | V3-MAX | 37374 | 27038 | 404.600 | 381886.400 | 0.939 | 0.989 | 0.580 | 0.731 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.847 | 0.398 | 0.398 | 0.931 | 0.840 |
| within | loo | 0.1% | 1 | V3-MAX-RBF | 37362 | 27050 | 387.600 | 381903.400 | 0.939 | 0.990 | 0.580 | 0.731 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.852 | 0.397 | 0.397 | 0.944 | 0.839 |
| within | loo | 0.1% | 1 | V3-SUP | 37725 | 26687 | 389.300 | 381901.700 | 0.939 | 0.990 | 0.586 | 0.736 | 0.001 | 0.999 | 0.792 | 0.735 | 0.144 | 0.853 | 0.417 | 0.417 | 0.930 | 0.849 |
| within | loo | 0.1% | 1 | V3-SUP-DENSE | 37442 | 26970 | 397.500 | 381893.500 | 0.939 | 0.989 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.850 | 0.408 | 0.408 | 0.932 | 0.816 |
| within | loo | 0.1% | 1 | V3-SUP-TT | 37794 | 26618 | 418.500 | 381872.500 | 0.939 | 0.989 | 0.587 | 0.737 | 0.001 | 0.999 | 0.793 | 0.736 | 0.144 | 0.844 | 0.418 | 0.418 | 0.911 | 0.851 |
| within | loo | 0.1% | 2 | TREE | 37426 | 26986 | 385.000 | 381906.000 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.854 | 0.379 | 0.379 | 0.929 | 0.854 |
| within | loo | 0.1% | 2 | V3-MAX | 37029 | 27383 | 406.500 | 381884.500 | 0.938 | 0.989 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.727 | 0.144 | 0.845 | 0.365 | 0.365 | 0.979 | 0.857 |
| within | loo | 0.1% | 2 | V3-MAX-RBF | 37029 | 27383 | 399.500 | 381891.500 | 0.938 | 0.989 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.728 | 0.144 | 0.847 | 0.365 | 0.365 | 0.978 | 0.849 |
| within | loo | 0.1% | 2 | V3-SUP | 37388 | 27024 | 393.900 | 381897.100 | 0.939 | 0.990 | 0.580 | 0.732 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.851 | 0.380 | 0.380 | 0.978 | 0.857 |
| within | loo | 0.1% | 2 | V3-SUP-DENSE | 37349 | 27063 | 387.500 | 381903.500 | 0.939 | 0.990 | 0.580 | 0.731 | 0.001 | 0.999 | 0.789 | 0.731 | 0.144 | 0.852 | 0.376 | 0.376 | 0.942 | 0.857 |
| within | loo | 0.1% | 2 | V3-SUP-TT | 37513 | 26899 | 393.500 | 381897.500 | 0.939 | 0.990 | 0.582 | 0.733 | 0.001 | 0.999 | 0.791 | 0.733 | 0.144 | 0.851 | 0.380 | 0.380 | 0.861 | 0.860 |
| within | loo | 1% | 0 | TREE | 47062 | 17350 | 3810.600 | 378480.400 | 0.953 | 0.925 | 0.731 | 0.816 | 0.010 | 0.990 | 0.860 | 0.797 | 0.144 | 0.425 | 0.485 | 0.485 | 0.935 | 0.832 |
| within | loo | 1% | 0 | V3-MAX | 47782 | 16630 | 4105.300 | 378185.700 | 0.954 | 0.921 | 0.742 | 0.822 | 0.011 | 0.989 | 0.866 | 0.802 | 0.144 | 0.411 | 0.542 | 0.542 | 0.953 | 0.825 |
| within | loo | 1% | 0 | V3-MAX-RBF | 52738 | 11674 | 3976.600 | 378314.400 | 0.965 | 0.930 | 0.819 | 0.871 | 0.010 | 0.990 | 0.904 | 0.853 | 0.144 | 0.443 | 0.560 | 0.560 | 0.953 | 0.827 |
| within | loo | 1% | 0 | V3-SUP | 48364 | 16048 | 3609.800 | 378681.200 | 0.956 | 0.931 | 0.751 | 0.831 | 0.009 | 0.991 | 0.871 | 0.812 | 0.144 | 0.445 | 0.516 | 0.516 | 0.954 | 0.841 |
| within | loo | 1% | 0 | V3-SUP-DENSE | 46307 | 18105 | 3850.700 | 378440.300 | 0.951 | 0.923 | 0.719 | 0.808 | 0.010 | 0.990 | 0.854 | 0.789 | 0.144 | 0.419 | 0.481 | 0.481 | 0.949 | 0.816 |
| within | loo | 1% | 0 | V3-SUP-TT | 46448 | 17964 | 3597.600 | 378693.400 | 0.952 | 0.928 | 0.721 | 0.812 | 0.009 | 0.991 | 0.856 | 0.793 | 0.144 | 0.436 | 0.501 | 0.501 | 0.934 | 0.829 |
| within | loo | 1% | 1 | TREE | 47142 | 17270 | 3791.900 | 378499.100 | 0.953 | 0.926 | 0.732 | 0.817 | 0.010 | 0.990 | 0.861 | 0.798 | 0.144 | 0.427 | 0.481 | 0.481 | 0.975 | 0.839 |
| within | loo | 1% | 1 | V3-MAX | 50298 | 14114 | 4142.100 | 378148.900 | 0.959 | 0.924 | 0.781 | 0.846 | 0.011 | 0.989 | 0.885 | 0.827 | 0.144 | 0.421 | 0.536 | 0.536 | 0.931 | 0.840 |
| within | loo | 1% | 1 | V3-MAX-RBF | 48268 | 16144 | 4130.600 | 378160.400 | 0.955 | 0.921 | 0.749 | 0.826 | 0.011 | 0.989 | 0.869 | 0.806 | 0.144 | 0.412 | 0.528 | 0.528 | 0.944 | 0.839 |
| within | loo | 1% | 1 | V3-SUP | 48562 | 15850 | 3647.800 | 378643.200 | 0.956 | 0.930 | 0.754 | 0.833 | 0.010 | 0.990 | 0.872 | 0.814 | 0.144 | 0.444 | 0.486 | 0.486 | 0.930 | 0.849 |
| within | loo | 1% | 1 | V3-SUP-DENSE | 46569 | 17843 | 3749.400 | 378541.600 | 0.952 | 0.925 | 0.723 | 0.812 | 0.010 | 0.990 | 0.857 | 0.792 | 0.144 | 0.427 | 0.477 | 0.477 | 0.932 | 0.816 |
| within | loo | 1% | 1 | V3-SUP-TT | 48626 | 15786 | 3485.100 | 378805.900 | 0.957 | 0.933 | 0.755 | 0.835 | 0.009 | 0.991 | 0.873 | 0.816 | 0.144 | 0.455 | 0.502 | 0.502 | 0.911 | 0.851 |
| within | loo | 1% | 2 | TREE | 48213 | 16199 | 3839.900 | 378451.100 | 0.955 | 0.926 | 0.749 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.429 | 0.541 | 0.541 | 0.929 | 0.854 |
| within | loo | 1% | 2 | V3-MAX | 55699 | 8713 | 4141.100 | 378149.900 | 0.971 | 0.931 | 0.865 | 0.897 | 0.011 | 0.989 | 0.927 | 0.881 | 0.144 | 0.446 | 0.598 | 0.598 | 0.979 | 0.857 |
| within | loo | 1% | 2 | V3-MAX-RBF | 49477 | 14935 | 3874.200 | 378416.800 | 0.958 | 0.927 | 0.768 | 0.840 | 0.010 | 0.990 | 0.879 | 0.821 | 0.144 | 0.434 | 0.575 | 0.575 | 0.978 | 0.849 |
| within | loo | 1% | 2 | V3-SUP | 48596 | 15816 | 3784.600 | 378506.400 | 0.956 | 0.928 | 0.754 | 0.832 | 0.010 | 0.990 | 0.872 | 0.813 | 0.144 | 0.435 | 0.542 | 0.542 | 0.978 | 0.857 |
| within | loo | 1% | 2 | V3-SUP-DENSE | 48238 | 16174 | 3828.200 | 378462.800 | 0.955 | 0.926 | 0.749 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.430 | 0.540 | 0.540 | 0.942 | 0.857 |
| within | loo | 1% | 2 | V3-SUP-TT | 49057 | 15355 | 3688.800 | 378602.200 | 0.957 | 0.930 | 0.762 | 0.837 | 0.010 | 0.990 | 0.876 | 0.819 | 0.144 | 0.444 | 0.544 | 0.544 | 0.861 | 0.860 |

## R12_v33_cross10. Derived metrics from v33_cross10/metrics_overall.csv

| protocol | scenario | op | seed | model | TP | FN | FP | TN | accuracy | precision | recall | f1 | fpr | specificity | balanced_acc | mcc | prevalence | precision_at_prev1 | macro_recall | macro_recall_nontiny | auc | pauc1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| cross | known | 0.1% | 0 | TREE | 14043 | 103677 | 72.000 | 86823.000 | 0.493 | 0.995 | 0.119 | 0.213 | 0.0008 | 0.999 | 0.559 | 0.231 | 0.575 | 0.593 | 0.280 | 0.160 | 0.834 | 0.619 |
| cross | known | 0.1% | 0 | V3-MAX | 13434 | 104286 | 90.000 | 86805.000 | 0.490 | 0.993 | 0.114 | 0.205 | 0.001 | 0.999 | 0.557 | 0.225 | 0.575 | 0.527 | 0.200 | 0.102 | 0.879 | 0.614 |
| cross | known | 0.1% | 0 | V3-MAX-RBF | 13469 | 104251 | 94.000 | 86801.000 | 0.490 | 0.993 | 0.114 | 0.205 | 0.001 | 0.999 | 0.557 | 0.225 | 0.575 | 0.517 | 0.208 | 0.103 | 0.875 | 0.614 |
| cross | known | 0.1% | 0 | V3-SUP | 21735 | 95985 | 78.000 | 86817.000 | 0.531 | 0.996 | 0.185 | 0.312 | 0.0009 | 0.999 | 0.592 | 0.294 | 0.575 | 0.675 | 0.306 | 0.191 | 0.886 | 0.633 |
| cross | known | 0.1% | 0 | V3-SUP-DENSE | 16821 | 100899 | 64.000 | 86831.000 | 0.507 | 0.996 | 0.143 | 0.250 | 0.0007 | 0.999 | 0.571 | 0.255 | 0.575 | 0.662 | 0.199 | 0.151 | 0.777 | 0.597 |
| cross | known | 0.1% | 1 | TREE | 13385 | 104335 | 61.000 | 86834.000 | 0.490 | 0.995 | 0.114 | 0.204 | 0.0007 | 0.999 | 0.557 | 0.225 | 0.575 | 0.621 | 0.101 | 0.115 | 0.789 | 0.615 |
| cross | known | 0.1% | 1 | V3-MAX | 8614 | 109106 | 94.000 | 86801.000 | 0.466 | 0.989 | 0.073 | 0.136 | 0.001 | 0.999 | 0.536 | 0.177 | 0.575 | 0.406 | 0.074 | 0.058 | 0.803 | 0.595 |
| cross | known | 0.1% | 1 | V3-MAX-RBF | 8069 | 109651 | 98.000 | 86797.000 | 0.464 | 0.988 | 0.069 | 0.128 | 0.001 | 0.999 | 0.534 | 0.170 | 0.575 | 0.380 | 0.064 | 0.054 | 0.802 | 0.596 |
| cross | known | 0.1% | 1 | V3-SUP | 15349 | 102371 | 81.000 | 86814.000 | 0.499 | 0.995 | 0.130 | 0.231 | 0.0009 | 0.999 | 0.565 | 0.242 | 0.575 | 0.586 | 0.159 | 0.111 | 0.817 | 0.626 |
| cross | known | 0.1% | 1 | V3-SUP-DENSE | 13393 | 104327 | 73.000 | 86822.000 | 0.490 | 0.995 | 0.114 | 0.204 | 0.0008 | 0.999 | 0.556 | 0.225 | 0.575 | 0.578 | 0.101 | 0.115 | 0.806 | 0.569 |
| cross | known | 0.1% | 2 | TREE | 16813 | 100907 | 79.000 | 86816.000 | 0.506 | 0.995 | 0.143 | 0.250 | 0.0009 | 0.999 | 0.571 | 0.255 | 0.575 | 0.613 | 0.196 | 0.137 | 0.853 | 0.608 |
| cross | known | 0.1% | 2 | V3-MAX | 15587 | 102133 | 99.000 | 86796.000 | 0.500 | 0.994 | 0.132 | 0.234 | 0.001 | 0.999 | 0.566 | 0.244 | 0.575 | 0.540 | 0.162 | 0.098 | 0.903 | 0.631 |
| cross | known | 0.1% | 2 | V3-MAX-RBF | 15588 | 102132 | 99.000 | 86796.000 | 0.500 | 0.994 | 0.132 | 0.234 | 0.001 | 0.999 | 0.566 | 0.244 | 0.575 | 0.540 | 0.162 | 0.098 | 0.893 | 0.630 |
| cross | known | 0.1% | 2 | V3-SUP | 17803 | 99917 | 79.000 | 86816.000 | 0.511 | 0.996 | 0.151 | 0.263 | 0.0009 | 0.999 | 0.575 | 0.263 | 0.575 | 0.627 | 0.178 | 0.116 | 0.904 | 0.672 |
| cross | known | 0.1% | 2 | V3-SUP-DENSE | 17010 | 100710 | 83.000 | 86812.000 | 0.507 | 0.995 | 0.144 | 0.252 | 0.0010 | 0.999 | 0.572 | 0.256 | 0.575 | 0.604 | 0.174 | 0.112 | 0.849 | 0.601 |
| cross | known | 0.1% | 3 | TREE | 16623 | 101097 | 61.000 | 86834.000 | 0.506 | 0.996 | 0.141 | 0.247 | 0.0007 | 0.999 | 0.570 | 0.254 | 0.575 | 0.670 | 0.206 | 0.163 | 0.793 | 0.574 |
| cross | known | 0.1% | 3 | V3-MAX | 13313 | 104407 | 78.000 | 86817.000 | 0.489 | 0.994 | 0.113 | 0.203 | 0.0009 | 0.999 | 0.556 | 0.224 | 0.575 | 0.560 | 0.152 | 0.096 | 0.738 | 0.570 |
| cross | known | 0.1% | 3 | V3-MAX-RBF | 13331 | 104389 | 91.000 | 86804.000 | 0.489 | 0.993 | 0.113 | 0.203 | 0.001 | 0.999 | 0.556 | 0.224 | 0.575 | 0.522 | 0.140 | 0.097 | 0.721 | 0.570 |
| cross | known | 0.1% | 3 | V3-SUP | 15495 | 102225 | 76.000 | 86819.000 | 0.500 | 0.995 | 0.132 | 0.232 | 0.0009 | 0.999 | 0.565 | 0.244 | 0.575 | 0.603 | 0.200 | 0.113 | 0.740 | 0.585 |
| cross | known | 0.1% | 3 | V3-SUP-DENSE | 15757 | 101963 | 65.000 | 86830.000 | 0.501 | 0.996 | 0.134 | 0.236 | 0.0007 | 0.999 | 0.567 | 0.246 | 0.575 | 0.644 | 0.157 | 0.107 | 0.761 | 0.569 |
| cross | known | 0.1% | 4 | TREE | 12931 | 104789 | 75.000 | 86820.000 | 0.488 | 0.994 | 0.110 | 0.198 | 0.0009 | 0.999 | 0.554 | 0.221 | 0.575 | 0.562 | 0.081 | 0.094 | 0.832 | 0.553 |
| cross | known | 0.1% | 4 | V3-MAX | 7890 | 109830 | 83.000 | 86812.000 | 0.463 | 0.990 | 0.067 | 0.126 | 0.0010 | 0.999 | 0.533 | 0.169 | 0.575 | 0.415 | 0.045 | 0.052 | 0.811 | 0.536 |
| cross | known | 0.1% | 4 | V3-MAX-RBF | 7787 | 109933 | 81.000 | 86814.000 | 0.462 | 0.990 | 0.066 | 0.124 | 0.0009 | 0.999 | 0.533 | 0.168 | 0.575 | 0.418 | 0.044 | 0.051 | 0.814 | 0.536 |
| cross | known | 0.1% | 4 | V3-SUP | 8242 | 109478 | 73.000 | 86822.000 | 0.465 | 0.991 | 0.070 | 0.131 | 0.0008 | 0.999 | 0.535 | 0.173 | 0.575 | 0.457 | 0.046 | 0.054 | 0.835 | 0.538 |
| cross | known | 0.1% | 4 | V3-SUP-DENSE | 13021 | 104699 | 78.000 | 86817.000 | 0.488 | 0.994 | 0.111 | 0.199 | 0.0009 | 0.999 | 0.555 | 0.222 | 0.575 | 0.555 | 0.081 | 0.094 | 0.812 | 0.552 |
| cross | known | 0.1% | 5 | TREE | 13201 | 104519 | 68.000 | 86827.000 | 0.489 | 0.995 | 0.112 | 0.202 | 0.0008 | 0.999 | 0.556 | 0.224 | 0.575 | 0.591 | 0.222 | 0.098 | 0.789 | 0.576 |
| cross | known | 0.1% | 5 | V3-MAX | 12817 | 104903 | 87.000 | 86808.000 | 0.487 | 0.993 | 0.109 | 0.196 | 0.001 | 0.999 | 0.554 | 0.219 | 0.575 | 0.523 | 0.158 | 0.093 | 0.816 | 0.566 |
| cross | known | 0.1% | 5 | V3-MAX-RBF | 12815 | 104905 | 92.000 | 86803.000 | 0.487 | 0.993 | 0.109 | 0.196 | 0.001 | 0.999 | 0.554 | 0.219 | 0.575 | 0.509 | 0.158 | 0.093 | 0.815 | 0.566 |
| cross | known | 0.1% | 5 | V3-SUP | 14627 | 103093 | 92.000 | 86803.000 | 0.496 | 0.994 | 0.124 | 0.221 | 0.001 | 0.999 | 0.562 | 0.236 | 0.575 | 0.542 | 0.235 | 0.110 | 0.849 | 0.592 |
| cross | known | 0.1% | 5 | V3-SUP-DENSE | 8642 | 109078 | 58.000 | 86837.000 | 0.467 | 0.993 | 0.073 | 0.137 | 0.0007 | 0.999 | 0.536 | 0.178 | 0.575 | 0.526 | 0.189 | 0.059 | 0.741 | 0.568 |
| cross | known | 0.1% | 6 | TREE | 13231 | 104489 | 68.000 | 86827.000 | 0.489 | 0.995 | 0.112 | 0.202 | 0.0008 | 0.999 | 0.556 | 0.224 | 0.575 | 0.592 | 0.104 | 0.099 | 0.841 | 0.554 |
| cross | known | 0.1% | 6 | V3-MAX | 6765 | 110955 | 84.000 | 86811.000 | 0.457 | 0.988 | 0.057 | 0.109 | 0.0010 | 0.999 | 0.528 | 0.155 | 0.575 | 0.375 | 0.037 | 0.043 | 0.871 | 0.558 |
| cross | known | 0.1% | 6 | V3-MAX-RBF | 8304 | 109416 | 86.000 | 86809.000 | 0.465 | 0.990 | 0.071 | 0.132 | 0.0010 | 0.999 | 0.535 | 0.173 | 0.575 | 0.419 | 0.050 | 0.056 | 0.867 | 0.558 |
| cross | known | 0.1% | 6 | V3-SUP | 14426 | 103294 | 77.000 | 86818.000 | 0.495 | 0.995 | 0.123 | 0.218 | 0.0009 | 0.999 | 0.561 | 0.234 | 0.575 | 0.583 | 0.107 | 0.102 | 0.886 | 0.562 |
| cross | known | 0.1% | 6 | V3-SUP-DENSE | 13138 | 104582 | 73.000 | 86822.000 | 0.489 | 0.994 | 0.112 | 0.201 | 0.0008 | 0.999 | 0.555 | 0.223 | 0.575 | 0.573 | 0.082 | 0.095 | 0.857 | 0.553 |
| cross | known | 0.1% | 7 | TREE | 13633 | 104087 | 73.000 | 86822.000 | 0.491 | 0.995 | 0.116 | 0.207 | 0.0008 | 0.999 | 0.557 | 0.227 | 0.575 | 0.582 | 0.271 | 0.149 | 0.822 | 0.623 |
| cross | known | 0.1% | 7 | V3-MAX | 14215 | 103505 | 84.000 | 86811.000 | 0.494 | 0.994 | 0.121 | 0.215 | 0.0010 | 0.999 | 0.560 | 0.232 | 0.575 | 0.558 | 0.213 | 0.113 | 0.817 | 0.628 |
| cross | known | 0.1% | 7 | V3-MAX-RBF | 14126 | 103594 | 92.000 | 86803.000 | 0.493 | 0.994 | 0.120 | 0.214 | 0.001 | 0.999 | 0.559 | 0.231 | 0.575 | 0.534 | 0.210 | 0.110 | 0.801 | 0.628 |
| cross | known | 0.1% | 7 | V3-SUP | 18768 | 98952 | 81.000 | 86814.000 | 0.516 | 0.996 | 0.159 | 0.275 | 0.0009 | 0.999 | 0.579 | 0.271 | 0.575 | 0.633 | 0.280 | 0.160 | 0.824 | 0.663 |
| cross | known | 0.1% | 7 | V3-SUP-DENSE | 13534 | 104186 | 73.000 | 86822.000 | 0.490 | 0.995 | 0.115 | 0.206 | 0.0008 | 0.999 | 0.557 | 0.226 | 0.575 | 0.580 | 0.245 | 0.119 | 0.858 | 0.608 |
| cross | known | 0.1% | 8 | TREE | 15410 | 102310 | 58.000 | 86837.000 | 0.500 | 0.996 | 0.131 | 0.231 | 0.0007 | 0.999 | 0.565 | 0.244 | 0.575 | 0.665 | 0.264 | 0.146 | 0.846 | 0.653 |
| cross | known | 0.1% | 8 | V3-MAX | 11222 | 106498 | 93.000 | 86802.000 | 0.479 | 0.992 | 0.095 | 0.174 | 0.001 | 0.999 | 0.547 | 0.204 | 0.575 | 0.474 | 0.153 | 0.077 | 0.869 | 0.593 |
| cross | known | 0.1% | 8 | V3-MAX-RBF | 11268 | 106452 | 95.000 | 86800.000 | 0.479 | 0.992 | 0.096 | 0.175 | 0.001 | 0.999 | 0.547 | 0.204 | 0.575 | 0.469 | 0.153 | 0.077 | 0.858 | 0.594 |
| cross | known | 0.1% | 8 | V3-SUP | 17539 | 100181 | 83.000 | 86812.000 | 0.510 | 0.995 | 0.149 | 0.259 | 0.0010 | 0.999 | 0.574 | 0.261 | 0.575 | 0.612 | 0.229 | 0.126 | 0.869 | 0.629 |
| cross | known | 0.1% | 8 | V3-SUP-DENSE | 9747 | 107973 | 73.000 | 86822.000 | 0.472 | 0.993 | 0.083 | 0.153 | 0.0008 | 0.999 | 0.541 | 0.190 | 0.575 | 0.499 | 0.053 | 0.061 | 0.838 | 0.638 |
| cross | known | 0.1% | 9 | TREE | 13976 | 103744 | 64.000 | 86831.000 | 0.493 | 0.995 | 0.119 | 0.212 | 0.0007 | 0.999 | 0.559 | 0.231 | 0.575 | 0.620 | 0.210 | 0.099 | 0.824 | 0.562 |
| cross | known | 0.1% | 9 | V3-MAX | 9259 | 108461 | 93.000 | 86802.000 | 0.469 | 0.990 | 0.079 | 0.146 | 0.001 | 0.999 | 0.539 | 0.184 | 0.575 | 0.426 | 0.121 | 0.062 | 0.801 | 0.570 |
| cross | known | 0.1% | 9 | V3-MAX-RBF | 9100 | 108620 | 100.000 | 86795.000 | 0.469 | 0.989 | 0.077 | 0.143 | 0.001 | 0.999 | 0.538 | 0.182 | 0.575 | 0.404 | 0.120 | 0.060 | 0.807 | 0.570 |
| cross | known | 0.1% | 9 | V3-SUP | 14998 | 102722 | 99.000 | 86796.000 | 0.497 | 0.993 | 0.127 | 0.226 | 0.001 | 0.999 | 0.563 | 0.239 | 0.575 | 0.530 | 0.211 | 0.111 | 0.834 | 0.576 |
| cross | known | 0.1% | 9 | V3-SUP-DENSE | 9219 | 108501 | 95.000 | 86800.000 | 0.469 | 0.990 | 0.078 | 0.145 | 0.001 | 0.999 | 0.539 | 0.183 | 0.575 | 0.420 | 0.052 | 0.060 | 0.846 | 0.536 |
| cross | known | 1% | 0 | TREE | 34427 | 83293 | 556.000 | 86339.000 | 0.590 | 0.984 | 0.292 | 0.451 | 0.006 | 0.994 | 0.643 | 0.376 | 0.575 | 0.316 | 0.363 | 0.257 | 0.834 | 0.619 |
| cross | known | 1% | 0 | V3-MAX | 33361 | 84359 | 805.000 | 86090.000 | 0.584 | 0.976 | 0.283 | 0.439 | 0.009 | 0.991 | 0.637 | 0.363 | 0.575 | 0.236 | 0.374 | 0.270 | 0.879 | 0.614 |
| cross | known | 1% | 0 | V3-MAX-RBF | 33435 | 84285 | 770.000 | 86125.000 | 0.584 | 0.977 | 0.284 | 0.440 | 0.009 | 0.991 | 0.638 | 0.365 | 0.575 | 0.245 | 0.374 | 0.270 | 0.875 | 0.614 |
| cross | known | 1% | 0 | V3-SUP | 43084 | 74636 | 891.000 | 86004.000 | 0.631 | 0.980 | 0.366 | 0.533 | 0.010 | 0.990 | 0.678 | 0.428 | 0.575 | 0.265 | 0.400 | 0.300 | 0.886 | 0.633 |
| cross | known | 1% | 0 | V3-SUP-DENSE | 24829 | 92891 | 832.000 | 86063.000 | 0.542 | 0.968 | 0.211 | 0.346 | 0.010 | 0.990 | 0.601 | 0.301 | 0.575 | 0.182 | 0.320 | 0.207 | 0.777 | 0.597 |
| cross | known | 1% | 1 | TREE | 37886 | 79834 | 531.000 | 86364.000 | 0.607 | 0.986 | 0.322 | 0.485 | 0.006 | 0.994 | 0.658 | 0.400 | 0.575 | 0.347 | 0.403 | 0.303 | 0.789 | 0.615 |
| cross | known | 1% | 1 | V3-MAX | 34423 | 83297 | 804.000 | 86091.000 | 0.589 | 0.977 | 0.292 | 0.450 | 0.009 | 0.991 | 0.642 | 0.371 | 0.575 | 0.242 | 0.360 | 0.257 | 0.803 | 0.595 |
| cross | known | 1% | 1 | V3-MAX-RBF | 33818 | 83902 | 767.000 | 86128.000 | 0.586 | 0.978 | 0.287 | 0.444 | 0.009 | 0.991 | 0.639 | 0.367 | 0.575 | 0.247 | 0.359 | 0.256 | 0.802 | 0.596 |
| cross | known | 1% | 1 | V3-SUP | 42744 | 74976 | 842.000 | 86053.000 | 0.629 | 0.981 | 0.363 | 0.530 | 0.010 | 0.990 | 0.677 | 0.427 | 0.575 | 0.275 | 0.413 | 0.315 | 0.817 | 0.626 |
| cross | known | 1% | 1 | V3-SUP-DENSE | 18774 | 98946 | 913.000 | 85982.000 | 0.512 | 0.954 | 0.159 | 0.273 | 0.011 | 0.989 | 0.574 | 0.250 | 0.575 | 0.133 | 0.212 | 0.145 | 0.806 | 0.569 |
| cross | known | 1% | 2 | TREE | 28957 | 88763 | 296.000 | 86599.000 | 0.565 | 0.990 | 0.246 | 0.394 | 0.003 | 0.997 | 0.621 | 0.343 | 0.575 | 0.422 | 0.259 | 0.201 | 0.853 | 0.608 |
| cross | known | 1% | 2 | V3-MAX | 44525 | 73195 | 788.000 | 86107.000 | 0.638 | 0.983 | 0.378 | 0.546 | 0.009 | 0.991 | 0.685 | 0.439 | 0.575 | 0.296 | 0.380 | 0.297 | 0.903 | 0.631 |
| cross | known | 1% | 2 | V3-MAX-RBF | 44130 | 73590 | 769.000 | 86126.000 | 0.637 | 0.983 | 0.375 | 0.543 | 0.009 | 0.991 | 0.683 | 0.437 | 0.575 | 0.300 | 0.387 | 0.295 | 0.893 | 0.630 |
| cross | known | 1% | 2 | V3-SUP | 57245 | 60475 | 847.000 | 86048.000 | 0.700 | 0.985 | 0.486 | 0.651 | 0.010 | 0.990 | 0.738 | 0.522 | 0.575 | 0.335 | 0.451 | 0.375 | 0.904 | 0.672 |
| cross | known | 1% | 2 | V3-SUP-DENSE | 26447 | 91273 | 838.000 | 86057.000 | 0.550 | 0.969 | 0.225 | 0.365 | 0.010 | 0.990 | 0.608 | 0.313 | 0.575 | 0.190 | 0.231 | 0.178 | 0.849 | 0.601 |
| cross | known | 1% | 3 | TREE | 18678 | 99042 | 299.000 | 86596.000 | 0.514 | 0.984 | 0.159 | 0.273 | 0.003 | 0.997 | 0.578 | 0.265 | 0.575 | 0.318 | 0.295 | 0.177 | 0.793 | 0.574 |
| cross | known | 1% | 3 | V3-MAX | 22369 | 95351 | 832.000 | 86063.000 | 0.530 | 0.964 | 0.190 | 0.317 | 0.010 | 0.990 | 0.590 | 0.281 | 0.575 | 0.167 | 0.325 | 0.213 | 0.738 | 0.570 |
| cross | known | 1% | 3 | V3-MAX-RBF | 22695 | 95025 | 817.000 | 86078.000 | 0.532 | 0.965 | 0.193 | 0.321 | 0.009 | 0.991 | 0.592 | 0.284 | 0.575 | 0.172 | 0.327 | 0.215 | 0.721 | 0.570 |
| cross | known | 1% | 3 | V3-SUP | 26228 | 91492 | 854.000 | 86041.000 | 0.549 | 0.968 | 0.223 | 0.362 | 0.010 | 0.990 | 0.606 | 0.311 | 0.575 | 0.186 | 0.326 | 0.213 | 0.740 | 0.585 |
| cross | known | 1% | 3 | V3-SUP-DENSE | 17381 | 100339 | 892.000 | 86003.000 | 0.505 | 0.951 | 0.148 | 0.256 | 0.010 | 0.990 | 0.569 | 0.238 | 0.575 | 0.127 | 0.243 | 0.117 | 0.761 | 0.569 |
| cross | known | 1% | 4 | TREE | 13124 | 104596 | 127.000 | 86768.000 | 0.488 | 0.990 | 0.111 | 0.200 | 0.001 | 0.999 | 0.555 | 0.221 | 0.575 | 0.435 | 0.084 | 0.098 | 0.832 | 0.553 |
| cross | known | 1% | 4 | V3-MAX | 10387 | 107333 | 796.000 | 86099.000 | 0.472 | 0.929 | 0.088 | 0.161 | 0.009 | 0.991 | 0.540 | 0.172 | 0.575 | 0.089 | 0.074 | 0.087 | 0.811 | 0.536 |
| cross | known | 1% | 4 | V3-MAX-RBF | 10414 | 107306 | 765.000 | 86130.000 | 0.472 | 0.932 | 0.088 | 0.162 | 0.009 | 0.991 | 0.540 | 0.173 | 0.575 | 0.092 | 0.102 | 0.087 | 0.814 | 0.536 |
| cross | known | 1% | 4 | V3-SUP | 10110 | 107610 | 892.000 | 86003.000 | 0.470 | 0.919 | 0.086 | 0.157 | 0.010 | 0.990 | 0.538 | 0.166 | 0.575 | 0.078 | 0.058 | 0.067 | 0.835 | 0.538 |
| cross | known | 1% | 4 | V3-SUP-DENSE | 13238 | 104482 | 900.000 | 85995.000 | 0.485 | 0.936 | 0.112 | 0.201 | 0.010 | 0.990 | 0.551 | 0.199 | 0.575 | 0.099 | 0.084 | 0.098 | 0.812 | 0.552 |
| cross | known | 1% | 5 | TREE | 25461 | 92259 | 849.000 | 86046.000 | 0.545 | 0.968 | 0.216 | 0.354 | 0.010 | 0.990 | 0.603 | 0.305 | 0.575 | 0.183 | 0.318 | 0.205 | 0.789 | 0.576 |
| cross | known | 1% | 5 | V3-MAX | 19785 | 97935 | 801.000 | 86094.000 | 0.517 | 0.961 | 0.168 | 0.286 | 0.009 | 0.991 | 0.579 | 0.261 | 0.575 | 0.156 | 0.285 | 0.165 | 0.816 | 0.566 |
| cross | known | 1% | 5 | V3-MAX-RBF | 19719 | 98001 | 755.000 | 86140.000 | 0.517 | 0.963 | 0.168 | 0.285 | 0.009 | 0.991 | 0.579 | 0.262 | 0.575 | 0.163 | 0.285 | 0.165 | 0.815 | 0.566 |
| cross | known | 1% | 5 | V3-SUP | 37678 | 80042 | 842.000 | 86053.000 | 0.605 | 0.978 | 0.320 | 0.482 | 0.010 | 0.990 | 0.655 | 0.392 | 0.575 | 0.250 | 0.354 | 0.247 | 0.849 | 0.592 |
| cross | known | 1% | 5 | V3-SUP-DENSE | 24592 | 93128 | 863.000 | 86032.000 | 0.541 | 0.966 | 0.209 | 0.344 | 0.010 | 0.990 | 0.599 | 0.298 | 0.575 | 0.175 | 0.310 | 0.195 | 0.741 | 0.568 |
| cross | known | 1% | 6 | TREE | 13322 | 104398 | 88.000 | 86807.000 | 0.489 | 0.993 | 0.113 | 0.203 | 0.001 | 0.999 | 0.556 | 0.224 | 0.575 | 0.530 | 0.168 | 0.102 | 0.841 | 0.554 |
| cross | known | 1% | 6 | V3-MAX | 16597 | 101123 | 855.000 | 86040.000 | 0.502 | 0.951 | 0.141 | 0.246 | 0.010 | 0.990 | 0.566 | 0.232 | 0.575 | 0.126 | 0.194 | 0.132 | 0.871 | 0.558 |
| cross | known | 1% | 6 | V3-MAX-RBF | 16697 | 101023 | 827.000 | 86068.000 | 0.502 | 0.953 | 0.142 | 0.247 | 0.010 | 0.990 | 0.566 | 0.234 | 0.575 | 0.131 | 0.206 | 0.141 | 0.867 | 0.558 |
| cross | known | 1% | 6 | V3-SUP | 16653 | 101067 | 950.000 | 85945.000 | 0.501 | 0.946 | 0.141 | 0.246 | 0.011 | 0.989 | 0.565 | 0.230 | 0.575 | 0.116 | 0.225 | 0.130 | 0.886 | 0.562 |
| cross | known | 1% | 6 | V3-SUP-DENSE | 13290 | 104430 | 926.000 | 85969.000 | 0.485 | 0.935 | 0.113 | 0.201 | 0.011 | 0.989 | 0.551 | 0.199 | 0.575 | 0.097 | 0.085 | 0.099 | 0.857 | 0.553 |
| cross | known | 1% | 7 | TREE | 49380 | 68340 | 788.000 | 86107.000 | 0.662 | 0.984 | 0.419 | 0.588 | 0.009 | 0.991 | 0.705 | 0.472 | 0.575 | 0.318 | 0.453 | 0.362 | 0.822 | 0.623 |
| cross | known | 1% | 7 | V3-MAX | 43383 | 74337 | 806.000 | 86089.000 | 0.633 | 0.982 | 0.369 | 0.536 | 0.009 | 0.991 | 0.680 | 0.432 | 0.575 | 0.286 | 0.423 | 0.327 | 0.817 | 0.628 |
| cross | known | 1% | 7 | V3-MAX-RBF | 43159 | 74561 | 780.000 | 86115.000 | 0.632 | 0.982 | 0.367 | 0.534 | 0.009 | 0.991 | 0.679 | 0.431 | 0.575 | 0.292 | 0.414 | 0.316 | 0.801 | 0.628 |
| cross | known | 1% | 7 | V3-SUP | 51072 | 66648 | 836.000 | 86059.000 | 0.670 | 0.984 | 0.434 | 0.602 | 0.010 | 0.990 | 0.712 | 0.482 | 0.575 | 0.313 | 0.451 | 0.359 | 0.824 | 0.663 |
| cross | known | 1% | 7 | V3-SUP-DENSE | 34647 | 83073 | 807.000 | 86088.000 | 0.590 | 0.977 | 0.294 | 0.452 | 0.009 | 0.991 | 0.643 | 0.372 | 0.575 | 0.242 | 0.400 | 0.300 | 0.858 | 0.608 |
| cross | known | 1% | 8 | TREE | 66823 | 50897 | 790.000 | 86105.000 | 0.747 | 0.988 | 0.568 | 0.721 | 0.009 | 0.991 | 0.779 | 0.587 | 0.575 | 0.387 | 0.541 | 0.465 | 0.846 | 0.653 |
| cross | known | 1% | 8 | V3-MAX | 33486 | 84234 | 805.000 | 86090.000 | 0.584 | 0.977 | 0.284 | 0.441 | 0.009 | 0.991 | 0.638 | 0.364 | 0.575 | 0.237 | 0.384 | 0.281 | 0.869 | 0.593 |
| cross | known | 1% | 8 | V3-MAX-RBF | 33456 | 84264 | 773.000 | 86122.000 | 0.584 | 0.977 | 0.284 | 0.440 | 0.009 | 0.991 | 0.638 | 0.365 | 0.575 | 0.244 | 0.384 | 0.281 | 0.858 | 0.594 |
| cross | known | 1% | 8 | V3-SUP | 44365 | 73355 | 866.000 | 86029.000 | 0.637 | 0.981 | 0.377 | 0.545 | 0.010 | 0.990 | 0.683 | 0.437 | 0.575 | 0.276 | 0.422 | 0.326 | 0.869 | 0.629 |
| cross | known | 1% | 8 | V3-SUP-DENSE | 55448 | 62272 | 854.000 | 86041.000 | 0.691 | 0.985 | 0.471 | 0.637 | 0.010 | 0.990 | 0.731 | 0.510 | 0.575 | 0.326 | 0.472 | 0.384 | 0.838 | 0.638 |
| cross | known | 1% | 9 | TREE | 15866 | 101854 | 185.000 | 86710.000 | 0.501 | 0.988 | 0.135 | 0.237 | 0.002 | 0.998 | 0.566 | 0.244 | 0.575 | 0.390 | 0.238 | 0.126 | 0.824 | 0.562 |
| cross | known | 1% | 9 | V3-MAX | 20759 | 96961 | 847.000 | 86048.000 | 0.522 | 0.961 | 0.176 | 0.298 | 0.010 | 0.990 | 0.583 | 0.268 | 0.575 | 0.155 | 0.314 | 0.199 | 0.801 | 0.570 |
| cross | known | 1% | 9 | V3-MAX-RBF | 20823 | 96897 | 809.000 | 86086.000 | 0.522 | 0.963 | 0.177 | 0.299 | 0.009 | 0.991 | 0.584 | 0.269 | 0.575 | 0.161 | 0.313 | 0.199 | 0.807 | 0.570 |
| cross | known | 1% | 9 | V3-SUP | 20631 | 97089 | 897.000 | 85998.000 | 0.521 | 0.958 | 0.175 | 0.296 | 0.010 | 0.990 | 0.582 | 0.266 | 0.575 | 0.146 | 0.298 | 0.181 | 0.834 | 0.576 |
| cross | known | 1% | 9 | V3-SUP-DENSE | 9527 | 108193 | 918.000 | 85977.000 | 0.467 | 0.912 | 0.081 | 0.149 | 0.011 | 0.989 | 0.535 | 0.158 | 0.575 | 0.072 | 0.055 | 0.065 | 0.846 | 0.536 |
| cross | loo | 0.1% | 0 | TREE | 10949 | 90600 | 69.833 | 86825.167 | 0.519 | 0.994 | 0.108 | 0.195 | 0.0008 | 0.999 | 0.554 | 0.227 | 0.539 | 0.575 | 0.090 | 0.107 | 0.842 | 0.580 |
| cross | loo | 0.1% | 0 | V3-MAX | 9961 | 91588 | 89.250 | 86805.750 | 0.514 | 0.991 | 0.098 | 0.179 | 0.001 | 0.999 | 0.549 | 0.215 | 0.539 | 0.491 | 0.082 | 0.089 | 0.734 | 0.577 |
| cross | loo | 0.1% | 0 | V3-MAX-RBF | 9993 | 91556 | 93.750 | 86801.250 | 0.514 | 0.991 | 0.098 | 0.179 | 0.001 | 0.999 | 0.549 | 0.216 | 0.539 | 0.480 | 0.082 | 0.089 | 0.731 | 0.577 |
| cross | loo | 0.1% | 0 | V3-SUP | 11531 | 90018 | 79.417 | 86815.583 | 0.522 | 0.993 | 0.114 | 0.204 | 0.0009 | 0.999 | 0.556 | 0.234 | 0.539 | 0.557 | 0.103 | 0.097 | 0.773 | 0.583 |
| cross | loo | 0.1% | 0 | V3-SUP-DENSE | 12977 | 88572 | 77.167 | 86817.833 | 0.530 | 0.994 | 0.128 | 0.226 | 0.0009 | 0.999 | 0.563 | 0.249 | 0.539 | 0.592 | 0.094 | 0.113 | 0.803 | 0.580 |
| cross | loo | 0.1% | 1 | TREE | 9512 | 92037 | 71.333 | 86823.667 | 0.511 | 0.993 | 0.094 | 0.171 | 0.0008 | 0.999 | 0.546 | 0.211 | 0.539 | 0.535 | 0.193 | 0.097 | 0.660 | 0.569 |
| cross | loo | 0.1% | 1 | V3-MAX | 8577 | 92972 | 88.250 | 86806.750 | 0.506 | 0.990 | 0.084 | 0.156 | 0.001 | 0.999 | 0.542 | 0.199 | 0.539 | 0.457 | 0.185 | 0.087 | 0.690 | 0.579 |
| cross | loo | 0.1% | 1 | V3-MAX-RBF | 8503 | 93046 | 91.000 | 86804.000 | 0.506 | 0.989 | 0.084 | 0.154 | 0.001 | 0.999 | 0.541 | 0.198 | 0.539 | 0.447 | 0.171 | 0.086 | 0.655 | 0.580 |
| cross | loo | 0.1% | 1 | V3-SUP | 12241 | 89308 | 82.083 | 86812.917 | 0.526 | 0.993 | 0.121 | 0.215 | 0.0009 | 0.999 | 0.560 | 0.241 | 0.539 | 0.563 | 0.247 | 0.110 | 0.716 | 0.589 |
| cross | loo | 0.1% | 1 | V3-SUP-DENSE | 9633 | 91916 | 73.750 | 86821.250 | 0.512 | 0.992 | 0.095 | 0.173 | 0.0008 | 0.999 | 0.547 | 0.212 | 0.539 | 0.530 | 0.193 | 0.096 | 0.735 | 0.569 |
| cross | loo | 0.1% | 2 | TREE | 10995 | 90554 | 71.583 | 86823.417 | 0.519 | 0.994 | 0.108 | 0.195 | 0.0008 | 0.999 | 0.554 | 0.228 | 0.539 | 0.570 | 0.185 | 0.093 | 0.782 | 0.570 |
| cross | loo | 0.1% | 2 | V3-MAX | 10535 | 91014 | 90.333 | 86804.667 | 0.517 | 0.991 | 0.104 | 0.188 | 0.001 | 0.999 | 0.551 | 0.222 | 0.539 | 0.502 | 0.119 | 0.090 | 0.722 | 0.557 |
| cross | loo | 0.1% | 2 | V3-MAX-RBF | 10522 | 91027 | 88.583 | 86806.417 | 0.516 | 0.992 | 0.104 | 0.188 | 0.001 | 0.999 | 0.551 | 0.222 | 0.539 | 0.507 | 0.109 | 0.090 | 0.725 | 0.557 |
| cross | loo | 0.1% | 2 | V3-SUP | 11011 | 90538 | 79.000 | 86816.000 | 0.519 | 0.993 | 0.108 | 0.196 | 0.0009 | 0.999 | 0.554 | 0.228 | 0.539 | 0.546 | 0.199 | 0.093 | 0.778 | 0.562 |
| cross | loo | 0.1% | 2 | V3-SUP-DENSE | 10977 | 90572 | 76.250 | 86818.750 | 0.519 | 0.993 | 0.108 | 0.195 | 0.0009 | 0.999 | 0.554 | 0.227 | 0.539 | 0.554 | 0.185 | 0.092 | 0.796 | 0.567 |
| cross | loo | 0.1% | 3 | TREE | 7262 | 94287 | 68.667 | 86826.333 | 0.499 | 0.991 | 0.072 | 0.133 | 0.0008 | 0.999 | 0.535 | 0.182 | 0.539 | 0.478 | 0.099 | 0.077 | 0.866 | 0.563 |
| cross | loo | 0.1% | 3 | V3-MAX | 7036 | 94513 | 81.500 | 86813.500 | 0.498 | 0.989 | 0.069 | 0.129 | 0.0009 | 0.999 | 0.534 | 0.179 | 0.539 | 0.427 | 0.066 | 0.071 | 0.783 | 0.543 |
| cross | loo | 0.1% | 3 | V3-MAX-RBF | 7085 | 94464 | 91.667 | 86803.333 | 0.498 | 0.987 | 0.070 | 0.130 | 0.001 | 0.999 | 0.534 | 0.179 | 0.539 | 0.400 | 0.060 | 0.072 | 0.776 | 0.545 |
| cross | loo | 0.1% | 3 | V3-SUP | 7128 | 94421 | 81.167 | 86813.833 | 0.499 | 0.989 | 0.070 | 0.131 | 0.0009 | 0.999 | 0.535 | 0.180 | 0.539 | 0.432 | 0.095 | 0.072 | 0.823 | 0.562 |
| cross | loo | 0.1% | 3 | V3-SUP-DENSE | 7087 | 94462 | 73.833 | 86821.167 | 0.498 | 0.990 | 0.070 | 0.130 | 0.0008 | 0.999 | 0.534 | 0.180 | 0.539 | 0.453 | 0.098 | 0.075 | 0.786 | 0.561 |
| cross | loo | 0.1% | 4 | TREE | 9739 | 91810 | 66.750 | 86828.250 | 0.512 | 0.993 | 0.096 | 0.175 | 0.0008 | 0.999 | 0.548 | 0.214 | 0.539 | 0.558 | 0.155 | 0.085 | 0.790 | 0.555 |
| cross | loo | 0.1% | 4 | V3-MAX | 4006 | 97543 | 84.583 | 86810.417 | 0.482 | 0.979 | 0.039 | 0.076 | 0.0010 | 0.999 | 0.519 | 0.132 | 0.539 | 0.290 | 0.027 | 0.033 | 0.669 | 0.533 |
| cross | loo | 0.1% | 4 | V3-MAX-RBF | 3904 | 97645 | 79.000 | 86816.000 | 0.481 | 0.980 | 0.038 | 0.074 | 0.0009 | 0.999 | 0.519 | 0.130 | 0.539 | 0.299 | 0.026 | 0.032 | 0.595 | 0.533 |
| cross | loo | 0.1% | 4 | V3-SUP | 5010 | 96539 | 78.500 | 86816.500 | 0.487 | 0.985 | 0.049 | 0.094 | 0.0009 | 0.999 | 0.524 | 0.149 | 0.539 | 0.356 | 0.112 | 0.037 | 0.663 | 0.542 |
| cross | loo | 0.1% | 4 | V3-SUP-DENSE | 5009 | 96540 | 76.833 | 86818.167 | 0.487 | 0.985 | 0.049 | 0.094 | 0.0009 | 0.999 | 0.524 | 0.149 | 0.539 | 0.360 | 0.112 | 0.037 | 0.736 | 0.535 |
| cross | loo | 0.1% | 5 | TREE | 8007 | 93542 | 69.750 | 86825.250 | 0.503 | 0.991 | 0.079 | 0.146 | 0.0008 | 0.999 | 0.539 | 0.192 | 0.539 | 0.498 | 0.202 | 0.077 | 0.824 | 0.561 |
| cross | loo | 0.1% | 5 | V3-MAX | 7455 | 94094 | 94.750 | 86800.250 | 0.500 | 0.987 | 0.073 | 0.137 | 0.001 | 0.999 | 0.536 | 0.184 | 0.539 | 0.405 | 0.177 | 0.072 | 0.740 | 0.563 |
| cross | loo | 0.1% | 5 | V3-MAX-RBF | 6741 | 94808 | 97.917 | 86797.083 | 0.496 | 0.986 | 0.066 | 0.124 | 0.001 | 0.999 | 0.533 | 0.174 | 0.539 | 0.373 | 0.171 | 0.065 | 0.731 | 0.563 |
| cross | loo | 0.1% | 5 | V3-SUP | 8909 | 92640 | 81.417 | 86813.583 | 0.508 | 0.991 | 0.088 | 0.161 | 0.0009 | 0.999 | 0.543 | 0.203 | 0.539 | 0.486 | 0.208 | 0.084 | 0.787 | 0.576 |
| cross | loo | 0.1% | 5 | V3-SUP-DENSE | 7680 | 93869 | 74.667 | 86820.333 | 0.501 | 0.990 | 0.076 | 0.141 | 0.0009 | 0.999 | 0.537 | 0.188 | 0.539 | 0.471 | 0.195 | 0.075 | 0.798 | 0.559 |
| cross | loo | 0.1% | 6 | TREE | 12625 | 88924 | 67.833 | 86827.167 | 0.528 | 0.995 | 0.124 | 0.221 | 0.0008 | 0.999 | 0.562 | 0.246 | 0.539 | 0.617 | 0.159 | 0.116 | 0.783 | 0.577 |
| cross | loo | 0.1% | 6 | V3-MAX | 7515 | 94034 | 90.667 | 86804.333 | 0.501 | 0.988 | 0.074 | 0.138 | 0.001 | 0.999 | 0.536 | 0.185 | 0.539 | 0.417 | 0.048 | 0.058 | 0.710 | 0.562 |
| cross | loo | 0.1% | 6 | V3-MAX-RBF | 7630 | 93919 | 93.083 | 86801.917 | 0.501 | 0.988 | 0.075 | 0.140 | 0.001 | 0.999 | 0.537 | 0.186 | 0.539 | 0.415 | 0.049 | 0.059 | 0.718 | 0.562 |
| cross | loo | 0.1% | 6 | V3-SUP | 11060 | 90489 | 77.667 | 86817.333 | 0.519 | 0.993 | 0.109 | 0.196 | 0.0009 | 0.999 | 0.554 | 0.228 | 0.539 | 0.552 | 0.141 | 0.094 | 0.757 | 0.568 |
| cross | loo | 0.1% | 6 | V3-SUP-DENSE | 12665 | 88884 | 71.500 | 86823.500 | 0.528 | 0.994 | 0.125 | 0.222 | 0.0008 | 0.999 | 0.562 | 0.246 | 0.539 | 0.605 | 0.155 | 0.111 | 0.788 | 0.577 |
| cross | loo | 0.1% | 7 | TREE | 9975 | 91574 | 69.333 | 86825.667 | 0.514 | 0.993 | 0.098 | 0.179 | 0.0008 | 0.999 | 0.549 | 0.216 | 0.539 | 0.554 | 0.157 | 0.089 | 0.788 | 0.560 |
| cross | loo | 0.1% | 7 | V3-MAX | 8966 | 92583 | 86.667 | 86808.333 | 0.508 | 0.990 | 0.088 | 0.162 | 0.0010 | 0.999 | 0.544 | 0.203 | 0.539 | 0.472 | 0.129 | 0.080 | 0.800 | 0.557 |
| cross | loo | 0.1% | 7 | V3-MAX-RBF | 8993 | 92556 | 93.750 | 86801.250 | 0.508 | 0.990 | 0.089 | 0.163 | 0.001 | 0.999 | 0.544 | 0.204 | 0.539 | 0.453 | 0.129 | 0.081 | 0.795 | 0.557 |
| cross | loo | 0.1% | 7 | V3-SUP | 10032 | 91517 | 81.417 | 86813.583 | 0.514 | 0.992 | 0.099 | 0.180 | 0.0009 | 0.999 | 0.549 | 0.216 | 0.539 | 0.516 | 0.162 | 0.090 | 0.840 | 0.576 |
| cross | loo | 0.1% | 7 | V3-SUP-DENSE | 9953 | 91596 | 73.583 | 86821.417 | 0.514 | 0.993 | 0.098 | 0.178 | 0.0008 | 0.999 | 0.549 | 0.216 | 0.539 | 0.539 | 0.157 | 0.089 | 0.868 | 0.562 |
| cross | loo | 0.1% | 8 | TREE | 7631 | 93918 | 64.667 | 86830.333 | 0.501 | 0.992 | 0.075 | 0.140 | 0.0007 | 0.999 | 0.537 | 0.187 | 0.539 | 0.505 | 0.099 | 0.080 | 0.772 | 0.580 |
| cross | loo | 0.1% | 8 | V3-MAX | 9461 | 92088 | 91.833 | 86803.167 | 0.511 | 0.990 | 0.093 | 0.170 | 0.001 | 0.999 | 0.546 | 0.209 | 0.539 | 0.471 | 0.087 | 0.079 | 0.695 | 0.566 |
| cross | loo | 0.1% | 8 | V3-MAX-RBF | 9507 | 92042 | 93.917 | 86801.083 | 0.511 | 0.990 | 0.094 | 0.171 | 0.001 | 0.999 | 0.546 | 0.210 | 0.539 | 0.467 | 0.087 | 0.079 | 0.700 | 0.567 |
| cross | loo | 0.1% | 8 | V3-SUP | 10952 | 90597 | 80.333 | 86814.667 | 0.519 | 0.993 | 0.108 | 0.195 | 0.0009 | 0.999 | 0.553 | 0.227 | 0.539 | 0.541 | 0.106 | 0.089 | 0.752 | 0.578 |
| cross | loo | 0.1% | 8 | V3-SUP-DENSE | 7577 | 93972 | 72.667 | 86822.333 | 0.501 | 0.991 | 0.075 | 0.139 | 0.0008 | 0.999 | 0.537 | 0.186 | 0.539 | 0.474 | 0.082 | 0.079 | 0.721 | 0.573 |
| cross | loo | 0.1% | 9 | TREE | 10261 | 91288 | 65.833 | 86829.167 | 0.515 | 0.994 | 0.101 | 0.183 | 0.0008 | 0.999 | 0.550 | 0.220 | 0.539 | 0.574 | 0.130 | 0.090 | 0.780 | 0.567 |
| cross | loo | 0.1% | 9 | V3-MAX | 8072 | 93477 | 88.250 | 86806.750 | 0.503 | 0.989 | 0.079 | 0.147 | 0.001 | 0.999 | 0.539 | 0.192 | 0.539 | 0.442 | 0.104 | 0.077 | 0.775 | 0.564 |
| cross | loo | 0.1% | 9 | V3-MAX-RBF | 8063 | 93486 | 93.500 | 86801.500 | 0.503 | 0.989 | 0.079 | 0.147 | 0.001 | 0.999 | 0.539 | 0.192 | 0.539 | 0.427 | 0.104 | 0.077 | 0.737 | 0.564 |
| cross | loo | 0.1% | 9 | V3-SUP | 9855 | 91694 | 81.167 | 86813.833 | 0.513 | 0.992 | 0.097 | 0.177 | 0.0009 | 0.999 | 0.548 | 0.214 | 0.539 | 0.512 | 0.137 | 0.087 | 0.792 | 0.580 |
| cross | loo | 0.1% | 9 | V3-SUP-DENSE | 9719 | 91830 | 70.833 | 86824.167 | 0.512 | 0.993 | 0.096 | 0.175 | 0.0008 | 0.999 | 0.547 | 0.213 | 0.539 | 0.543 | 0.107 | 0.086 | 0.777 | 0.561 |
| cross | loo | 1% | 0 | TREE | 18616 | 82933 | 698.000 | 86197.000 | 0.556 | 0.964 | 0.183 | 0.308 | 0.008 | 0.992 | 0.588 | 0.288 | 0.539 | 0.187 | 0.180 | 0.197 | 0.842 | 0.580 |
| cross | loo | 1% | 0 | V3-MAX | 18765 | 82784 | 826.833 | 86068.167 | 0.556 | 0.958 | 0.185 | 0.310 | 0.010 | 0.990 | 0.588 | 0.286 | 0.539 | 0.164 | 0.198 | 0.176 | 0.734 | 0.577 |
| cross | loo | 1% | 0 | V3-MAX-RBF | 18871 | 82678 | 782.167 | 86112.833 | 0.557 | 0.960 | 0.186 | 0.311 | 0.009 | 0.991 | 0.588 | 0.288 | 0.539 | 0.173 | 0.223 | 0.177 | 0.731 | 0.577 |
| cross | loo | 1% | 0 | V3-SUP | 18821 | 82728 | 862.917 | 86032.083 | 0.556 | 0.956 | 0.185 | 0.310 | 0.010 | 0.990 | 0.588 | 0.286 | 0.539 | 0.159 | 0.181 | 0.153 | 0.773 | 0.583 |
| cross | loo | 1% | 0 | V3-SUP-DENSE | 18610 | 82939 | 863.667 | 86031.333 | 0.555 | 0.956 | 0.183 | 0.308 | 0.010 | 0.990 | 0.587 | 0.284 | 0.539 | 0.157 | 0.127 | 0.152 | 0.803 | 0.580 |
| cross | loo | 1% | 1 | TREE | 17764 | 83785 | 664.167 | 86230.833 | 0.552 | 0.964 | 0.175 | 0.296 | 0.008 | 0.992 | 0.584 | 0.281 | 0.539 | 0.188 | 0.285 | 0.142 | 0.660 | 0.569 |
| cross | loo | 1% | 1 | V3-MAX | 20906 | 80643 | 825.833 | 86069.167 | 0.568 | 0.962 | 0.206 | 0.339 | 0.010 | 0.990 | 0.598 | 0.306 | 0.539 | 0.180 | 0.312 | 0.174 | 0.690 | 0.579 |
| cross | loo | 1% | 1 | V3-MAX-RBF | 21010 | 80539 | 789.833 | 86105.167 | 0.568 | 0.964 | 0.207 | 0.341 | 0.009 | 0.991 | 0.599 | 0.308 | 0.539 | 0.187 | 0.318 | 0.181 | 0.655 | 0.580 |
| cross | loo | 1% | 1 | V3-SUP | 21023 | 80526 | 884.417 | 86010.583 | 0.568 | 0.960 | 0.207 | 0.341 | 0.010 | 0.990 | 0.598 | 0.306 | 0.539 | 0.170 | 0.303 | 0.164 | 0.716 | 0.589 |
| cross | loo | 1% | 1 | V3-SUP-DENSE | 17789 | 83760 | 829.250 | 86065.750 | 0.551 | 0.955 | 0.175 | 0.296 | 0.010 | 0.990 | 0.583 | 0.277 | 0.539 | 0.156 | 0.286 | 0.143 | 0.735 | 0.569 |
| cross | loo | 1% | 2 | TREE | 18405 | 83144 | 717.667 | 86177.333 | 0.555 | 0.962 | 0.181 | 0.305 | 0.008 | 0.992 | 0.586 | 0.286 | 0.539 | 0.181 | 0.324 | 0.189 | 0.782 | 0.570 |
| cross | loo | 1% | 2 | V3-MAX | 13411 | 88138 | 833.250 | 86061.750 | 0.528 | 0.942 | 0.132 | 0.232 | 0.010 | 0.990 | 0.561 | 0.231 | 0.539 | 0.122 | 0.288 | 0.146 | 0.722 | 0.557 |
| cross | loo | 1% | 2 | V3-MAX-RBF | 13407 | 88142 | 814.250 | 86080.750 | 0.528 | 0.943 | 0.132 | 0.232 | 0.009 | 0.991 | 0.561 | 0.231 | 0.539 | 0.125 | 0.288 | 0.145 | 0.725 | 0.557 |
| cross | loo | 1% | 2 | V3-SUP | 16141 | 85408 | 861.417 | 86033.583 | 0.542 | 0.949 | 0.159 | 0.272 | 0.010 | 0.990 | 0.575 | 0.259 | 0.539 | 0.139 | 0.305 | 0.166 | 0.778 | 0.562 |
| cross | loo | 1% | 2 | V3-SUP-DENSE | 17935 | 83614 | 844.333 | 86050.667 | 0.552 | 0.955 | 0.177 | 0.298 | 0.010 | 0.990 | 0.583 | 0.278 | 0.539 | 0.155 | 0.285 | 0.142 | 0.796 | 0.567 |
| cross | loo | 1% | 3 | TREE | 18985 | 82564 | 605.250 | 86289.750 | 0.559 | 0.969 | 0.187 | 0.313 | 0.007 | 0.993 | 0.590 | 0.294 | 0.539 | 0.213 | 0.304 | 0.165 | 0.866 | 0.563 |
| cross | loo | 1% | 3 | V3-MAX | 13258 | 88291 | 819.417 | 86075.583 | 0.527 | 0.942 | 0.131 | 0.229 | 0.009 | 0.991 | 0.561 | 0.230 | 0.539 | 0.123 | 0.277 | 0.135 | 0.783 | 0.543 |
| cross | loo | 1% | 3 | V3-MAX-RBF | 13307 | 88242 | 803.917 | 86091.083 | 0.527 | 0.943 | 0.131 | 0.230 | 0.009 | 0.991 | 0.561 | 0.231 | 0.539 | 0.125 | 0.277 | 0.135 | 0.776 | 0.545 |
| cross | loo | 1% | 3 | V3-SUP | 18756 | 82793 | 861.667 | 86033.333 | 0.556 | 0.956 | 0.185 | 0.310 | 0.010 | 0.990 | 0.587 | 0.285 | 0.539 | 0.158 | 0.286 | 0.146 | 0.823 | 0.562 |
| cross | loo | 1% | 3 | V3-SUP-DENSE | 16379 | 85170 | 851.917 | 86043.083 | 0.544 | 0.951 | 0.161 | 0.276 | 0.010 | 0.990 | 0.576 | 0.262 | 0.539 | 0.142 | 0.281 | 0.138 | 0.786 | 0.561 |
| cross | loo | 1% | 4 | TREE | 13505 | 88044 | 690.167 | 86204.833 | 0.529 | 0.951 | 0.133 | 0.233 | 0.008 | 0.992 | 0.563 | 0.236 | 0.539 | 0.145 | 0.258 | 0.109 | 0.790 | 0.555 |
| cross | loo | 1% | 4 | V3-MAX | 9909 | 91640 | 807.583 | 86087.417 | 0.509 | 0.925 | 0.098 | 0.177 | 0.009 | 0.991 | 0.544 | 0.190 | 0.539 | 0.096 | 0.232 | 0.088 | 0.669 | 0.533 |
| cross | loo | 1% | 4 | V3-MAX-RBF | 9567 | 91982 | 779.083 | 86115.917 | 0.508 | 0.925 | 0.094 | 0.171 | 0.009 | 0.991 | 0.543 | 0.187 | 0.539 | 0.096 | 0.234 | 0.087 | 0.595 | 0.533 |
| cross | loo | 1% | 4 | V3-SUP | 11970 | 89579 | 859.250 | 86035.750 | 0.520 | 0.933 | 0.118 | 0.209 | 0.010 | 0.990 | 0.554 | 0.214 | 0.539 | 0.107 | 0.233 | 0.080 | 0.663 | 0.542 |
| cross | loo | 1% | 4 | V3-SUP-DENSE | 9040 | 92509 | 850.833 | 86044.167 | 0.505 | 0.914 | 0.089 | 0.162 | 0.010 | 0.990 | 0.540 | 0.177 | 0.539 | 0.084 | 0.222 | 0.066 | 0.736 | 0.535 |
| cross | loo | 1% | 5 | TREE | 15218 | 86331 | 660.833 | 86234.167 | 0.538 | 0.958 | 0.150 | 0.259 | 0.008 | 0.992 | 0.571 | 0.255 | 0.539 | 0.166 | 0.275 | 0.130 | 0.824 | 0.561 |
| cross | loo | 1% | 5 | V3-MAX | 18711 | 82838 | 834.583 | 86060.417 | 0.556 | 0.957 | 0.184 | 0.309 | 0.010 | 0.990 | 0.587 | 0.286 | 0.539 | 0.162 | 0.306 | 0.170 | 0.740 | 0.563 |
| cross | loo | 1% | 5 | V3-MAX-RBF | 18577 | 82972 | 794.667 | 86100.333 | 0.555 | 0.959 | 0.183 | 0.307 | 0.009 | 0.991 | 0.587 | 0.285 | 0.539 | 0.168 | 0.308 | 0.170 | 0.731 | 0.563 |
| cross | loo | 1% | 5 | V3-SUP | 19697 | 81852 | 851.000 | 86044.000 | 0.561 | 0.959 | 0.194 | 0.323 | 0.010 | 0.990 | 0.592 | 0.295 | 0.539 | 0.167 | 0.293 | 0.151 | 0.787 | 0.576 |
| cross | loo | 1% | 5 | V3-SUP-DENSE | 15043 | 86506 | 855.167 | 86039.833 | 0.536 | 0.946 | 0.148 | 0.256 | 0.010 | 0.990 | 0.569 | 0.248 | 0.539 | 0.132 | 0.274 | 0.129 | 0.798 | 0.559 |
| cross | loo | 1% | 6 | TREE | 21282 | 80267 | 637.417 | 86257.583 | 0.571 | 0.971 | 0.210 | 0.345 | 0.007 | 0.993 | 0.601 | 0.314 | 0.539 | 0.224 | 0.236 | 0.170 | 0.783 | 0.577 |
| cross | loo | 1% | 6 | V3-MAX | 15277 | 86272 | 810.750 | 86084.250 | 0.538 | 0.950 | 0.150 | 0.260 | 0.009 | 0.991 | 0.571 | 0.252 | 0.539 | 0.140 | 0.289 | 0.147 | 0.710 | 0.562 |
| cross | loo | 1% | 6 | V3-MAX-RBF | 15376 | 86173 | 786.167 | 86108.833 | 0.539 | 0.951 | 0.151 | 0.261 | 0.009 | 0.991 | 0.571 | 0.253 | 0.539 | 0.145 | 0.298 | 0.157 | 0.718 | 0.562 |
| cross | loo | 1% | 6 | V3-SUP | 16308 | 85241 | 851.333 | 86043.667 | 0.543 | 0.950 | 0.161 | 0.275 | 0.010 | 0.990 | 0.575 | 0.261 | 0.539 | 0.142 | 0.282 | 0.138 | 0.757 | 0.568 |
| cross | loo | 1% | 6 | V3-SUP-DENSE | 21158 | 80391 | 841.750 | 86053.250 | 0.569 | 0.962 | 0.208 | 0.343 | 0.010 | 0.990 | 0.599 | 0.308 | 0.539 | 0.178 | 0.215 | 0.161 | 0.788 | 0.577 |
| cross | loo | 1% | 7 | TREE | 14678 | 86871 | 632.000 | 86263.000 | 0.536 | 0.959 | 0.145 | 0.251 | 0.007 | 0.993 | 0.569 | 0.250 | 0.539 | 0.167 | 0.278 | 0.134 | 0.788 | 0.560 |
| cross | loo | 1% | 7 | V3-MAX | 16521 | 85028 | 796.000 | 86099.000 | 0.545 | 0.954 | 0.163 | 0.278 | 0.009 | 0.991 | 0.577 | 0.265 | 0.539 | 0.152 | 0.287 | 0.145 | 0.800 | 0.557 |
| cross | loo | 1% | 7 | V3-MAX-RBF | 16304 | 85245 | 776.750 | 86118.250 | 0.544 | 0.955 | 0.161 | 0.275 | 0.009 | 0.991 | 0.576 | 0.263 | 0.539 | 0.154 | 0.281 | 0.137 | 0.795 | 0.557 |
| cross | loo | 1% | 7 | V3-SUP | 22044 | 79505 | 857.833 | 86037.167 | 0.574 | 0.963 | 0.217 | 0.354 | 0.010 | 0.990 | 0.604 | 0.316 | 0.539 | 0.182 | 0.308 | 0.169 | 0.840 | 0.576 |
| cross | loo | 1% | 7 | V3-SUP-DENSE | 15920 | 85629 | 842.167 | 86052.833 | 0.541 | 0.950 | 0.157 | 0.269 | 0.010 | 0.990 | 0.574 | 0.258 | 0.539 | 0.140 | 0.290 | 0.148 | 0.868 | 0.562 |
| cross | loo | 1% | 8 | TREE | 21532 | 80017 | 645.667 | 86249.333 | 0.572 | 0.971 | 0.212 | 0.348 | 0.007 | 0.993 | 0.602 | 0.317 | 0.539 | 0.224 | 0.308 | 0.169 | 0.772 | 0.580 |
| cross | loo | 1% | 8 | V3-MAX | 18234 | 83315 | 833.417 | 86061.583 | 0.553 | 0.956 | 0.180 | 0.302 | 0.010 | 0.990 | 0.585 | 0.281 | 0.539 | 0.159 | 0.234 | 0.171 | 0.695 | 0.566 |
| cross | loo | 1% | 8 | V3-MAX-RBF | 18202 | 83347 | 802.417 | 86092.583 | 0.553 | 0.958 | 0.179 | 0.302 | 0.009 | 0.991 | 0.585 | 0.281 | 0.539 | 0.164 | 0.269 | 0.171 | 0.700 | 0.567 |
| cross | loo | 1% | 8 | V3-SUP | 20000 | 81549 | 885.500 | 86009.500 | 0.563 | 0.958 | 0.197 | 0.327 | 0.010 | 0.990 | 0.593 | 0.297 | 0.539 | 0.163 | 0.230 | 0.159 | 0.752 | 0.578 |
| cross | loo | 1% | 8 | V3-SUP-DENSE | 19182 | 82367 | 851.750 | 86043.250 | 0.558 | 0.957 | 0.189 | 0.316 | 0.010 | 0.990 | 0.590 | 0.290 | 0.539 | 0.163 | 0.284 | 0.144 | 0.721 | 0.573 |
| cross | loo | 1% | 9 | TREE | 17098 | 84451 | 699.583 | 86195.417 | 0.548 | 0.961 | 0.168 | 0.287 | 0.008 | 0.992 | 0.580 | 0.273 | 0.539 | 0.174 | 0.295 | 0.154 | 0.780 | 0.567 |
| cross | loo | 1% | 9 | V3-MAX | 16873 | 84676 | 828.167 | 86066.833 | 0.546 | 0.953 | 0.166 | 0.283 | 0.010 | 0.990 | 0.578 | 0.268 | 0.539 | 0.150 | 0.299 | 0.162 | 0.775 | 0.564 |
| cross | loo | 1% | 9 | V3-MAX-RBF | 16918 | 84631 | 794.500 | 86100.500 | 0.547 | 0.955 | 0.167 | 0.284 | 0.009 | 0.991 | 0.579 | 0.269 | 0.539 | 0.155 | 0.299 | 0.162 | 0.737 | 0.564 |
| cross | loo | 1% | 9 | V3-SUP | 21782 | 79767 | 861.917 | 86033.083 | 0.572 | 0.962 | 0.214 | 0.351 | 0.010 | 0.990 | 0.602 | 0.314 | 0.539 | 0.179 | 0.309 | 0.171 | 0.792 | 0.580 |
| cross | loo | 1% | 9 | V3-SUP-DENSE | 15133 | 86416 | 838.583 | 86056.417 | 0.537 | 0.947 | 0.149 | 0.258 | 0.010 | 0.990 | 0.570 | 0.249 | 0.539 | 0.135 | 0.282 | 0.139 | 0.777 | 0.561 |

## R12_v33_within10. Derived metrics from v33_within10/metrics_overall.csv

| protocol | scenario | op | seed | model | TP | FN | FP | TN | accuracy | precision | recall | f1 | fpr | specificity | balanced_acc | mcc | prevalence | precision_at_prev1 | macro_recall | macro_recall_nontiny | auc | pauc1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| within | loo | 0.1% | 0 | TREE | 37436 | 26976 | 379.900 | 381911.100 | 0.939 | 0.990 | 0.581 | 0.732 | 0.0010 | 0.999 | 0.790 | 0.732 | 0.144 | 0.855 | 0.401 | 0.401 | 0.935 | 0.832 |
| within | loo | 0.1% | 0 | V3-MAX | 37925 | 26487 | 379.300 | 381911.700 | 0.940 | 0.990 | 0.589 | 0.738 | 0.0010 | 0.999 | 0.794 | 0.737 | 0.144 | 0.857 | 0.418 | 0.418 | 0.953 | 0.825 |
| within | loo | 0.1% | 0 | V3-MAX-RBF | 37244 | 27168 | 417.600 | 381873.400 | 0.938 | 0.989 | 0.578 | 0.730 | 0.001 | 0.999 | 0.789 | 0.730 | 0.144 | 0.842 | 0.390 | 0.390 | 0.953 | 0.827 |
| within | loo | 0.1% | 0 | V3-SUP | 37492 | 26920 | 375.800 | 381915.200 | 0.939 | 0.990 | 0.582 | 0.733 | 0.0010 | 0.999 | 0.791 | 0.733 | 0.144 | 0.857 | 0.402 | 0.402 | 0.954 | 0.841 |
| within | loo | 0.1% | 0 | V3-SUP-DENSE | 37420 | 26992 | 383.300 | 381907.700 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.854 | 0.397 | 0.397 | 0.949 | 0.816 |
| within | loo | 0.1% | 1 | TREE | 37432 | 26980 | 402.200 | 381888.800 | 0.939 | 0.989 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.848 | 0.406 | 0.406 | 0.975 | 0.839 |
| within | loo | 0.1% | 1 | V3-MAX | 37374 | 27038 | 404.600 | 381886.400 | 0.939 | 0.989 | 0.580 | 0.731 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.847 | 0.398 | 0.398 | 0.931 | 0.840 |
| within | loo | 0.1% | 1 | V3-MAX-RBF | 37362 | 27050 | 387.600 | 381903.400 | 0.939 | 0.990 | 0.580 | 0.731 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.852 | 0.397 | 0.397 | 0.944 | 0.839 |
| within | loo | 0.1% | 1 | V3-SUP | 37725 | 26687 | 389.300 | 381901.700 | 0.939 | 0.990 | 0.586 | 0.736 | 0.001 | 0.999 | 0.792 | 0.735 | 0.144 | 0.853 | 0.417 | 0.417 | 0.930 | 0.849 |
| within | loo | 0.1% | 1 | V3-SUP-DENSE | 37442 | 26970 | 397.500 | 381893.500 | 0.939 | 0.989 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.850 | 0.408 | 0.408 | 0.932 | 0.816 |
| within | loo | 0.1% | 2 | TREE | 37426 | 26986 | 385.000 | 381906.000 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.854 | 0.379 | 0.379 | 0.929 | 0.854 |
| within | loo | 0.1% | 2 | V3-MAX | 37029 | 27383 | 406.500 | 381884.500 | 0.938 | 0.989 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.727 | 0.144 | 0.845 | 0.365 | 0.365 | 0.979 | 0.857 |
| within | loo | 0.1% | 2 | V3-MAX-RBF | 37029 | 27383 | 399.500 | 381891.500 | 0.938 | 0.989 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.728 | 0.144 | 0.847 | 0.365 | 0.365 | 0.978 | 0.849 |
| within | loo | 0.1% | 2 | V3-SUP | 37388 | 27024 | 393.900 | 381897.100 | 0.939 | 0.990 | 0.580 | 0.732 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.851 | 0.380 | 0.380 | 0.978 | 0.857 |
| within | loo | 0.1% | 2 | V3-SUP-DENSE | 37349 | 27063 | 387.500 | 381903.500 | 0.939 | 0.990 | 0.580 | 0.731 | 0.001 | 0.999 | 0.789 | 0.731 | 0.144 | 0.852 | 0.376 | 0.376 | 0.942 | 0.857 |
| within | loo | 0.1% | 3 | TREE | 35681 | 28731 | 391.400 | 381899.600 | 0.935 | 0.989 | 0.554 | 0.710 | 0.001 | 0.999 | 0.776 | 0.713 | 0.144 | 0.845 | 0.320 | 0.320 | 0.938 | 0.843 |
| within | loo | 0.1% | 3 | V3-MAX | 35322 | 29090 | 403.700 | 381887.300 | 0.934 | 0.989 | 0.548 | 0.705 | 0.001 | 0.999 | 0.774 | 0.709 | 0.144 | 0.840 | 0.312 | 0.312 | 0.951 | 0.833 |
| within | loo | 0.1% | 3 | V3-MAX-RBF | 35323 | 29089 | 412.700 | 381878.300 | 0.934 | 0.988 | 0.548 | 0.705 | 0.001 | 0.999 | 0.774 | 0.709 | 0.144 | 0.837 | 0.312 | 0.312 | 0.951 | 0.829 |
| within | loo | 0.1% | 3 | V3-SUP | 35841 | 28571 | 380.000 | 381911.000 | 0.935 | 0.990 | 0.556 | 0.712 | 0.0010 | 0.999 | 0.778 | 0.715 | 0.144 | 0.850 | 0.324 | 0.324 | 0.931 | 0.841 |
| within | loo | 0.1% | 3 | V3-SUP-DENSE | 35819 | 28593 | 388.500 | 381902.500 | 0.935 | 0.989 | 0.556 | 0.712 | 0.001 | 0.999 | 0.778 | 0.714 | 0.144 | 0.847 | 0.323 | 0.323 | 0.927 | 0.844 |
| within | loo | 0.1% | 4 | TREE | 42746 | 21666 | 394.700 | 381896.300 | 0.951 | 0.991 | 0.664 | 0.795 | 0.001 | 0.999 | 0.831 | 0.788 | 0.144 | 0.867 | 0.387 | 0.387 | 0.915 | 0.862 |
| within | loo | 0.1% | 4 | V3-MAX | 36648 | 27764 | 410.700 | 381880.300 | 0.937 | 0.989 | 0.569 | 0.722 | 0.001 | 0.999 | 0.784 | 0.723 | 0.144 | 0.843 | 0.353 | 0.353 | 0.977 | 0.874 |
| within | loo | 0.1% | 4 | V3-MAX-RBF | 36450 | 27962 | 406.700 | 381884.300 | 0.936 | 0.989 | 0.566 | 0.720 | 0.001 | 0.999 | 0.782 | 0.721 | 0.144 | 0.843 | 0.345 | 0.345 | 0.977 | 0.852 |
| within | loo | 0.1% | 4 | V3-SUP | 40098 | 24314 | 391.200 | 381899.800 | 0.945 | 0.990 | 0.623 | 0.764 | 0.001 | 0.999 | 0.811 | 0.760 | 0.144 | 0.860 | 0.380 | 0.380 | 0.975 | 0.883 |
| within | loo | 0.1% | 4 | V3-SUP-DENSE | 37370 | 27042 | 400.400 | 381890.600 | 0.939 | 0.989 | 0.580 | 0.731 | 0.001 | 0.999 | 0.790 | 0.731 | 0.144 | 0.848 | 0.366 | 0.366 | 0.963 | 0.859 |
| within | loo | 0.1% | 5 | TREE | 37016 | 27396 | 389.400 | 381901.600 | 0.938 | 0.990 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.728 | 0.144 | 0.851 | 0.371 | 0.371 | 0.927 | 0.842 |
| within | loo | 0.1% | 5 | V3-MAX | 38808 | 25604 | 377.500 | 381913.500 | 0.942 | 0.990 | 0.602 | 0.749 | 0.0010 | 0.999 | 0.801 | 0.747 | 0.144 | 0.860 | 0.449 | 0.449 | 0.971 | 0.837 |
| within | loo | 0.1% | 5 | V3-MAX-RBF | 38882 | 25530 | 387.600 | 381903.400 | 0.942 | 0.990 | 0.604 | 0.750 | 0.001 | 0.999 | 0.801 | 0.748 | 0.144 | 0.857 | 0.452 | 0.452 | 0.972 | 0.837 |
| within | loo | 0.1% | 5 | V3-SUP | 37816 | 26596 | 353.500 | 381937.500 | 0.940 | 0.991 | 0.587 | 0.737 | 0.0009 | 0.999 | 0.793 | 0.737 | 0.144 | 0.865 | 0.411 | 0.411 | 0.979 | 0.865 |
| within | loo | 0.1% | 5 | V3-SUP-DENSE | 37014 | 27398 | 393.800 | 381897.200 | 0.938 | 0.989 | 0.575 | 0.727 | 0.001 | 0.999 | 0.787 | 0.727 | 0.144 | 0.849 | 0.370 | 0.370 | 0.912 | 0.806 |
| within | loo | 0.1% | 6 | TREE | 37368 | 27044 | 378.400 | 381912.600 | 0.939 | 0.990 | 0.580 | 0.732 | 0.0010 | 0.999 | 0.790 | 0.731 | 0.144 | 0.855 | 0.403 | 0.403 | 0.974 | 0.847 |
| within | loo | 0.1% | 6 | V3-MAX | 37573 | 26839 | 410.800 | 381880.200 | 0.939 | 0.989 | 0.583 | 0.734 | 0.001 | 0.999 | 0.791 | 0.733 | 0.144 | 0.846 | 0.406 | 0.406 | 0.964 | 0.842 |
| within | loo | 0.1% | 6 | V3-MAX-RBF | 38288 | 26124 | 423.100 | 381867.900 | 0.941 | 0.989 | 0.594 | 0.743 | 0.001 | 0.999 | 0.797 | 0.741 | 0.144 | 0.844 | 0.434 | 0.434 | 0.964 | 0.843 |
| within | loo | 0.1% | 6 | V3-SUP | 38333 | 26079 | 370.800 | 381920.200 | 0.941 | 0.990 | 0.595 | 0.743 | 0.0010 | 0.999 | 0.797 | 0.742 | 0.144 | 0.861 | 0.435 | 0.435 | 0.969 | 0.854 |
| within | loo | 0.1% | 6 | V3-SUP-DENSE | 37404 | 27008 | 384.400 | 381906.600 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.854 | 0.403 | 0.403 | 0.946 | 0.849 |
| within | loo | 0.1% | 7 | TREE | 37410 | 27002 | 389.000 | 381902.000 | 0.939 | 0.990 | 0.581 | 0.732 | 0.001 | 0.999 | 0.790 | 0.732 | 0.144 | 0.852 | 0.377 | 0.377 | 0.934 | 0.846 |
| within | loo | 0.1% | 7 | V3-MAX | 37127 | 27285 | 424.800 | 381866.200 | 0.938 | 0.989 | 0.576 | 0.728 | 0.001 | 0.999 | 0.788 | 0.728 | 0.144 | 0.840 | 0.359 | 0.359 | 0.982 | 0.881 |
| within | loo | 0.1% | 7 | V3-MAX-RBF | 37172 | 27240 | 429.900 | 381861.100 | 0.938 | 0.989 | 0.577 | 0.729 | 0.001 | 0.999 | 0.788 | 0.729 | 0.144 | 0.838 | 0.360 | 0.360 | 0.982 | 0.864 |
| within | loo | 0.1% | 7 | V3-SUP | 40623 | 23789 | 370.800 | 381920.200 | 0.946 | 0.991 | 0.631 | 0.771 | 0.0010 | 0.999 | 0.815 | 0.766 | 0.144 | 0.868 | 0.409 | 0.409 | 0.986 | 0.861 |
| within | loo | 0.1% | 7 | V3-SUP-DENSE | 38033 | 26379 | 388.700 | 381902.300 | 0.940 | 0.990 | 0.590 | 0.740 | 0.001 | 0.999 | 0.795 | 0.739 | 0.144 | 0.854 | 0.399 | 0.399 | 0.913 | 0.835 |
| within | loo | 0.1% | 8 | TREE | 45790 | 18622 | 394.000 | 381897.000 | 0.957 | 0.991 | 0.711 | 0.828 | 0.001 | 0.999 | 0.855 | 0.819 | 0.144 | 0.874 | 0.404 | 0.404 | 0.907 | 0.867 |
| within | loo | 0.1% | 8 | V3-MAX | 46178 | 18234 | 395.300 | 381895.700 | 0.958 | 0.992 | 0.717 | 0.832 | 0.001 | 0.999 | 0.858 | 0.823 | 0.144 | 0.875 | 0.399 | 0.399 | 0.967 | 0.895 |
| within | loo | 0.1% | 8 | V3-MAX-RBF | 46154 | 18258 | 379.000 | 381912.000 | 0.958 | 0.992 | 0.717 | 0.832 | 0.0010 | 0.999 | 0.858 | 0.823 | 0.144 | 0.880 | 0.398 | 0.398 | 0.970 | 0.878 |
| within | loo | 0.1% | 8 | V3-SUP | 46608 | 17804 | 362.500 | 381928.500 | 0.959 | 0.992 | 0.724 | 0.837 | 0.0009 | 0.999 | 0.861 | 0.828 | 0.144 | 0.885 | 0.407 | 0.407 | 0.969 | 0.869 |
| within | loo | 0.1% | 8 | V3-SUP-DENSE | 45632 | 18780 | 386.300 | 381904.700 | 0.957 | 0.992 | 0.708 | 0.826 | 0.001 | 0.999 | 0.854 | 0.818 | 0.144 | 0.876 | 0.393 | 0.393 | 0.939 | 0.862 |
| within | loo | 0.1% | 9 | TREE | 20274 | 44138 | 383.300 | 381907.700 | 0.900 | 0.981 | 0.315 | 0.477 | 0.001 | 0.999 | 0.657 | 0.525 | 0.144 | 0.760 | 0.306 | 0.306 | 0.901 | 0.809 |
| within | loo | 0.1% | 9 | V3-MAX | 20646 | 43766 | 366.500 | 381924.500 | 0.901 | 0.983 | 0.321 | 0.483 | 0.0010 | 0.999 | 0.660 | 0.530 | 0.144 | 0.772 | 0.311 | 0.311 | 0.957 | 0.801 |
| within | loo | 0.1% | 9 | V3-MAX-RBF | 20588 | 43824 | 374.700 | 381916.300 | 0.901 | 0.982 | 0.320 | 0.482 | 0.0010 | 0.999 | 0.659 | 0.529 | 0.144 | 0.767 | 0.310 | 0.310 | 0.957 | 0.803 |
| within | loo | 0.1% | 9 | V3-SUP | 27880 | 36532 | 358.700 | 381932.300 | 0.917 | 0.987 | 0.433 | 0.602 | 0.0009 | 0.999 | 0.716 | 0.623 | 0.144 | 0.823 | 0.386 | 0.386 | 0.966 | 0.842 |
| within | loo | 0.1% | 9 | V3-SUP-DENSE | 20776 | 43636 | 378.200 | 381912.800 | 0.901 | 0.982 | 0.323 | 0.486 | 0.0010 | 0.999 | 0.661 | 0.532 | 0.144 | 0.767 | 0.324 | 0.324 | 0.951 | 0.804 |
| within | loo | 1% | 0 | TREE | 47062 | 17350 | 3810.600 | 378480.400 | 0.953 | 0.925 | 0.731 | 0.816 | 0.010 | 0.990 | 0.860 | 0.797 | 0.144 | 0.425 | 0.485 | 0.485 | 0.935 | 0.832 |
| within | loo | 1% | 0 | V3-MAX | 47782 | 16630 | 4105.300 | 378185.700 | 0.954 | 0.921 | 0.742 | 0.822 | 0.011 | 0.989 | 0.866 | 0.802 | 0.144 | 0.411 | 0.542 | 0.542 | 0.953 | 0.825 |
| within | loo | 1% | 0 | V3-MAX-RBF | 52738 | 11674 | 3976.600 | 378314.400 | 0.965 | 0.930 | 0.819 | 0.871 | 0.010 | 0.990 | 0.904 | 0.853 | 0.144 | 0.443 | 0.560 | 0.560 | 0.953 | 0.827 |
| within | loo | 1% | 0 | V3-SUP | 48364 | 16048 | 3609.800 | 378681.200 | 0.956 | 0.931 | 0.751 | 0.831 | 0.009 | 0.991 | 0.871 | 0.812 | 0.144 | 0.445 | 0.516 | 0.516 | 0.954 | 0.841 |
| within | loo | 1% | 0 | V3-SUP-DENSE | 46307 | 18105 | 3850.700 | 378440.300 | 0.951 | 0.923 | 0.719 | 0.808 | 0.010 | 0.990 | 0.854 | 0.789 | 0.144 | 0.419 | 0.481 | 0.481 | 0.949 | 0.816 |
| within | loo | 1% | 1 | TREE | 47142 | 17270 | 3791.900 | 378499.100 | 0.953 | 0.926 | 0.732 | 0.817 | 0.010 | 0.990 | 0.861 | 0.798 | 0.144 | 0.427 | 0.481 | 0.481 | 0.975 | 0.839 |
| within | loo | 1% | 1 | V3-MAX | 50298 | 14114 | 4142.100 | 378148.900 | 0.959 | 0.924 | 0.781 | 0.846 | 0.011 | 0.989 | 0.885 | 0.827 | 0.144 | 0.421 | 0.536 | 0.536 | 0.931 | 0.840 |
| within | loo | 1% | 1 | V3-MAX-RBF | 48268 | 16144 | 4130.600 | 378160.400 | 0.955 | 0.921 | 0.749 | 0.826 | 0.011 | 0.989 | 0.869 | 0.806 | 0.144 | 0.412 | 0.528 | 0.528 | 0.944 | 0.839 |
| within | loo | 1% | 1 | V3-SUP | 48562 | 15850 | 3647.800 | 378643.200 | 0.956 | 0.930 | 0.754 | 0.833 | 0.010 | 0.990 | 0.872 | 0.814 | 0.144 | 0.444 | 0.486 | 0.486 | 0.930 | 0.849 |
| within | loo | 1% | 1 | V3-SUP-DENSE | 46569 | 17843 | 3749.400 | 378541.600 | 0.952 | 0.925 | 0.723 | 0.812 | 0.010 | 0.990 | 0.857 | 0.792 | 0.144 | 0.427 | 0.477 | 0.477 | 0.932 | 0.816 |
| within | loo | 1% | 2 | TREE | 48213 | 16199 | 3839.900 | 378451.100 | 0.955 | 0.926 | 0.749 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.429 | 0.541 | 0.541 | 0.929 | 0.854 |
| within | loo | 1% | 2 | V3-MAX | 55699 | 8713 | 4141.100 | 378149.900 | 0.971 | 0.931 | 0.865 | 0.897 | 0.011 | 0.989 | 0.927 | 0.881 | 0.144 | 0.446 | 0.598 | 0.598 | 0.979 | 0.857 |
| within | loo | 1% | 2 | V3-MAX-RBF | 49477 | 14935 | 3874.200 | 378416.800 | 0.958 | 0.927 | 0.768 | 0.840 | 0.010 | 0.990 | 0.879 | 0.821 | 0.144 | 0.434 | 0.575 | 0.575 | 0.978 | 0.849 |
| within | loo | 1% | 2 | V3-SUP | 48596 | 15816 | 3784.600 | 378506.400 | 0.956 | 0.928 | 0.754 | 0.832 | 0.010 | 0.990 | 0.872 | 0.813 | 0.144 | 0.435 | 0.542 | 0.542 | 0.978 | 0.857 |
| within | loo | 1% | 2 | V3-SUP-DENSE | 48238 | 16174 | 3828.200 | 378462.800 | 0.955 | 0.926 | 0.749 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.430 | 0.540 | 0.540 | 0.942 | 0.857 |
| within | loo | 1% | 3 | TREE | 48271 | 16141 | 3822.200 | 378468.800 | 0.955 | 0.927 | 0.749 | 0.829 | 0.010 | 0.990 | 0.870 | 0.809 | 0.144 | 0.431 | 0.526 | 0.526 | 0.938 | 0.843 |
| within | loo | 1% | 3 | V3-MAX | 54007 | 10405 | 4085.500 | 378205.500 | 0.968 | 0.930 | 0.838 | 0.882 | 0.011 | 0.989 | 0.914 | 0.865 | 0.144 | 0.442 | 0.526 | 0.526 | 0.951 | 0.833 |
| within | loo | 1% | 3 | V3-MAX-RBF | 51662 | 12750 | 4155.300 | 378135.700 | 0.962 | 0.926 | 0.802 | 0.859 | 0.011 | 0.989 | 0.896 | 0.841 | 0.144 | 0.427 | 0.517 | 0.517 | 0.951 | 0.829 |
| within | loo | 1% | 3 | V3-SUP | 47143 | 17269 | 3760.400 | 378530.600 | 0.953 | 0.926 | 0.732 | 0.818 | 0.010 | 0.990 | 0.861 | 0.798 | 0.144 | 0.429 | 0.479 | 0.479 | 0.931 | 0.841 |
| within | loo | 1% | 3 | V3-SUP-DENSE | 47981 | 16431 | 3758.300 | 378532.700 | 0.955 | 0.927 | 0.745 | 0.826 | 0.010 | 0.990 | 0.868 | 0.807 | 0.144 | 0.434 | 0.509 | 0.509 | 0.927 | 0.844 |
| within | loo | 1% | 4 | TREE | 48803 | 15609 | 3801.200 | 378489.800 | 0.957 | 0.928 | 0.758 | 0.834 | 0.010 | 0.990 | 0.874 | 0.815 | 0.144 | 0.435 | 0.516 | 0.516 | 0.915 | 0.862 |
| within | loo | 1% | 4 | V3-MAX | 57262 | 7150 | 4248.100 | 378042.900 | 0.974 | 0.931 | 0.889 | 0.909 | 0.011 | 0.989 | 0.939 | 0.895 | 0.144 | 0.447 | 0.577 | 0.577 | 0.977 | 0.874 |
| within | loo | 1% | 4 | V3-MAX-RBF | 54951 | 9461 | 4065.400 | 378225.600 | 0.970 | 0.931 | 0.853 | 0.890 | 0.011 | 0.989 | 0.921 | 0.874 | 0.144 | 0.448 | 0.569 | 0.569 | 0.977 | 0.852 |
| within | loo | 1% | 4 | V3-SUP | 54793 | 9619 | 3628.900 | 378662.100 | 0.970 | 0.938 | 0.851 | 0.892 | 0.009 | 0.991 | 0.921 | 0.876 | 0.144 | 0.475 | 0.528 | 0.528 | 0.975 | 0.883 |
| within | loo | 1% | 4 | V3-SUP-DENSE | 48629 | 15783 | 3965.600 | 378325.400 | 0.956 | 0.925 | 0.755 | 0.831 | 0.010 | 0.990 | 0.872 | 0.812 | 0.144 | 0.424 | 0.507 | 0.507 | 0.963 | 0.859 |
| within | loo | 1% | 5 | TREE | 46950 | 17462 | 3811.500 | 378479.500 | 0.952 | 0.925 | 0.729 | 0.815 | 0.010 | 0.990 | 0.859 | 0.796 | 0.144 | 0.425 | 0.515 | 0.515 | 0.927 | 0.842 |
| within | loo | 1% | 5 | V3-MAX | 51206 | 13206 | 4082.600 | 378208.400 | 0.961 | 0.926 | 0.795 | 0.856 | 0.011 | 0.989 | 0.892 | 0.837 | 0.144 | 0.429 | 0.560 | 0.560 | 0.971 | 0.837 |
| within | loo | 1% | 5 | V3-MAX-RBF | 51883 | 12529 | 3963.300 | 378327.700 | 0.963 | 0.929 | 0.805 | 0.863 | 0.010 | 0.990 | 0.898 | 0.845 | 0.144 | 0.440 | 0.563 | 0.563 | 0.972 | 0.837 |
| within | loo | 1% | 5 | V3-SUP | 53406 | 11006 | 3444.800 | 378846.200 | 0.968 | 0.939 | 0.829 | 0.881 | 0.009 | 0.991 | 0.910 | 0.864 | 0.144 | 0.482 | 0.520 | 0.520 | 0.979 | 0.865 |
| within | loo | 1% | 5 | V3-SUP-DENSE | 43342 | 21070 | 3711.800 | 378579.200 | 0.945 | 0.921 | 0.673 | 0.778 | 0.010 | 0.990 | 0.832 | 0.759 | 0.144 | 0.412 | 0.489 | 0.489 | 0.912 | 0.806 |
| within | loo | 1% | 6 | TREE | 48157 | 16255 | 3738.700 | 378552.300 | 0.955 | 0.928 | 0.748 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.436 | 0.540 | 0.540 | 0.974 | 0.847 |
| within | loo | 1% | 6 | V3-MAX | 49244 | 15168 | 3946.100 | 378344.900 | 0.957 | 0.926 | 0.765 | 0.837 | 0.010 | 0.990 | 0.877 | 0.818 | 0.144 | 0.428 | 0.578 | 0.578 | 0.964 | 0.842 |
| within | loo | 1% | 6 | V3-MAX-RBF | 49294 | 15118 | 4027.000 | 378264.000 | 0.957 | 0.924 | 0.765 | 0.837 | 0.011 | 0.989 | 0.877 | 0.818 | 0.144 | 0.423 | 0.578 | 0.578 | 0.964 | 0.843 |
| within | loo | 1% | 6 | V3-SUP | 49999 | 14413 | 3579.900 | 378711.100 | 0.960 | 0.933 | 0.776 | 0.848 | 0.009 | 0.991 | 0.883 | 0.829 | 0.144 | 0.456 | 0.566 | 0.566 | 0.969 | 0.854 |
| within | loo | 1% | 6 | V3-SUP-DENSE | 48150 | 16262 | 3731.600 | 378559.400 | 0.955 | 0.928 | 0.748 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.436 | 0.540 | 0.540 | 0.946 | 0.849 |
| within | loo | 1% | 7 | TREE | 48421 | 15991 | 3759.300 | 378531.700 | 0.956 | 0.928 | 0.752 | 0.831 | 0.010 | 0.990 | 0.871 | 0.811 | 0.144 | 0.436 | 0.533 | 0.533 | 0.934 | 0.846 |
| within | loo | 1% | 7 | V3-MAX | 55854 | 8558 | 4167.200 | 378123.800 | 0.972 | 0.931 | 0.867 | 0.898 | 0.011 | 0.989 | 0.928 | 0.882 | 0.144 | 0.446 | 0.609 | 0.609 | 0.982 | 0.881 |
| within | loo | 1% | 7 | V3-MAX-RBF | 52880 | 11532 | 3914.700 | 378376.300 | 0.965 | 0.931 | 0.821 | 0.873 | 0.010 | 0.990 | 0.905 | 0.855 | 0.144 | 0.447 | 0.597 | 0.597 | 0.982 | 0.864 |
| within | loo | 1% | 7 | V3-SUP | 48423 | 15989 | 3455.000 | 378836.000 | 0.956 | 0.933 | 0.752 | 0.833 | 0.009 | 0.991 | 0.871 | 0.814 | 0.144 | 0.457 | 0.528 | 0.528 | 0.986 | 0.861 |
| within | loo | 1% | 7 | V3-SUP-DENSE | 46385 | 18027 | 3707.800 | 378583.200 | 0.951 | 0.926 | 0.720 | 0.810 | 0.010 | 0.990 | 0.855 | 0.791 | 0.144 | 0.429 | 0.513 | 0.513 | 0.913 | 0.835 |
| within | loo | 1% | 8 | TREE | 49201 | 15211 | 3816.800 | 378474.200 | 0.957 | 0.928 | 0.764 | 0.838 | 0.010 | 0.990 | 0.877 | 0.819 | 0.144 | 0.436 | 0.563 | 0.563 | 0.907 | 0.867 |
| within | loo | 1% | 8 | V3-MAX | 55438 | 8974 | 4146.500 | 378144.500 | 0.971 | 0.930 | 0.861 | 0.894 | 0.011 | 0.989 | 0.925 | 0.878 | 0.144 | 0.445 | 0.545 | 0.545 | 0.967 | 0.895 |
| within | loo | 1% | 8 | V3-MAX-RBF | 55431 | 8981 | 4141.300 | 378149.700 | 0.971 | 0.930 | 0.861 | 0.894 | 0.011 | 0.989 | 0.925 | 0.878 | 0.144 | 0.445 | 0.544 | 0.544 | 0.970 | 0.878 |
| within | loo | 1% | 8 | V3-SUP | 49072 | 15340 | 3621.300 | 378669.700 | 0.958 | 0.931 | 0.762 | 0.838 | 0.009 | 0.991 | 0.876 | 0.819 | 0.144 | 0.448 | 0.522 | 0.522 | 0.969 | 0.869 |
| within | loo | 1% | 8 | V3-SUP-DENSE | 48214 | 16198 | 3773.400 | 378517.600 | 0.955 | 0.927 | 0.749 | 0.828 | 0.010 | 0.990 | 0.869 | 0.809 | 0.144 | 0.434 | 0.560 | 0.560 | 0.939 | 0.862 |
| within | loo | 1% | 9 | TREE | 49128 | 15284 | 3757.500 | 378533.500 | 0.957 | 0.929 | 0.763 | 0.838 | 0.010 | 0.990 | 0.876 | 0.819 | 0.144 | 0.439 | 0.546 | 0.546 | 0.901 | 0.809 |
| within | loo | 1% | 9 | V3-MAX | 48918 | 15494 | 4016.400 | 378274.600 | 0.956 | 0.924 | 0.759 | 0.834 | 0.011 | 0.989 | 0.874 | 0.814 | 0.144 | 0.422 | 0.576 | 0.576 | 0.957 | 0.801 |
| within | loo | 1% | 9 | V3-MAX-RBF | 48596 | 15816 | 4157.200 | 378133.800 | 0.955 | 0.921 | 0.754 | 0.830 | 0.011 | 0.989 | 0.872 | 0.809 | 0.144 | 0.412 | 0.575 | 0.575 | 0.957 | 0.803 |
| within | loo | 1% | 9 | V3-SUP | 51923 | 12489 | 3534.400 | 378756.600 | 0.964 | 0.936 | 0.806 | 0.866 | 0.009 | 0.991 | 0.898 | 0.849 | 0.144 | 0.468 | 0.556 | 0.556 | 0.966 | 0.842 |
| within | loo | 1% | 9 | V3-SUP-DENSE | 48046 | 16366 | 3739.500 | 378551.500 | 0.955 | 0.928 | 0.746 | 0.827 | 0.010 | 0.990 | 0.868 | 0.808 | 0.144 | 0.435 | 0.541 | 0.541 | 0.951 | 0.804 |
