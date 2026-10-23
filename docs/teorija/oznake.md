# Oznake i pojmovi

| Oznaka | Značenje | Jedinica |
|---|---|---|
| $i$ | novi korisnik (projekt, Owner 3) | — |
| $k$ | element mreže (vod, transformator) | — |
| $c$ | stanje: $c = 0$ osnovno, inače ispad elementa $c$ | — |
| $s$ | scenarij A–F | — |
| $y$ | godina 2029.–2035. | — |
| $P_i$ | djelatna snaga korisnika u scenariju | MW |
| $\mathrm{RATE}_k$ | termička snaga elementa (RATE1 iz `.raw`) | MVA |
| $L_{k,c}^{(0)}$ | opterećenje elementa $k$ u stanju $c$, svi korisnici uključeni | % |
| $L_{k,c}^{(1,i)}$ | isto, korisnik $i$ isključen | % |
| $E_{k,c}$ | višak prijenosa iznad 100 % | MVA |
| $C_{k,c,i}$ | doprinos korisnika $i$ preopterećenju para $(k,c)$ | MVA |
| $f$ | faktor proporcionalnosti iteracije (broj iteracije) | — |
| $\Delta P_{i,k,c}$ | smanjenje snage korisnika $i$ za par $(k,c)$ | MW |
| $\Delta P_{max,i,s}$ | smanjenje snage korisnika $i$ kojim se uklanjaju sva preopterećenja scenarija $s$ | MW |
| $t_s$ | godišnje trajanje scenarija | h |
| $E_{oo,god}$ | energija ograničenja u godini | MWh |
| $E_{oo,raz}$ | energija ograničenja u razdoblju 2029.–2035. | MWh |
| $\mathrm{PTDF}_{k,i}$ | udio injekcije na mjestu $i$ koji teče elementom $k$ | — |
| $F(\alpha)$ | faktor korekcije impedancije PST-a za kut $\alpha$ | — |
| $Z_{12}, Z_{23}, Z_{31}$ | impedancije parova namota tronamotnog transformatora | p.u. |
| $Z_1, Z_2, Z_3$ | impedancije ekvivalentne zvijezde | p.u. |

| Pojam | Značenje |
|---|---|
| EOTRP | elaborat optimalnog tehničkog rješenja priključenja |
| STUM | stvaranje tehničkih uvjeta u mreži |
| UoP | ugovor o priključenju |
| X-čvorište | fiktivna sabirnica na granici modela, na sredini prekograničnog voda |
| V1, V2, V3 | varijante uravnoteženja snage (pogl. 6) |
| G1–G4 | zastavice N-1 slučajeva blizu granice i otoka (pogl. 3, §3.3) |
| DTR | *Dynamic Thermal Rating* — dinamičko određivanje termičkog kapaciteta |
| HTLS | *High Temperature Low Sag* — visokotemperaturni vodiči malog provjesa |
| PST | *Phase Shifting Transformer* — transformator s mogućnošću zakreta kuta |
| ZPBN | *Zero Power Balance Network* — mreža nulte bilance snage u REI ekvivalentu |
