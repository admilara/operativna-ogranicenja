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
Pokazatelji su heuristički - ako je nešto flaggano, ne znači da je nešto nužno krivo, nego bi ga trebalo pregledati.

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

Kako smo rekli, sabirnice se razdvajaju u tri kategorije - unutarnje $I$, granične $B$ i vanjske $E$.
Linearne jednadžbe vanjskog dijela (vrijede i za ostale metode) :

$$
\begin{bmatrix}\mathbf{I}_B\\ \mathbf{I}_E\end{bmatrix} =
\begin{bmatrix}\mathbf{Y}_{BB} & \mathbf{Y}_{BE}\\ \mathbf{Y}_{EB} & \mathbf{Y}_{EE}\end{bmatrix}
\begin{bmatrix}\mathbf{U}_B\\ \mathbf{U}_E\end{bmatrix}.
$$

gdje je $\mathbf{I}$ vektor injektiranih struja, a $\mathbf{U}$ vektor napona na sabirnicama.
Jednadžbe se rješavaju za dobiti napon vanjskih sabirnica $\mathbf{U}_{E}$.

$$
\mathbf{U}_{E} = \mathbf{Y}_{EE}^{-1}\left(\mathbf{I}_{E}-\mathbf{Y}_{EB}\mathbf{U}_{B}\right)
$$

Supstituiramo taj izraz u prvu linearnu jednadžbu:

$$
\left(\mathbf{Y}_{BB}-\mathbf{Y}_{BE}\mathbf{Y}_{EE}^{-1}\mathbf{Y}_{EB}\right)\mathbf{U}_{B} = \mathbf{I}-\mathbf{Y}_{BE}\mathbf{Y}_{EE}^{-1}\mathbf{I}_{E}
$$

Vanjske sabirnice uklanjaju se Gaussovom eliminacijom $E$ čvorišta (Kronova redukcija):

$$\mathbf{Y}_{eq} = \mathbf{Y}_{BB} - \mathbf{Y}_{BE}\,\mathbf{Y}_{EE}^{-1}\,\mathbf{Y}_{EB},$$

- $\mathbf{Y}_{eq}$ se naziva još i Schurov komplement od $\mathbf{Y}_{EE}$. 

$$\mathbf{I}_{B,eq} = -\mathbf{Y}_{BE}\,\mathbf{Y}_{EE}^{-1}\,\mathbf{I}_E,\qquad
\mathbf{I}_E = \left(\frac{\mathbf{S}_E}{\mathbf{U}_E}\right)^{*}\ \text{(osnovno stanje)}.$$

Rezultat na granici:

- **ekvivalentne grane između svakog para graničnih sabirnica** — $\mathbf{Y}_{eq}$ je puna
  matrica. To je najvažniji dio: vandijagonalni članovi opisuju paralelne putove *kroz*
  susjedne sustave, između sabirnica $i$ i $j$, koji preuzimaju dio toka kad unutar Hrvatske dođe do ispada;
- **poprečne admitancije** na graničnim sabirnicama (dijagonala);
- **injekcije** na graničnim sabirnicama, $\mathbf{S}_{B,eq} = \mathbf{U}_B\,\mathbf{I}_{B,eq}^{*}$,
  koje u osnovnom stanju točno reproduciraju razmjene;
- matrica može biti nesimetrična ukoliko vanjski sustav sadrži phase shiftere.

Minusi Wardovog ekvivalenta: vanjski generatori i tereti su stalne injekcije struje (tj. stalne snage na granici).
Vanjski sustav nema regulaciju napona ni rezerve jalove snage, a točnost opada s udaljenošću od
osnovnog stanja.

### Fizikalno značenje ekvivalentnih grana
 
Vandijagonalni član nakon eliminacije je
 
$$Y_{eq,ij}=Y_{BB,ij}-\sum_{k,l\in E}Y_{BE,ik}\,\big(\mathbf Y_{EE}^{-1}\big)_{kl}\,Y_{EB,lj}.$$
 
To je **prijenosna admitancija**: koliko struje se pojavi u sabirnici $i$ po voltu narinutom
na sabirnicu $j$, kroz sve vanjske putove, uključujući i putove preko poprečnih elemenata prema
zemlji. Prikaz te veličine kao grane $y_{ij}=-Y_{eq,ij}$ standardni je π-prikaz — 
**ekvivalentna grana nije vodič**. Svaki fizički element vanjske mreže ima
$\mathrm{Re}\,z\ge 0$, ali $Y_{eq,ij}$ je **omjer umnožaka** tih elemenata, a umnošci i
kvocijenti kompleksnih brojeva različitih kutova mogu završiti u bilo kojem kvadrantu - tako da ta
vrijednost može biti **pozitivna ili negativna**. Najjednostavniji primjer je pretvorba zvijezde u trokut. 


**Ukupni gubici ostaju točni.** Kronova redukcija čuva ponašanje vanjske mreže gledano s
rubnih čvorišta: za iste napone dobivaju se iste struje kao u izvornoj pasivnoj
mreži, pa je ukupna snaga koju ekvivalent troši za bilo koje napone jednaka izvornoj i $\ge 0$.
Umjetna je samo podjela na grane i poprečne elemente — grana s negativnim R uvijek je
kompenzirana susjednim granama i poprečnim elementima. Zato gubici na pojedinom fiktivnom
elementu nemaju značenje, što je, uz nepostojanje nazivne vrijednosti, još jedan razlog da
fiktivni elementi ne ulaze u N-1 ni u nadzor opterećenja.
 
> [!NOTE]
> **Koliko je to često?** U Wardovu ekvivalentu poprečni elementi s negativnom vodljivošću su
> uobičajeni, osobito u admitancijskom obliku (generatori pretvoreni u admitancije
> $y = S^*/\lvert U\rvert^2$ imaju negativnu vodljivost). Grane s negativnim R ili kapacitivnim X
> moguće su, ali nisu tipičan ishod.


### **Što se događa s generatorima i teretima?**
Kronova redukcija točna je samo za potpuno linearne sustave. Tereti i generatori su
nelinearni elementi i oni injektiraju stalnu snagu, a ne stalnu struju. Ideja Wardovog 
ekvivalenta je da se koristi na **rješenom baznom slučaju** tako da se svaka vanjska injekcija
može pretvoriti u rubni uvjet. Dva načina na koji se to postiže su:

| Varijanta | Vanjska injekcija | Što se dogodi? |
|---|---|---|
| Wardova injekcija | konstantna struja (iz base-case napona) | ekvivalentne injekcije snage u rubnim čvorištima |
| Wardova admitancija | konstantna admitancija | 'apsorbira' se u $\mathbf{Y}_{EE}$ tako da je $\mathbf{I}_{E} = 0$. Ostaju ekvivalentni shuntovi na rubovima. |

Razlika je u odzivu na promjenu u unutarnjem sustavu. 
- Wardova injekcija - vanjski sustav je konstantna injekcija. S obzirom da iznos ovisi o naponu u rubnom
čvorištu, u slučaju ispada nekog elementa mijenjaju se **kutovi i naponi graničnih čvorišta**, a time onda
i tokovi po ekvivalentnim granama. Bilanca djelatne snage u graničnoj sabirnici $i$ je:

$$P_{pv,i}=P_{inj,i}-P_{lok,i}-P_{sh,i}(U_i)-\sum_j P_{ij},\qquad
P_{ij}\approx\frac{\theta_i-\theta_j}{x_{ij}},$$

gdje su: 
- $P_{pv,i}$ tok prekograničnim vodom prema unutarnjoj mreži, 
- $P_{inj,i}$ Wardova injekcija, 
- $P_{lok,i}$ teret ili proizvodnja priključeni na samu sabirnicu, a 
- $P_{sh,i}$ snaga ekvivalentnog poprečnog elementa.

Dakle, **Wardova injekcija je stalna**, a **kutovi $\theta_i$, $\theta_j$ i iznos napona $U_i$ se mijenjaju, 
što mijenja i tokove. Kod stalnih PQ injekcija na X-čvorištima, rubno čvorište ima samo impedanciju tog prekograničnog voda
i injekciju, što ne dopušta da se tokovi mijenjaju. 

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
