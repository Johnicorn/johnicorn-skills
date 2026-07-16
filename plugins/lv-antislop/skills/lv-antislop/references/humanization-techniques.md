# Humanization techniques — LV-specifiskās prompt-inženierijas tehnikas

> Adaptēts no `C:\Projects\obsidian-wiki\obsidian-wiki\wiki\concepts\ai-humanization-prompting.md`. Avoti: LV language research, publicistika-claude-research, publicistika-gemini-research.

## Mērķis

Prompt-engineering tehnikas, kas pārvirza LLM output no tā noklusējuma centra (formāls, simetrisks, pozitīvs, kancelejas reģistrs LV) uz tekstu, kas lasās kā ar roku rakstīts.

**Tas nav AI-detector evasion** — tā ir tas, ko prasa laba rakstība valodā, kur LLM noklusējums ir objektīvi slikts.

## 5 pamattehnikas

### 1. Persona emulācija + toņa virziens

Eksplicītas balss instrukcijas vinnē pret abstraktu "esi radošs":

- *Izmanto sarunvalodas toni.*
- *Skani dabiski un uztverami.*
- *Izvairies no robotiskas rakstīšanas.*
- *Raksti kā īsts cilvēks ar konkrētu personību.*

**Spoguļa efekts:** kā TU raksti prompt, tā arī output. Neformāli prompti rada neformālus output-us; formāli prompti rada formālus. **Prompt-o tajā balsī, ko gribi atpakaļ.**

### 2. Teikuma garuma + ritma variācija

Viens no spēcīgākajiem AI-signāliem ir vienmērīgs teikuma garums. Eksplicītā instrukcija:

- *Sajauc īsus, vidējus un garus teikumus, lai izveidotu ritmu.*
- *Limitē teikumus līdz 10–20 vārdiem.*
- *Raksti aptuveni 8. klases lasīšanas grūtības līmenī.*
- *Izmanto tiešus apgalvojumus bez gariem ievadiem.*
- *Izvairies no vārdiem ar 4+ zilbēm, ja ir vienkāršāks variants.*

### 3. Banned-word blacklist prompt-ā

**Visefektīvākā tehnika.** Piemērs:

> *Nekad neizmanto šādus vārdus: iedziļināsimies, digitālais laikmets, turklāt, neskatoties uz to, inovatīvs, gobelēns, nenoliedzami.*

Spiež modeļa varbūtību masu pārdalīties prom no tā statistiskajiem favorītiem. Pilns saraksts: [banned-phrases.md](banned-phrases.md).

### 4. Stāstniecība + analoģijas injekcija

Aizvieto sausu uzskaitījumu. Konkrēti piemēri:

- *Paskaidro doto tēmu, izmantojot vienkāršu analoģiju, ko saprastu iesācējs.*
- *Iekļauj 3–5 teikumu garu naratīvu ar kādu emocionālu atziņu vai reflekciju.*
- *Balsties uz reālas dzīves salīdzinājumiem, nevis industrijas žargonu.*

### 5. Multi-parameter psiholoģiskā ietvarošana (advanced)

Ekspertu līmeņa tehnika — modelis pirms ģenerēšanas pats izvērtē:

- **Publisks vs privāts uzstādījums** (1–10)?
- **Rakstītāja psiholoģiskais ierobežojums** (1–10)? Balstoties uz svešisks vs uzticams adresāts.
- **Situatīvais stresa līmenis** (1–10)?
- *Opcionāli:* attiecību audits (platonisks vs romantisks).

Output tad sintezēts pār četriem slāņiem:
1. Vides norādes
2. Fiziskas reakcijas (pauzes, elpa)
3. Zemapziņas patiesās jūtas
4. Pati verbālā teksta

Sabojā plakaņas-atbildes matricas; pārvirza tekstu uz psiholoģisko ticamību.

## LV-specifiskās piebildes

Pār universālajām tehnikām, LV output iegūst no:

### Eksplicīta instrukcija lietot partikulas
> *Integrē dabiskās latviešu partikulas: nu, jau, taču, gan, vien, jel — kur tas ritmā iederas.*

LLM-i tās izlaiž pēc noklusējuma.

### Instrukcija pret kancelejismiem
> *Nepārtulko no angļu. Neraksti kā valsts iestādes paziņojumu. Aktīvā balss, nevis "tiek".*

### Few-shot piemēri no labākajām iepriekšējām darbām
Padod 5–10 iepriekšējos spēcīgos output-us kā kontekstu — tas sit pār instrukciju vien.

> *We fed every piece of their existing content into Claude as training context… The AI output sounded like their practice.* (210 Digital Marketing case study)

### Post-edit obligācija
Pat ar perfektu prompting paliek **30–60 min native-redaktora laika uz 1000 LV vārdiem**. Tas ir LV LLM bottleneck — nav iespējams atcelt. Plāno pipeline ap to.

## Teorētiskā bāze

Tonis-balss noteikumi ir empīriski apstiprināti ar **self-determination theory** (SDT):

- **Autonomy-supportive valoda** — *uzaicini, apsver, ievēro* — ir SDT recepte ilgtspējīgai internalizācijai. Humanizācijas noteikumi nav tikai stilistiskas preferences; tie ir motivacionāli noslogoti.
- **Informatīva vs vērtējoša feedback** (SDT princips) — *"tu pabeidzi 4 no 7 sesijām; lūk, kas tām bija kopīgs"* > *"tu nokavēji 3 dienas."*

Tas padara humanization-prompting skill **dual-purpose**:
1. Producē tekstu, kas SKAN cilvēka rakstīts
2. ATBALSTA lietotāja motivāciju, kad teksts ir agent-uz-lietotāju komunikācija

## Praktiska prompt-skelets LV uzdevumam

```
[CONTEXT]
Tu raksti [konkrēts uzdevums, piem. landing-page sekciju] zīmolam [nosaukums],
auditorijai [konkrēts profils].

[VOICE]
- Sarunvalodas, izkopta latviešu valoda. Žurnāla "Ir" / "Rīgas Laiks" reģistrs.
- Aktīvā balss. Mainīgs teikuma garums. Konkrētas detaļas.
- Integrē partikulas (nu, jau, taču, gan, vien) tur, kur ritmā iederas.
- Ironija un šaubas kā bāzes līnija — bez amerikāņu entuziasma.

[BANNED]
Nekad neizmanto: turklāt, tādējādi, līdz ar to, ir svarīgi atzīmēt, kopumā,
visaptverošs, inovatīvs, nodrošināt (kā generic verb), tiek (vairāk par 1× tekstā).
[+ pilnais saraksts no banned-phrases.md]

[FEW-SHOT]
Lūk, 3 piemēri no labākā iepriekšējā satura:
[piemērs 1]
[piemērs 2]
[piemērs 3]

[TASK]
[konkrēts uzdevums]
```

## Saistība

- [banned-phrases.md](banned-phrases.md) — taktiskais blacklist
- [kancelejismi.md](kancelejismi.md) — kāpēc LV LLM noklusējums ir slikts
- [publicistika.md](publicistika.md) — tradīcija, uz kuru pārvirzīties
