## 10.1 Docker Compose og docker-compose.yaml

Vi har tidligere sett at det er en ryddigere og mer systematisk måte å bygge containere på ved å bruke en Dockerfile. Da kan man definere alt man ønsker skal være med når man starter containeren, som vilken programvare som skal være installert, hvilke filer som skal kopieres inn og så videre. Dette er et bedre alternativ enn å starte en container, installere det som trengs av programvare og innhold og så lagre denne containeren som et image og senere bruke denne. Da er det vanskligere å gjøre endringer, vanskligere å huske hva containeren egentlig inneholder og generelt vanskligere å gjenskape det samme imaget med noen endringer til å bruke i andre sammenhenger.

Docker compose med den tilhørende docker-compose.yaml filen er en metode som gjør noe av den samme forenklingen for å kjøre containere som Dockerfile gjør for å bygge containere. Ofte trenger man å legge til mange flagg og opsjoner når man starter en container og dette kan gi lange og uoversiktlige docker container run-kommandoer. Man kan gjøre dette på en mye mer ryddig og systematisk måte ved å definere alt som skal skje når man starter en container i en docker-compose.yaml fil. Man kan i en slik fil også velge å starte flere samtidige containere som skal samarbeide om å gi den tjenesten man ønsker. For eksempel kan man med Docker compose samtidig starte både en webserver og en database-server som webserveren henter dataene sine fra. Generelt kan man bruke dette til å sette opp mange forskjellig typer oppsett av samtidige containere på en ryddig og oversiktlig måte. Dermed er det også enkelt å endre på konfigurasjonen og stoppe og starte hele clusteret av containere for å få alt til å virke som man ønsker.

YAML sto opprinnelig for "Yet Another Markup Language" og er som XML et maskinlesbart format som også er inspirert av Python i den forstand at riktig innrykk i teksten er viktig og det fører til feilmeldinger om dette ikke er riktig definert. Derfor må man være svært nøye med innrykk/antall mellomrom og også med å ha mellomrom på riktige steder. Dette gir noe av de samme syntaks-problemene som ved bash-scripting, derfor er det også her en god strategi å sakte bygge opp en docker-compose.yaml fil og teste hver gang man gjør endringer.

---

## 10.2 Docker Compose hello-world

Det gir kanskje ikke så mye mening å bruke Docker compose for å kjøre en hello-world container, men det kan være nyttig å teste ut for å gjøre seg kjent med konseptene. En docker-compose.yaml som starter en hello-world container kan se slik ut:

```
services:
  hello:
    image: hello-world:latest
```

Tidligere var det vanlig å starte med en linje av typen `version: '3.0'` som forteller hvilken Yaml-versjon som skal brukes, men det er ikke lenger nødvendig. Filen viser alle services som skal være med. I dette er det kun en som vi gir navnet 'hello'. Deretter følger hvilket image som skal brukes. Dermed er man klar til å kjøre hello-world containeren med:

```
root@os180:~/compose# docker compose up
[+] Running 1/1
Container compose-hallo-1  Created
Attaching to hallo-1
hallo-1  | 
hallo-1  | Hello from Docker!
```

Tidligere var kommandoen `docker-compose up` og hvis man prøver det får man nå en feilmelding.

Hvis man her ikke markerer at 'hello' er en av tjenestene og skriver filen slik:

```
services:
  hello:
  image: hello-world:latest
```

får man med en gang en feilmelding:

```
root@os180:~/compose# docker compose up
services.image must be a mapping
```

---

## 10.3 Docker Compose nginx

Hvis man ønsker å starte en nginx-container kan man bruke følgende yaml-fil:

```
services:
  nginx:
    image: nginx:latest
```

og starte tjenesten med

```
root@os180:~/compose# docker compose up -d
[+] Running 1/1
Container compose-ng1-1  Started
root@os180:~/compose# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED         STATUS	       PORTS     NAMES
14d123a939af   nginx:latest   “/docker-entrypoint.…” 8 seconds ago Up 7 seconds    80/tcp    compose-ng1-1
```

Hvis dette er første gang man laster ned nginx-imaget, vil det først lastes ned på samme måte som når man kjører `docker run nginx` . Deretter kan man stoppe det hele med:

```
root@os180:~/compose# docker compose down
[+] Running 2/2
Container compose-ng1-1  Removed
Network compose_default  Removed
```

Docker compose rydder opp etter seg ved å fjerne containeren som ble kjørt.

Hvis man ønsker at port 80 som nginx default bruker som source port skal vises som port 8080 på host'en som kjører containeren, kan man gjøre det ved å definere følgende i yaml-filen:

```
services:
  nginx:
    image: nginx:latest
    ports:
      - 8080:80
```

Generelt kan alle parametre og opsjoner man kan gi til `docker container run` defineres i yaml-filen. Deretter kan man starte nginx:

```
root@os180:~/compose# docker compose up -d
[+] Running 0/1
 Network compose_default  Creating
[+] Running 2/2d 
Network compose_default  Created
Container compose-ng1-1  Started
root@os180:~/compose# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED        STATUS          PORTS                  NAMES
6ba1338871fa   nginx:latest   “/docker-entrypoint.…” 34 seconds ago Up 33 seconds   0.0.0.0:8080->80/tcp   compose-ng1-1
```

og man vil kunne få en hilsen fra nginx:

```
# curl localhost:8080
<!DOCTYPE html>
<html>
<head>
<title>Welcome to nginx!</title>
```

Videre kan man på en enkel måte definere en mappe på host'en som nginx skal hente sine web-sider fra ved å legge til følgende rett under ports: i yaml-filen:

```
volumes:
        - ./innhold:/usr/share/nginx/html:ro
```

Dette gjør at man nå vil få opp innhold/index.html filen på host'en når man starter nginx.

---

## 10.4 Tjenester med flere samtidige containere

Det er først og fremst med tanke på å sette opp flere samtidige containere som jobber sammen om å tilby en gitt tjeneste at docker compose virkelig er et kraftig verktøy. Hvis man definerer flere services innen samme docker.compose.yaml fil, vil docker compose også sette opp et lokalt privat nettverk som containerene kan kommunisere på. Dermed kan man for eksempel sette opp et lite nettverk med en database og en web-server som kommuniserer med hverandre.

Følgende yaml-fil definerer to containere som leverer forskjellig innhold på henholdsvis port 8080 og 8081:

```
services:
  nginx:
    image: nginx:latest
      ports:
        - 8080:80
      volumes:
        - ./innhold:/usr/share/nginx/html:ro
  nginx2:
    image: nginx:latest
      ports:
        - 8081:80
      volumes:
        - ./innhold2:/usr/share/nginx/html:ro
```

Dermed kan man starte begge containerene samtidig og se at de virker som de skal. Og stoppe begge etterpå.

```
root@os180:~/compose# docker compose up -d --remove-orphans
[+] Running 3/3
Network compose_default  Created                   0.4s 
Container compose-ng1-1  Started                   0.9s 
Container compose-ng2-1  Started                   0.8s 
root@os180:~/compose# docker ps
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS                NAMES
f0343357eb3a   nginx:latest   “/docker-entrypoint.…” 6 seconds ago Up 6 seconds 0.0.0.0:8081->80/tcp compose-ng2-1
cc1dfa99cf5c   nginx:latest   “/docker-entrypoint.…” 6 seconds ago Up 6 seconds 0.0.0.0:8080->80/tcp compose-ng1-1

root@os180:~/compose# curl localhost:8080
hei 
root@os180:~/compose# curl localhost:8081
hei fra 2
root@os180:~/compose# docker compose down
[+] Running 3/3
Container compose-ng2-1  Removed                  0.8s 
Container compose-ng1-1  Removed                  0.9s 
Network compose_default  Removed
```

Om man går inn i den ene nginx og installerer ping og ifconfig (med apt install iputils-ping net-tools) vil man kunne se at man kan kommunisere over det lokale private nettverket med den andre containeren ved å bruke navnet som er definert i yaml-filen:

```
# docker exec -it f2 bash
root@f2d45f6e9bf5:/# ping nginx2
PING nginx2 (192.168.32.3) 56(84) bytes of data.
64 bytes from test_nginx2_1.test_default (192.168.32.3): icmp_seq=1 ttl=64 time=0.137 ms
```

De to containerene har IPer 192.168.32.3 og 192.168.32.2 og kan kommunisere med hverandre som på andre nettverk. Dette gjør det mulig å sette opp relistiske systemer, ikke minst for å teste kode som man utvikler for dette service-scenariet.

Hvis man for eksempel ønsker å gi containeren et eget navn, kan man bruke variabelen `container_name` .

---

## 10.5 docker-compose build

Man kan kombinere docker-compose med en eller flere Dockerfiles ved å spesifisere en mappe der den tilhørende Dockerfile ligger ved å angi 'build' istedet for image i yaml-filen:

```
services:
  nginx:
    build: ./nginx
    ports:
      - 8080:80
```

Dermed vil docker-compose prøve å bygge et image fra Dockerfile i mappen ./nginx og starte en container med det image't som er resultatet av denne byggingen. Og man kan sette opp en oversiktlig mappestruktur som definerer alle containerene som er med i et compose-prosjekt.

---

## 10.6 Virtuelle maskiner

[Slides brukt i forelesningen](https://www.cs.oslomet.no/~haugerud/vm.pdf)

---

## 10.8 Virtualisering

* Virtualisering av server/desktop hardware
* En hypervisor simulerer hardware ved å gi samme grensesnitt som virkelig hardware gir
* Operativsystemene som kjører på en virtuell maskin, tror de kjører på ekte hardware

Illustrasjon:
.

---

## 10.9 Hvorfor virtualisering?

* Isolasjon
* Ressurssparing
* Fleksibilitet
* Programvare-utvikling
* Skytjenester

Alle disse fordelene gjelder også for containere og Docker, bortsett fra den første, isolasjon og sikkerhet. Men fleksibiliteten blir enda større med containere.

---

## 10.10 Isolasjon

* Tjenester og programmer kan kjøre på hver sin dedikerte server
* Unngår at de forskjellige tjenestene ødelegger for hverandre og gir ryddigere drift
* Men hva om den fysiske serveren eller hypervisor feiler?
* Det meste av nedetid og feil skyldes ikke hardware men software. Og software for en hypervisor er generelt mindre kompleks enn all programvaren på en hel maskin
* Sikkerhet: hvis en tjeneste blir hacket, vil det ikke påvirke de andre tjenestene
* Dette er fordi Operativsystemet og applikasjonene kun kommuniserer mot det virtuelle hardware-API'et som hypervisor gir dem tilgang til. De har ingen mulighet til å kommunisere med andre deler av en hypervisor eller andre VMer.

---

## 10.11 Ressurssparing

* Man kan oppnå isolasjon ved å ha en fysisk server for hver tjeneste, men det gir store driftskostnader
* Med virtualisering kan det samme oppnås på en enkelt server
* Virtuelle maskiner (VMer) som for eksempel bruker lite CPU kan settes på samme fysiske server
* VMer kan enkelt flyttes til og fra fysiske servere og man kan dermed spare hardware og strøm
* Hage, Thomas: *The CERES project - A Cloud Energy Reduction System*, Veileder: Kyrre Begnum (Masteroppgave i Nettverk og Systemadministrasjon, oslomet/UiO)
* `https://www.cs.oslomet.no/teaching/materials/MS100A/html/NSA.html`

---

## 10.12 Fleksibilitet

* Kapasiteten kan enkelt økes ved å legge til flere VMer, lastbalansering blir enklere
* Elastisitet: Man kan dynamisk tildele CPUer og internminne til VMer
* Har en VM blitt ødelagt eller kompromittert kan man enkelt starte opp en ny kopi
* Tradisjonelt er det arbeidskrevende å flytte en tjeneste eller et softwareprosjekt til en ny server på grunn av avhengighet av operativsystemet og annen programvare: når noe er utviklet på en VM så kan hele VMen flyttes eller kopieres
* Live migration: Hele VM flyttes til annen fysisk server uten nedetid på tjenestene
* Ung, Fredrik: *Towards efficient and cost-effective live migrations of virtual machines*, NSA masteroppgave
* Ahmad, Bilal: *Coordinating vertical and horizontal scaling for achieving differentiated QoS*, NSA masteroppgave, Veiledere: Anis Yazidi og Hårek Haugerud

---

## 10.13 Skalering av ressurser

Illustrasjon:
.

---

## 10.14 Programvare-utvikling

* Man kan raskt teste ut programvare på forskjellige operativsystemer, Window, Linux, Mac, etc. ved å kjøre VMer med en rekke forskjellige OS
* Det er enklere å automatisere tester på flere plattformer (Test Driven Development)
* Ønsker man å teste ut nye ideer, kan man raskt sette opp miljøer for å teste dem ut

---

## 10.15 Skytjenester

* Virtualisering er grunnlaget for fleksible skytjenester
* Kunder kan gis egne VMer med et antall CPUer, disk og minne
* Disse kundene kan dele fysiske servere, noe som gir store besparelser av hardware
* Nettbokhandelen Amazon startet med skytjenester fordi de bare hadde bruk for store mengder hardware til webserverene sine før jul og tenkte at de kunne leie ut hardware-ressursene resten av året

---

## 10.16 Historie

* IBM startet med virtualisering av stormaskiner på 1960-tallet
* En VMM (Virtual Machine Monitor) styrte flere virtuelle maskiner på samme fysiske maskin
* Første virtualiseringsløsning for x86: VMware i 1999
* Deretter fulgte Xen, VirtualBox, KVM og mange andre
* Hardware-støtte for x86 virtualisering kom først i 2005

---

## 10.17 Krav til virtualisering

* Popek og Goldberg, 1974: En maskin kan bare virtualiseres hvis alle **sensitive instruksjonene** også er **priviligerte instruksjoner**
* En **Sensitiv instruksjon** kan bare utføres i kernel mode
* En **Priviligert instruksjon** forårsaker en trap til kernel mode hvis den gjøres i user mode

Eksempel:

* X86 instruksjonen POPF (skrur av og på interrupts) er en sensitiv instruksjon
* Hvis den utføres i user mode vil ingenting skje, som for NOP (No Operation)
* Instruksjonen CLI (CLear Interupt flag) er en sensitiv instruksjon, men den er også priviligert. Hvis den utføres i user mode, gjøres en trap til kernel mode
* Vanlige instruksjoner som ADD, CMP og MOV er hverken sensitive eller priviligerte.

---

## 10.18 Hardware støttet virtualisering

* Hardware-støtte for x86 virtualisering kom først i 2005
* Inntil da fantes det sensitive instruksjoner (som POPF) som bare ble droppet
* Gjeste-OS kjører i user mode og vil ikke fungere som på vanlig hardware om en slik instruksjon droppes. Det vil føre til uforutsigbar oppførsel og kan føre til at OS crasher i verste fall.
* Med Intel VT-x og AMD-V vil alle sensitive instruksjoner trap'e til kernel mode når de utføres i user mode

Illustrasjon:
Hardware støttet virtualisering.

---

## 10.19 Type 1 hypervisor

* En type 1 hypervisor kjører direkte på hardware som et OS
* Alle sensitive instuksjoner som utføres i user mode av gjeste-OS må trap'e til kernel mode og fanges opp av hypervisor
* Eksempler: VMware ESX og vSphere, Xen, Hyper-V(Microsoft)

Illustrasjon:
Type 1 Hypervisor.

---

## 10.20 Type 2 hypervisor

* En type 2 hypervisor kjører oppå et eksisternede OS
* Deler av hypervisor kan inngå i det underliggende OS'et i form av kjernemoduler
* Det kan være litt flytende grenser mellom type 1 og type 2
* KVM/Qemu(Linux), VirtualBox, VMware Fusion (Mac)

Illustrasjon:
Type 2 hypervisor.

---

## 10.21 Binær oversettelse

* Før 2005 måtte alternative metoder brukes, uten hardware-støtte
* VMware lagde en hypervisor som mens et program kjører scanner koden etter sensitive instruksjoner
* Dette gjøres for hver kodeblokk som ender i jump, call, trap eller lignende
* Sensitive instruksjoner oversettes til kall til VMware-prosedyrer i hypervisor
* De oversatte kodeblokkene cashes og dette gjør kjøringen effektiv
* Hardware med VT-støtte genererer mange traps og dette tar lang tid
* Noe binær oversettelse finnes også i VirtualBox

---

## 10.22 Paravirtualisering

* Paravirtualisering krever at Gjeste-OS endres
* Alle sensitive instruksjoner erstattes med kall til hypervisor
* Gjeste-OS kan optimaliseres for virtualisering
* Ved å installere drivere laget for paravirtualisering, kan denne metoden bli meget effektiv