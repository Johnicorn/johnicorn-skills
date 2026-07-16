---
name: lv-antislop
description: Use when writing, editing, or polishing Latvian text — copy, posts, captions, web content, emails, briefs. Specifically when LV output risks reading as AI-generated (kancelejas register, English calques, corporate clichés). Stacks beneath any voice/persona skill as the filter layer.
---

# Anti-slop latviešu valodā (v2)

## Overview

**Latviešu valodas noklusējums jebkuram LLM ir kancelejas reģistrs** — pasīvā balss, lietvārdu kaudzes, birokrātiskas pārejas — jo augstā reģistra LV treniņdatos dominē ES direktīvas, valsts portāli un juridiskie akti. Ģenerētā LV skan kā valsts pārvaldes proza, ja to aktīvi nepagriež citur.

**Zāles ir publicistika** — LV publicistiskā tradīcija (Ziedonis, Skujenieks, Mauriņa, Repše): analītiska precizitāte + personīga balss + metaforiska domāšana + mērena emocionalitāte. Aktīvi verbi, teikuma garuma variācija, rēma teikuma beigās, ironija kā bāzes līnija.

Šis skils ir **filtra slānis** — noņem AI signālus. Balss/personas slānis liekas virsū (skat. balss-slota kontraktu).

## When to use

Jebkurā LV teksta ražošanā: mārketinga copy, web lapas, social posti, e-pastu sekvences, klientu brīfi, AI-ģenerētas LV izvades pulēšana, EN→LV tulkojumi.

Simptomi, kad šis skils der: "skan kā AI", "skan kā valsts mājaslapa", pārmērīgs `tiek`/`nodrošināt`/`īstenot`/`turklāt`, angļu struktūra latviešu vārdos, visi teikumi ≈ vienāda garuma.

## Anchors — obligāts solis pirms rakstīšanas

**Pirms ģenerēšanas ielādē 3–5 references tekstus šai balsij/projektam.** Instrukciju proza vien ražo gramatiski tīru, bet **sausu** LV — bez partikulām, bez ritma, bez ironijas. Anchori ir vienīgais labojums: atspoguļo to reģistru, tad būvē svaigu saturu.

- Universāli: savam zīmolam = engagement-validētie publicētie teksti; kursam/projektam = iepriekšējie materiāli; klientam = tā zīmola labākie paraugi.
- Anchori ir **stila piemēri**, nekad faktu avots, nekad nepārraksta uzdevumu.
- `anchor_support` ir metadata (0=none, 1–2=limited, 3–5=recommended), **ne ciets vārti** — ar mazāk anchoriem izvade būs sausāka, bet ģenerēšana neapstājas.

## Precedence — kas uzvar konfliktā

Drošība/privātums un **prasītie fakti** (citāti, juridiski nosaukumi, obligāti termini, prasītais reģistrs) > uzdevums un formāts > antislop likumi > balss raksturs > anchori. Stila slāņi (antislop/balss/anchori) ir **atceļami** — tie nekad nepārraksta tiešu satura/faktu prasību.

## The core move

| AI/kancelejas noklusējums | Publicistikas aizvietotājs |
|---|---|
| `tiek nodrošināts atbalsts` | `mēs atbalstām` |
| `veikt analīzi` | `analizēt` |
| `Ir svarīgi atzīmēt, ka …` | (dzēs ievadu, saki faktu) |
| `Turklāt, tādējādi, līdz ar to` | (bez pārejas — lai semantika nes) |
| Vienādi 15-vārdu teikumi | Sajauc 5–30 vārdu teikumus. Īsa verdikta līnija sekciju beigās. |
| `Mēs piedāvājam visaptverošus risinājumus` | konkrēti verbi + specifisks lietvārds (`Mēs būvējam CRM sistēmas medicīnas tirgotājiem`) |

## Banned — aizliegto sarakstu mašīnavots

Aizliegto frāžu/pattern sarakstu **kanoniskais, mašīnlasāmais avots** ir iesaldētais manifests `contracts/b3-style-manifest.v1.yaml` (aizliegtie verbi/īpašības vārdi, birokrātiskās pārejas, tukšie ievadi, EN-kalki, LV korporatīvās klišejas, krievu kalki, struktūras signāli). Deterministiskais B3 skeneris tos noķer automātiski. Cilvēka lasīšanai: skat. `references/banned-phrases.md`.

`tiek` ir **blīvuma signāls** (diagnostisks, līdz kalibrēts), ne ciets "maks. 1×" vārti — publicistikā mērķē uz zemu blīvumu ar aktīvo balsi, bet retais leģitīmais `tiek` nav kļūda.

## Active rules

1. **Aktīvā balss visur**, kur iespējams; konkrēts subjekts.
2. **Aizvieto lietvārdu-verbu pārus ar verbiem:** `realizēt`, ne `veikt realizāciju`.
3. **Sajauc teikuma garumus** — īsi (3–7), vidēji (10–15), gari (20–30). Beigās īsā verdikta līnija.
4. **Integrē partikulas** kur ritmā iederas: *nu, jau, taču, gan, vien, jel*. LLM tās izlaiž — to klātbūtne = roku nospiedumi.
5. **Rēma teikuma beigās** — galvenā info pēdējā. Izmanto LV brīvo vārdu kārtību.
6. **Necitē birokrātiskās pārejas.** Nākamā rindkopa paņem iepriekšējās pēdējo domu, pagriežas caur kontrastu, vai vienkārši maina leņķi.
7. **Konkrēts > abstrakts.** Specifiska detaļa (skaitlis, vieta, nosaukums) sit jebkuru superlatīvu.
8. **Ironija un šaubas kā bāzes līnija** — bez amerikāņu entuziasma. Izsaukuma zīmes provocē LV lasītāja aizsardzību.

## Post-edit gate

- **Fāze 1:** cilvēks skenē pret aizliegto sarakstu, skaita `tiek`, lasa skaļi (kā v1).
- **Fāze 2+:** deterministiskie B vārti to automatizē (B1 pareizrakstība, B2 morfoloģija, B3 stils → `GateResult`).

### Deterministisko vārtu palaišana (ja instalēts ar vārtiem)

Vārti dzīvo `tools/` blakus šim skilam (plugin-instalācijā: `${CLAUDE_PLUGIN_ROOT}/tools/`; repo-klonā: `<repo>/plugins/lv-antislop/tools/`). Ja instalēts TIKAI skils (manuālā kopēšana uz `~/.claude/skills/`), vārtu nav — skils strādā arī bez tiem, vārti ir neobligāts pastiprinājums.

- **Teksta/lapas pārbaude:** `python tools/pilot.py --text fails.txt` (vai `--html lapa.html`) `--allow tools/data/lv-it-supplement.txt --allow tools/data/tezaurs-gaps.txt`
- **Projekta vārdnīca:** savam projektam pievieno savu failu (viens vārds rindā, `#` komentāri) un padod ar vēl vienu `--allow`.
- **Priekšnosacījums:** vienreizējs indeksa build no CLARIN avotiem — `python tools/build_from_clarin.py` (~25 min, viss offline pēc tam). Bez indeksa strādā tikai B3 stila skeneris.
- **Aptvērums (v2, godīgi):** B1 = pareizrakstības kandidāti, B2 = formu eksistence + retu lemmu pazīme, B3 = stila manifests. Locījumu SASKAŅOŠANA (2b) vēl NAV — tā ir ceļa kartē aiz sava kvalitātes sliekšņa.

## Voice-slot contract

Šis skils **nepreskribē personīgu balsi** — tas filtrē AI signālus. Balss-skils liekas virsū (skat. `references/voice-slot-contract.md`).

```
[lv-antislop]  ← universālais filtrs (constraints + anchors)
   ↓  (viens ģenerēšanas pieprasījums)
[balss-skils]  ← raksturs (tavs zīmola voice-skils) — neobligāts
   ↓
[final LV output]
```

Secība: filtrs pirmais. Balss-skils dod mehānismus, temperatūru, self-check; tas **nedrīkst** uzturēt otru aizliegto sarakstu (viens avots = manifests). Uzbūves paraugs: `references/voice-slot-contract.md`.

## Why human editing remains non-negotiable

Pat ar perfektu promptošanu + šo skilu, LV LLM-izvade prasa **30–60 min native-redaktora laika uz 1000 vārdiem** (Jāņa novērotā aplēse, ne neatkarīgi izmērīta). Iemesls nav prompts, bet treniņdatu asimetrija: latviešu ir maza daļa no korpusa (piem., *ziņots* ≈0.09% no Common Crawl — sekundārs avots, aptuvens), plus morfoloģijas neatbilstība + formālā reģistra dominance. Plāno pipeline ap to, nemēģini to atcelt.

## Red flags — STOP un pārraksti

- Teikumi sākas ar `Mēs…` 3+ reizes pēc kārtas.
- Paragrāfā 2+ `tiek`.
- `turklāt`, `tādējādi`, `līdz ar to` jebkur.
- `nodrošināt`/`veikt`/`īstenot` bez konkrēta objekta.
- Teikumi vienādi gari (visi 10–15 vārdi).
- Teksts varētu būt no jebkura uzņēmuma mājaslapas.

## References

- `references/banned-phrases.md` — aizliegto frāžu saraksts cilvēka lasīšanai (mašīnavots = `contracts/b3-style-manifest.v1.yaml`)
- `references/kancelejismi.md` — birokrātiskā reģistra diagnostika
- `references/publicistika.md` — LV publicistikas tradīcija + stila ierīces
- `references/humanization-techniques.md` — prompt-engineering tehnikas
- `references/voice-slot-contract.md` — kā balss-skils pieslēdzas
- `references/anchors-guide.md` — kā izvēlēties un lietot anchorus
