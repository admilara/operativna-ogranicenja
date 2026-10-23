# 4. N-1 i opterećenje elemenata

## 4.1 Popis ispada

Smjernice traže N-1 analizu "za sve utjecajne okolne elemente". Alat ne bira utjecajne
elemente nego **ispituje sve**:

| Uključeno | Isključeno |
|---|---|
| svi unutarnji vodovi u pogonu (110, 220, 400 kV) | prekogranični vodovi (do X-čvorišta) — v. pogl. 3, §3.2 |
| svi dvonamotni transformatori u pogonu | elementi izvan pogona u modelu te godine |
| svi tronamotni transformatori u pogonu — ispada **cijela jedinica** | |

Za model A-2029 to je 409 vodova, 1 dvonamotni i 39 tronamotnih transformatora, ukupno
**449 ispada**. Od toga 85 vodova su radijalni (njihov ispad odvaja sabirnicu ili postrojenje);
ti slučajevi dobivaju zastavicu G4, a izgubljena proizvodnja ili potrošnja otoka preuzima se
odabranom varijantom uravnoteženja (pogl. 6).

**Nadzire se** opterećenje svih vodova i transformatora u pogonu, uključujući prekogranične
vodove (njihov tok se može mijenjati i bez ispada, kad se mijenja razmjena u varijanti V3).

## 4.2 Definicija opterećenja

U `.raw`-u su nazivne vrijednosti (RATE1) zadane u MVA i za vodove i za transformatore. Kod
transformatora je RATE1 jednak nazivnoj snazi (SBASE para namota) u 51 od 52 slučaja, pa izbor
"RATE1 ili nazivna snaga" ne mijenja broj. Mijenja ga **mjera opterećenja**: struja ili prividna
snaga. Razlikuju se kad napon nije 1 p.u. — pri 0,95 p.u. opterećenje izraženo snagom je za 5 %
manje od opterećenja izraženog strujom.

### Vodovi — strujno opterećenje

$$I_n = \frac{\mathrm{RATE1}}{\sqrt{3}\,U_n},\qquad
L_k = 100\,\frac{\max(I_{od}, I_{do})}{I_n}\ [\%].$$

Obrazloženje: granica vodiča je termička, dakle **struja**; Tablica 4 smjernica daje dopuštenu
struju u A (MVA vrijednosti u njoj su $\sqrt3\,U_n I$), a Tablice 5 i 6 traže I (A) i %In.

### Transformatori — prividna snaga po namotu

$$L_k = 100\,\max_w \frac{S_w}{\mathrm{RATE1}_w}\ [\%],$$

gdje $w$ ide po namotima (dva ili tri), a $S_w$ je prividna snaga na priključku namota $w$.

| Slučaj | Postupak |
|---|---|
| RATE1 namota = 0 (tercijari Melina T1, Velebit T3/T4, Sisak T1) | namot se ne nadzire |
| RATE1 namota 1 = 0 (Melina T1) | uzima se SBASE para namota (400 MVA) uz zastavicu |

> [!NOTE]
> Vjerujem da je ovo i zadana konvencija PSS/E-a (vodovi: struja izražena kao MVA;
> transformatori: MVA), ali to treba potvrditi prema načinu na koji HOPS ispisuje
> rezultate. Alat računa obje mjere i u nalazima navodi elemente kod kojih se razlikuju za više
> od 3 postotna boda.

pandapower `res_trafo3w.loading_percent` računa se prema nazivnoj snazi `sn_*`, a ne prema
RATE1, pa ga alat ne koristi — opterećenje se računa iz tokova i spremljenih RATE1 vrijednosti.

## 4.3 Tipovi vodiča iz RATE1

`.raw` ne sadrži tip vodiča, a on je potreban za DTR i HTLS (pogl. 7). RATE1 vrijednosti se
podudaraju sa **stupcem 40 °C Tablice 4** smjernica — RATE1 je dakle statička ljetna nazivna
vrijednost:

| Napon | RATE1 [MVA] | Tablica 4, 40 °C | Vodič | Broj zapisa (A-2029, i izvan pogona) |
|---|---|---|---|---|
| 110 kV | 115 | 115 | Al/Fe 240/40 | 185 |
| 110 kV | 84 | 84 | Al/Fe 150/25 | 41 |
| 220 kV | 297 | 297 | Al/Fe 360/57 | 22 |
| 400 kV | 1316–1330 | 2 × 658 = 1316 | 2 × Al/Fe 490/65 (snop) | 83 |

Pravilo prepoznavanja: RATE1 unutar ±2 % vrijednosti iz stupca 40 °C za tu naponsku razinu
(400 kV: dvostruka vrijednost, snop od dva vodiča). Ostali vodovi (npr. 110 kV s 123, 160,
141, 120, 90 MVA; 220 kV s 366, 461 MVA) dobivaju tip **"nepoznato"** — to mogu biti kabeli,
drugi presjeci ili vodovi ograničeni opremom u polju.

### Nadjačavanje

Datoteka `config/conductor_overrides.csv` ima prednost pred prepoznavanjem:

```
from_bus,to_bus,ckt,conductor,limited_by,note
60079,60133,1,240/40,line,
60072,60130,1,,terminal_equipment,strujni transformatori 600 A
```

| Polje | Vrijednosti |
|---|---|
| `conductor` | `150/25`, `240/40`, `360/57`, `490/65`, `490/65x2`, `cable`, ili prazno |
| `limited_by` | `line` (vodič) ili `terminal_equipment` (oprema u polju) |

Ako je vod ograničen opremom u polju, DTR i HTLS ga **ne mogu** rasteretiti i alat ih za
taj vod ne predlaže.

## 4.4 Preopterećenje

Element je preopterećen kad je $L_k > 100\,\%$. Višak prijenosa, koji ulazi u proračun
ograničenja (pogl. 5):

$$E_k = \frac{L_k - 100}{100}\,\mathrm{RATE1}_k\ [\mathrm{MVA}].$$

Za svaki par (element $k$, ispad $c$) pamte se $P$, $Q$, $S$, $I$ i $L$ u stanju N i stanju N-1
— to su upravo stupci Tablice 7 smjernica.
