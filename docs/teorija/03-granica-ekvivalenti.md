# 3. Granica sustava i ekvivalenti

## 3.1 Problem

Isporučeni modeli sadrže **samo hrvatski podsustav**. Prekogranični vodovi završavaju u
X-čvorištima, a mreža susjednih sustava (BA, SI, HU, RS, ME) modelirana je kao konstantna PQ injekcija. 
Takav način ekvivalentiranja je okej za jednostavne tokove snaga, ali kada se u priču ubace N-1 i
proračuni operativnih ograničenja, imamo neke manjkavosti. U ovom dijelu istražujemo na koji 
način se vanjski sustavi mogu modelirati (bar u pandapoweru) da služe svrsi u svim ovim slučajevima i 
što zapravo ovakav način modeliranja znači za konačne rezultate.

Trenutno stanje: **razmjene na X-čvorištima zadaju se kao stalne PQ injekcije** iz spremljenog
rješenja (v. §1.6). O

## 3.2 Stalne PQ injekcije na X-čvorištima

### Što je dobro

U osnovnom stanju scenarija model je točan: tokovi na svim prekograničnim vodovima su upravo
oni iz dostavljenog modela, što odgovara razmjenama po vodovima koji su naveni u tablici u Smjernicama.

### Što je manje dobro

Stalna injekcija znači da je **vanjska mreža za promjene tokova beskonačna impedancija**: kad
se unutar Hrvatske nešto promijeni, preraspodjela toka može ići samo unutarnjim putovima. U
stvarnosti dio preraspodjele ide kroz susjedne sustave (kružni tokovi).

| Slučaj | Pogreška | Odluka |
|---|---|---|
| Ispad prekograničnog voda | X-čvorište ostaje otok; cijela razmjena tog voda (npr. ~1000 MW na 400 kV) seli se na referentni čvor | **prekogranični vodovi isključeni su iz N-1** |
| Ispad unutarnjeg elementa daleko od granice | malena | — |
| Ispad unutarnjeg elementa blizu granice | preraspodjela samo unutarnjim putovima precjenjuje opterećenje unutarnjih paralelnih putova i podcjenjuje promjenu na prekograničnim vodovima | **zadržava se u N-1, uz zastavice (§3.3)** |
| Promjena proizvodnje unutar HR (isključenje korisnika, ograničenje) | razmjene se ne mijenjaju; neravnoteža ide na odabrani način uravnoteženja | tri varijante (pogl. 6) |

## 3.3 Ispadi blizu granice

Za svaki N-1 slučaj računaju se sljedeći pokazatelji i flaggaju se u slučaju prekoračenja. 
Pokazatelji su heuristički - ako je nešto flagagno, ne znači da je nešto nužno krivo, nego bi ga trebalo pregledati.

| Oznaka | Pokazatelj | Zadana granica | Zašto |
|--------|------------|----------------|-------|
| G1 | Hrvatska strana prekograničnog voda nakon ispada ostaje povezana s ostatkom mreže samo jednim putem | — | sav tok preko tog voda mora proći jednim unutarnjim putem; u stvarnosti bi se dio razmjene preusmjerio na druge prekogranične vodove |
| G2 | Kutna razlika na krajevima ispalog elementa u stanju nakon ispada, $\lvert \theta_i - \theta_j \rvert$ | 20° | velika razlika znači da je unutarnji zaobilazni put "dugačak" (velika impedancija); kroz susjedne sustave postoji kraći put koji model nema |
| G3 | Porast opterećenja nekog elementa unutar dva čvorišta od X-čvorišta | +20 postotnih bodova | izravan znak preraspodjele uz granicu |
| G4 | Ispad odvaja dio mreže (otok) | — | izgubljena proizvodnja/potrošnja otoka ide na uravnoteženje (mijenjaju se tokovi) |

Kad postane dostupan ekvivalent (§3.4–3.6), označene slučajeve moguće je izravno usporediti s točnijim modelom i provjeriti koliko je
heuristika dobra.

## 3.4 Mrežni ekvivalenti — zajednička osnova

Sabirnice kategoriziramo kao unutarnje ($I$, Hrvatska), granične ($B$, X-čvorišta ili
hrvatske sabirnice prekograničnih vodova) i vanjske ($E$, susjedni sustavi).

Ekvivalent vanjske mreže bi trebao mijenjati cijelu vanjsku mrežu manjim modelom koji bi, gledano na granici, 
davao isto rješenje u osnovnom stanju i približno isti odziv na promjene. Sva tri prijedloga ekvivalenta niže 
**zahtijevaju model vanjske mreže** — iz ovako reduciranog modela hrvatske mreže ne mogu se napraviti.

## 3.5 Wardov i prošireni Wardov ekvivalent

Wardov ekvivalent zamijenjuje vanjski sustav (dakle sve susjedne države) puno manjom mrežom. 
Što želimo od Wardovih ekvivalenata u našem slučaju?
- Preciznu 'reprezentaciju' za napone i tokove snaga u svakom X-čvorištu 
- Približnu točnost u slučajevima kada se uvjeti u sustavu mijenjaju (npr. ispad, redispečing) - ekvivalent bi se trebao 
odazvati približno isto kao i full vanjski model

Prvu točku je relativno jednostavno modelirati Ward ekvivalentom. Druga točka je ono što 
nam radi razliku i zbog čega promatramo nekoliko varijacija na temu - Ward, prošireni Ward i REI.

### Wardov ekvivalent

Kako smo rekli, sabirnice se razdvajaju u tri kategorije - unutarnje ($I$), granične ($B$) i vanjske ($E$).
Linearne jednadžbe vanjskog dijela (vrijede i za ostale metode) :

$$
\begin{bmatrix}\mathbf{I}_B\\ \mathbf{I}_E\end{bmatrix} =
\begin{bmatrix}\mathbf{Y}_{BB} & \mathbf{Y}_{BE}\\ \mathbf{Y}_{EB} & \mathbf{Y}_{EE}\end{bmatrix}
\begin{bmatrix}\mathbf{U}_B\\ \mathbf{U}_E\end{bmatrix}.
$$

gdje je $\mathbf{I}$ vektor injektiranih struja, a $\mathbf{U}$ vektor napona na sabirnicama.
Jednadžbe se rješavaju za dobiti napon vanjskih sabirnica $\mathbf{U}_{E}$.

$$
\mathbf{U}_(E} = \mathbf{Y}_{EE}^{-1}(\mathbf{I}_{E}-\mathbf{Y}_{EB}\mathbf{U}_{B}
$$

Supstituiramo taj izraz u prvu linearnu jednadžbu:

$$
(\mathbf{Y}_{BB}-\mathbf{Y}_{BE}\mathbf{Y}_{EE}^{-1}\mathbf{Y}-{EB})\mathbf{U}_{B} = \mathbf{I}-\mathbf{Y}_{BE}\mathbf{Y}_{EE}^{-1}\mathbf{I}_{E}
$$

Vanjske sabirnice uklanjaju se Gaussovom eliminacijom (Kronova redukcija):

$$\mathbf{Y}_{eq} = \mathbf{Y}_{BB} - \mathbf{Y}_{BE}\,\mathbf{Y}_{EE}^{-1}\,\mathbf{Y}_{EB},$$

$$\mathbf{I}_{B,eq} = -\mathbf{Y}_{BE}\,\mathbf{Y}_{EE}^{-1}\,\mathbf{I}_E,\qquad
\mathbf{I}_E = \left(\frac{\mathbf{S}_E}{\mathbf{U}_E}\right)^{*}\ \text{(osnovno stanje)}.$$

Rezultat na granici:

- **ekvivalentne grane između svakog para graničnih sabirnica** — $\mathbf{Y}_{eq}$ je puna
  matrica. To je najvažniji dio: izvandijagonalni članovi opisuju paralelne putove *kroz*
  susjedne sustave, koji preuzimaju dio toka kad unutar Hrvatske ispadne element;
- **poprečne admitancije** na graničnim sabirnicama (dijagonala);
- **injekcije** na graničnim sabirnicama, $\mathbf{S}_{B,eq} = \mathbf{U}_B\,\mathbf{I}_{B,eq}^{*}$,
  koje u osnovnom stanju točno reproduciraju razmjene.

Slabost: vanjski generatori i tereti postaju stalne struje (odnosno stalne snage na granici).
Vanjski sustav nema regulaciju napona ni jalovu rezervu, a točnost opada s udaljenošću od
osnovnog stanja.

### Prošireni Wardov ekvivalent (xWard)

Na svaku graničnu sabirnicu dodaje se fiktivni PV generator iza impedancije. Generator daje
jalovu snagu kojom vanjski sustav podupire napon na granici. Djelatni dio ostaje kao kod
Wardova ekvivalenta. U pandapoweru: element `xward`.

> [!NOTE]
> **Théveninova impedancija po X-čvorištu nije Wardov ekvivalent.** Impedancije iz proračuna
> kratkog spoja (kao u NEPLAN-u za EVP Novska) daju samo dijagonalu matrice
> $\mathbf{Z}_{eq} = \mathbf{Y}_{eq}^{-1}$ — svako X-čvorište zasebno prema "krutoj mreži".
> Izvandijagonalni članovi, koji opisuju prijenos između X-čvorišta kroz susjedne sustave,
> tada nedostaju. Za preraspodjelu tokova nakon ispada upravo su oni bitni.

## 3.6 REI ekvivalent (Dimo)

### Ideja

REI (*Radial, Equivalent and Independent*, P. Dimo, 1975.) prije eliminacije **grupira aktivne
vanjske injekcije** (npr. sve generatore jednog susjednog sustava) u jedan fiktivni čvor, tako
da te injekcije prežive eliminaciju kao **stvarni PV generator**, a ne kao stalna struja.
Zato REI bolje opisuje odziv vanjskog sustava na promjene — djelatnu (generator može
preuzimati neravnotežu) i jalovu (regulira napon).

### Konstrukcija

Neka je $G$ skupina vanjskih sabirnica s injekcijama koje se grupiraju, s naponima $U_i$ i
injekcijama $S_i$ iz riješenog osnovnog stanja.

**1. Zbirne veličine.** Za $i \in G$:

$$I_i = \left(\frac{S_i}{U_i}\right)^{*},\qquad
S_R = \sum_{i\in G} S_i,\qquad I_R = \sum_{i\in G} I_i,\qquad U_R = \frac{S_R}{I_R^{*}}.$$

$U_R$ je napon novog čvora R koji u osnovnom stanju točno predaje snagu $S_R$ strujom $I_R$.

**2. Mreža nulte bilance snage (ZPBN, *zero power balance network*).** Dodaju se čvor 0 s
naponom $U_0 = 0$ i čvor R s naponom $U_R$, te grane:

$$y_{i0} = -\frac{S_i^{*}}{|U_i|^2}\quad (i \in G),\qquad
y_{0R} = \frac{S_R^{*}}{|U_R|^2}.$$

Provjera: struja grane od $i$ prema 0 je $U_i\,y_{i0} = -S_i^{*}/U_i^{*} = -I_i$, tj. grana u
sabirnicu $i$ utiskuje upravo $I_i$ — zamjenjuje izvornu injekciju. U čvor 0 utječe
$\sum(-I_i) = -I_R$, a granom 0–R teče $(U_0 - U_R)\,y_{0R} = -I_R$ — Kirchhoffov zakon u čvoru 0
je zadovoljen. Snaga koju ZPBN troši:

$$\sum_{i\in G} U_i (-I_i)^{*} - U_R(-I_R)^{*} = -\sum_i S_i + S_R = 0,$$

otuda naziv: ZPBN u osnovnom stanju ne troši ni ne predaje snagu.

**3. Zamjena injekcija.** Izvorne injekcije u $G$ se uklanjaju; u čvor R postavlja se generator
$P_R = \mathrm{Re}\,S_R$ s naponom $|U_R|$ i zbrojenim granicama jalove snage. Sabirnice iz $G$
sada su pasivne.

**4. Eliminacija.** Čvor 0 i sve pasivne vanjske sabirnice uklanjaju se Kronovom redukcijom
(§3.5). Ostaju granične sabirnice, čvor R (ili više njih) i ekvivalentne grane između njih.

### Svojstva

- **Točan u osnovnom stanju**, po konstrukciji.
- **Izvan osnovnog stanja**: promjena snage generatora R raspodjeljuje se na izvorne jedinice
  u omjeru admitancija ZPBN-a, dakle približno razmjerno njihovim strujama u osnovnom stanju.
  To je implicitni GSK (*generation shift key*) razmjeran proizvodnji — isti princip koji
  ENTSO-E koristi za proračun prijenosnih kapaciteta.
- **Izbor skupina** određuje točnost: grupiranje po sustavu (jedan R po susjedu) daje prirodnu
  vezu s razmjenama po granicama; grupiranje po električnoj blizini (koherentnosti) daje veću
  točnost za ispade blizu granice; tereti se obično grupiraju odvojeno od generatora.

| | Ward | xWard | REI |
|---|---|---|---|
| Paralelni putovi kroz susjede | da | da | da |
| Jalova potpora napona na granici | ne | da (fiktivni PV po graničnoj sabirnici) | da (stvarni zbirni generatori) |
| Djelatni odziv vanjskih generatora | ne | ne | da (preko R čvorova) |
| Točnost za velike promjene | najmanja | srednja | najveća |
| Broj fiktivnih elemenata | grane između svih graničnih sabirnica | + PV po sabirnici | + R čvorovi i njihove grane |

## 3.7 Uporaba REI ekvivalenta u ovom alatu (buduće)

Preduvjet je model susjednih sustava za isti scenarij i godinu — npr. ENTSO-E zajednički mrežni
model (CGM/IGM, CGMES format, koji pandapower uvozi) ili regionalni PSS/E model. pandapower ima
gotovu funkciju:

```python
from pandapower.grid_equivalents import get_equivalent
net_eq = get_equivalent(net, "rei", boundary_buses, internal_buses)
```

Što bi se time dobilo:

1. **Ispadi prekograničnih vodova** postaju valjani N-1 slučajevi.
2. **Ispadi blizu granice** dobivaju ispravnu preraspodjelu kroz susjedne sustave. Zastavice
   G1–G3 mogu se umjesto heuristike zamijeniti stvarnom razlikom između modela sa stalnim
   injekcijama i REI modela.
3. **Varijanta uravnoteženja V3** (prekogranično, pogl. 6) dobiva fizikalnu podlogu: umjesto
   proizvoljne raspodjele po X-čvorištima, neravnotežu preuzimaju R generatori susjednih sustava
   s GSK-om iz ZPBN-a.
4. **Naponi na granici**: vanjski sustav podupire napon jalovom snagom.

Ograničenja koja treba imati na umu:

- Ekvivalentnih grana ima puno (do $n_B(n_B-1)/2$; za 35 graničnih sabirnica 595). Obično se
  zanemaruju one s vrlo malom admitancijom.
- Fiktivne grane **ne smiju ući u N-1 ni u nadzor opterećenja** — nemaju fizikalnu nazivnu
  vrijednost, a mogu imati i negativne parametre.
- Ekvivalent vrijedi za stanje iz kojeg je izrađen: **za svaki scenarij i godinu (42 modela)
  izrađuje se zasebno**.
- Granice jalove i djelatne snage R generatora su zbroj granica izvornih jedinica — za velike
  promjene to je optimističnije od stvarnosti.
