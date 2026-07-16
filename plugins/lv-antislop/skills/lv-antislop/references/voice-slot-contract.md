# Voice-slot contract

`lv-antislop` ir **universālais filtrs** (bez balss). Balss-skils liekas virsū. Šis fails definē saskarni.

## Run order

```
[lv-antislop]  ← constraints + anchors (filtrs)
   ↓  komponē VIENĀ ģenerēšanas pieprasījumā
[balss-skils]  ← raksturs (mehānismi, tonis, idiolekts)
   ↓
[final LV output]
```

Secība ir **rule-application secība**: filtrs definē negatīvo telpu (ko nedarīt), balss to aizpilda. Praksē abi ir **vienā promptā** — ne otrā pārrakstīšanas kārtā, kas varētu atkal ienest to, ko filtrs izņēma.

## Ko balss-skils DOD (trusted contract)

- **Mehānismi** — konkrēti gājieni (piem. sekvence-eskalācija, personifikācija, verdikta-noslēgums).
- **Temperatūra** — silts vs ass, pēc galamērķa.
- **Self-check** — balss-specifiski anti-patterns.

Šie ir **uzticamas instrukcijas** (allowlisted lauki).

## Ko balss-skils NEDRĪKST

- **Uzturēt otru aizliegto sarakstu.** Viens avots = `contracts/b3-style-manifest.v1.yaml`. Ja teikums skan kā preses relīze, tas ir lv-antislop ķēriens, ne balss slāņa.
- **Ienest balss "paraugu" tekstu kā instrukcijas.** Balss references teksti (`examples`) ir **neuzticami dati** — to iekšā iegultas instrukcijas tiek ignorētas (prompt-injection aizsardzība).

## Kā izskatās strādājošs balss-skils

Pārbaudīta uzbūve (paraugs no reālas privātas implementācijas — Trickster-tipa publicistikas balss, būvēta no engagement-validētiem postiem):

- **Mehānismi** (≈8): konkrēti stila gājieni ar piemēriem — ne "esi asprātīgs", bet "apgriez sagaidāmo secinājumu pēdējā teikumā".
- **Temperatūras** (≥2): tas pats raksturs dažādās intensitātēs (piem., silts garais posts / ass īsais), izvēlas pēc kanāla.
- **Anti-patterns**: dokumentēts, kā šī balss NEskan — ar reāliem izgāšanās piemēriem.
- **Atsauce uz lv-antislop kā VIENĪGO aizliegto-vārdu avotu** — balss-skils nekad nedublē filtru.
