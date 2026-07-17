# lv-antislop instrukciju slāņa benchmarks (2026-07-16)

## Ko šis mēra — un ko ne

Cross-model A/B: tie paši uzdevumi CITAM modelim (OpenAI Codex CLI,
`model_reasoning_effort=low`) bez skila (A) un ar lv-antislop operatīvajām
prasībām promptā (B). Metrika ir deterministiska: iesaldētais B3 stila
manifests v1.1.0 + SKILL.md aktīvo likumu teksta statistika (teikumu garuma
variācija, teikumu sākumi ar Mēs, kancelejas verbi, tiek blīvums, izsaukuma
zīmes).

Godīgi par cirkularitāti: metrika ir paša skila definētais signālu saraksts —
benchmarks pierāda, ka instrukcijas PĀRNESAS uz citu modeli un signāli kustas,
nevis mēra galīgo teksta kvalitāti (to mēra §7 efektivitātes pilots ar
cilvēku rediģēšanas laiku; protokols: `docs/pilots/` dev repo).

## Uzbūve

- 2 × 10 promptu × 2 armas; prompti un visas izvades saglabātas šajā mapē
  (`outputs/`, `outputs-v2/`, `*.prompt.txt` — pilna atkārtojamība).
- 1. kārta: īsi mārketinga teksti (140–170 vārdu). 2. kārta: formāli
  institucionāli žanri (320–420 vārdu; pašvaldība, ES fonds, banka,
  apdrošināšana, valsts iestāde u.c.) — apzināta kancelejas reģistra
  provokācija.
- Palaišana: `python benchmark/run_benchmark.py` (prasa codex CLI;
  `--score` pārvērtē esošos failus bez ģenerēšanas).

## Rezultāti

**1. kārta — nulle abos armos.** Īsos mārketinga tekstos ģenerators B3
manifestu nepārkāpj arī bez skila (0 issue abos; skeneris verificēts ar
zināmi sliktu tekstu). Negatīvs rezultāts, publicēts kā ir.

**2. kārta — formāli žanri (mediānas pa 10 promptiem):**

| Metrika | A (bāzes) | B (skils) |
|---|---|---|
| B3 issue flagi kopā | 1 (`transition.tadejadi`) | **0** |
| B3 diagnostikas kopā | 9 | **4** |
| diagnostikas / 1k tokenu (mediāna) | 3.7 | **0.0** |
| teikumu garuma stdev (mediāna) | 4.65 | **5.42** |
| teikumi, kas sākas ar Mēs (kopā) | 3 | **1** |
| izsaukuma zīmes (kopā) | 1 | **0** |
| tiek / 1k · kancelejas verbi / 1k | 0 · 0 | 0 · 0 |
| tokeni (mediāna) | 265.5 | 280.5 |

## Secinājumi (godīgie)

1. **Instrukciju slānis pārnesas:** visi izmērītie signāli kustas skila
   virzienā arī citam modelim — issue un diagnostiku kritums, lielāka teikumu
   garuma variācija, mazāk Mēs-sākumu un izsaukuma zīmju.
2. **Frontier ģenerators īsos/vidējos tekstos manifestu tikpat kā nepārkāpj.**
   Deterministisko vārtu galvenā pierādītā vērtība tāpēc ir citur: (a) reāli
   darba artefakti — publiskās lapas pilotā vārti atrada 348 issue līmeņa
   flagus pirms tīrīšanas (B1 pareizrakstība + B2 formas + B3 stils kopā);
   (b) morfoloģijas pārkāpumu ķeršana — 2b saskaņas vārti uz 110 native
   validētiem minimālajiem pāriem sasniedz precizitāti 0.986 (Vilsona LB
   0.926): skat. `../spike/`.
3. **Ierobežojumi:** N=10 promptu kārtā, viens ģenerators, viena effort
   konfigurācija, benchmarka autors = metrikas autors, LLM-pret-LLM bez
   cilvēka vērtējuma. Galīgo efektivitātes apgalvojumu dos pre-reģistrētais
   §7 pilots.
