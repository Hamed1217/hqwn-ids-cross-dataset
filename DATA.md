# Datasets

The datasets are not redistributed. Download them from the Canadian Institute for Cybersecurity and place them as shown. The scripts take the locations as command-line arguments, so other folders also work.

| Dataset | Source | Expected location | Files |
|---|---|---|---|
| CIC-IDS2017 | https://www.unb.ca/cic/datasets/ids-2017.html | `data/CIC-IDS2017/` | The eight labelled flow CSV files of `GeneratedLabelledFlows/TrafficLabelling` (listed below) |
| CSE-CIC-IDS2018 | https://www.unb.ca/cic/datasets/ids-2018.html | `data/CSE-CIC-IDS2018/` | The ten daily CSV files (listed below) |
| CIC-UNSW-NB15 | https://www.unb.ca/cic/datasets/cic-unsw-nb15.html | `data/CIC-UNSW-NB15/` | `Data.csv`, `CICFlowMeter_out.csv` |

## SHA256 of the raw files used

These hashes were recorded by `count_manifest.py` (`results/manifest/manifest_files.csv`). Compute your own in PowerShell with `Get-FileHash <file> -Algorithm SHA256`.

### CIC-IDS2017

| File | Bytes | SHA256 |
|---|---|---|
| `Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv` | 96,101,069 | `1f779b4f0d78f9225554c4de53b5a2c07912b60dcd136ee4c5c1d0d2496b7cc4` |
| `Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv` | 101,874,777 | `7e2ddaa80a5849ba629463296b6128436c161b4a32e8034bb5beae06b0c45e08` |
| `Friday-WorkingHours-Morning.pcap_ISCX.csv` | 75,386,737 | `c061cd98f39d8054aeaed6244a5129a20b3985983d0d022b860ae8aa07fe8d21` |
| `Monday-WorkingHours.pcap_ISCX.csv` | 268,649,908 | `96f26aea87d513073769b48ce204c2921791149e1c6225f7db65a3fed7973820` |
| `Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv` | 108,723,183 | `d74238e054023c8bd4d8056650463cadb25c100fb0e26ebd4272c07b5c022c4b` |
| `Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv` | 92,030,223 | `e3deaff483d18b53b100a441dff9b8919416df8876b4edcc0f0d1e4bf48397d0` |
| `Tuesday-WorkingHours.pcap_ISCX.csv` | 174,696,560 | `ae9c88e10c41a8eb1ff454ae98bc513454925097d0b0b57180f94e79de445815` |
| `Wednesday-workingHours.pcap_ISCX.csv` | 285,642,925 | `ed538e85b84181e8897dedb3d37d365982f44b27eccd67c477581a8b65f3d170` |

### CSE-CIC-IDS2018

| File | Bytes | SHA256 |
|---|---|---|
| `02-14-2018.csv` | 358,223,333 | `acff8bc61376ee031d80878ee6099e0b1a87a1bd711d8068298421418c9f8147` |
| `02-15-2018.csv` | 375,945,899 | `fa2947a8256d81ee9103ae16139d62d0e17aa23e696ee80d9e76fb51c01c9c4b` |
| `02-16-2018.csv` | 333,723,605 | `1a4919faa0c49c7af97230b0c2d076eba23ee6dd81103a3801d51ac316355d8b` |
| `02-20-2018.csv` | 4,054,925,350 | `7287a4d7740a1dddbf330ceb2beb6a4889d33ba63674558a68b5eb50d16711df` |
| `02-21-2018.csv` | 328,893,673 | `a5f4a1c2689e0aa6566c03a58466de9c407c0be0cbd3cc69306544026611be04` |
| `02-22-2018.csv` | 382,636,202 | `da33c927018274f9d49b145baa00e4ce0526c25b3b890b34c489e247b5e24544` |
| `02-23-2018.csv` | 382,840,456 | `d0a7f5059d9823b6e9b392b759e306481a3502d190dea7a1b5502ae079ea069b` |
| `02-28-2018.csv` | 209,249,758 | `f15e2a12304446058a0186c8ad67de2bd15735a9ba5c70c9a1f4c4242ab06771` |
| `03-01-2018.csv` | 107,842,858 | `b0534c5d7d8b41e03df71c6966c995d116a8ed28e61f377c8b14cdf5d28f4edf` |
| `03-02-2018.csv` | 352,368,373 | `d96f38e7496aba83475031e6fb8c6fdf1abf6aa1b71325a917798f3c7de93de1` |

### CIC-UNSW-NB15

The hashes of the two raw files were not recorded. The analysis plan (`analysis_plan/prereg_unsw.txt`) records the hashes of the sampled caches built from them:

| File | SHA256 |
|---|---|
| `unsw_sample_v1.npz` (raw features) | `c7eece1631492500f45ca1433b8fa7b7d0a065a3711fcc05690009686683db38` |
| `unsw_sample_v1h.npz` (harmonized features) | `86ff9d27875b4d7f16f009354ddde7b9a14572ff9c2735cb98532f0769d7c6da` |

Please cite the original dataset papers (references in the article).
