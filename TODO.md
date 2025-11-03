* Forelesningsvideoer som kontekst
  * Egen collection i vectordb for å sikre at vi henter kilder både i pensummateriale og i forelesningsvideoer
  * Tagges med timestamp, slik at vi kan lage link til rett sted i videoen
  * Kan video embeddes direkte i chatten?
* Streaming responses (vis svaret linje for linje mens det genereres)
* Samtalekontekst (la boten huske hva vi nettopp snakket om)
  * Kan kontekst caches, eller sender vi bare samtalehistorikken sammen med hver nye prompt?
* Husk tidligere samtaletråder, slik de fleste offentlige LLM-er gjør
* Mulighet for oppslag i oppgaver / gamle eksamener
  * Bør kanskje ikke være del av default kontekst, men kan legges til hvis brukeren spør spesifikt om oppgaver/eksamener?
  * Pass på å utelukke oppgaver som ikke er publisert ennå
* Caching av spørsmål som allerede er stilt, gjenbruk av svar for å spare ressurser
  * Kan en LLM eller embedding-modell raskt avgjøre om essensen i et spørsmål tilsvarer et som allerede er stilt?
  * Tommel opp / tommel ned på svar, kan regenereres hvis det blir gitt tommel ned
* Debug view i frontend for å se endelig prompt som sendes til LLM
* Load-balansering til eksternt API
* Stresstesting