# Bin Pipeline
Dit is een repo voor de bio informatica toolbox.


## Inleiding 

Voor de opdracht van BIN toolbox gaan we een website bouwen die en bio info pipeline bestuurt. De opdrachtgevers, Ronald Wedema en Peter, hebben ons gevraagd een interactieve interface te bouwen voor het aanroepen van verschillende bio informatische tools. De keuze in de tools was vrij aan ons, wij hebben vervolgens gekozen voor FastP en Kraken2 om onze hoofdonderzoeksvraag te kunnen beantwoorden (zie onder). Daarnaast is het van belang dat onze tools interim-rapporten deelt met de gebruiker over de kwaliteit van de door de gebruiker meegegeven DNA-sequentiesamples. De focusgroep van gebruikers bestaat uit hobbyisten, studenten, en researchers. 

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
 



