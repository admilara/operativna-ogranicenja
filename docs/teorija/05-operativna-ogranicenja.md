# 5. Operativna ograničenja

## 5.1 Pojam

**Operativno ograničenje** je smanjenje izlazne snage novog proizvodnog postrojenja koje operator
prijenosnog sustava primjenjuje u fazi planiranja ili vođenja kako bi mreža ostala unutar
dopuštenih opterećenja u osnovnom stanju i u svakom N-1 stanju. Primjenjuje se **do izgradnje
mjera** (stvaranja tehničkih uvjeta u mreži, STUM) potrebnih da se svi novi korisnici priključe
bez ograničenja.

Smjernice (§3.1.1) iznos ograničenja u EOTRP-u definiraju kao **isključivo indikativan,
neobvezujući podatak**: u stvarnom vođenju sustava iznos i trajanje ograničenja mogu biti veći.

Ograničenje se iskazuje na dva načina:

| Veličina | Jedinica | Razina |
|---|---|---|
| $\Delta P_{max,i,s}$ — smanjenje snage korisnika $i$ kojim se uklanjaju sva preopterećenja u N i svim N-1 stanjima scenarija $s$ | MW | korisnik × scenarij × godina |
| $E_{oo,god}$ — energija koja neće biti predana zbog ograničenja u godini | MWh | korisnik × godina |
| $E_{oo,raz}$ — isto za cijelo razdoblje 2029.–2035. | MWh | korisnik |

Ograničenje je **preventivno**: jedno smanjenje snage mora vrijediti u osnovnom stanju i u svim
N-1 stanjima istodobno, jer se ne zna unaprijed koji će ispad nastupiti.

## 5.2 Tko je novi korisnik

Polja vlasnika proizvodnih jedinica (Tablica 2 smjernica):

| Polje | Značenje | Primjer |
|---|---|---|
| Owner 1 | tip jedinice (ENTSO-E): 33 sunčana, 31 vjetroelektrana na kopnu, 44 baterija, 45 vodik, 27/28 akumulacijska/reverzibilna HE … | 33 |
| Owner 2 | planirana godina priključenja | 2027 |
| Owner 3 | redni broj projekta iz Priloga 1–3 | 12 |
| Owner 4 | godina zahtjeva za izradu EOTRP-a: 2024, 2025 ili 2026 | 2024 |

**Novi korisnici** su jedinice s Owner 4 ∈ {2024, 2025, 2026}. U modelu A-2029 to je 88 jedinica,
od kojih je 64 u pogonu. Proračun se provodi **po projektu (Owner 3)**, ne po jedinici: hibridna
postrojenja (SE + BS) imaju više jedinica s istim rednim brojem, a "isključenje korisnika" znači
isključenje svih njegovih jedinica.

Iste oznake određuju i topologiju po godinama: u modelu godine $y$ u pogonu su jedinice s
Owner 2 ≤ $y$ (u modelu A-2029 provjereno: nijedna jedinica s Owner 2 > 2029 nije u pogonu).

## 5.3 Postupak prema smjernicama

Za svaki scenarij $s$ i godinu $y$:

1. **Osnovno stanje** sa svim novim korisnicima: tokovi snaga u N stanju i u svim N-1 stanjima.
   Popis preopterećenih parova $(k, c)$ — element $k$ preopterećen u stanju $c$ ($c = 0$ je
   osnovno stanje).
2. **Doprinos korisnika**: za svaki preopterećeni par i svakog novog korisnika $i$ ponoviti
   proračun s isključenim korisnikom $i$ (§5.4).
3. **Raspodjela ograničenja** formulom [1] iterativno, dok sva preopterećenja ne nestanu (§5.6).
4. **Prijedlog mjere** za svako preopterećenje i godina od koje mjera djeluje (pogl. 7).
5. **Energija ograničenja** po godinama do izgradnje svih mjera (§5.10).

Prije koraka 1 kutovi PST-ova postavljaju se jednom za scenarij (pogl. 2, §2.7).

## 5.4 Doprinos korisnika

Oznake za par (element $k$, stanje $c$):

- $L_{k,c}^{(0)}$ — postotno opterećenje elementa $k$ u stanju $c$ sa svim novim korisnicima (stanje 0),
- $L_{k,c}^{(1,i)}$ — isto, uz isključenog korisnika $i$ (stanje 1),
- $\mathrm{RATE}_k$ — termička snaga elementa [MVA].

**Doprinos** korisnika $i$:

$$C_{k,c,i} = \frac{L_{k,c}^{(1,i)} - L_{k,c}^{(0)}}{100}\,\mathrm{RATE}_k\quad [\mathrm{MVA}].$$

| Predznak | Značenje | Postupak prema smjernicama |
|---|---|---|
| $C_{k,c,i} < 0$ | isključenje korisnika smanjuje opterećenje — korisnik **pridonosi** preopterećenju | sudjeluje u otklanjanju, ograničava mu se snaga formulom [1] |
| $C_{k,c,i} \ge 0$ | isključenje ne smanjuje opterećenje | izuzet za taj par |

Doprinos se računa **u stanju $c$**: za N-1 par s ispalim elementom $c$ i isključenim
korisnikom $i$. Doprinos istog korisnika istom elementu u različitim ispadima općenito je
različit.

> [!IMPORTANT]
> Stanje 1 ovisi o tome **odakle dolazi snaga koja nadomješta isključenog korisnika**. Smjernice
> to ne propisuju. Vidi [pogl. 6](06-uravnotezenje.md).

## 5.5 Linearna interpretacija doprinosa

Neka je $\mathrm{PTDF}_{k,i}$ udio injekcije od 1 MW na mjestu korisnika $i$ koji teče
elementom $k$, uz povlačenje te snage na mjestu uravnoteženja. Za male promjene i djelatni dio
toka:

$$C_{k,c,i} \approx -\,\mathrm{PTDF}_{k,i}^{(c)}\;P_i,$$

gdje je $\mathrm{PTDF}^{(c)}$ izračunat u topologiji stanja $c$. Odatle dvije posljedice koje
određuju ponašanje formule [1]:

1. $|C_{k,c,i}|$ je promjena toka kad se ukloni **cijelo** postrojenje snage $P_i$.
2. Smanjenje snage za $\Delta P_i$ mijenja tok za samo $\mathrm{PTDF}_{k,i}\,\Delta P_i$, a
   iz (1) je $\mathrm{PTDF}_{k,i} \approx |C_{k,c,i}|/P_i$.

Interpretacija je približna jer je opterećenje mjereno strujom ili prividnom snagom (uključuje
jalovu snagu i napon), a ne djelatnim tokom — alat zato doprinos uvijek računa punim AC
proračunom, a linearni oblik služi samo za razumijevanje i procjenu broja iteracija.

## 5.6 Formula [1] i faktor *f*

Smjernice:

$$\Delta P_i = \frac{L_k(1) - L_k(0)}{100}\,\mathrm{RATE}_k\cdot f \quad [\mathrm{MW}] \qquad [1]$$

uz "*f* — faktor proporcionalnosti iteracije, *f* = broj iteracije · 1". Dakle $|\Delta P_i| = f\,|C_{k,c,i}|$:

- **iteracija 1** ($f = 1$): svaki korisnik koji pridonosi smanjuje snagu za iznos svog doprinosa;
  proračun se ponavlja;
- ako preopterećenje i dalje postoji, **iteracija 2** ($f = 2$): smanjenje za dvostruki doprinos;
- i tako dalje, dok preopterećenje ne nestane.

Smanjenje ne može biti veće od snage korisnika:

$$\Delta P_i^{(f)} = \min\left(P_i,\ f\,|C_{k,c,i}|\right).$$

### Koliko iteracija treba

Višak prijenosa na elementu (pogl. 4): $E_{k,c} = \dfrac{L_{k,c}^{(0)} - 100}{100}\,\mathrm{RATE}_k$.

Rasterećenje nakon iteracije $f$, dok nijedan korisnik nije dosegao $P_i$:

$$R(f) \approx \sum_i \mathrm{PTDF}_{k,i}\,\Delta P_i^{(f)} = f\sum_i \frac{|C_{k,c,i}|^2}{P_i}.$$

Preopterećenje nestaje kad je $R(f) \ge E_{k,c}$, pa je potreban broj iteracija približno

$$f^{*} = \left\lceil \frac{E_{k,c}}{\sum_i |C_{k,c,i}|^2 / P_i} \right\rceil .$$

Budući da je PTDF obično 0,05–0,5, rasterećenje po iteraciji je mnogo manje od zbroja
doprinosa. **$f > 1$ je zato uobičajen slučaj, a ne iznimka.**

### Gornja granica

Kad su svi korisnici koji pridonose potpuno isključeni, rasterećenje je

$$R_{max} = \sum_{i:\,C_{k,c,i}<0} |C_{k,c,i}|.$$

Ako je $R_{max} < E_{k,c}$, **nijedan $f$ ne uklanja preopterećenje**: element je preopterećen i
bez novih korisnika (ili su za preopterećenje odgovorni i drugi uzroci). Takvo preopterećenje se
ne može riješiti ograničenjem novih korisnika — alat ga označava kao **"nerješivo ograničenjem"**,
ne iskazuje ga kao ograničenje korisnika i za njega obvezno predlaže mjeru (pogl. 7).

### Primjer 1 — jedan korisnik, nerješivo ograničenjem

Element s $\mathrm{RATE} = 1300$ MVA, $L^{(0)} = 133\,\%$. Korisnik snage $P = 300$ MW; uz
njegovo isključenje $L^{(1)} = 125\,\%$.

| Veličina | Vrijednost |
|---|---|
| Doprinos $C = (125 - 133)/100 \cdot 1300$ | −104 MVA |
| $\Delta P$ uz $f = 1$ | 104 MW |
| $\mathrm{PTDF} \approx 104/300$ | 0,347 |
| Rasterećenje po iteraciji $0{,}347 \cdot 104$ | 36,1 MVA |
| Višak $E = 0{,}33 \cdot 1300$ | 429 MVA |
| Potreban $f^{*}$ | 12 → $\Delta P = \min(300,\ 1248) = 300$ MW |
| Najveće moguće rasterećenje (korisnik isključen) | 104 MVA < 429 MVA |

Ni potpuno isključenje ne uklanja preopterećenje (ostaje 125 %). Ako nema drugih korisnika koji
pridonose s još barem 325 MVA, preopterećenje je nerješivo ograničenjem.

### Primjer 2 — tri korisnika, f = 2

Vod 110 kV, $\mathrm{RATE} = 115$ MVA, $L^{(0)} = 112\,\%$, višak $E = 13{,}8$ MVA.

| Korisnik | $P_i$ [MW] | $L^{(1,i)}$ [%] | $C_i$ [MVA] | PTDF | Rasterećenje po iteraciji [MVA] |
|---|---|---|---|---|---|
| A | 50 | 96 | −18,40 | 0,368 | 6,77 |
| B | 80 | 104 | −9,20 | 0,115 | 1,06 |
| C | 20 | 111 | −1,15 | 0,058 | 0,07 |
| **Ukupno** | | | | | **7,90** |

| $f$ | $\Delta P_A$ | $\Delta P_B$ | $\Delta P_C$ | $\sum \Delta P$ [MW] | Rasterećenje [MVA] | Preopterećenje uklonjeno? |
|---|---|---|---|---|---|---|
| 1 | 18,4 | 9,2 | 1,15 | 28,75 | 7,9 | ne |
| **2** | **36,8** | **18,4** | **2,3** | **57,5** | **15,8** | **da** |

### Napomena o "usporedivom redu veličine"

Smjernice kažu da bi zbroj $\Delta P_i$ trebao biti usporediv s ukupnim preopterećenjem. Iz
§5.5 slijedi da je $\sum \Delta P_i \ge E_{k,c}$ uvijek, a omjer je otprilike
$1/\overline{\mathrm{PTDF}}$. U primjeru 2 omjer je $57{,}5 / 13{,}8 = 4{,}2$. Alat taj omjer
ispisuje uz svaki par, ali ga ne koristi kao kriterij.

### Što metoda raspodjeljuje

Formula [1] raspodjeljuje ograničenje **razmjerno odgovornosti** ($\Delta P_i \propto C_i \propto
\mathrm{PTDF}_i\,P_i$): korisnik koji više opterećuje element više se ograničava. To **nije
najmanje ukupno ograničenje**. Najmanje ukupno ograničenje dobije se ograničavanjem korisnika s
najvećim PTDF-om — u primjeru 2 samo korisnika A za $13{,}8/0{,}368 = 37{,}5$ MW, umjesto
57,5 MW ukupno. Alat službeno računa prema smjernicama; najmanje ograničenje može ispisati kao
dijagnostiku.

## 5.7 Više preopterećenja i N-1 stanja

Korisnik općenito pridonosi većem broju parova $(k, c)$ i za svaki dobiva drugi $\Delta P$.
Smjernice traže jedan $\Delta P_{max,s}$ "kojim se eliminiraju sva preopterećenja u osnovnom
stanju i svim N-1 stanjima", ali ne kažu kako se parovi kombiniraju. Alat koristi:

$$\Delta P_{max,i,s} = \max_{(k,c)}\ \Delta P_{i,k,c}.$$

**Maksimum, a ne zbroj**, jer je ograničenje preventivno: isto smanjenje snage korisnika $i$
djeluje u svim stanjima istodobno. Zbrajanje bi isto rasterećenje brojalo više puta.

Postupak:

```
za svaki preopterećeni par (k, c):
    f_kc = 1
    ponavljaj:
        ΔP_i,kc = min(P_i, f_kc · |C_k,c,i|)  za sve i s C_k,c,i < 0
        proračun stanja c s primijenjenim ΔP_i,kc
        ako L_k,c ≤ 100 %: kraj
        ako su svi ΔP_i,kc = P_i: označi "nerješivo ograničenjem", kraj
        f_kc = f_kc + 1
ΔP_max,i = max po parovima ΔP_i,kc
provjera: N i svi N-1 sa svim ΔP_max,i istodobno
    ako postoji preopterećenje (staro ili novo): povećaj f za te parove i ponovi
```

Završna provjera je nužna jer ograničenje jednog korisnika i preuzimanje te snage drugdje
(pogl. 6) može **stvoriti novo preopterećenje** na drugom elementu.

### Cjelobrojni i kontinuirani *f*

Smjernice definiraju $f$ kao broj iteracije, dakle cijeli broj. Ograničenje je zato kvantizirano:
može biti veće od potrebnog za najviše jedan korak $\sum_i |C_{k,c,i}|$. Alat službeno računa s
cjelobrojnim $f$, a kao dijagnostiku ispisuje i najmanji realni $f$ (bisekcija) uz koji
preopterećenje nestaje. Razlika pokazuje koliki je dio ograničenja posljedica kvantizacije.

### Spremnici u režimu punjenja

U scenarijima D i E faktor istodobnosti spremnika je negativan (−1, −0,5): spremnik puni i ponaša
se kao potrošač. Ako tada pridonosi preopterećenju, "ograničenje" znači **smanjenje snage
punjenja** (pomak snage prema nuli). Alat ograničenje uvijek tumači kao pomak $|P_i|$ prema nuli,
a slučajeve sa spremnikom u punjenju posebno označava.

## 5.8 Rezultat po scenariju

Nakon §5.7 za scenarij $s$ i godinu $y$ alat ima, za svakog korisnika:

- $\Delta P_{max,i,s}(y)$ [MW],
- popis parova $(k, c)$ na koje korisnik utječe, s doprinosom, $f$ i $\Delta P$ po paru,
- oznaku je li ograničenje mjerodavno zbog N ili N-1 stanja.

## 5.9 Godine i mjere

Mjere imaju najranije godine djelovanja (pogl. 7): DTR i HTLS od 2030., uređaji za kontrolu
tokova od 2031., novi element od 2032. U modelu godine $y$ uključuju se sve mjere koje su do
tada izgrađene, pa se ograničenje s godinama smanjuje i nestaje kad je izgrađen cijeli STUM.

## 5.10 Energija ograničenja

Godišnje trajanje scenarija $t_s = d_s \cdot 8760$ h, prema Tablici 1:

| Scenarij | A | B | C | D | E | F | Ukupno |
|---|---|---|---|---|---|---|---|
| Udio godine $d_s$ | 1 % | 4 % | 5 % | 5 % | 5 % | 1 % | 21 % |
| $t_s$ [h] | 87,6 | 350,4 | 438 | 438 | 438 | 87,6 | 1839,6 |

$$E_{oo,god,i}(y) = \sum_{s=A}^{F} \Delta P_{max,i,s}(y)\cdot t_s\quad [\mathrm{MWh}]$$

$$E_{oo,raz,i} = \sum_{y=2029}^{2035} E_{oo,god,i}(y)\quad [\mathrm{MWh}]$$

> [!NOTE]
> U smjernicama druga formula pod znakom zbroja ima $P_{oo,god}$ — to je tipfeler za
> $E_{oo,god}$.

Tumačenje: scenariji su karakteristična stanja visokog opterećenja mreže i pokrivaju 21 % godine.
Ograničenje $\Delta P_{max}$ pripisuje se cijelom trajanju scenarija, a za preostalih 79 % godine
pretpostavlja se da ograničenja nema. Energija je zato **ponderirana procjena**, a ne godišnja
simulacija.

## 5.11 Hibridna postrojenja (SE + BS)

Smjernice traže da se ograničenje izračuna za postrojenje, a zatim uzme u obzir baterijski
spremnik za **odgođenu isporuku**: dio snage koja bi bila ograničena puni bateriju i predaje se
kasnije. Kako, smjernice ne propisuju, a podaci o spremniku nisu dio modela
([N5](../nedostaci-smjernica.md)). Podaci se zato zadaju **po projektu**
(`config/hybrid_storage.csv`):

| Podatak | Oznaka | Jedinica |
|---|---|---|
| snaga spremnika (punjenje) | $P_{BS}$ | MW |
| kapacitet spremnika | $E_{BS}$ | MWh |
| učinkovitost punjenje–pražnjenje | $\eta$ | — |
| trajanje jednog događaja ograničenja (za konzervativnu procjenu) | $T_{ev}$ | h |

### Snaga i energija su dvije različite granice

Spremnik ograničava pomak na dva načina: **snagom** ($P_{BS}$, koliko MW može primati) i
**energijom** ($E_{BS}$, koliko MWh stane prije nego se napuni). Kapacitet u MWh ne može se
izravno oduzeti od ograničenja u MW.

### Raspoloživa snaga punjenja u scenariju

Tablica 1 propisuje angažman spremnika po scenariju, $\varphi_s$ (pozitivno = pražnjenje):
A 0; B 0,5; C 0; D −1; E −0,5; F 1. Spremnik koji već puni ne može primiti dodatnu snagu, a
spremnik koji prazni može najprije prestati prazniti. Snaga kojom spremnik može preuzeti
ograničenje:

$$P_{abs,s} = P_{BS}\,(1 + \varphi_s),\qquad 0 \le P_{abs,s} \le 2P_{BS}.$$

| Scenarij | $\varphi_s$ | $P_{abs,s}$ |
|---|---|---|
| A, C | 0 | $P_{BS}$ |
| B | 0,5 | $1{,}5\,P_{BS}$ |
| D | −1 | 0 — spremnik već puni punom snagom |
| E | −0,5 | $0{,}5\,P_{BS}$ |
| F | 1 | $2\,P_{BS}$ |

### Dvije granice procjene

Scenariji nemaju vremenski slijed (to su ponderirana karakteristična stanja), pa se ne zna koliko
dugo traje pojedini događaj ograničenja. Alat zato daje dvije granice.

**Najbolji slučaj — ograničava samo snaga.** Svaki događaj je dovoljno kratak da se spremnik ne
napuni ($T_{ev} \le E_{BS}/P_{abs,s}$), a između događaja se isprazni:

$$P_{pomak,s} = \min(\Delta P_{max,s},\ P_{abs,s}),$$

$$E_{oo,s}^{min} = (\Delta P_{max,s} - P_{pomak,s})\,t_s + (1-\eta)\,P_{pomak,s}\,t_s .$$

**Konzervativno — ograničava energija.** Događaji traju $T_{ev}$ sati; u svakom spremnik primi
najviše $E_{BS}$:

$$n_{ev,s} = \frac{t_s}{T_{ev}},\qquad
E_{pomak,s} = n_{ev,s}\,\min\left(P_{pomak,s}\,T_{ev},\ E_{BS}\right),$$

$$E_{oo,s}^{kons} = \Delta P_{max,s}\,t_s - \eta\,E_{pomak,s}.$$

### Primjer

Scenarij A ($t_s = 87{,}6$ h, $\varphi = 0$), $\Delta P_{max} = 70$ MW, spremnik 40 MW / 40 MWh,
$\eta = 1$. Bez spremnika: $70 \cdot 87{,}6 = 6132$ MWh.

| Slučaj | Pomaknuto [MWh] | Ograničeno [MWh] |
|---|---|---|
| Najbolji: događaji ≤ 1 h, spremnik prazan prije svakog | $40 \cdot 87{,}6 = 3504$ | $30 \cdot 87{,}6 = 2628$ |
| Konzervativno: događaji od 4 h ($n_{ev} = 21{,}9$) | $21{,}9 \cdot 40 = 876$ | $6132 - 876 = 5256$ |

Najbolji slučaj, "70 − 40 MW kroz cijelo trajanje scenarija", vrijedi samo ako je snaga spremnika
40 MW **i** ako nijedan događaj ne traje dulje od $E_{BS}/P_{BS} = 1$ h. Uz $\eta = 0{,}85$
najbolji slučaj raste na $2628 + 0{,}15 \cdot 3504 = 3154$ MWh.

Alat ispisuje obje granice. Bez vremenskog niza proizvodnje i ograničenja točnija procjena nije
moguća.

## 5.12 Numerički prikaz

| Razina | Sadržaj | Oblik |
|---|---|---|
| Par $(k, c)$ | $P$, $Q$, $S$, $I$, $L$ u N i N-1; doprinosi $C_{k,c,i}$; $f$; $\Delta P_{i,k,c}$ | Tablica 7 (Excel) + lista doprinosa |
| Element, scenarij | najnepovoljniji ispad, broj preopterećenja, korisnici isključeni/uključeni | Tablice 5 i 6 |
| Korisnik, scenarij, godina | $\Delta P_{max,i,s}(y)$ | matrica 6 scenarija × 7 godina |
| Korisnik, godina | $E_{oo,god,i}(y)$ | tablica + graf (pogl. 8) |
| Korisnik | $E_{oo,raz,i}$ | jedan broj po varijanti uravnoteženja |
| Mjere | prijedlog STUM-a, godina djelovanja, trošak | Tablica 8 |

Svaka veličina iskazuje se za **sve tri varijante uravnoteženja** (pogl. 6).
