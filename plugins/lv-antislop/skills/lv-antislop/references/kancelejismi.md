# Kancelejismi — birokrātiskā reģistra LV diagnostika

> Adaptēts no `C:\Projects\obsidian-wiki\obsidian-wiki\wiki\concepts\kancelejismi.md`. Avoti: LV language research, publicistika-claude-research, publicistika-gemini-research.

## Kas tas ir

**Kancelejismi** — smagais, pasīvās balss, lietvārdu sakraušanas LV reģistrs, ko izmanto valsts pārvalde un juridiskie teksti. Dziļi iesakņojies reģistrs, kas standartizējās līdz ar Latvijas valsts aparātu un ES dokumentiem.

2026. gadā tas ir **galvenais ienaidnieks dzīvai LV rakstībai** — un tieši tas reģistrs, uz kuru LLM-i pēc noklusējuma iet, ģenerējot LV, jo formālos treniņdatos dominē ES direktīvu tulkojumi, valsts portāli un juridiskie akti.

**Kancelejismi + AI angļu klišejas = nepārprotamais "AI latviešu".**

## Diagnostiskie signāli

### Pasīvās balss dominance
- *tiek nodrošināts*
- *tiek piedāvāts*
- *tiek realizēts*
- *tiek veikts*

### Substantive inflation — dinamiski darbības vārdi nomainīti ar lietvārdu-darbības vārdu pāriem

| Slikti | Pareizi |
|---|---|
| veikt realizāciju | realizēt |
| sniegt atbalstu | atbalstīt |
| veikt analīzi | analizēt |
| veikt izmaiņas | mainīt |
| nodrošināt pieejamību | dot pieeju |

### Garas pakārtotības ķēdes
3–4 *kas*-palīgteikumi vienā teikumā:

> *Sistēma, kas nodrošina atbalstu klientiem, kas izmanto pakalpojumus, kas tiek piedāvāti uzņēmuma platformā…*

### Tukšie ievadi
- *Ir svarīgi atzīmēt, ka …*
- *Ir vērts piebilst, ka …*
- *Kopumā var secināt, ka …*
- *Noslēgumā jāatzīmē, ka …*

### Birokrātiskās pārejas
- *turklāt*
- *tādējādi*
- *līdz ar to*
- *kā arī*
- *tai skaitā*
- *neatkarīgi no tā, vai*

### Lietvārdu sakraušanas teikumi, kas varētu dzīvot kā aktīvi verbi
> *Tiek veikta klientu apkalpošanas kvalitātes uzlabošana.* → **Mēs uzlabojam klientu apkalpošanu.**

## Kāpēc LLM-i to ražo

LATE projekts uzkrāja 1,3B+ tokenu LNCC korpusā — bet augstā reģistra LV korpusi, kas pieejami pasaules komerciālajiem LLM-iem, ir dominēti ar:

1. **ES-direktīvu tulkojumiem** (pēc dizaina pilni ar kancelejismiem)
2. **Valsts portāliem un aģentūru tekstu**
3. **Juridiskajiem un regulējošajiem dokumentiem**

Kad modelis, kas apmācīts uz šāda korpusa, ražo "augsta reģistra latviešu valodu", tas ražo kancelejismus. Tā nav modeļa kļūda — tas ir statistiskais formālā LV digitālā teksta gravitācijas centrs.

## Vēsturiskās saknes

LV rakstu valoda gāja cauri **grafizācijai** (13.–17. gs.), **normalizācijai** (18.–19. gs.) un **modernizācijai** (19.–20. gs.). Normalizācijas posmā, kad veidojās Latvijas valsts aparāts un juridiskā sistēma, formālais reģistrs sastinga — pasīvi orientēts, lietvārdu piesātināts, izstiepts. Tas saglabājies līdz 2026. gadam kā LV "formālā" noklusējuma forma.

## Ārstniecība

- **[publicistika](publicistika.md) kā aizvietotājs** — nevis vairāk sarunvaloda, bet **citā funkcionālā centrā**.
- **Aktīvi darbības vārdi:** *darām, būvējam, rādām, mainām, ietaupām, samazinām, palielinām*.
- **Strip pasīvo:** maks. **viens** *tiek* visā tekstā.
- **Strip filler intros:** vienkārši pasaki faktu.
- **Aizvieto lietvārdu pārus ar verbiem:** *realizēt* nevis *veikt realizāciju*.
- **Pārtraukt garas pakārtotības ķēdes:** divi vai trīs īsi teikumi.
- **Per-zīmola aizliegto frāžu saraksts** — skat. [banned-phrases.md](banned-phrases.md).

## Attiecība pret AI-slop

AI-slop ir virsklase; kancelejismi ir **specifiski-latviskais apakštips**. Quality-gate hook (PostToolUse uz Write) LV satura klientiem jānoķer abi:

1. **Tulkotās EN AI-klišejas** — *iedziļināsimies, bezšuvju, gobelēns*
2. **Vietējās LV kancelejas konstrukcijas** — pasīvi-smagas, lietvārdu-piesātinātas

## Saistība ar citiem konceptiem

- `banned-phrases.md` — pilns aizliegto frāžu/patternsu saraksts
- `publicistika.md` — ārstniecības tradīcija
- `humanization-techniques.md` — prompt-engineering pretpasākumi
