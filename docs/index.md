# Operativna ograničenja

Alat za proračun **operativnih ograničenja novih proizvodnih postrojenja** prema
*Smjernicama za izvođenje mrežnih analiza na modelima prijenosne elektroenergetske mreže*
(HOPS, lipanj 2026.), koje se primjenjuju pri izradi elaborata optimalnog tehničkog rješenja
priključenja (EOTRP) proizvodnih postrojenja.

Smjernice predviđaju proračune u PSS/E-u. Ovaj alat iste proračune radi u otvorenom
kodu (Python, [pandapower](https://www.pandapower.org/)) na modelima koje HOPS isporučuje
u PSS/E `.raw` formatu (v35):

1. izgradnja pandapower modela iz `.raw` datoteke i provjera prema spremljenom PSS/E rješenju,
2. proračun tokova snaga u osnovnom (N) stanju i N-1 analiza,
3. određivanje doprinosa novih korisnika preopterećenjima i operativnih ograničenja (formula [1] smjernica),
4. prijedlog mjera (PST, DTR, HTLS, uređaji za kontrolu tokova, novi elementi) i vremenski tijek ograničenja do izgradnje STUM-a,
5. tablični (Tablice 5–8 smjernica) i grafički prikaz rezultata.

> [!IMPORTANT]
> **Smjernice ne propisuju kako se uravnotežuje snaga** kad se novi korisnik isključi ili
> ograniči — a o tome izravno ovise i doprinosi korisnika i iznos ograničenja.
> Alat zato svaki proračun radi u **tri varijante uravnoteženja** i rezultate prikazuje
> usporedno. Vidi [poglavlje 6](teorija/06-uravnotezenje.md) i
> [obveznu napomenu za izvještaje](izvjestaji/napomena-uravnotezenje.md).

> [!CAUTION]
> Smjernice i isporučeni modeli imaju nedostatke koji utječu na rezultat — najvažniji je
> zahtjev za istodobnom naponskom regulacijom i podešavanjem kuta PST-ova s dijagonalnom
> regulacijom, za koji modeli nemaju podataka. Popis: [Nedostaci smjernica i podataka](nedostaci-smjernica.md).

## Status

| Dio | Stanje |
|---|---|
| Pretvorba PSS/E v35 `.raw` → pandapower | radi; provjereno na modelu scenarija A 2029. (max ΔU 0,00017 p.u., max Δθ 0,025°) |
| N-1 analiza | u izradi |
| Operativna ograničenja (formula [1], tri varijante uravnoteženja) | u izradi |
| Prijedlog mjera i energija ograničenja 2029.–2035. | u izradi |
| Vizualizacija | u izradi |

## Struktura repozitorija

```
docs/            teorijska knjiga i dokumentacija (ova stranica, GitHub Pages)
src/oplimits/    Python paket (kod na engleskom)
scripts/         skripte za pokretanje iz IDLE-a (F5), postavke na vrhu datoteke
config/          korisničke postavke i nadjačavanja (vodiči, PST tablice, troškovi)
data/            lokalni modeli i rezultati — NE objavljuju se
tests/           testovi
```

## Podaci

Mrežni modeli HOPS-a, popisi korisnika u postupku priključenja i rezultati proračuna
**nisu dio repozitorija** i ne smiju se objaviti. 
