* Nok dokumentasjon til at OS-bot kan vedlikeholdes og oppdateres etter at vi er ferdige
  * Dokumentere prosess for å oppdatere vektordatabaser basert på oppdaterte pensumsider og nye videoer osv.
  * "Big picture"-forklaring av prosjektet, skal være forståelig for studentassistent
  * Forklare kort valg av embedding-modell, språkmodell, inferensmotor osv.
  * Dokumentere hvordan vi kjører tester, stress-testing, simulere mange samtidige spørringer

* Stramme opp pipeline for videotranskribering, chunking og ingestion, så det blir enkelt å gjenbruke og oppdatere materiale.

* Bedre logging/innsyn - f.eks eit enkelt Grafana-dashbord som viser trafikk (t.d. spørringar per time) og andre nøkkelmetrikkar. Antall tokens per spørring

* Pedagogisk modus, kanskje kjøre det i starten av semesteret, hvor man ikke "bare" gir lange detaljerte og presise svar, men heller hint om hvordan man kan gå fram for å løse et problem eller forstå noe, eventuelt en slags dialog-metode "Er det ikke noe helt i starten av feilmeldingen du får som kan sette deg på rett spor?"
  * "Socratic tutor"-modus
  * Skal det være opp til brukeren å slå dette av/på, eller er det en innstilling som emneansvarlig skal styre? Begge deler?
  * Legge inn eksempler på hvordan modellen skal svare. oneshot/fewshot

* Inkludere eksamen, jeg har gjennomgang av en del eksamner som kan transkriberes og jeg har testet å fore Claude med PDFer med eksamner og den klarer å tyde det meste.
  * Bør kanskje ikke være del av default kontekst, men kan legges til hvis brukeren spør spesifikt om oppgaver/eksamener?
  * Vi har eksamener helt tilbake til 1998, men det er kanskje mest hensiktsmessig å kun inkludere eksamener fra 2017 og senere?
  * "Har dette vært på en tidligere eksamen?"
  * "Hvilke spørsmål kommer ofte på eksamen?" <- Vanskelig for RAG å svare på
  
* Intro til os-bot - hvilke spørsmål fungerer bra, hvilke spørsmål fungerer ikke
  
* Inkludere oppgaver?
  * Pass på å utelukke oppgaver som ikke er publisert ennå
  * Egen collection med alle oppgaver i oppgavesett, ((kan brukes for å sjekke om brukeren vil ha hjelp med en oppgave og kanskje peile prompten mer inn mot å hjelpe med å løse oppgaven uten å bare gi svaret))

* Forelesningsvideoer som kontekst
  * Kan video embeddes direkte i chatten?
  
* Samtalekontekst (la boten huske hva vi nettopp snakket om)
  * Kan kontekst caches, eller sender vi bare samtalehistorikken sammen med hver nye prompt?
  
* Husk tidligere samtaletråder, slik de fleste offentlige LLM-er gjør
  * Bruk av cookies krever samtykke (GDPR)

* Load-balansering til eksternt API

* Transkripsjoner:
  * Bruke LLM for å gjøre transkripsjonene mer konsise, fjerne irrelevant informasjon
  * Eksperimentere med chunk size og overlap
  * Hente ut mindre chunks enn de som brukes til RAG lookup (altså, gjør lookup med stor chunk, men send en rekke mindre chunks til LLM-en for å få presise timestamps)
  
* Eksperimenter med kontekstvindu, token limits for minne osv.
* Bedre navngiving av referanser

* GraphRAG

* Tekst til tale og omvendt