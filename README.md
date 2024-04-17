# ProjectIndexer
This is a RoboticsBrno indexer generator for out GitHub projects.
ProjectIndexer is a static web generator written in Python.
It generates a static web page with a list of all our projects based on the GitHub API.

## How to use it
1. Clone this repository
2. Install dependencies
3. create file `.env` with content `MY_GITHUB_TOKEN=your_github_token`
    - you can generate your token [here](https://github.com/settings/tokens?type=beta)
4. run `python3 project_indexer.py --help` to see available options

## ProjectIndexer options
- `fetch-github` - fetches data from GitHub API and saves it to `data/repos.json`
- `generate` - generates static web page from `data/repos.json` and saves it to `output` folder
  - `--compile-tailwind` - compiles tailwind css
- `serve` - serves the static web page from `output` folder

More predefined commands in `Makefile`.

# Indexace projektů pro RoboticsBrno (CZ)

Tento projekt slouží k automatickému generování portfolia projektů naší organizace na GitHubu.
ProjektIndexer je statický web generátor napsaný v Pythonu a měl by se automaticky spouštět v nastavených intervalech pomocí GitHub Actions.

## Cíl
Cílem projektu je udržovat aktuální seznam, popis a informace o projektech bez nutnosti ruční údržby.
Ukázat veřejnosti (i členům) naši práci v přehledné a jednoduché formě na webu.
Projekty se budou seskupovat podle kategorií a bude možné je filtrovat například podle projektů.
Každý projekt bude mít svoji podstránku s relevantními informacemi a odkazy na repozitáře.
Část funkcionality se bude zpracovávat z informací (tagů, popisu) z GitHubu a druhou část bude muset uživatel vyplnit ručně (např. obrázky, popis - asi YAML).

## Fungování

## Data z GitHubu
Data o projektech se získávají z GitHub API. Pro získání dat je potřeba mít GitHub token, který se uloží do souboru `.env` do proměnné `MY_GITHUB_TOKEN`.

Zpracovávaná data
- `name` - název projektu
- `description` - popis projektu
- `html_url` - odkaz na GitHub repozitář
- `homepage` - odkaz na web projektu
- `topics` - tagy projektu
  - jelikož se dají tagy jednoduše nastavovat, můžeme je použít pro kategorizaci projektů (např. `robotka`, `rbcx`, `smd-challenge`, `hardware`, ...)
  - také by šlo taky využit na skrývýní / zobrazení projektů na webu (např. `hidden`). Nebo naopak zveřejnění hlavičky privátního repozitáře (např. `private-publish-header`) - pro kompletní prolinkování našich repozitářů.
- `language` - programovací jazyk projektu
- `created_at` - datum vytvoření projektu
  - lze využít pro řazení projektů
- `updated_at` - datum poslední aktualizace projektu
  - lze využít pro řazení projektů
  - na úvodní stránce můžeme informovat o změnách v projektech
- `license` - licence projektu
- `contributors` - seznam přispěvatelů
  - do budoucna propojit s https://team.robotikabrno.cz/ (lépe sjednotit)
- `readme` - obsah README.md
  - zobrazit na podstránce projektu (správně zpracovat obrázky, odkazy, ...)
- `images` - obrázky projektu
  - aktuálně nejspíš nepoužíváme (možná do budoucna)
- `stars` - počet hvězdiček
  - lze využít pro řazení projektů
- `issues` - počet issues

### README a popis projektu
Každý repozitář by měl mít ideálně nastaven Popis projektu na GH a ideálně by měl obsahovat i README.md soubor (CZ/EN - lépe EN).
Pokud nebude README.md soubor, tak se zobrazí pouze popis projektu z GH.
Popis projektu by mohl ideálně začínat Emoji (např. 🤖 ) a následně krátkým popisem projektu.

### Obrázky projektu
Obrázky projektu by měly být v adresáři `images` případně `img` v kořenovém adresáři repozitáře.
Na webu se budou řadit podle názvů z repa.
Akceptované soubory: `.png`, `.jpg`, `.jpeg`, (`.svg` spíše ne).

## Doplnění dat
Některá data se nedají získat z GitHubu a je potřeba je doplnit ručně.

### Kategorie
Aby bylo možné projekty seskupovat do kategorií, je potřeba každý projekt označit tagem v GitHubu.
Při generování se bude hledat složka `projects` a v ní soubor s názvem tagu (např. `robotka.md`).
Readme bude začínat YAML hlavičkou s informacemi o projektu.
```yaml
name: Robotka
name_cz: Robotka
description: Robotka is a small robot for educational purposes.
description_cz: Robotka je malý robot pro vzdělávací účely.
repository:
  - name: robotka library
    url: https://github.com/RoboticsBrno/RB3204-RBCX-Robotka-library
  - name: robotka-examples
    url: https://github.com/RoboticsBrno/robotka-examples
web: https://robotka.robotickytabor.cz/
authors:
  - name: Jan Novák (dohledá si další údaje samo)
...
---
Markdown text...

```

### Obrázky
Cesta k obrázkům začíná `R:<repo name>/images/...` (např. `R:robotka/images/...`)

## Úvodní stránka
Kdo jsme a co děláme.
Tahle stánka ideálně anglicky i česky - zbytek stačí v angličtině (pokud je to možné).

Déle zde zobrazova informace o změnách v projektech (např. poslední aktualizace).
Nachystat několik šablon a při každé kompilaci se náhodně vybere jedna a zobrazí se na úvodní stránce (např. obrázek z nějakého projektu s popisem a linkem).

## Náš tým
Zde by se měli zobrazovat členové týmu (případně i přispěvatelé).
Přesunout informace z https://team.robotikabrno.cz/ sem na jeden web.