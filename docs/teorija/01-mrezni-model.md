# 1. Mrežni model iz PSS/E

## 1.1 Polazište

HOPS isporučuje modele u PSS/E `.raw` formatu, revizija 35: šest scenarija (A–F) za svaku
godinu 2029.–2035., ukupno 42 modela. Model sadrži **samo hrvatski podsustav**; prekogranični
vodovi završavaju u fiktivnim X-čvorištima (brojevi 99961–99998), a sabirnice susjednih
sustava na drugom kraju tih vodova u modelu ne postoje.

pandapower nema uvoznik za PSS/E, pa alat ima vlastiti čitač `.raw` formata i vlastitu
pretvorbu. Cilj pretvorbe je **1:1 reprodukcija PSS/E modela**, a ne "slična" mreža:
pretvorba se smatra ispravnom tek kad pandapower na istim podacima daje isto rješenje kao
PSS/E (§1.5).

## 1.2 Pridruživanje elemenata

| PSS/E zapis | pandapower element | Napomene |
|---|---|---|
| Bus | `bus` | indeks = PSS/E broj sabirnice; IDE=4 → `in_service=False`; spremljeni VM/VA u `psse_vm`, `psse_va` |
| Load | `load` | konstantna snaga; I- i Y-komponente se provjeravaju (u modelima ih nema) |
| Generator | `sgen` po jedinici + `gen` "Vreg_⟨sabirnica⟩" po PV sabirnici | v. §1.3 |
| Branch | `line` | π-model, $R$, $X$, $B$ iz zapisa, duljina 1 km |
| Transformer (K=0) | `trafo` | namotni naponi WINDV kao `vn_hv_kv`/`vn_lv_kv`, PST kut i korekcija impedancije (pogl. 2) |
| Transformer (K≠0) | `trafo3w` | model zvijezde, korekcija impedancije namota 1 (pogl. 2) |
| Fixed shunt | `shunt` | |
| Switched shunt | `shunt` | fiksno na BINIT (u modelima `SWSHNT=0`) |
| Impedance correction | tablica u memoriji | primjenjuje se pri izgradnji (pogl. 2) |

**Vodovi.** Parametri u p.u. na bazi $S_B$ (SBASE = 100 MVA) i baznom naponu sabirnice
$U_B$ pretvaraju se u fizikalne vrijednosti:

$$
Z_B = \frac{U_B^2}{S_B},\qquad
R = r\,Z_B,\qquad X = x\,Z_B,\qquad
C = \frac{b}{Z_B\,\omega},\quad \omega = 2\pi f .
$$

Vod se u pandapoweru zadaje s duljinom 1 km i parametrima "po km", pa su $R$, $X$, $C$
upravo ukupne vrijednosti voda. Stvarna duljina čuva se u stupcu `psse_len_km`, a
nazivne vrijednosti RATE1–RATE3 u `rate1_mva`… (opterećenje se računa prema njima,
v. pogl. 4).

**Transformatori.** Namotni naponi (WINDV, uz CW=2 u kV) zadaju se izravno kao
`vn_hv_kv` i `vn_lv_kv`. pandapower tada sam računa izvannazivni omjer prema baznim
naponima sabirnica — isto kao PSS/E. Impedancija se, ovisno o CZ, pretvara u
$u_k$ i $u_{kr}$ na nazivnoj snazi para namota:

| CZ | Ulaz | Pretvorba |
|---|---|---|
| 1 | $R$, $X$ u p.u. na SBASE sustava | $r = R\,S_n/S_B$, $z = \lvert R + jX \rvert\,S_n/S_B$ |
| 2 | $R$, $X$ u p.u. na SBASE para namota | $r = R$, $z = \lvert R + jX \rvert$ |
| 3 | $R$ = gubici u W, $X$ = $\lvert Z \rvert$ u p.u. | $r = P_{Cu}/S_n$, $z = X$ |

$$u_k = 100\,z\,F,\qquad u_{kr} = 100\,r\,F$$

gdje je $F$ faktor korekcije impedancije za zadani kut PST-a (pogl. 2), inače $F = 1$.

## 1.3 Proizvodne jedinice i regulacija napona

Svaka proizvodna jedinica (zapis Generator) postaje **zaseban `sgen`** sa svojom djelatnom
snagom i poljima vlasnika `psse_o1`…`psse_o4`. To je nužno jer se operativna ograničenja
određuju po korisniku (Owner 3 = redni broj projekta, Owner 4 = godina zahtjeva za EOTRP),
a ne po sabirnici.

Regulaciju napona na sabirnici drži **jedan** element `gen` "Vreg_⟨sabirnica⟩" s
$P = 0$, zadanim naponom VS i zbrojenim granicama jalove snage svih aktivnih jedinica na
sabirnici:

$$Q_{\min} = \sum_g Q_{B,g},\qquad Q_{\max} = \sum_g Q_{T,g}.$$

Tako se ponaša i PSS/E: jalova snaga PV sabirnice raspodjeljuje se na jedinice tek nakon
rješenja, a granica se provjerava za sabirnicu kao cjelinu.

**Udaljena regulacija.** pandapower `gen` ne podržava regulaciju udaljene sabirnice. Jedinica
koja regulira drugu sabirnicu koja već ima vlastitu lokalnu regulaciju modelira se kao PQ
s jalovom snagom QG iz spremljenog rješenja (u modelu A-2029: jedna jedinica, 80144 'S2' →
60144). Svaki takav slučaj se zapisuje u nalaze.

### Granice jalove snage — VARLIM petlja

Ugrađena opcija `enforce_q_lims=True` u pandapoweru na ovim mrežama ne konvergira (preko 160
regulatora završi na granici). Alat zato koristi vlastitu vanjsku petlju po uzoru na PSS/E
opciju VARLIM:

1. Newton–Raphson s PV regulatorima bez granica.
2. Svaki regulator s $Q > Q_{\max}$ ili $Q < Q_{\min}$ prelazi u PQ na toj granici.
3. Regulator na granici vraća se u PV ako napon sabirnice prijeđe zadanu vrijednost na
   "pogrešnu" stranu ($Q = Q_{\max}$ i $U > U_{zad}$, odnosno $Q = Q_{\min}$ i $U < U_{zad}$).
4. Ponavlja se dok nema promjena.

Na modelu A-2029 petlja se smiri u 10 koraka.

## 1.4 Sabirnica referentnog čvora (slack)

U isporučenim modelima **nijedna sabirnica nije tipa 3**, a sabirnica 60158 navedena kao
"area swing" nema jedinicu u pogonu. Referentni čvor se zato mora zadati.

Odabrana je **RHE Velebit** (400 kV sabirnica 60132): reverzibilna hidroelektrana koja može
preuzeti neravnotežu u oba smjera. pandapower `ext_grid` na toj sabirnici dobiva napon i kut
iz spremljenog rješenja, pa se osnovno stanje ne mijenja; regulator sabirnice se isključuje,
a jedinice H1 i H2 zadržavaju svoju snagu — `ext_grid` preuzima samo razliku (gubitke i
neravnotežu).

> [!WARNING]
> `ext_grid` nema granice djelatne snage. U modelu A-2029 RHE Velebit ima 2 × 89,7 MW uz
> PT = 2 × 138 MW i PB = 2 × 40 MW, tj. **+96,6 MW / −99,4 MW** rezerve u turbinskom radu.
> Zapisa za crpni rad u modelu nema. Kad neravnoteža prijeđe te granice, alat to označava —
> rješenje je i dalje matematički ispravno, ali fizikalno neostvarivo. Ovo je jedan od razloga
> za tri varijante uravnoteženja (pogl. 6).

## 1.5 Provjera prema spremljenom PSS/E rješenju

`.raw` datoteka sadrži i rješenje tokova snaga (VM, VA svake sabirnice). Pretvorba se provjerava
u dva koraka.

### Korak 1 — neusklađenost snage u spremljenom stanju

Iz pandapower modela gradi se matrica admitancija $\mathbf{Y}$ i u nju se uvrste spremljeni
naponi. Injekcija koju mreža "traži" na sabirnici $i$:

$$S_i^{mreža} = U_i \left(\sum_j Y_{ij} U_j\right)^{*}$$

uspoređuje se sa zadanom injekcijom $S_i^{zad} = \sum P_G + jQ_G - \sum (P_L + jQ_L)$.
Razlika $\Delta S_i = S_i^{mreža} - S_i^{zad}$ mora biti na razini zaokruživanja (VM u
`.raw` ima 5, VA 4 decimale). Ovaj korak **ne ovisi o rješavaču** — ispituje samo jesu li
parametri elemenata isti kao u PSS/E-u — i zato je najosjetljiviji test pretvorbe.

**Zvjezdišta tronamotnih transformatora.** pandapower dodaje pomoćnu sabirnicu za zvjezdište
svakog `trafo3w`. Njezin napon se ne preuzima iz VMSTAR/ANSTAR (pandapower stavlja fazni pomak
na drugu stranu zvjezdišta od PSS/E-a), nego se računa iz uvjeta da zvjezdište nema injekcije
(Kronova redukcija):

$$\mathbf{U}_s = -\mathbf{Y}_{ss}^{-1}\,\mathbf{Y}_{sk}\,\mathbf{U}_k .$$

Zvjezdišta isključenih transformatora izuzimaju se iz redukcije — inače NaN tiho "preskoči"
čitavo postrojenje (to se dogodilo u razvoju; alat sada prekida s greškom ako se u
neusklađenosti pojavi NaN).

### Korak 2 — usporedba rješenja

Na model s granicom (§1.6) i referentnim čvorom pokreće se load flow s VARLIM petljom i
uspoređuju se naponi. Referentni čvor dobiva spremljeni napon i kut, a jedinice na njemu
zadržavaju svoju snagu, pa bi uz ispravan model `ext_grid` trebao preuzeti približno 0 MW.

| Provjera (model A-2029) | Rezultat |
|---|---|
| Najveća neusklađenost na unutarnjim sabirnicama | 0,71 MW / 2,41 Mvar (zaokruživanje preko kratkih kabela) |
| Najveće odstupanje modula napona | 0,00017 p.u. |
| Najveće odstupanje kuta | 0,025° |
| Snaga referentnog čvora (RHE Velebit) | 0,00 MW (PSS/E: 0) |
| Ukupna proizvodnja / potrošnja | 6291,40 MW / 2320,55 MW — jednako Prilogu 6, scenarij A |

## 1.6 Granica: X-čvorišta

Prekogranični vodovi u modelu idu od hrvatske sabirnice do X-čvorišta, a od X-čvorišta do
sabirnice susjednog sustava koja u modelu ne postoji. Taj drugi dio voda se izostavlja, a na
X-čvorište se postavlja **teret jednak razmjeni** izračunatoj iz spremljenog rješenja
(neusklađenost iz §1.5 na X-čvorištu je upravo snaga koja teče preko izostavljenog dijela).
Teret se označava stupcem `granica=True`; pozitivna vrijednost znači izvoz iz Hrvatske.

Razmjene se razlikuju od Priloga 5 za 0–5,5 MW: Prilog 5 je mjeren na hrvatskom kraju voda, a
model na X-čvorištu — razlika su gubici na hrvatskom dijelu voda. Posljedice ovakvog modeliranja
granice za N-1 opisane su u [pogl. 3](03-granica-ekvivalenti.md).

## 1.7 Nalazi u isporučenom modelu A-2029

| Nalaz | Posljedica |
|---|---|
| Nema sabirnice tipa 3; "area swing" 60158 bez jedinice u pogonu | referentni čvor se zadaje (RHE Velebit) |
| 31 prekogranični vod završava na sabirnicama izvan modela | granica kao PQ injekcije (§1.6) |
| Vod 62056–99974: sabirnica 62056 ne postoji; X-čvorište 99974 ostaje otok | isključeno |
| Generator 80002 'HE': skraćeni zapis (24 polja umjesto 29) | polja vlasnika/WMOD nepotpuna |
| 80144 'S2' regulira 60144 koja ima vlastitu regulaciju | modelirano kao PQ |
| Melina T1: RATE1 namota 1 = 0 | za opterećenje se uzima SBASE para namota, uz zastavicu |
| PST Divača (Tablica 3) izvan modela | kut 30° prema smjernicama nije primjenjiv u ovom izvatku |

## 1.8 Datoteke

| Datoteka | Kako nastaje | Sadržaj |
|---|---|---|
| `<model>_pp.json` | `scripts/build_model.py` | pandapower mreža (`pp.from_json`), **prije** rješavanja; svi PSS/E podaci potrebni kasnije u stupcima `psse_*` |
| `<model>_validacija.xlsx` | isto | listovi: `naponi_usporedba` (svaka sabirnica, PSS/E vs pandapower), `neuskladenost_S` (ΔP, ΔQ u spremljenom stanju), `granica_X` (razmjena po X-čvorištu), `nalazi` (popis odstupanja i pretpostavki iz pretvorbe) |
