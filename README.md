# operativna-ogranicenja

Proračun operativnih ograničenja novih proizvodnih postrojenja prema *Smjernicama za izvođenje
mrežnih analiza na modelima prijenosne elektroenergetske mreže* (HOPS, lipanj 2026.), u otvorenom
kodu (Python, [pandapower](https://www.pandapower.org/)) na modelima isporučenima u PSS/E `.raw`
formatu (v35).

> [!IMPORTANT]
> Smjernice ne propisuju kako se uravnotežuje snaga kad se novi korisnik isključi ili ograniči,
> a o tome izravno ovisi rezultat. Alat računa **tri varijante** i prikazuje ih usporedno —
> [teorija, pogl. 6](docs/teorija/06-uravnotezenje.md).

> [!WARNING]
> PST-ovi su zasad modelirani **samo kutno**. Dio stvarnih PST-ova ima dijagonalnu regulaciju,
> pa rezultati koji ovise o kutu PST-a nisu točni dok se ne zadaju tablice po položajima —
> [teorija, pogl. 2](docs/teorija/02-pst-korekcija-impedancije.md).

## Dokumentacija

Teorijska knjiga je u [`docs/teorija/`](docs/teorija/index.md) i čita se izravno na GitHubu ili kao
stranica (MkDocs):

```
pip install -r requirements.txt
mkdocs serve          # lokalni pregled na http://127.0.0.1:8000
```

**Objava na GitHub Pages** radi se automatski (`.github/workflows/docs.yml`): pri svakom pushu
na `master` koji mijenja `docs/`, `mkdocs.yml` ili `requirements.txt` stranica se izgradi i objavi.
Jednokratno treba uključiti: *Settings → Pages → Build and deployment → Source: GitHub Actions*.
Stranica je tada na `https://admilara.github.io/operativna-ogranicenja/`.

## Pokretanje

Skripte u `scripts/` pokreću se iz IDLE-a (F5); postavke su u bloku `POSTAVKE` na vrhu datoteke.

| Skripta | Što radi |
|---|---|
| `scripts/build_model.py` | `.raw` → pandapower, provjera prema spremljenom PSS/E rješenju, granica (X-čvorišta), spremanje mreže i izvještaja provjere |
| `scripts/pst_report.py` | pregled PST-ova iz `.raw`-a: osnovni podaci i tablice korekcije impedancije (Markdown) |
| `scripts/htls_ratings.py` | nazivne vrijednosti vodova s HTLS (ACCC) vodičem u obliku Tablice 4 → `config/htls_ratings.csv` |

Kod je u paketu `src/oplimits` (identifikatori na engleskom, poruke i izlazne tablice na hrvatskom).
Testovi: `python -m pytest tests/` (integracijski testovi se izvode samo ako je model lokalno u
`data/modeli/`).

## Podaci

Mrežni modeli, popisi korisnika u postupku priključenja i rezultati **nisu dio repozitorija**.
Spremaju se lokalno u `data/` koju `.gitignore` isključuje.
