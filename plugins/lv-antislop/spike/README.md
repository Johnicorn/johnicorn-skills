# 2b spike — saskaņas vārtu pierādījumu pakete

Šī mape ir publiskais pierādījums tam, ka 2b locījumu saskaņas pārbaude
(`pilot.py --agreement`) savus kvalitātes vārtus izgāja, nevis tika ieslēgta uz
labu ticību.

## Datu kopa

`../contracts/2b-minimal-pairs.v1.yaml` — 110 dzimtās valodas runātāja
validēti minimālie pāri (amod 55 / nsubj 55, ieskaitot 10 izstrādātus
paraugus): viens teikums divos variantos, kas atšķiras ar TIEŠI vienu
morfoloģisko pazīmi, plus 22 negatīvās kontroles (bez pārkāpuma) un 10
malformed robustuma ievades. Fails ir iesaldēts — integritātes hash glabājas
`meta.frozen_sha256`, pārbaude: `python spike/freeze_pairs.py verify`.
Licence: CC BY 4.0 (skat. `../DATA-LICENSE.md`).

## Rezultāti (2026-07-16, fp32 lvnlp, CPU)

| Vārti | Slieksnis | Izmērīts |
|---|---|---|
| precision (Vilsona 95% apakšējā robeža) | ≥ 0.90 | 0.986 (LB **0.926**) |
| coverage | ≥ 0.70 | **0.818** (amod 0.761 / nsubj 0.881) |
| abstention | ≤ 0.30 | 0.0 |
| latence cold / warm mediāna | ≤ 1000 / ≤ 500 ms | 500 / 259 ms |
| peak RSS | ≤ 2048 MB | 890 MB |
| malformed crash/timeout | 0 | 0 (10/10 ok) |

Pilnie dati pa pāriem: `spike-results.json`. Galvenā zināmā robeža:
parsers daļu pārkāpumu kontekstuāli normalizē (uzmin saskanīgas pazīmes
sabojātajam vārdam), tāpēc coverage ir 0.82, ne 1.0.

## Atkārtošana

```text
pip install lvnlp psutil pyyaml        # torch CPU; Windows: PYTHONUTF8=1
python spike/run_spike.py              # verificē hash, mēra, raksta JSON
```

Skripti: `run_spike.py` (mērījums), `freeze_pairs.py` (freeze/verify),
`validate_pairs.py` (kolekcijas struktūras pārbaude),
`check_pairs_morph.py` (autorēšanas QA pret Tēzaura formu indeksu; prasa
lokāli uzbūvētu B2 sqlite indeksu — ceļu padod kā pirmo argumentu).
