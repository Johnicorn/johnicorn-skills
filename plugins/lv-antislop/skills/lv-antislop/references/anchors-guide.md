# Anchors guide

**Anchori = 3–5 references teksti, ko dod pirms ģenerēšanas.** Tie ir vienīgais labojums AI-sausumam: instrukciju proza vien ražo gramatiski tīru, bet mirušu LV — bez partikulām, bez ritma variācijas, bez ironijas reģistra.

## Kāpēc

LLM zina *noteikumus* ("lieto partikulas", "sajauc garumus"), bet neražo *ritmu* no noteikumiem. Ritms nāk no imitācijas. 3–5 labi paraugi dod modelim ko atspoguļot; tad tas būvē svaigu saturu tajā reģistrā.

## No kurienes

Pēc projekta/balss — **konkrētā balss labākie iepriekšējie teksti**:

- Savam zīmolam = engagement-validētie publicētie posti.
- Kursam/programmai = iepriekšējie materiāli tajā pašā balsī.
- Klientam = tā zīmola labākie paraugi (ne konkurentu, ne ģeneriski).
- Jaunam projektam bez vēstures = 3–5 tekstu no autora, kura balsi grib.

## Likumi

- **Stila piemēri, ne faktu avots.** Anchori dod *kā skanēt*, nekad *ko apgalvot*. Tie nekad nepārraksta uzdevumu vai neievieš faktus.
- **`anchor_support` ir metadata, ne vārti.** 0 = none, 1–2 = limited, 3–5 = recommended. Ar mazāk anchoriem izvade būs sausāka — bet ģenerēšana neapstājas un `anchor_support` pats nepiespiež cilvēka caurskati. (Vai maz anchoru tiešām ražo sausāku tekstu — mērāma hipotēze, ne pieņēmums.)
- **Kvalitāte > skaits.** Divi spēcīgi anchori sit piecus vājus. Izvēlies tekstus, kas *tiešām* skan tā, kā gribi.
