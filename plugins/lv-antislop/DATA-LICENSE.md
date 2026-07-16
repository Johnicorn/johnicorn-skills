# Data license

- Code and skill text: MIT. See [LICENSE](../../LICENSE).
- The gate consumes two CC BY-SA 4.0 datasets, downloaded or built locally and never kept in this git tree:
  1. Tēzaurs.lv 2026 (Summer Edition), handle `20.500.12574/160`. Attribution: "Tēzaurs.lv 2026 (Summer Edition), Institute of Mathematics and Computer Science, University of Latvia (AILab). Licensed CC BY-SA 4.0."
  2. Latvian Word Frequency Dataset (25K lemmas), handle `20.500.12574/148`. Attribution: "Mikus Grasmanis, Baiba Valkovska, Kristīne Levāne-Petrova (2025-12-19): Latvian Word Frequency Dataset (25K lemmas). AiLab IMCS UL. http://hdl.handle.net/20.500.12574/148. Licensed CC BY-SA 4.0."
- Derived index files (`forms.txt`, `wordforms.tsv`, `wordforms.sqlite`, `freq.tsv`) are CC BY-SA 4.0 derivatives of these datasets. If you redistribute them, for example as Release assets, keep the same license and attribution. A local build for your own use carries no redistribution obligation.
- `tools/data/*.txt` allowlists are author-written and MIT.
- `contracts/2b-minimal-pairs.v1.yaml` — the Latvian agreement minimal-pairs dataset (110 native-validated pairs + 10 malformed robustness inputs) — is an original work by Jānis Patmalnieks (sentence drafting assisted by Claude; every pair reviewed and validated by the author, a native speaker). Licensed **CC BY 4.0**. Attribution: "Latvian agreement minimal pairs (lv-antislop 2b), Jānis Patmalnieks, 2026. https://github.com/Johnicorn/johnicorn-skills". The frozen file's integrity hash lives in its `meta.frozen_sha256`; verify with `spike/freeze_pairs.py verify`.
