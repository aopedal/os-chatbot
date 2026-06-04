
* Sammenlign de ulike embedding modellene og vektordatabasene for å se hva som gir best resultater. Kan automatiseres:
  - Develop a comparison pipeline:
    - Come up with some good benchmark questions to identify decent and poor embedding model quality. Can be done by feeding a few knowledge files directly to the LLM at a time and asking it to identify good questions for this purpose.
    - Ask each question to each of the 10 configurations, and record the responses.
    - Feed each set of 10 responses back to the LLM, and ask it to rank them based on some criteria.
    - Whichever configuration gets the highest total score is our winner.
    
* Bør kanskje kunne gå inn og se samtalene studentene har med systemet, for å avdekke hva det brukes til og mulige forbedringsområdet
  * Må selvsagt informere tydelig om at samtalene kan bli lest av andre mennesker