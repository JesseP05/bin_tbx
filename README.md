# Bin Pipeline
- [Bin Pipeline](#bin-pipeline)
  - [Inleiding](#inleiding)
  - [Hoofdvraag:](#hoofdvraag)
    - [Tools: TODO: uitleg](#tools-todo-uitleg)
    - [Requirements (prolly remove cus Docker)](#requirements-prolly-remove-cus-docker)
- [Installation Instructions](#installation-instructions)
  - [Uninstalling](#uninstalling)


## Inleiding 

Voor de opdracht van BIN toolbox gaan we een website bouwen die en bio info pipeline bestuurt. De opdrachtgevers, Ronald W. en Peter K., hebben ons gevraagd een interactieve interface te bouwen voor het aanroepen van verschillende bio informatische tools. De keuze in de tools was vrij aan ons, wij hebben vervolgens gekozen voor FastP en Kraken2 om onze hoofdonderzoeksvraag te kunnen beantwoorden (zie onder). Daarnaast is het van belang dat onze tools interim-rapporten deelt met de gebruiker over de kwaliteit van de door de gebruiker meegegeven DNA-sequentiesamples. De focusgroep van gebruikers bestaat uit hobbyisten, studenten, en researchers. 

## Hoofdvraag:
“Hoe kunnen we DNA-data van verschillende soorten virussen specifiek classificeren en visualiseren?”

Waarom dit van belang is: Met de uitbraak van Covid-19 hebben we allemaal meegemaakt hoe belangrijk het is om vroegtijdig een diagnose te kunnen stellen. Deze tool zal een soort imitatie zijn van tools die bijvoorbeeld het RIVM bezit om virussen snel te classificeren en daarmee een positieve ofwel negatieve diagnose te stellen.


### Tools: TODO: uitleg
1. FASTP 
2. KRAKEN2 
3. Krona (visualisatie)

### Requirements (prolly remove cus Docker)
De tools FastP en Kraken2 hebben de volgende benodigheden: 
* Linux (of WSL)
* Python 3.x 
* isa-l 	(apt install libisal-dev, sudo apt install isal) 
* libdeflate 	(apt install libdeflate-dev libdeflate0) 
* Buildtools	(apt install build-essential) 
* Zlib (apt install zlib1g-dev) 
* Krona (apt install krona) 
* Flask 
 

# Installation Instructions

Dit project runned geheel in Docker, waardoor er geen individuele dependencies naast Docker handmatig geinstalleerd hoeven te worden. Voor het installeren van Docker -- raadpleeg de volgende link: [Installatie instructies.](https://docs.docker.com/engine/install/)

Nadat Docker geinstalleerd is, kunnen we doorgaan met de volgende stappen.

Clone deze repo, of download de .zip van de repo naar een handige plaats.
```bash
$ git clone https://github.com/JesseP05/bin_tbx.git
$ cd bin_tbx
```

Nu we in de console in de folder zitten kunnen we Docker starten.
```bash
$ docker compose up --build
```
Dit kan even duren en voor de complete installatie is een internetverbinding nodig.

Wanneer de installatie klaar is de interface lokaal te vinden op:
```json
127.0.0.1:8080
```
Hiermee is de installatie compleet en kunnen sequenties worden geupload.

## Uninstalling
Het verwijderen van de software wederom is eenvoudig dankzij Docker:

Open een cli in de bin_tbx folder, en run de commandos:
```bash
$ docker compose down -v
```
Om de repo helemaal te verwijderen:
```bash
$ cd ..
```
Linux & MacOS
```bash
$ rm -rf bin_tbx
```
Windows
```bash
$ rmdir /s /q bin_tbx
```


---

Jesse Postma & Robin Offringa