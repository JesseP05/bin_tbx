# Bin Pipeline
Dit is een repo voor de bio informatica toolbox.


## Inleiding 

Voor de opdracht van BIN toolbox gaan we een website bouwen die en bio info pipeline bestuurt. De opdrachtgevers, Ronald W. en Peter K., hebben ons gevraagd een interactieve interface te bouwen voor het aanroepen van verschillende bio informatische tools. De keuze in de tools was vrij aan ons, wij hebben vervolgens gekozen voor FastP en Kraken2 om onze hoofdonderzoeksvraag te kunnen beantwoorden (zie onder). Daarnaast is het van belang dat onze tools interim-rapporten deelt met de gebruiker over de kwaliteit van de door de gebruiker meegegeven DNA-sequentiesamples. De focusgroep van gebruikers bestaat uit hobbyisten, studenten, en researchers. 

## Hoofdvraag:
“Hoe kunnen we DNA-data van verschillende soorten virussen specifiek classificeren en visualiseren?”

Waarom dit van belang is: Met de uitbraak van Covid-19 hebben we allemaal meegemaakt hoe belangrijk het is om vroegtijdig een diagnose te kunnen stellen. Deze tool zal een soort imitatie zijn van tools die bijvoorbeeld het RIVM bezit om virussen snel te classificeren en daarmee een positieve ofwel negatieve diagnose te stellen.


### Tools:
1. FASTP
2. KRAKEN2 
3. Krona (visualisatie)

### Requirements
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

## FASTP
FastP heeft een aantal requirements, installeer deze eerst:
1. libdeflate
> (sudo) apt install libdeflate-dev
2. libisal
> (sudo) apt install libisal-dev
> (sudo) apt install isal
3. buildtools (gcc)
> sudo apt install build-essential

Hierna kan de binary van fastp gecompileerd en geinstalleerd worden:
```bash
wget https://github.com/OpenGene/fastp/archive/refs/tags/v1.1.0.tar.gz
tar -xf v1.1.0.tar.gz
cd fastp-1.1.0/

make -j
sudo make install
```
fastp is nu geinstalleerd

## Kraken2
Kraken2 heeft een aantal requirements, installeer deze eerst:
1. zlib
> (sudo) apt install zlib1g-dev
2. Krona
```bash
git clone https://github.com/marbl/Krona.git
cd Krona/KronaTools
sudo ./install.pl

mkdir taxonomy && ./updateTaxonomy
```

Hierna kan de binary van Kraken2 gecompileerd en geinstalleerd worden:
```bash
wget https://github.com/DerrickWood/kraken2/archive/refs/tags/v2.17.1.tar.gz
tar -xf v2.17.1.tar.gz

cd kraken2-2.17.1/
chmod +x install_kraken2.sh

sudo ./install_kraken2.sh /usr/local/bin
```
kraken2 is nu geinstalleerd

## Download de virology database voor kraken2
> GAAT VERANDEREN!
Download locatie is willekeurig dmv symlink (e.g. ../viral_db)
```bash
mkdir viral_db && cd viral_db
wget https://g-e320e6.63720f.75bc.data.globus.org/gen101/world-shared/doi-data/OLCF/202004/10.13139_OLCF_1615774/viral-jgi-krakendb-all.tar.gz
tar -xf viral-jgi-krakendb-all.tar.gz

cd viral-jgi-krakend-all

sudo mkdir -p /usr/local/share/kraken2

pwd
sudo ln -s PWD_OUTPUT /virology_db

rm viral-jgi-krakendb-all.tar.gz
```

## kraken test run
```bash
kraken2 --db /virology_db --threads 4 --report out.txt *.fasta
```

