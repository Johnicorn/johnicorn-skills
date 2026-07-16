# Banned phrases & patterns — Latvian anti-slop blacklist

Konsolidēts no `kancelejismi.md`, `ai-slop.md`, `ai-humanization-prompting.md` (Obsidian wiki). Lieto kā skenēšanas sarakstu: katra atrasta frāze = pārrakstīt.

---

## 1. AI-overused verbi (izvairies kā no generiska aizstājēja)

- nodrošināt
- veicināt
- piedāvāt
- sniegt
- ļaut
- īstenot
- realizēt (kā lietvārdu pārī: `veikt realizāciju`)
- optimizēt
- pielāgot (kā vispārējs aizstājējs)
- uzlabot
- sasniegt

**Likme:** ja tu vari aizstāt ar konkrētu darbības vārdu (`būvēt`, `rakstīt`, `pārdot`, `sūtīt`, `mainīt`, `samazināt`), to dari.

---

## 2. AI-overused īpašības vārdi

- būtisks
- visaptverošs
- inovatīvs
- efektīvs
- kvalitatīvs
- uzticams
- profesionāls
- daudzpusīgs

**Likme:** īpašības vārds bez konkrēta seguma = klišeja. Pierādi ar skaitli vai piemēru, vai izmet.

---

## 3. Birokrātiskās pārejas (kancelejismi)

- turklāt
- tādējādi
- līdz ar to
- kā arī
- tai skaitā
- neatkarīgi no tā vai
- savukārt (kā formāla pāreja, ne kā kontrasts)

**Likme:** publicistika pārejas notiek **semantiski** — nākamā rindkopa paņem iepriekšējās pēdējo domu, vai pagriežas caur kontrastu, vai vienkārši maina leņķi. Nav vajadzīgs vārds-savienotājs.

---

## 4. Tukšie ievadi (filler intros)

- Ir svarīgi atzīmēt, ka …
- Ir vērts piebilst, ka …
- Kopumā var secināt, ka …
- Noslēgumā jāatzīmē, ka …
- Jāuzsver, ka …

**Likme:** tieši pasaki to, ko gribi pateikt. Bez ievada.

---

## 5. Pasīvā balss eksplozija

- tiek nodrošināts
- tiek piedāvāts
- tiek realizēts
- tiek īstenots
- tiek veikts

**Likme:** maks. **1× `tiek`** visā tekstā. Visur citur — aktīvā balss ar konkrētu subjektu.

---

## 6. Lietvārdu-darbības vārdu pāri (substantive inflation)

| Pāris ar lietvārdu | Aizstāj ar darbības vārdu |
|---|---|
| veikt analīzi | analizēt |
| sniegt atbalstu | atbalstīt |
| veikt realizāciju | realizēt |
| veikt izmaiņas | mainīt |
| nodrošināt pieejamību | dot pieeju / padarīt pieejamu |
| veikt pārbaudi | pārbaudīt |
| sniegt informāciju | informēt |
| veikt pasākumus | rīkoties |

---

## 7. Angļu kalku tells (AI tulkojuma artefakti)

| Angļu | LV kalka (slikti) | LV aizstājējs |
|---|---|---|
| We are passionate about… | Mēs esam aizrautīgi par… | Mums rūp… |
| In today's dynamic environment | Mūsdienu dinamiskajā vidē | (izmest) vai *šobrīd* |
| Unlock your potential | Atslēdziet savu potenciālu | Izmantojiet savas spējas |
| Seamless experience | Bezšuvju pieredze | Ērta lietošana |
| Game-changing solutions | Spēli mainoši risinājumi | Risinājumi, kas maina pieeju |
| Empowering businesses | Dāvinot spēku uzņēmumiem | Palīdzam uzņēmumiem augt |
| Delve | Iedziļināsimies | (izmest — vai *paskatīsimies*) |
| Tapestry (of) | Gobelēns | (izmest) |
| Realm | Valstība | joma / nozare |
| Robust | Robusta | stabila / izturīga |

---

## 8. LV korporatīvās klišejas (no LV web-copy izpētes)

- Uzticams partneris
- Individuāla pieeja katram klientam
- Profesionāla komanda ar ilggadēju pieredzi
- Nodrošinām augstākās kvalitātes …
- Visaptverošs risinājums
- No idejas līdz rezultātam / No A līdz Z
- Sazinieties ar mums jau šodien!
- Pilna spektra pakalpojumi
- Pat vissarežģītākajās situācijās
- Mēs palīdzam sasniegt jūsu mērķus

**Likme:** ja šī frāze var stāvēt JEBKURA uzņēmuma mājaslapā — tā ir klišeja. Atrod, kas ir konkrēti par TAVU klientu, un raksti to.

---

## 9. Brāļa-specifiskās klišejas (alus zīmoliem)

- Izcila kvalitāte
- Unikāls garšas baudījums
- Īstiem gardēžiem
- Paceļam glāzes!
- Ienirsti garšās!
- Mūsdienu dinamiskajā pasaulē

---

## 10. Krievu kalki (joprojām dzīvi LV — labot)

| Slikti (kalks) | Pareizi |
|---|---|
| pieņemt mērus | veikt pasākumus |
| pacelt jautājumu | izvirzīt jautājumu |
| piegriezt uzmanību | pievērst uzmanību |
| X gadus atpakaļ | pirms X gadiem |

---

## 11. Strukturāli AI-signāli (nav frāzes, bet patternsi)

- Visi teikumi sākas ar **`Mēs…`** — egocentrisks ritms
- **Triādiski saraksti** uz cilpas: `gan A, gan B, gan C`
- **Pasīvās balss kaudzes** — 3+ `tiek` vienā rindkopā
- **Garas pakārtotības ķēdes** — 3–4 `kas` palīgteikumi
- **Vienādi paragrāfu garumi** — mehānisks ritms bez elpas
- **Uniform sentence length** — visi teikumi 10–15 vārdi

---

## 12. Emocionālā reģistra slazdi

- Izsaukuma zīmes mārketinga tekstā (`Mainīsim jūsu dzīvi!`)
- Superlatīvi bez seguma (`vislabākais`, `unikāls`, `neatkārtojams`, `brīnišķīgs`)
- Amerikāņu entuziasma tonis (LV lasītājs uz to reaģē ar skepsi/aizsardzību)
- Adjective-stack: `brīnišķīgs, neatkārtojams, izcils, unikāls` vienā teikumā

**Likme:** LV publicistika rāda aizrautību caur **detaļas meistarību**, ne caur deklaratīvo intensitāti.

---

## Procedūra

1. **Pirms ģenerēšanas** — iekļauj šo sarakstu (vai būtisku tā daļu) prompt-ā:
   > Nekad neizmanto šādus vārdus/frāzes: [...iekop sarakstu...]
2. **Pēc ģenerēšanas** — skenē output pret šo sarakstu. Katra atrasta frāze = pārrakstīt.
3. **Cilvēka redaktora caurskate** — 30–60 min uz 1000 vārdiem; obligāta arī ar perfekto promptu.

---

## Avoti

- `wiki/concepts/kancelejismi.md`
- `wiki/concepts/ai-slop.md`
- `wiki/concepts/ai-humanization-prompting.md`
- `raw/latvian-copywriting/LV language research.md`
- `raw/latvian-copywriting/publicistika-claude-research.md`
- `raw/latvian-copywriting/publicistika-gemini-research.md`
