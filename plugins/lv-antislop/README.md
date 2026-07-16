# LV Antislop

A Latvian de-slop skill plus a deterministic B1/B2/B3 gate.

## Quick start

Install it from the marketplace:

```text
/plugin marketplace add OWNER-GITHUB/johnicorn-skills
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

## Godīgā robeža

v2 vārti pārbauda pareizrakstības kandidātus, vārdu formu esību un stila manifestu. Locījumu saskaņa (2b) nav iekļauta — tā stāv ceļa kartē aiz saviem kvalitātes vārtiem un neienāks, kamēr tos neizies. Vārdnīcas strādā ar precīzām formām (bez celmošanas): ja vārds ir sarakstā nominatīvā, tā locījumi vēl var uzpeldēt kā diagnostika. LV-IT vārdnīcas ir kurētas ar roku. Projekta vārdnīcai pievieno savu failu ar `--allow` — viens vārds rindā, `#` komentāri.

## Datu stāsts

Būvētājs izmanto CLARIN avotus ar CC BY-SA 4.0 licenci un glabā lejupielādes un indeksus lokāli. Pilna būve aizņem apmēram 25 minūtes, un pēc tās viss strādā offline. GitHub Release faili ir plānoti kā ērtības ceļš — lejupielāde būves vietā. Licences un atribūcijas skaties [DATA-LICENSE.md](DATA-LICENSE.md).

Ja instalē caur marketplace: būvē indeksus ĀRPUS spraudņa mapes, piemēram `python tools/build_from_clarin.py --data-dir ~/lv-antislop-data`, un padod `pilot.py` to pašu ceļu ar `--index`. Spraudņa atjauninājums nomaina tā mapi — ārējais datu ceļš pārdzīvo atjauninājumus, iekšējais ne.

## Testu palaišana

```text
cd tools && python -m pytest tests -q
```

Komplektā ir 220 testi.
