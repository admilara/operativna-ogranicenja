# Prilog A — PST-ovi u modelu A-2029

Pregled svih transformatora s mogućnošću zakreta kuta u modelu scenarija A 2029.: osnovni podaci
svakog transformatora i njegova tablica korekcije impedancije. Transformatori koji dijele istu
tablicu prikazani su zajedno — **Konjsko i Melina imaju istu tablicu (4, od −5,4° do +9°) i iste
podatke o impedancijama**.

Svi podaci su iz `.raw` datoteke; vrijednosti označene *(izračunato)* izvedene su iz njih.
Stranicu generira skripta `scripts/pst_report.py`, pa se ista usporedba može napraviti za bilo
koji od 42 modela. Napon namota po položaju preklopke u datoteci ne postoji
([Nedostaci smjernica, N1](../nedostaci-smjernica.md)).

Kako čitati tablice korekcije:

- **F** je faktor kojim se množi nazivna impedancija (pogl. 2, §2.2); impedancija u `.raw`-u
  je ona uz F = 1, na rubu tablice.
- **u<sub>k12</sub>** je efektivna impedancija između namota 1 i 2 pri tom faktoru, na nazivnoj
  snazi para. Kod autotransformatora F djeluje na Z<sub>1</sub> zvijezde, pa se u<sub>k12</sub>
  mijenja više od F.
- Redak *u kosim slovima* je kut iz modela kad ne pada na točku tablice — faktor je tada
  linearno interpoliran.
- Podebljane vrijednosti u tablicama osnovnih podataka označavaju odstupanja koja treba
  primijetiti (izvan pogona, nula umjesto vrijednosti).

## Konjsko i Melina — tablica korekcije 4

### Konjsko (autotransformator)

| | T1 | T2 | T3 |
|---|---|---|---|
| Priključak (namot 1 → namot 2) | 60049 HKONJS11 (400 kV) → 60050 HKONJS21 (220 kV) | 60049 HKONJS11 (400 kV) → 60050 HKONJS21 (220 kV) | 60049 HKONJS11 (400 kV) → 60050 HKONJS21 (220 kV) |
| Tercijar (namot 3) | 23079 KONJSKO (30 kV) | 23080 KONJSKO (30 kV) | 23078 KONJSKO (30 kV) |
| U pogonu | da | da | da |
| Nazivni naponi namota NOMV [kV] | 400 / 220 / 30 | 400 / 220 / 30 | 400 / 220 / **0** (= bazni napon) |
| Namotni naponi WINDV [kV] | 412,5 / 231 / 31,5 | 412,5 / 231 / 31,5 | 412,5 / 230,999 / 30 |
| Nazivne snage parova 1-2 / 2-3 / 3-1 [MVA] | 400 / 100 / 100 | 400 / 100 / 100 | 400 / 100 / 100 |
| RATE namota 1 / 2 / 3 [MVA] | 400 / 400 / 100 | 400 / 400 / 100 | 400 / 400 / 100 |
| u<sub>k</sub> parova 1-2 / 2-3 / 3-1 [%] (na snazi para) | 11,67 / 4,00 / 13,35 | 11,67 / 4,00 / 13,35 | 11,67 / 4,00 / 13,35 |
| Gubici u bakru parova 1-2 / 2-3 / 3-1 [kW] | 582,4 / 233,6 / 237,1 | 582,4 / 233,6 / 237,1 | 582,4 / 233,6 / 237,1 |
| Kut u modelu ANG1 [°] | **5,5** | **5,5** | **5,5** |
| Faktor F pri tom kutu *(izračunato)* | 0,7903 | 0,7903 | 0,7903 |
| u<sub>k12</sub> pri tom kutu [%] *(izračunato)* | 6,52 | 6,52 | 6,52 |
| Raspon kuta prema Tablici 3 smjernica | −5,4° do +9° | −5,4° do +9° | −5,4° do +9° |
| Tablica korekcije / broj točaka / raspon | 4 / 25 / −5,4° … 9° | 4 / 25 / −5,4° … 9° | 4 / 25 / −5,4° … 9° |
| Broj položaja preklopke NTP1 | 33 | 33 | 33 |
| Granice u zapisu (RMA/RMI, VMA/VMI) | granice **napona** 367,701–416,738 kV, pojas 0,9–1,1 p.u. | granice **napona** 367,701–416,738 kV, pojas 0,9–1,1 p.u. | granice **napona** 367,701–416,738 kV, pojas 0,9–1,1 p.u. |
| Regulacija (COD1 / regulirana sabirnica) | −3 (kut, isključena) / 60050 | −3 (kut, isključena) / 60050 | −3 (kut, isključena) / 60050 |
| Grupa spoja | — | — | — |
| Zvjezdište u rješenju (VMSTAR / ANSTAR) | 1,00119 p.u. / 127,0577° | 1,00119 p.u. / 127,0577° | 1,00120 p.u. / 127,0577° |

### Melina (autotransformator)

| | T1 | T2 |
|---|---|---|
| Priključak (namot 1 → namot 2) | 60066 HMELIN11 (400 kV) → 60067 HMELIN21 (220 kV) | 60066 HMELIN11 (400 kV) → 60067 HMELIN21 (220 kV) |
| Tercijar (namot 3) | 23047 MELINA (30 kV) | 23048 MELINA (30 kV) |
| U pogonu | da | da |
| Nazivni naponi namota NOMV [kV] | **0** (= bazni napon) / **0** (= bazni napon) / **0** (= bazni napon) | 400 / 220 / 30 |
| Namotni naponi WINDV [kV] | 400 / 231 / 30 | 400 / 231 / 31,5 |
| Nazivne snage parova 1-2 / 2-3 / 3-1 [MVA] | 400 / 100 / 100 | 400 / 100 / 100 |
| RATE namota 1 / 2 / 3 [MVA] | **0** / 400 / **0** | 400 / 400 / 100 |
| u<sub>k</sub> parova 1-2 / 2-3 / 3-1 [%] (na snazi para) | 11,67 / 4,00 / 13,35 | 11,67 / 4,00 / 13,35 |
| Gubici u bakru parova 1-2 / 2-3 / 3-1 [kW] | 582,4 / 233,6 / 237,1 | 582,4 / 233,6 / 237,1 |
| Kut u modelu ANG1 [°] | **0** | **0** |
| Faktor F pri tom kutu *(izračunato)* | 0,8333 | 0,8333 |
| u<sub>k12</sub> pri tom kutu [%] *(izračunato)* | 7,58 | 7,58 |
| Raspon kuta prema Tablici 3 smjernica | −5,4° do +9° | −5,4° do +9° |
| Tablica korekcije / broj točaka / raspon | 4 / 25 / −5,4° … 9° | 4 / 25 / −5,4° … 9° |
| Broj položaja preklopke NTP1 | 33 | 33 |
| Granice u zapisu (RMA/RMI, VMA/VMI) | granice **napona** 367,7–416,74 kV, pojas 0,9–1,1 p.u. | granice **napona** 367,7–416,74 kV, pojas 0,9–1,1 p.u. |
| Regulacija (COD1 / regulirana sabirnica) | −3 (kut, isključena) / 60067 | −3 (kut, isključena) / 60067 |
| Grupa spoja | YNa0d5 | YNa0d5 |
| Zvjezdište u rješenju (VMSTAR / ANSTAR) | 0,95381 p.u. / 83,6743° | 0,95381 p.u. / 83,6743° |

### Tablica korekcije impedancije 4

u<sub>k12</sub> je izračunata efektivna impedancija para 1-2 na nazivnoj snazi para za faktor F (F se primjenjuje na Z<sub>1</sub> zvijezde, pogl. 2, §2.4); Konjsko i Melina imaju jednake podatke o impedancijama, pa je stupac zajednički.

| Točka | Kut [°] | F | u<sub>k12</sub> [%] | U modelu |
|---|---|---|---|---|
| 1 | −5,40 | 1,00000 | 11,67 |  |
| 2 | −5,05 | 0,98610 | 11,33 |  |
| 3 | −4,69 | 0,97220 | 10,99 |  |
| 4 | −4,30 | 0,95830 | 10,65 |  |
| 5 | −3,91 | 0,94440 | 10,31 |  |
| 6 | −3,48 | 0,93060 | 9,97 |  |
| 7 | −3,04 | 0,91670 | 9,63 |  |
| 8 | −2,58 | 0,90280 | 9,28 |  |
| 9 | −2,11 | 0,88890 | 8,94 |  |
| 10 | −1,60 | 0,87500 | 8,60 |  |
| 11 | −1,10 | 0,86110 | 8,26 |  |
| 12 | −0,55 | 0,84720 | 7,92 |  |
| 13 | 0,00 | 0,83330 | 7,58 | **Melina T1, T2** |
| 14 | 0,64 | 0,82780 | 7,44 |  |
| 15 | 1,29 | 0,82220 | 7,31 |  |
| 16 | 1,97 | 0,81670 | 7,17 |  |
| 17 | 2,68 | 0,81110 | 7,03 |  |
| 18 | 3,39 | 0,80560 | 6,90 |  |
| 19 | 4,14 | 0,80000 | 6,76 |  |
| 20 | 4,91 | 0,79440 | 6,62 |  |
| *—* | ***5,5*** | ***0,7903*** | *6,52* | **Konjsko T1, T2, T3** *(interpolirano)* |
| 21 | 5,70 | 0,78890 | 6,49 |  |
| 22 | 6,50 | 0,78330 | 6,35 |  |
| 23 | 7,31 | 0,77780 | 6,22 |  |
| 24 | 8,15 | 0,77222 | 6,08 |  |
| 25 | 9,00 | 0,76670 | 5,94 |  |

## Žerjavinec — tablica korekcije 2

### Žerjavinec (autotransformator)

| | T1 |
|---|---|
| Priključak (namot 1 → namot 2) | 60150 HZERJA11 (400 kV) → 60151 HZERJA21 (220 kV) |
| Tercijar (namot 3) | 23039 ZERJAVINEC (10 kV) |
| U pogonu | da |
| Nazivni naponi namota NOMV [kV] | 400 / 220 / 10 |
| Namotni naponi WINDV [kV] | 400,663 / 231 / 10,5 |
| Nazivne snage parova 1-2 / 2-3 / 3-1 [MVA] | 400 / 100 / 100 |
| RATE namota 1 / 2 / 3 [MVA] | 400 / 400 / 100 |
| u<sub>k</sub> parova 1-2 / 2-3 / 3-1 [%] (na snazi para) | 12,22 / 9,00 / 14,00 |
| Gubici u bakru parova 1-2 / 2-3 / 3-1 [kW] | 582,4 / 242,0 / 236,0 |
| Kut u modelu ANG1 [°] | **0** |
| Faktor F pri tom kutu *(izračunato)* | 0,8349 |
| u<sub>k12</sub> pri tom kutu [%] *(izračunato)* | 9,56 |
| Raspon kuta prema Tablici 3 smjernica | −4,48° do +6,76° |
| Tablica korekcije / broj točaka / raspon | 2 / 25 / −4,48° … 6,76° |
| Broj položaja preklopke NTP1 | 25 |
| Granice u zapisu (RMA/RMI, VMA/VMI) | granice **napona** 375,1–416 kV, pojas 1–1,04 p.u. |
| Regulacija (COD1 / regulirana sabirnica) | −3 (kut, isključena) / 60151 |
| Grupa spoja | — |
| Zvjezdište u rješenju (VMSTAR / ANSTAR) | 0,97288 p.u. / 87,0324° |

### Tablica korekcije impedancije 2

u<sub>k12</sub> je izračunata efektivna impedancija para 1-2 na nazivnoj snazi para za faktor F (F se primjenjuje na Z<sub>1</sub> zvijezde, pogl. 2, §2.4).

| Točka | Kut [°] | F | u<sub>k12</sub> [%] | U modelu |
|---|---|---|---|---|
| 1 | −4,48 | 1,00000 | 12,22 |  |
| 2 | −4,19 | 0,98620 | 12,00 |  |
| 3 | −3,89 | 0,97250 | 11,78 |  |
| 4 | −3,57 | 0,95870 | 11,55 |  |
| 5 | −3,24 | 0,94500 | 11,33 |  |
| 6 | −2,89 | 0,93120 | 11,11 |  |
| 7 | −2,52 | 0,91740 | 10,89 |  |
| 8 | −2,14 | 0,90370 | 10,67 |  |
| 9 | −1,75 | 0,88990 | 10,45 |  |
| 10 | −1,33 | 0,87620 | 10,23 |  |
| 11 | −0,91 | 0,86240 | 10,00 |  |
| 12 | −0,46 | 0,84870 | 9,78 |  |
| 13 | 0,00 | 0,83490 | 9,56 | **Žerjavinec T1** |
| 14 | 0,48 | 0,83000 | 9,48 |  |
| 15 | 0,97 | 0,82510 | 9,40 |  |
| 16 | 1,48 | 0,82020 | 9,32 |  |
| 17 | 2,01 | 0,81530 | 9,24 |  |
| 18 | 2,55 | 0,81040 | 9,17 |  |
| 19 | 3,11 | 0,80550 | 9,09 |  |
| 20 | 3,69 | 0,80060 | 9,01 |  |
| 21 | 4,28 | 0,79570 | 8,93 |  |
| 22 | 4,88 | 0,79080 | 8,85 |  |
| 23 | 5,49 | 0,78590 | 8,77 |  |
| 24 | 6,12 | 0,78100 | 8,69 |  |
| 25 | 6,76 | 0,77610 | 8,61 |  |

## Senj — tablica korekcije 3

### Senj (autotransformator)

| | T1 |
|---|---|
| Priključak (namot 1 → namot 2) | 60109 HSENJ 21 (220 kV) → 60157 HSENJ 51 (110 kV) |
| Tercijar (namot 3) | 23065 HESENJ (10 kV) |
| U pogonu | da |
| Nazivni naponi namota NOMV [kV] | 220 / 110 / 10 |
| Namotni naponi WINDV [kV] | 230,562 / 115 / 10,5 |
| Nazivne snage parova 1-2 / 2-3 / 3-1 [MVA] | 200 / 66 / 66 |
| RATE namota 1 / 2 / 3 [MVA] | 200 / 200 / 66 |
| u<sub>k</sub> parova 1-2 / 2-3 / 3-1 [%] (na snazi para) | 12,93 / 9,50 / 12,93 |
| Gubici u bakru parova 1-2 / 2-3 / 3-1 [kW] | 510,0 / 225,0 / 225,0 |
| Kut u modelu ANG1 [°] | **8,97** |
| Faktor F pri tom kutu *(izračunato)* | 0,7403 |
| u<sub>k12</sub> pri tom kutu [%] *(izračunato)* | 9,90 |
| Raspon kuta prema Tablici 3 smjernica | −6,3° do +10,54° |
| Tablica korekcije / broj točaka / raspon | 3 / 25 / −6° … 10,54° |
| Broj položaja preklopke NTP1 | 25 |
| Granice u zapisu (RMA/RMI, VMA/VMI) | granice **kuta** −6,3° … 10°, pojas toka −195 … −190 MW |
| Regulacija (COD1 / regulirana sabirnica) | −3 (kut, isključena) / 60157 |
| Grupa spoja | — |
| Zvjezdište u rješenju (VMSTAR / ANSTAR) | 0,96473 p.u. / 92,8033° |

### Tablica korekcije impedancije 3

u<sub>k12</sub> je izračunata efektivna impedancija para 1-2 na nazivnoj snazi para za faktor F (F se primjenjuje na Z<sub>1</sub> zvijezde, pogl. 2, §2.4).

| Točka | Kut [°] | F | u<sub>k12</sub> [%] | U modelu |
|---|---|---|---|---|
| 1 | −6,00 | 1,00000 | 12,93 |  |
| 2 | −5,93 | 0,97780 | 12,67 |  |
| 3 | −5,53 | 0,95560 | 12,41 |  |
| 4 | −5,10 | 0,93340 | 12,15 |  |
| 5 | −4,65 | 0,91110 | 11,89 |  |
| 6 | −4,18 | 0,88890 | 11,63 |  |
| 7 | −3,67 | 0,86670 | 11,38 |  |
| 8 | −3,14 | 0,84450 | 11,12 |  |
| 9 | −2,57 | 0,82230 | 10,86 |  |
| 10 | −1,98 | 0,80010 | 10,60 |  |
| 11 | −1,35 | 0,77780 | 10,34 |  |
| 12 | −0,69 | 0,75560 | 10,08 |  |
| 13 | 0,00 | 0,73340 | 9,82 |  |
| 14 | 0,72 | 0,73410 | 9,83 |  |
| 15 | 1,48 | 0,73470 | 9,84 |  |
| 16 | 2,26 | 0,73540 | 9,84 |  |
| 17 | 3,08 | 0,73610 | 9,85 |  |
| 18 | 3,92 | 0,73670 | 9,86 |  |
| 19 | 4,80 | 0,73740 | 9,87 |  |
| 20 | 5,70 | 0,73800 | 9,87 |  |
| 21 | 6,63 | 0,73870 | 9,88 |  |
| 22 | 7,58 | 0,73940 | 9,89 |  |
| 23 | 8,55 | 0,74000 | 9,90 |  |
| *—* | ***8,97*** | ***0,7403*** | *9,90* | **Senj T1** *(interpolirano)* |
| 24 | 9,54 | 0,74070 | 9,91 |  |
| 25 | 10,54 | 0,74130 | 9,91 |  |

## Gračac — tablica korekcije 1

### Gračac (dvonamotni PST)

| | VP Velebit | VP Licki Osik |
|---|---|---|
| Priključak (namot 1 → namot 2) | 80049 PST GRACAC (110 kV) → 60035 HGRACA51 (110 kV) | 80050 PST GRACAC2 (110 kV) → 60035 HGRACA51 (110 kV) |
| U pogonu | **ne** | da |
| Nazivni naponi namota NOMV [kV] | 110 / 110 | 110 / 110 |
| Namotni naponi WINDV [kV] | 110 / 110 | 110 / 110 |
| Nazivna snaga [MVA] | 150 | 150 |
| RATE [MVA] | 150 | 150 |
| u<sub>k</sub> [%] | 8,503 | 8,503 |
| Gubici u bakru [kW] | 318,8 | 318,8 |
| Gubici u željezu [kW] (MAG1 · S<sub>B</sub>) | 40,5 | 40,5 |
| Kut u modelu ANG1 [°] | **18** | **9** |
| Faktor F pri tom kutu *(izračunato)* | 0,3661 | 0,0925 |
| u<sub>k12</sub> pri tom kutu [%] *(izračunato)* | 3,11 | 0,79 |
| Raspon kuta prema Tablici 3 smjernica | ±30° | ±30° |
| Tablica korekcije / broj točaka / raspon | 1 / 32 / −30° … 30° | 1 / 32 / −30° … 30° |
| Broj položaja preklopke NTP1 | 33 | 33 |
| Granice u zapisu (RMA/RMI, VMA/VMI) | granice **kuta** −30° … 30°, pojas toka −150 … 150 MW | granice **kuta** −30° … 30°, pojas toka −150 … 150 MW |
| Regulacija (COD1 / regulirana sabirnica) | −3 (kut, isključena) / 80049 | −3 (kut, isključena) / 80050 |

### Tablica korekcije impedancije 1

u<sub>k12</sub> je izračunata efektivna impedancija para 1-2 na nazivnoj snazi para za faktor F.

| Točka | Kut [°] | F | u<sub>k12</sub> [%] | U modelu |
|---|---|---|---|---|
| 1 | −30,00 | 1,00000 | 8,50 |  |
| 2 | −28,12 | 0,88135 | 7,49 |  |
| 3 | −26,25 | 0,76970 | 6,54 |  |
| 4 | −24,38 | 0,66532 | 5,66 |  |
| 5 | −22,50 | 0,56810 | 4,83 |  |
| 6 | −20,62 | 0,47840 | 4,07 |  |
| 7 | −18,75 | 0,39612 | 3,37 |  |
| 8 | −16,88 | 0,32140 | 2,73 |  |
| 9 | −15,00 | 0,25433 | 2,16 |  |
| 10 | −13,12 | 0,19499 | 1,66 |  |
| 11 | −11,25 | 0,14342 | 1,22 |  |
| 12 | −9,38 | 0,09970 | 0,85 |  |
| 13 | −7,50 | 0,06386 | 0,54 |  |
| 14 | −5,63 | 0,03594 | 0,31 |  |
| 15 | −3,75 | 0,01598 | 0,14 |  |
| 16 | −1,88 | 0,00400 | 0,03 |  |
| 17 | 0,00 | 0,00010 | 0,00 |  |
| 18 | 1,88 | 0,00400 | 0,03 |  |
| 19 | 3,75 | 0,01600 | 0,14 |  |
| 20 | 5,63 | 0,03590 | 0,31 |  |
| 21 | 7,50 | 0,06390 | 0,54 |  |
| *—* | ***9*** | ***0,0925*** | *0,79* | **Gračac VP Licki Osik** *(interpolirano)* |
| 22 | 9,38 | 0,09970 | 0,85 |  |
| 23 | 11,25 | 0,14340 | 1,22 |  |
| 24 | 13,12 | 0,19500 | 1,66 |  |
| 25 | 15,00 | 0,25430 | 2,16 |  |
| 26 | 16,88 | 0,32140 | 2,73 |  |
| *—* | ***18*** | ***0,3661*** | *3,11* | **Gračac VP Velebit (izvan pogona)** *(interpolirano)* |
| 27 | 18,75 | 0,39610 | 3,37 |  |
| 28 | 20,62 | 0,47840 | 4,07 |  |
| 29 | 24,38 | 0,66530 | 5,66 |  |
| 30 | 26,25 | 0,76970 | 6,54 |  |
| 31 | 28,12 | 0,88140 | 7,49 |  |
| 32 | 30,00 | 1,00000 | 8,50 |  |


## Zapažanja

**Konjsko i Melina**

- Svih pet autotransformatora ima iste impedancije, istu tablicu (4) i iste granice (oko 367,7–416,7 kV).
- **Konjsko T3** razlikuje se od T1 i T2: namot 2 ima 230,999 kV umjesto 231 kV, a tercijar
  30 kV bez nazivnog napona umjesto 31,5/30 kV.
- **Zapis Melina T1 je nepotpun** u odnosu na T2: nazivni naponi svih namota su 0, RATE namota
  1 i 3 je 0, a tercijar je 30 kV umjesto 31,5 kV ([M4](../nedostaci-smjernica.md)).
- Granice u zapisu su naponi namota 400 kV, a ne kutovi (dijagonalna regulacija).
- Tablica ima 25 točaka, a zapis 33 položaja preklopke.

**Žerjavinec**

- Ista vrsta zapisa kao Konjsko i Melina (granice napona), ali uži naponski pojas (1,00–1,04 p.u.)
  i druga tablica (2); broj položaja (25) jednak je broju točaka tablice.

**Senj**

- Pravi kutni zapis: granice kuta i pojas toka.
- **Gornja granica kuta je 10,0°, a Tablica 3 smjernica navodi +10,54°.**
- **Donja granica −6,3° je izvan tablice korekcije**, koja počinje na −6,00°; za −6,3° vrijedi
  rubni faktor F = 1.

**Gračac**

- Dva dvonamotna PST-a prema sabirnici HGRACA51: VP Velebit **izvan pogona** (kut 18°) i
  VP Lički Osik u pogonu (kut 9°).
- Impedancija u nultom položaju praktički nestaje (F = 0,0001), a raste s kutom: pri 9° je
  u<sub>k</sub> = 0,79 %.
- Tablica ima 32 točke uz 33 položaja: nedostaje +22,5° (−22,5° postoji).
- Jedini PST-ovi s magnetiziranjem u zapisu (oko 40,5 kW gubitaka u željezu).
