* Forelesningsvideoer som kontekst
  * Egen collection i vectordb for å sikre at vi henter kilder både i pensummateriale og i forelesningsvideoer
  * Tagges med timestamp, slik at vi kan lage link til rett sted i videoen
  * Kan video embeddes direkte i chatten?
* Samtalekontekst (la boten huske hva vi nettopp snakket om)
  * Kan kontekst caches, eller sender vi bare samtalehistorikken sammen med hver nye prompt?
* Husk tidligere samtaletråder, slik de fleste offentlige LLM-er gjør
* Mulighet for oppslag i oppgaver / gamle eksamener
  * Bør kanskje ikke være del av default kontekst, men kan legges til hvis brukeren spør spesifikt om oppgaver/eksamener?
  * Pass på å utelukke oppgaver som ikke er publisert ennå
  * Vi har eksamener helt tilbake til 1998, men det er kanskje mest hensiktsmessig å kun inkludere eksamener fra 2017 og senere?
  * Mange eksamener har screenshots i fasit. Blir da vanskelig å se for seg hvordan eksamener skal berike i praksis.
    * "Har dette vært på en tidligere eksamen?"
    * "Hvilke spørsmål kommer ofte på eksamen?" <- Vanskelig for RAG å svare på, kanskje CAG er bedre egnet
* Caching av spørsmål som allerede er stilt, gjenbruk av svar for å spare ressurser
  * Kan en LLM eller embedding-modell raskt avgjøre om essensen i et spørsmål tilsvarer et som allerede er stilt?
  * Tommel opp / tommel ned på svar, kan regenereres hvis det blir gitt tommel ned
* Debug view i frontend for å se endelig prompt som sendes til LLM
* Bør kanskje kunne gå inn og se samtalene studentene har med systemet, for å avdekke hva det brukes til og mulige forbedringsområdet
  * Må selvsagt informere tydelig om at samtalene kan bli lest av andre mennesker
* Load-balansering til eksternt API
* Stresstesting

- Develop a comparison pipeline:
  - Come up with some good benchmark questions to identify decent and poor embedding model quality. Can be done by feeding a few knowledge files directly to the LLM at a time and asking it to identify good questions for this purpose.
  - Ask each question to each of the 10 configurations, and record the responses.
  - Feed each set of 10 responses back to the LLM, and ask it to rank them based on some criteria.
  - Whichever configuration gets the highest total score is our winner.