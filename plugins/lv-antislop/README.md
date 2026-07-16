# LV Antislop

A Latvian de-slop skill plus a deterministic B1/B2/B3 gate.

## Quick start

Install it from the marketplace:

```text
/plugin marketplace add Johnicorn/johnicorn-skills
/plugin install lv-antislop@johnicorn-skills
```

Manual fallback: copy `skills/lv-antislop/*` to `~/.claude/skills/lv-antislop/`. This installs the skill only, without the gate.

Build the gate locally:

```text
python tools/build_from_clarin.py
```

Requirements: Python >=3.11, then `pip install pyyaml pytest`.

## Kas tas ir un kāpēc

Ģenerēts teksts bieži iekrīt kancelejas reģistrā: abstrakti lietvārdi aizstāj darbības vārdus, teikumi zaudē ritmu, un vienas frāzes atkārtojas. Skils palīdz pamanīt šos signālus latviešu tekstā, bet vārti pārbauda konkrētus pareizrakstības, formas un stila riskus.

## Ko satur

- Skilu ar publicistiska reģistra norādēm un atsaucēm.
- B1 pareizrakstības kandidātu pārbaudi.
- B2 vārdu formu esības pārbaudi.
- B3 stila manifesta pārbaudi.
- 2b locījumu saskaņas pārbaudi (`pilot.py --agreement`) — neobligāta, ar AiLab lvnlp parseri.

## Godīgā robeža

v2 vārti pārbauda pareizrakstības kandidātus, vārdu formu esību, stila manifestu un — ar `--agreement` — locījumu saskaņu (amod/nsubj). Saskaņas pārbaude savus kvalitātes vārtus izgāja 2026. gada 16. jūlijā uz 110 dzimtās valodas runātāja validētiem minimālajiem pāriem: precizitāte 0.986 (Vilsona apakšējā robeža 0.926), pārklājums 0.818. Robeža, ko zināt: parsers daļu kļūdu kontekstuāli normalizē, tāpēc tā ķer lielāko daļu locījumu kļūdu, ne visas. Šis režīms prasa atsevišķu vidi: `pip install lvnlp` (torch CPU; pirmā palaišana lejupielādē ~0.6 GB modeli), Windows vidē `PYTHONUTF8=1`; ātrums ap 0.3 s uz teikumu. Vārdnīcas strādā ar precīzām formām (bez celmošanas): ja vārds ir sarakstā nominatīvā, tā locījumi vēl var uzpeldēt kā diagnostika. LV-IT vārdnīcas ir kurētas ar roku. Projekta vārdnīcai pievieno savu failu ar `--allow` — viens vārds rindā, `#` komentāri.

## Datu stāsts

Būvētājs izmanto CLARIN avotus ar CC BY-SA 4.0 licenci un glabā lejupielādes un indeksus lokāli. Pilna būve aizņem apmēram 25 minūtes, un pēc tās viss strādā offline. GitHub Release faili ir plānoti kā ērtības ceļš — lejupielāde būves vietā. Licences un atribūcijas skaties [DATA-LICENSE.md](DATA-LICENSE.md).

Ja instalē caur marketplace: būvē indeksus ĀRPUS spraudņa mapes, piemēram `python tools/build_from_clarin.py --data-dir ~/lv-antislop-data`, un padod `pilot.py` to pašu ceļu ar `--index`. Spraudņa atjauninājums nomaina tā mapi — ārējais datu ceļš pārdzīvo atjauninājumus, iekšējais ne.

## Datu kopa: saskaņas minimālie pāri

Saskaņas pārbaudes kvalitātes mērījums balstās uz autora veidotu un dzimtās valodas runātāja validētu datu kopu — 110 minimālajiem pāriem ar iesaldētu integritātes hash: [contracts/2b-minimal-pairs.v1.yaml](contracts/2b-minimal-pairs.v1.yaml), licence CC BY 4.0. Mērījuma protokols, skripti un pilnie rezultāti: [spike/](spike/). Cik zināms, tas ir pirmais publiskais latviešu locījumu saskaņas minimālo pāru komplekts.

## Testu palaišana

```text
cd tools && python -m pytest tests -q
```

Komplektā ir 233 testi. Saskaņas pārbaudes likumu dzinēja testi iet bez lvnlp — smagā vide vajadzīga tikai pašam `--agreement` režīmam.
