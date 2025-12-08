## 9.3 Systemkall og timer ticks

Et eksempel på et systemkall er getppid som returnerer PID for prosessens parent, foreldre-prosessen som startet prosessen.

```
rex:~$ grep getppid /usr/src/linux-source-4.4.0/arch/x86/entry/syscalls/syscall_64.tbl 
110	common	getppid			sys_getppid
```

Som vi ser er getppid systemkall nummer 110 for Linux sin 4.4 kjerne. Programmeringsspråket C ble laget samtidig som operativsystemet Unix og er dermed også tett beslektet med Linux. Mange av systemkallene i Linux er egne funksjoner i C. Det er tilfellet for getppid og følgende er et C-program som gjør dette systemkallet 10 millioner ganger.

```
#include<unistd.h>

int main(void) {
   int i;
   for (i=0; i<10000000; i++) {
      getppid();
   }
   return(0);
}
```

Hvis vi ser på timer-ticks før og etter dette programmet, vil vi se at de fleste av tickene finner sted i kernel eller system mode. Vi tester dette med følgende script `sys.sh` :

```
#! /bin/bash

grep cpu3 /proc/stat
taskset -c 3 ./getppid
grep cpu3 /proc/stat
```

Dette scriptet starter getppid-programmet på CPU 3 og leser ticks fra den CPUen før og etter. Ett tick (også kalt jiffie) varer i 10 millisekunder (ett hundredels sekund) og om for eksempel en CPU bruker all tid i user mode når en prosess kjøres på den, vil denne kolonnen øke med 100 ticks i løpet av ett sekund. De fire første kolonnene i `/proc/stat` er som følger:

* user (1) Time spent in user mode.
* nice (2) Time spent in user mode with low priority (nice).
* system (3) Time spent in system mode.
* idle (4) Time spent in the idle task.

og resultatet av kjøringen er:

```
rex:~$ ./sys.sh 
cpu3 6354414 5212787 2789939 218067966 804787 0 198336 0 0 0
cpu3 6354490 5212787 2790067 218067966 804787 0 198336 0 0 0
```

Vi ser at det kun er kolonnene user (1) og system (3) som har endret seg. Av differansen mellom de to første kolonnene ser vi at ved 76 av tickene som ble foretatt mens programmet kjørte, ble programmet kjørt i user-mode. Av differansen i tredje kolonne, ser vi at 128 av tickene skjedde mens programmet var i system elle kernel-mode. Det siste betyr at operativsystemet utførte et systemkall, getppid, på vegne av programmet som ble startet opp i user-mode. Totalt antall ticks adderer opp til 204 og det betyr at programmet totalt brukte 2.04 sekunder CPU-tid på CPU nr 3.

Omtrent det samme kan vi konkludere om vi bruker time-kommandoen til å ta tiden på prosessen:

```
rex:~/undervisning/OSogUNIX/unixnotater/virt$ time ./getppid
Real:2.068 User:0.772 System:1.292 99.83%
```

som viser at programmet bruker 0.77 sekunder i user-mode og 1.29 sekunder i kernel-mode. Hvis man tar tiden på sys.sh scriptet ser man at det stemmer meget godt overens.

```
rex:~$ time ./sys.sh 
cpu3 6355584 5212992 2790765 218120204 804824 0 198434 0 0 0
cpu3 6355662 5212992 2790894 218120205 804824 0 198434 0 0 0
Real:2.072 User:0.780 System:1.284 99.59%
```

---

## 9.4 Prioritet

Det er vanlig å kategorisere prosesser og gi dem prioritet etter hvilken kategori de tilhører.

Hvis en prosess i en høyere prioritetsklasse ønsker å kjøre, for eksempel en kjerne-prosess, overtar den med en gang for prosesser fra en lavere prioritetsklasse og kjører til den er ferdig. Innen samme prioritetsklasse tildeles flere timeslices til prosesser med høyere prioritet, slik at de innen samme Round Robin-kø får mer CPU-tid men kjøres samtidig. FCFS (First Come First Served) er en annen scheduler algoritme som brukes for kjerne-tråder (kthreads) som må bli helt ferdige med det de skal gjøre før de avsluttes.

---

## 9.4.1 Scheduling-algoritmer

Scheduling (skedulering) betegner organiseringen av hvordan man tildeler ressurser til en arbeidsoppgave som skal gjennomføres. I mange sammenhenger trenger man algoritmer som sørger for at en arbeidsoppgave blir effektivt fullført og som fordeler tid eller andre ressurser, organiserer jobbflyt og hvordan prosesser utføres og det trenger ikke nødvendigvis å være prosesser i en datamaskin. Noen vanlige algoritmer er:

* RR (Round Robin) Prosesser kjører på omgang, litt tid hver runde
* FCFS (First Come First Served) Den første prosessen blir først prosessert
* FIFO (First In Firs Out) Samme som FCFS
* SJF (Shortest Job First) Den prosessen som tar kortest tid er den neste som kjøres

---

## 9.4.2 Linux-eksempel: nice

```
$ nice -n 9 regn     # Setter nice-verdi til 9 for prosess regn
$ renice +19 25567   # Endrer nice-verdi til 19
```

* nice vær snill med andre prosesser
* Høyere niceverdi gir mindre CPU-tid til prosessen
* default niceverdi er 0
* top viser niceverdier

---

## 9.5 Prosess-prioritet i Windows

Windows scheduling har store likeheter med Linux. Prosesser får i utgangspunktet en prioritet som kan endres dynamisk. CPU-prosesser gis gradvis mindre, I/O prosesser gradvis mer. Det finnes 4 forhåndsdefinerte prioritetsklasser:

* IDLE PRIORITY CLASS (prioritet 4)
* NORMAL PRIORITY CLASS (8)
* HIGH PRIORITY CLASS (13)
* REALTIME PRIORITY CLASS (24)

Prioritet for en prosess settes til verdier mellom 1 og 31. Prioritet endres dynamisk og prosessen som kjører et aktivt vindu, gis økt prioritet. Dette kan endres fra task-manager hvis man har admin-rettigheter og først velger 'go to details'. Men det er svært stor forskjell på prioritestnivåene som blir satt i task-manager.

---

## 9.6 Prosessforløp

Denne figuren viser de viktigste tilstandene i et prosessforløp. Prosesser som ligger i ready-list ønsker så snart som mulig å bli tildelt tid i prosessoren og dermed komme over i tilstand running. Prosesser som venter av fri vilje eller som for eksempel må vente på Input/Output (I/O) settes i waiting-tilstand.

---

## 9.6.1 Sentrale schedulingbegreper

**Enqueuer**: 
  * Legger i kø
  * Beregner prioritet

**Dispatcher**: 
  * Velger prosess fra READY LIST; liste med prosesser som er klare til å kjøre

---

## 9.6.2 Prosessforløp-demo

[En mp4-demo av dette prosessforløpet kan sees her](https://os.cs.oslomet.no/os/demoer/prosess.mp4)

---

## 9.7 Lage en ny prosess

Det mest sentrale konseptet for et operativsystem er prosessen. De følgende avsnitt viser hvordan prosesser fødes, lever og dør på Linux og Windows. Alle moderne OS har en mekanisme for å lage nye prosesser. Prosesser lages ved

* System oppstart (Linux: init-prosessen)
* En kjørende prosess utfører et systemkall som staret en ny prosess
* En bruker ber om at en prosess startes

Bortsett fra ved systemoppstart er det alttid en prosess som lager en annen og den prosessen kalles en forelder-prosess. I prosessverdenen er det bare en forelder til ett eller flere barn. En parent-prosess lager en child-prosess.

---

## 9.7.1 Linux: fork()

fork() er et Linux-systemkall for å lage en child-prosess. fork() lager en kloning, identisk prosess med kopi av program, data og PCB (bortsett fra PID, PPID og noen andre).

Vanligvis starter child med å laste inn koden for det programmet det skal kjøre, slik at child-prosessen likevel blir forskjellig fra parent-prosessen.

Linux-prosesser lager på denne måten et hierarki av prosesser med barn og barnebarn. Det kan da være mulig å sende signaler til alle prosessene i et hierarki.

---

## 9.7.2 Windows: CreateProcess

Win 32 API'et har også støtte for fork(), men standardmetoden for å lage en ny prosess er å gjøre et kall til `CreateProcess` med 10 parametre. Da lages et nytt prosess-objekt; hvilket program som skal kjøres, vinduer som skal åpnes, prioritet mm overføres med parameterene til kallet. Bindingen mellom parent og child er ikke like sterk som under Linux. Windowsprosesser kan gjøre sine barn arveløse.

---

## 9.8 Avslutte prosesser

Vanligvis avsluttes prosesser når jobben er ferdig. Noen prosesser, såkalte daemons, kjører hele tiden mens systemet er oppe. Prosesser avsluttes ved:

* Normal avslutning. Frivillig. Linux: exit, Windows: ExitProcess
* Avslutning ved feil. Frivillig. (f. eks. 'file not found')
* Fatal feil. Ufrivillig. (division by zero, Segmentation fault, core dumped)
* Drept av annen prosess. Ufrivillig. Linux: kill, Windows: TerminateProcess

---

## 9.8.1 Signaler

Prosesser kan kommunisere med hverandre ved hjelp av signaler. En bruker kan også sende et signal til en prosess, CTRL-C er et eksempel på et slikt signal som prøver å avslutte prosessen. Under Linux kan en prosess selv velge hva den skal gjøre når den mottar et signal. For eksempel er standard oppførsel for en prosess å avslutte når den mottar et CTRL-C signal, men den kan velge å ignorere det. Med kommandoen kill kan man sende mange forskjellige signaler og `kill -9` er et såkalt ustoppelig signal som dreper prosessen enten den vil eller ikke. For kill-signaler er det en forutsetning at den som sender signalet har riktig rettigheter, ellers vil signalet ikke ha noen effekt.

---

## 9.8.2 Signaler og trap i bash-script

En prosess kan stoppes av andre prosesser og av kjernen. Det gjøres ved å sende et signal. Alle signaler bortsett fra SIGKILL ( `kill -9` ) kan stoppes og behandles av bash-script med kommandoen `trap` . Følgende script kan bare stoppes ved å sende ( `kill -9` ) fra et annent shell.

```
#! /bin/bash

# definisjoner fra fra /usr/src/linux-2.2.18/include/asm-i386/signal.h:
#define SIGHUP          1       /* Hangup (POSIX).  */
#define SIGINT          2       /* Interrupt (ANSI).  */
#define SIGKILL         9       /* Kill, unblockable (POSIX).  */
#define SIGTERM         15      /* Termination (ANSI).  */
#define SIGTSTP         20      /* Keyboard stop (POSIX).  */

trap 'echo -e "\rSorry; ignores kill -1 (HUP)\r"' 1
trap 'echo -e "\rSorry; ignores kill -15 (TERM)\r"' 15
trap 'echo -e "\rSorry; ignores CTRL-C\r"' 2
trap 'echo -e "\rSorry; ignores CTRL-Z\r"' 20
trap 'echo -e "\rSorry; ignores kill - 3 4 5\r"' 3 4 5
trap 'echo -e "\rCannot stop kill -9\r"' 9

while [ true ]
do
   echo -en "\a quit? Answer y or n: "
   read answer
   if [ "$answer" = "y" ]
        then break
   fi
done
```

---

## 9.9 OS arkitektur

Den vanligste om ikke den beste måten å designe et OS på er en såkalt monolittisk arkitektur. Linux er et typisk eksempel på dette. Alle metoder i koden har tilgang til alle datastrukturer i kjernen. Dette gjør at kjernen blir hurtig og effektiv, men åpner for flere bugs. Windows NT kjernen er objektorientert og skrevet i C++ og har gjennom dette en ryddigere struktur. En ulempe med Windows er at GUI delvis inngår i kjernen slik at den blir mye mer omfattende. En bedre arkitektur er en såkalt microkernel. Bare det helt essensielle utføres av kjernen, som multitasking og behandling av interrupts. Resten utføres utenfor kjernen av prosesser i usermode som kommuniserer med hverandre og mikrokjernen.

---

## 9.9.1 Linux arkitektur

Illustrasjon:
Linux arkitektur

---

## 9.9.2 Windows arkitektur

Illustrasjon:
Windows arkitektur

---

## 9.10 Design av systemkommandoer

Analogt med forholdet mellom privilegert modus og usermodus er forholdet mellom superuser og en vanlig bruker. Men et program som kjører som root har bare utvidede rettigheter i forhold til filsystemet og devicer, det kjøres ikke som en del av OS-kjernen. To muligheter (eksempler fra Linux) ved design av systemkommandoer.

* Root-rettigheter (noen få: ping, mount, su, ...)
  * tilgang på alle filer
  * mye sikkerhets-overhead (alt må sjekkes)
  * stor sikkerhetsrisiko (kan være sikkerhetshull)
  * betrodd software
* Vanlig bruker-rettigheter (de fleste: ls, ps, mv,...)
  * Sikrere (*begrensede rettigheter*)
  * Lite feilsjekking lite overhead

---

## 9.10.1 Linux-eksempel: setuid-bit

```
group1@osG1:~$ ls -l /bin/ls
-rwxr-xr-x 1 root root 114032 jan.  26  2013 /bin/ls
group1@osG1:~$ ls -l /bin/ping
-rwsr-xr-x 1 root root 36136 april 12  2011 /bin/ping
```

*Kommandoen /bin/ls kjører med vanlige brukerrettigheter, men for /bin/ping 
betyr s'en på eierrettighetene at setuid-bit er satt. Dette betyr at en vanlig 
bruker kjører ping med root-rettigheter. Setuid-programmer er en stor sikkerhetsrisiko.* Setuid-bit settes med

```
$ chmod 4755 program  # Setter SETUID-bit
$ chmod 0755 program  # Skrur av SETUID-bit
```

---

## 9.11 Utbredelse av Operativsystemer

Det finnes mange undersøkelser om utbredelsen av operativsystemer og det er vanskelig å få en eksakt oversikt fra åpne kilder.

---

## 9.11.1 Desktop OS

Følgende er statistikk for desktop-OS basert på hva slags OS de som er inne på web-sider bruker. Slik så tallene ut i 2007:

```
Windows XP      85.30% 
Windows 2000    5.00% 
Mac OS          4.15% 
Windows 98      1.77% 
MacIntel        1.52% 
Windows ME      0.89% 
Windows NT      0.68% 
Linux 	        0.37% 
Windows Vista   0.16%
```

Tallene er hentet fra [marketshare.hitslink.com.]( 
https://marketshare.hitslink.com
) . De blir laget månedlig fra statistikk over hva slags OS som blir brukt av ca 160 millioner besøkende pr måned som er innom mer enn 40.000 forskjellige webservere verden over. En annen kilde med lignende statistikk er [https://gs.statcounter.com.]( 
https://gs.statcounter.com
) .

I 2009 så det slik ut:

```
Windows XP      63.76% 
 Windows Vista 	 22.48% 
 Mac OS X 10.5   5.28% 
 Mac OS X 10.4   2.74% 
 Windows 2000    1.37% 
 Mac OS X        1.00% 
 Linux           0.83%
```

2012:

```
Desktop Operating System Market Share February, 2012
Windows XP     45.39%
Windows 7      38.12%
Windows Vista  8.10%
Mac OS X 10.6  3.00%
Mac OS X 10.7  2.69%
Linux          1.16%
Mac OS X 10.5  0.95%
Mac OS X 10.4  0.23%
Windows 2000   0.15%
Windows NT     0.06%
Windows 98     0.05%
```

2017

```
TOTAL MARKET SHARE
Windows 7       48.41%
Windows 10      25.19%
Windows XP      8.45%
Windows 8.1	6.87%
Mac OS X 10.12  2.91%
Linux           2.05%
Windows 8       1.65%
Mac OS X 10.11  1.55%
Mac OS X 10.10  1.00%
Windows Vista   0.78%
Windows NT      0.39%
Mac OS X 10.9   0.35%
```

2019

```
Windows 7	40.17%
Windows 10	37.35%
Windows 8.1	4.87%
Mac OS X 10.13	4.36%
Windows XP	3.91%
Mac OS X 10.14	1.88%
Mac OS X 10.12	1.51%
Linux	        1.49%
Windows 8	0.99%
Mac OS X 10.11	0.98%
```

2021

```
Windows 10	55.17%
Windows 7	27.09%
Windows 8.1	3.41%
Mac OS X 10.14	3.34%
Mac OS X 10.15	2.96%
Mac OS X 10.13	1.52%
Linux	Linux	1.37%
Windows XP	1.35%
Linux	Ubuntu	0.81%
Mac OS X 10.12	0.65%
```

Illustrasjon:
Slik så trenden ut mellom 2018 og 2019, ikke så store endringer frem til 2021.

Tilsvarende tall for webbrowsere er som følger;

```
2007
Internet Explorer  79.64% 
Firefox            14.00% 
Safari 	           4.24% 
Opera 	           0.87% 
Netscape           0.85% 
Mozilla            0.22%
```

```
2009
Internet Explorer  67.55% 
Firefox            21.53% 
Safari             8.29% 
Chrome             1.12% 
Opera              0.70%
```

```
2012
Internet Explorer  52.84%
Firefox            20.92%
Chrome             18.90%
Safari             5.24%
Opera              1.71%
```

```
2017
Chrome             58.22%
Internet Explorer  19.45%
Firefox            11.73%
Microsoft Edge     5.51%
Safari             3.46%
Opera              1.26%
```

```
2019
Chrome	          65.00%
Internet Explorer 10.23%
Firefox	          9.72%
Edge	          4.33%
Safari	          3.74%
Opera	          1.57%
```

```
2021
Chrome	                68.75
Firefox	                7.91
Edge	                7.36
Internet Explorer	5.86
Safari	                3.64
QQ	                1.76
Sogou Explorer	        1.67
Opera	                1.22
```

---

## 9.11.2 Server OS

Servertall er vanskligere å finne fra åpne kilder. Netcrafts rapport fra Mars 2008 visete at av de 162 millioner webserverene de hadde mottatt respons fra i sin undersøkelse, kjørte ca 60% apache(typisk med Linux som OS), ca 30% Microsoft webserver og 10% på andre plattformer. Fire år etter så det litt anderledes ut, apache hadde økt andelen noe. ( [Se detaljer her.](
http://news.netcraft.com/archives/2012/03/05/march-2012-web-server-survey.html
) ) I 2019 hadde bildet endret seg med flere Microsoft webservere og ( [detaljene kan sees her.](

https://news.netcraft.com/archives/2019/02/28/february-2019-web-server-survey.html
  ) )

I 2020 har bildet igjen endret seg og Nginx er den mest brukte webserveren. ( [detaljene kan sees her.](
https://news.netcraft.com/archives/2020/
  ) )

Det mest korrekte bildet får man trolig av å se på 'active sites' som har reelle webservere som leverer innhold og ikke kun er reklame for f.eks. salg av domenenavn.

[En wikipedia artikkel](
https://en.wikipedia.org/wiki/Usage_share_of_operating_systems
) prøver å gi en oversikt over utbredelse av server-OS.