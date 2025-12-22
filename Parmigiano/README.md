# Parmigiano
This folder contains:
- The Lemma Bank of the [dialect of Parma](https://it.wikipedia.org/wiki/Dialetto_parmigiano). It consists of a large collection of lemmas, serving as the backbone to achieve interoperability, by linking all those entries in lexical resources and tokens in corpora that point to the same lemma.
- The VLP (Vocabolario della Lingua Parmigiana) glossary, that is a bilingual lexicon having Italian entries and the corresponding translations in Parmigiano, edited by [Umberto Pavarini and Gruppo di Lavoro Memento Mori](https://dialetto.comune.parma.it/vocabolarioparmigiano/avvio.htm).
Data are modelled according to the OntoLex-Lemon model and are provided in Turtle format. The RDF version of the glossary includes the linking to the LiIta Knowledge Base.
The subfolder *source* contains the same data but in csv format.

## Endpoint
Data can be queried through the following endpoint: [https://liita.it/sparql](https://liita.it/sparql).

## SPARQL queries
This section provides a set of SPARQL queries to be used on the aforementioned endpoint.

**Find all entries in Parmigiano marked as jargon.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%3Fwr%0D%0AWHERE+%7B%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+%3B%0D%0Adcterms%3AisPartOf+%3Chttp%3A%2F%2Fliita.it%2Fdata%2Fid%2FDialettoParmigiano%2Flemma%2FLemmaBank%3E+.%0D%0A%3Fentry+a+ontolex%3ALexicalEntry+%3B%0D%0Ardfs%3Acomment+%22Usage%3A+Voce+gergale%22+%3B%0D%0Aontolex%3AcanonicalForm+%3Flemma+.%0D%0A%7D&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?lemma ?wr
WHERE {
?lemma ontolex:writtenRep ?wr ;
dcterms:isPartOf <http://liita.it/data/id/DialettoParmigiano/lemma/LemmaBank> .
?entry a ontolex:LexicalEntry ;
rdfs:comment "Usage: Voce gergale" ;
ontolex:canonicalForm ?lemma .
}
```

**Find all translations of the entry "donna" (woman) and show the corresponding usage comment**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%0D%0A++%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3B+separator%3D%22%2C+%22%29+AS+%3FwrsIT%29+%0D%0A++%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3B+separator%3D%22%2C+%22%29+AS+%3Fwrs%29+%0D%0A++%3Fcomment%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+%3B%0D%0Aontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma+.%0D%0AOPTIONAL+%7B+%3Fle+rdfs%3Acomment+%3Fcomment+.+%7D%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle+%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma+.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT+.%0D%0AFILTER+regex%28str%28%3FwrIT%29%2C+%22%5Edonna%24%22%29%0D%0A%7D%0D%0AGROUP+BY+%3Fcomment%0D%0AORDER+BY+ASC%28%3Fcomment%29&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT 
  (GROUP_CONCAT(DISTINCT ?wrIT ; separator=", ") AS ?wrsIT) 
  (GROUP_CONCAT(DISTINCT ?wr ; separator=", ") AS ?wrs) 
  ?comment
WHERE {
?lemma a lila:Lemma ;
ontolex:writtenRep ?wr .
?le ontolex:canonicalForm ?lemma .
OPTIONAL { ?le rdfs:comment ?comment . }
?leITA vartrans:translatableAs ?le ;
ontolex:canonicalForm ?liitaLemma .
?liitaLemma ontolex:writtenRep ?wrIT .
FILTER regex(str(?wrIT), "^donna$")
}
GROUP BY ?comment
ORDER BY ASC(?comment)
```

**Find all Italian entries that contain the substring *vecch* (root meaning *old*) and show the corresponding translations into Parmigiano.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3FwrIT%29%2C+%22vecch%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wrIT), "vecch") .
} group by ?lemma ?liitaLemma
```

**Find entries that start with *z* in Parmigiano and with *s* in Italian.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3Fwr%29%2C+%22%5Ez%22%29+.%0D%0AFILTER+regex%28str%28%3FwrIT%29%2C+%22%5Es%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wr), "^z") .
FILTER regex(str(?wrIT), "^s") .
} group by ?lemma ?liitaLemma
```
**Find entries that contain *ci* (voiceless postalveolar affricate) in Parmigiano and *chi* (voiceless velar plosive) in Italian.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3Fwr%29%2C+%22ci%22%29+.%0D%0AFILTER+regex%28str%28%3FwrIT%29%2C+%22chi%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wr), "ci") .
FILTER regex(str(?wrIT), "chi") .
} group by ?lemma ?liitaLemma
```
**Find entries that contain *n’n* in Parmigiano and show the correspoding Italian translation.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3Fwr%29%2C+%22n%E2%80%99n%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wr), "n’n") .
} group by ?lemma ?liitaLemma
```

**Find verbs that end with *or* in Parmigiano and show the correspoding Italian translation.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Flemma+lila%3AhasPOS+lila%3Averb+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3Fwr%29%2C+%22or%24%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?lemma lila:hasPOS lila:verb .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wr), "or$") .
} group by ?lemma ?liitaLemma
```
**Find adjectives that end with *bil* in Parmigiano.** 

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lila%3A+%3Chttp%3A%2F%2Flila-erc.eu%2Fontologies%2Flila%2F%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+dcterms%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0A%0D%0ASELECT+%3Flemma+%28GROUP_CONCAT%28DISTINCT+%3Fwr+%3Bseparator%3D%22%2C+%22%29+as+%3Fwrs%29+%3FliitaLemma+%28GROUP_CONCAT%28DISTINCT+%3FwrIT+%3Bseparator%3D%22%2C+%22%29+as+%3FwrsIT%29%0D%0AWHERE+%7B%0D%0A%3Flemma+a+lila%3ALemma+.%0D%0A%3Flemma+ontolex%3AwrittenRep+%3Fwr+.%0D%0A%3Flemma+lila%3AhasPOS+lila%3Aadjective+.%0D%0A%3Fle+ontolex%3AcanonicalForm+%3Flemma.%0D%0A%3FleITA+vartrans%3AtranslatableAs+%3Fle%3B%0D%0Aontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A%3FliitaLemma+ontolex%3AwrittenRep+%3FwrIT.%0D%0AFILTER+regex%28str%28%3Fwr%29%2C+%22bil%24%22%29+.%0D%0A%7D+group+by+%3Flemma+%3FliitaLemma&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lila: <http://lila-erc.eu/ontologies/lila/>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>

SELECT ?lemma (GROUP_CONCAT(DISTINCT ?wr ;separator=", ") as ?wrs) ?liitaLemma (GROUP_CONCAT(DISTINCT ?wrIT ;separator=", ") as ?wrsIT)
WHERE {
?lemma a lila:Lemma .
?lemma ontolex:writtenRep ?wr .
?lemma lila:hasPOS lila:adjective .
?le ontolex:canonicalForm ?lemma.
?leITA vartrans:translatableAs ?le;
ontolex:canonicalForm ?liitaLemma.
?liitaLemma ontolex:writtenRep ?wrIT.
FILTER regex(str(?wr), "bil$") .
} group by ?lemma ?liitaLemma
```
**Query the [Compl-IT lexicon](https://dspace-clarin-it.ilc.cnr.it/repository/xmlui/handle/20.500.11752/ILC-1007) to find definitions that begin with the word *uccello* (EN: *bird*), the correspoding Italian entry and the translation into Parmigiano.**

[Results](https://kgccc.di.unito.it/sparql/?default-graph-uri=&query=PREFIX+lime%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Flime%23%3E%0D%0APREFIX+vartrans%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fvartrans%23%3E%0D%0APREFIX+rdfs%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0D%0APREFIX+skos%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F2004%2F02%2Fskos%2Fcore%23%3E%0D%0APREFIX+dct%3A+%3Chttp%3A%2F%2Fpurl.org%2Fdc%2Fterms%2F%3E%0D%0APREFIX+onto%3A+%3Chttp%3A%2F%2Fwww.ontotext.com%2F%3E%0D%0APREFIX+lexinfo%3A+%3Chttp%3A%2F%2Fwww.lexinfo.net%2Fontology%2F3.0%2Flexinfo%23%3E%0D%0APREFIX+ontolex%3A+%3Chttp%3A%2F%2Fwww.w3.org%2Fns%2Flemon%2Fontolex%23%3E%0D%0APREFIX+rdf%3A+%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0D%0ASELECT+%3FliitaLemma+%3Flemma+%3FparmigianoLemma+%3Fwr+%3Fdefinition+WHERE%0D%0A%7B%0D%0A++SERVICE+%3Chttps%3A%2F%2Fklab.ilc.cnr.it%2Fgraphdb-compl-it%2F%3E+%7B%0D%0A++++%3Fword+a+ontolex%3AWord+%3B%0D%0A++lexinfo%3ApartOfSpeech+%5B+rdfs%3Alabel+%3Fpos+%5D+%3B%0D%0A+++++++++++++++++++++++++ontolex%3Asense+%3Fsense+%3B%0D%0A+++++++++++++++++++++++++ontolex%3AcanonicalForm+%3Fform+.%0D%0A++++%3Fform+ontolex%3AwrittenRep+%3Flemma+.%0D%0A++++OPTIONAL+%7B%0D%0A++++++%3Fsense+skos%3Adefinition+%3Fdefinition+%0D%0A++++%7D+.%0D%0A++++OPTIONAL+%7B%0D%0A++++++%3Fsense+lexinfo%3AsenseExample+%3Fexample+%0D%0A++++%7D+.%0D%0A++++FILTER%28str%28%3Fpos%29+%3D+%22noun%22%29+.%0D%0A++++FILTER+%28strstarts%28str%28%3Fdefinition%29%2C+%22uccello%22%29%29.%0D%0A++%7D%0D%0A++%3Fword+ontolex%3AcanonicalForm+%3FliitaLemma.%0D%0A++%3FleItaLexiconPar+ontolex%3AcanonicalForm+%3FliitaLemma%3B%0D%0A+++++++++++++++++++%5Elime%3Aentry+%3Chttp%3A%2F%2Fliita.it%2Fdata%2FLexicalReources%2FDialettoParmigiano%2FLexicon%3E.%0D%0A++%3FleItaLexiconPar+vartrans%3AtranslatableAs+%3FleParLexiconPar.%0D%0A++%3FleParLexiconPar+ontolex%3AcanonicalForm+%3FparmigianoLemma.%0D%0A++%3FparmigianoLemma+ontolex%3AwrittenRep+%3Fwr%0D%0A%7D++group+by+%3Fwr&format=text%2Fhtml&should-sponge=&timeout=0&signal_void=on)
```
PREFIX lime: <http://www.w3.org/ns/lemon/lime#>
PREFIX vartrans: <http://www.w3.org/ns/lemon/vartrans#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX onto: <http://www.ontotext.com/>
PREFIX lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#>
PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

SELECT ?liitaLemma ?lemma ?parmigianoLemma ?wr ?definition WHERE
{
SERVICE <https://klab.ilc.cnr.it/graphdb-compl-it/> {
?word a ontolex:Word ;
lexinfo:partOfSpeech [ rdfs:label ?pos ] ;
ontolex:sense ?sense ;
ontolex:canonicalForm ?form .
?form ontolex:writtenRep ?lemma .
OPTIONAL {
?sense skos:definition ?definition 
} .
OPTIONAL {
?sense lexinfo:senseExample ?example 
} .
FILTER(str(?pos) = "noun") .
FILTER (strstarts(str(?definition), "uccello")).
}
?word ontolex:canonicalForm ?liitaLemma.
?leItaLexiconPar ontolex:canonicalForm ?liitaLemma;
^lime:entry <http://liita.it/data/id/LexicalReources/DialettoParmigiano/Lexicon>.
?leItaLexiconPar vartrans:translatableAs ?leParLexiconPar.
?leParLexiconPar ontolex:canonicalForm ?parmigianoLemma.
?parmigianoLemma ontolex:writtenRep ?wr
}group by ?wr
```
