## 9.2 Dockerhub

Vanligvis laster man ned docker image fra [Dockerhub](https://hub.docker.com) hvor det ligger tusensvis av ferdilagde image som man kan laste ned og bruke, som ubuntu og nginx. Men man kan også lage sitt eget repository og laste opp egne ferdiglagde image dit som andre så kan laste ned og bruke. Anta man vil lage en ubuntu container som har jed installert og bruker følgende Dockerfile:

```
root@os110:~/osbuntu# cat Dockerfile
from ubuntu
RUN apt-get -y update
RUN apt install -y jed
```

Deretter bygger man den og lager et image som man kaller for eksempel osbuntu:

```
root@os110:~/osbuntu# docker build -t osbuntu .
```

I dette tilfellet har jeg en bruker på dockerhub som heter haugerud og jeg må derfor tagge imaget på riktig måte for å laste det opp dit:

```
root@os110:~/osbuntu# docker tag osbuntu haugerud/osbuntu:latest
```

Dette kan også gjøres direkte når man bygger. Default versjon er 'latest', men man kan også lage flere versjoner med egendefinerte versjonsnummer som 1.0, 2.0, etc.

For å kunne pushe et image til Docker Hub må man først logge inn:

```
root@os110:~# docker login
Login with your Docker ID to push and pull images from Docker Hub. If you don't have a Docker ID, head over to https://hub.docker.com to create one.
Username: haugerud
Password: 
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded
```

og så kan man pushe et image:

```
root@os110:~# docker push haugerud/osubuntu:latest
The push refers to repository [docker.io/haugerud/osubuntu]
58657d799cb5: Pushed 
d0729e7aec69: Pushed 
8aaae71fccde: Pushed 
03cb13a80250: Pushed 
b93c1bd012ab: Mounted from library/ubuntu 
1.0: digest: sha256:5d9e384a97484e2af982d940833102b14638b057a286b0ca950906903e4b0220 size: 1368
root@os110:~#
```

Deretter kan hvem som helst laste ned dette imaget fra hvor som helst og sikre seg en fin Ubuntu-container med jed ferdig installert:

```
root@os800:~# docker pull haugerud/osbuntu
Using default tag: latest
latest: Pulling from haugerud/osbuntu
Digest: sha256:55bd19eebe21a365b789dbf7930df2027e3c860f87b31d161f8b143be361bbab
Status: Image is up to date for haugerud/osbuntu:latest
docker.io/haugerud/osbuntu:latest

root@os800:~# docker run -it haugerud/osbuntu /bin/bash
root@601858e8cd75:/# type jed
jed is /usr/bin/jed
```

Hvis man ønsker å laste ned en annen versjon enn latest, for eksempel versjon 1.0, kan man gjøre det på følgende måte:
```
root@os800:~# docker pull haugerud/osbuntu:1.0
```

---

## 9.3 Shell-programmering, oppsummering

|   |   |
|---|---|
| + | Fint til enkle oppgaver der Linux-kommandoer gjør jobben |
| + | Slipper å kompilere |
| + | Pipes, omdirigering: Kraftige verktøy |
| + | bra til enkle systemscript |
| - | dårlig programstruktur (variabel-typer, parameter-overføring, klasser, etc.) |
| - | dårlige feilmeldinger/debugging vanskelig |
| - | kryptisk syntaks |
| - | Veldig langsom sammenlignet med kompilert kode |

---

## 9.4 Hastighet til programmer skrevet i  bash, python, perl, Java og C

Vi skal nå sammenligne hastigheten til programmer skrevet i bash, python, perl, Java og C som utfører følgende kode:

```
for(j=0;j < TIMES;j++)
       {
       sum = 0;
       for(i=0;i < 40000;i++)
          {
          tall = (i + 1)*(i + 1) - i*i;
          sum = sum + tall;
          }
       }
```

I 2010 ble hastigheten til disse programmen testet på to av serverene ved oslomet og resultatene så da slik ut på cube (Linux) og nexus (Solaris):

|   |   |   |   |
|---|---|---|---|
| Språk | CPU-tid i sekunder på cube | CPU-tid i sekunder på nexus | TIMES |
| sh | 248 | - | 1 |
| bash | 5.7 | 11.8 | 1 |
| php | 5.6 | 13.3 | 21 |
| perl | 5.6 | 16.4 | 75 |
| Java | 5.6 | - | 13500 |
| C/C++ | 5.6 | 4.3 | 63000 |

Det viste altså at C-programmet var 63000 ganger raskere enn et bash-script.

På forelesningen i 2019 ble dette resultatene med 500.000 runder i innerste løkke (12 ganger mer enn i 2010):

```
sum.bash:  TIMES = 1;
sum.perl:  TIMES = 36;
sum.py:    TIMES = 44
sum.php:   TIMES = 400;
sum.c:     TIMES = 4100;
Sum.java:  TIMES = 20000;
sumO.c:    TIMES = 28000;
```

på en Linux PC med en Intel Core i7-3770 CPU med klokkefrekvens på 3.40GHz. Det er overraskende at forskjellene er så store. Og at Java er så nær C i effektivitet. Det siste skyldes at java bruker en såkalt JIT(Just-In-Time) kompilator, som kan kompilere hele eller deler av bytekoden om til maskinkode, tilsvarende som når C kompileres, rett før programmet kjøres. Forøvrig bruker java for å gjøre dette delvis to CPUer. Om java-programmet tvinges til å kjøre på en CPU, reduseres TIMES til 17000.

Forøvrig er resultatet for sum.c om man kompilerer med gcc uten å bruke opsjonen `-O` . Da kompileres programmet hurtig, men ikke med fokus på at det skal kjøre raskt. Programmet sumO.c er kompilert med `-O` og da går C-programmet mye raskere.

Å finne ut om forskjellen på Linux-VM'ene er den samme er en av ukens øvingsoppgaver.

Men det er viktig å teste på nøyaktig det man er ute etter. Følgende kode leser en fil og skriver den til en annen fil med linjenummer:

```
#! /bin/bash

echo "" > /tmp/ny.fil
nr=0
while read line
do
    (( nr++ ))
    echo "$nr: $line" >> /tmp/ny.fil
done < /tmp/stor
echo "Read $nr lines"
```

Testes dette på å lese en 13 Mbyte tekstfil på studssh gir det:

|   |   |
|---|---|
| Språk | CPU-tid i sekunder |
| bash | 68.57 |
| Java | 17.04 |
| php | 9.3 |
| perl | 2.18 |
| C++ | 2.00 |

Og som man ser er forskjellene mye mindre.

Følgende avsnitt om regulære uttrykk betegnes i dette kurset som "referansestoff". Dette er stoff som det er interessant og viktig å vite om og som kan være nyttig å bruke i praksis, men dette stoffet vil det ikke bli spurt om til eksamen og er slik sett ikke en del av pensum.