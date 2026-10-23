# Teorijska knjiga

Ova knjiga opisuje **što** alat računa, **zašto** baš tako i **gdje** se odstupa od
doslovnog teksta smjernica ili od PSS/E-a. Svaka odluka koja mijenja brojeve u rezultatu
ovdje je zapisana s obrazloženjem i, gdje je bilo moguće, s provjerom na podacima.

| Poglavlje | Sadržaj |
|---|---|
| [1. Mrežni model iz PSS/E](01-mrezni-model.md) | Kako se `.raw` pretvara u pandapower model, što se provjerava i koje datoteke nastaju |
| [2. PST i korekcija impedancije](02-pst-korekcija-impedancije.md) | Tablice korekcije impedancije, tronamotni PST-ovi, **upozorenje o dijagonalnoj regulaciji** |
| [3. Granica sustava i ekvivalenti](03-granica-ekvivalenti.md) | X-čvorišta kao PQ injekcije, Wardov, prošireni Wardov i REI ekvivalent |
| [4. N-1 i opterećenje elemenata](04-n-1-opterecenje.md) | Popis ispada, definicija opterećenja, vodiči i nazivne vrijednosti, zastavice |
| [5. Operativna ograničenja](05-operativna-ogranicenja.md) | Formula [1], značenje faktora *f*, više preopterećenja, energija ograničenja |
| [6. Uravnoteženje snage — tri varijante](06-uravnotezenje.md) | **Ono što metoda ne propisuje, a mijenja rezultat** |
| [7. Prijedlog mjera (STUM)](07-mjere.md) | PST, DTR, HTLS, uređaji za kontrolu tokova, novi elementi, rokovi |
| [8. Vizualizacija rezultata](08-vizualizacija.md) | Tablice, toplinske karte, matrica doprinosa, vremenski tijek |
| [Oznake i pojmovi](oznake.md) | Popis oznaka |

Formule su pisane u LaTeX-u (`$…$`) i prikazuju se i na GitHubu i na GitHub Pages stranici.
