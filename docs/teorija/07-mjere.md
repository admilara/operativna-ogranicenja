# 7. Prijedlog mjera (STUM)

Za svako preopterećenje smjernice traže prijedlog za njegovo otklanjanje. Alat mjere
**predlaže sam**, prema redoslijedu iz Slike 2 smjernica i provjerom na modelu. Do godine u kojoj
mjera počinje djelovati primjenjuje se operativno ograničenje (pogl. 5, §5.9).

## 7.1 Mjere i najranija godina djelovanja

| Mjera | Vrijeme izvedbe (od sklapanja UoP) | Najranija godina u modelu |
|---|---|---|
| Promjena kuta postojećih PST-ova | odmah, jednom po scenariju | 2029 |
| DTR — dinamičko određivanje termičkog kapaciteta | najmanje 3 godine | 2030 |
| HTLS — visokotemperaturni vodiči malog provjesa | najmanje 3 godine | 2030 |
| Uređaj za kontrolu tokova snaga (PST, serijska prigušnica …) | najmanje 5 godina | 2031 |
| Novi element mreže (vod, transformator) | u prosjeku do 10 godina | 2032 |
| Novi element vrlo visokog napona | u prosjeku do 15 godina | izvan razdoblja 2029.–2035. |

Za mjere na **prekograničnim elementima** potreban je dogovor sa susjednim operatorom; alat ih
predlaže uz oznaku "potreban dogovor sa susjednim OPS-om".

Predložena rješenja prihvatljiva su samo ako uklanjaju **sva** preopterećenja u osnovnom i svim
N-1 stanjima.

## 7.2 Redoslijed odlučivanja

Za svaki scenarij, nakon postavljanja kutova PST-ova (pogl. 2, §2.7), za svaki preopterećeni
element $k$:

### 1. DTR

Primjenjiv ako je element nadzemni vod poznatog vodiča, nije ograničen opremom u polju
(pogl. 4, §4.3) i ako je u **svakom** scenariju u kojem je preopterećen

$$\max_{c}\ I_{k,c} \le I_{DTR}(\text{vodič},\ T_{max,s}),$$

gdje je $I_{DTR}$ vrijednost iz Tablice 4 pri najvećoj vanjskoj temperaturi scenarija
$T_{max,s}$ (Tablica 1: A 25 °C, B 15 °C, C 35 °C, D 20 °C, E 40 °C, F 35 °C). Za 400 kV
vrijednost se udvostručuje (snop od dva vodiča).

Primjer, vod 110 kV 240/40 (RATE1 = 115 MVA = vrijednost pri 40 °C):

| Scenarij | $T_{max}$ | Dopušteno uz DTR | Dobitak prema RATE1 |
|---|---|---|---|
| B | 15 °C | 145 MVA | +26 % |
| A | 25 °C | 134 MVA | +17 % |
| C, F | 35 °C | 122 MVA | +6 % |
| E | 40 °C | 115 MVA | 0 % |

DTR dakle ne pomaže u scenariju E, a malo pomaže u C i F.

### 2. HTLS

Primjenjiv na nadzemni vod 110 kV ili 220 kV koji nije ograničen opremom u polju, ako je
opterećenje u svim stanjima ispod nazivne vrijednosti voda s HTLS vodičem pri najvećoj vanjskoj
temperaturi scenarija. Na 400 kV HTLS se ne predlaže.

> [!NOTE]
> **Smjernice ne daju nazivnu vrijednost HTLS vodiča** ([N3](../nedostaci-smjernica.md)).
> Prilog 4 daje samo cijenu zamjene po km za razrede postojećih vodova (110 kV 90 i 115 MVA,
> 220 kV 300 MVA) — to su nazivne vrijednosti **postojećih** vodiča, ne vodova nakon zamjene.
> Nazivne vrijednosti HTLS-a zato su izračunate iz kataloga proizvođača ACCC vodiča, kako je
> opisano niže.

#### Izbor vodiča

HTLS zamjena zadržava stupove, pa se bira ACCC vodič **istog promjera** kao postojeći Al/Fe vodič (katalog *ACCC Conductor: International Sizes*, CTC Global):

| Postojeći Al/Fe | Promjer | ACCC zamjena | Promjer | Masa ACCC | Napomena |
|---|---|---|---|---|---|
| 150/25 (110 kV) | 17,1 mm | ROVINJ | 17,10 mm | 574,8 kg/km | alternativa ZADAR (jača jezgra, oko 3 % manja opteretivost) |
| 240/40 (110 kV) | 21,9 mm | LISBON | 21,79 mm | 946,1 kg/km | katalog: "commonly replaces ACSR Hawk" (≈ 240/40) |
| 360/57 (220 kV) | 26,6 mm | STOCKHOLM 2L | 26,40 mm | 1394,6 kg/km | alternativa STOCKHOLM 3L (oko 1 % manja opteretivost) |

Promjeri i otpori Al/Fe vodiča su nazivne vrijednosti prema EN 50182 / DIN 48204; da su
međusobno usklađeni s Tablicom 4, potvrđuje kalibracija niže (odstupanje ispod 0,5 %). Masu
postojećeg vodiča i mehaničku provjeru treba potvrditi u projektu, kao i konačni izbor vodiča s
HOPS-om.

#### Zašto se vrijednosti iz kataloga ne mogu uzeti izravno

Katalog daje opteretivost pri 75, 180 i 200 °C na vodiču, uz **25 °C okoline, vjetar 0,61 m/s,
Sunce 1033 W/m², α = ε = 0,5** (IEEE 738-2006). Tablica 4 smjernica daje opteretivost Al/Fe
vodiča za okolinu 0–40 °C, ali **ne navodi uvjete** (vjetar, Sunce, najveću temperaturu vodiča).
Usporediv rezultat zato traži iste uvjete za oba vodiča.

#### Postupak

**1. Model toplinske ravnoteže** (IEEE 738, stacionarno stanje, vjetar okomit na vodič):

$$I = \sqrt{\frac{q_c(T_c, T_a, v) + q_r(T_c, T_a) - q_s}{R(T_c)}},$$

gdje je $q_c$ hlađenje konvekcijom (veće od prisilne i prirodne), $q_r$ zračenjem, $q_s = \alpha\,Q_s\,D$
zagrijavanje Suncem, a $R(T_c)$ otpor pri temperaturi vodiča (za ACCC linearno između kataloških
$R_{AC}$ pri 25 i 200 °C).

**2. Provjera prema katalogu.** Uz kataloške uvjete model reproducira katalog za svih šest
ispitanih ACCC vodiča na 75, 180 i 200 °C s odstupanjem **najviše 0,1 %**.

**3. Kalibracija na Tablicu 4.** Vjetar i Sunce prilagođeni su tako da model reproducira Tablicu 4
za sva četiri Al/Fe vodiča (150/25, 240/40, 360/57, 490/65) na svih devet temperatura okoline
(36 vrijednosti), za tri pretpostavke o najvišoj temperaturi Al/Fe vodiča:

| $T_{max}$ Al/Fe | Vjetar | Sunce | Odstupanje od Tablice 4 (RMS / najveće) |
|---|---|---|---|
| 80 °C | 0,48 m/s | 53 W/m² | 0,18 % / 0,50 % |
| 85 °C | 0,48 m/s | 586 W/m² | 0,33 % / 0,81 % |
| 90 °C | 0,48 m/s | 1113 W/m² | 0,65 % / 1,70 % |

Tablica 4 dakle odgovara vjetru od približno 0,5 m/s, ali se iz nje ne može jednoznačno odrediti
kombinacija najviše temperature vodiča i Sunca. Najbolje pristaje 80 °C bez znatnog Sunca.

**4. ACCC pri 180 °C** (trajna radna temperatura) uz kalibrirane uvjete. Za svaku temperaturu
okoline uzima se **najmanja** vrijednost preko triju kalibracija; razlika među njima je 2–3 %.

#### Rezultat (`config/htls_ratings.csv`)

**110 kV, 150/25 → ACCC ROVINJ**

| $T_a$ [°C] | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| Al/Fe 150/25, Tablica 4 [A] | 613 | 595 | 576 | 555 | 534 | 512 | 489 | 465 | 439 |
| **ACCC ROVINJ** [A] | **940** | **928** | **916** | **904** | **891** | **879** | **866** | **852** | **839** |
| ACCC ROVINJ [MVA] | 179,1 | 176,8 | 174,5 | 172,2 | 169,8 | 167,4 | 165,0 | 162,4 | 159,8 |

**110 kV, 240/40 → ACCC LISBON**

| $T_a$ [°C] | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| Al/Fe 240/40, Tablica 4 [A] | 843 | 817 | 791 | 764 | 735 | 705 | 673 | 640 | 605 |
| **ACCC LISBON** [A] | **1310** | **1294** | **1278** | **1261** | **1244** | **1226** | **1208** | **1190** | **1171** |
| ACCC LISBON [MVA] | 249,6 | 246,6 | 243,4 | 240,2 | 236,9 | 233,6 | 230,2 | 226,7 | 223,1 |

**220 kV, 360/57 → ACCC STOCKHOLM 2L**

| $T_a$ [°C] | 0 | 5 | 10 | 15 | 20 | 25 | 30 | 35 | 40 |
|---|---|---|---|---|---|---|---|---|---|
| Al/Fe 360/57, Tablica 4 [A] | 1084 | 1054 | 1020 | 985 | 948 | 910 | 869 | 826 | 780 |
| **ACCC STOCKHOLM 2L** [A] | **1683** | **1662** | **1641** | **1620** | **1598** | **1575** | **1553** | **1529** | **1505** |
| ACCC STOCKHOLM 2L [MVA] | 641,2 | 633,4 | 625,4 | 617,2 | 608,8 | 600,3 | 591,6 | 582,7 | 573,5 |

Zamjena povećava opteretivost za 1,5–1,9 puta, više pri višim temperaturama okoline jer ACCC
radi na 180 °C umjesto približno 80 °C. Prijenosna moć je $\sqrt3\,U_n I$, kao u Tablici 4.

> [!WARNING]
> - Vrijednosti su **termička** granica vodiča. Ako je vod ograničen opremom u polju (strujni
>   transformatori, rastavljači, VF prigušnice), mjerodavna je ta oprema — Prilog 4 cijenu HTLS-a
>   daje bez zamjene primarne opreme u vodnim poljima. Ograničenje opremom zadaje se u
>   `config/conductor_overrides.csv` (pogl. 4, §4.3).
> - Na 180 °C provjes ACCC vodiča je mali zbog kompozitne jezgre; provjera sigurnosnih visina
>   ipak je stvar projekta.
> - Otpor ACCC vodiča je manji od Al/Fe istog promjera; alat pri HTLS zamjeni zadržava parametre
>   voda iz modela (utjecaj na tokove je malen).

Tablicu se ponovno izračunava skriptom `scripts/htls_ratings.py`.

### 3. Uređaj za kontrolu tokova snaga

Ima smisla kad postoji paralelni put s rezervom. Alat ispituje serijsku reaktanciju $\Delta X$
dodanu elementu $k$: bisekcijom traži najmanji $\Delta X$ uz koji je $L_k \le 100\,\%$ u N i svim
N-1 stanjima, i provjerava da time nije preopterećen nijedan drugi element. Ako takav $\Delta X$
postoji, predlaže uređaj (serijska prigušnica ili PST) zadane reaktancije.

### 4. Novi element

Paralelni element jednakih parametara (drugi sustav voda ili paralelni transformator). Alat ga
dodaje u model i provjerava N i N-1. Ako ni to ne uklanja preopterećenje, element se označava za
ručnu obradu.

## 7.3 Interakcija mjera

Jedna mjera može rasteretiti više elemenata, a može i opteretiti druge. Alat zato mjere dodaje
**jednu po jednu** (najprije onu koja najranije djeluje i uklanja najviše preopterećenja), nakon
svake ponavlja N i N-1 i nastavlja dok preopterećenja ne nestanu. Rezultat je slijed mjera s
godinama djelovanja; model godine $y$ sadrži sve mjere s godinom djelovanja $\le y$.

## 7.4 Troškovi

Jedinične cijene su iz Priloga 4 smjernica (10G Plan 2025.–2034.) i spremljene su u
`config/unit_costs.csv`. Duljine vodova uzimaju se iz `.raw`-a (`psse_len_km`).

| Mjera | Stavka iz Priloga 4 | Cijena |
|---|---|---|
| DTR | SUMO + OTLM, neovisno o naponu | 8.500 €/km |
| HTLS | 110 kV, razred 90 MVA, jednostruki | 110.000 €/km |
| | 110 kV, razred 115 MVA, jednostruki | 140.000 €/km |
| | 110 kV, razred 115 MVA, dvostruki | 230.000 €/km |
| | 220 kV, razred 300 MVA, jednostruki | 210.000 €/km |
| Uređaj za kontrolu tokova | PST 220/110 kV, 150 MVA, ±9° (kosa regulacija) | 4.400.000 €/kom |
| | PST 110/110 kV, 150 MVA, ±30° | 5.750.000 €/kom |
| Novi vod | 400 kV jednostruki / dvostruki opremljen jednom / dvostruki (normalan – zahtjevniji teren) | 860.000 / 950.000 / 1.150.000–1.350.000 €/km |
| | 220 kV jednostruki / dvostruki | 530.000 / 790.000 €/km |
| | 110 kV jednostruki (normalan – zahtjevniji) | 265.000–330.000 €/km |
| | 110 kV dvostruki (normalan – zahtjevniji) | 450.000–560.000 €/km |
| | kabel 110 kV, Al 1000 mm² | 1.100.000 €/km |
| VN polje | AIS 400 / 220 / 110 kV | 2.000.000 / 1.530.000 / 950.000 € |
| | GIS 220 / 110 kV | 1.630.000 / 1.420.000 € |
| Novi transformator | 400/220 kV 400 MVA; 400/110 kV 300 MVA; 220/110 kV 150 MVA | 6.800.000; 6.000.000; 3.800.000 € |

Pravila sastavljanja troška:

- **novi vod** = duljina × cijena po km (normalan teren kao zadano) + **dva VN polja** (po jedno na
  svakom kraju, AIS kao zadano);
- **novi transformator** = cijena transformatora + **dva VN polja** (strana višeg i nižeg napona);
- **PST** = cijena PST-a + dva VN polja;
- **DTR, HTLS** = duljina × cijena po km, bez polja (Prilog 4: bez zamjene stupova i primarne
  opreme);
- 400 kV HTLS i vodovi kojima razred ne odgovara nijednoj stavci dobivaju oznaku "cijena nije
  definirana" i trošak se ne zbraja automatski.

Pretpostavke (teren, AIS/GIS) mijenjaju se po mjeri u izlaznoj tablici prije izrade Tablice 8.

## 7.5 Dva skupa STUM-a

Smjernice traže STUM odvojeno za:

1. korisnike sa zahtjevom za EOTRP iz 2024., 2025. i 2026. godine zajedno,
2. samo korisnike sa zahtjevom iz 2026. godine.

Alat postupak provodi dvaput. Za drugi skup korisnici iz 2024. i 2025. ostaju u modelu, a "novi
korisnici" su samo oni s Owner 4 = 2026.
