## 6.3 branch prediction

* Ved en branch i programmet (if-test), vet man ikke hva neste instruksjon er
* Stort problem for pipelining, må vente på resultatet fra forrige instruksjon
* Gjetter, basert på erfaring, hvilken branch (gren) som følges i programmet og utfører den
* Speculative execution, må gjøres om hvis feil
* I et superskalær arkitektur kan begge grener delvis utføres på forhånd

Følgende `C++` program inneholder kode som viser hva konsekvensene av branch prediction kan være. I starten av programmet lages et data-array med tilfeldig trukkede heltall mellom 0 og 255. De 10 første tallene blir skrevet ut og så gjentas en ytre løkke 100.000 ganger for at man skal få mer nøyaktige målinger av hvor lang tid den indre løkken tar. Den indre løkken består av at man går igjennom hvert element i det store arrayet og legger til verdien `data[c]` til en variable sum hvis verdien er større enn 127. I praksis vil dette skje omtrent halvparten av gangene.

```
#include <algorithm>
#include <iostream>

using namespace std;

int main()
{
   // Lager et data-array
   int i,c;
   int arraySize = 32768;
   int data[arraySize];
   
   for (c = 0; c < arraySize; ++c)
     {
       data[c] = rand() % 256;
     }
   
   // Gir tilfeldig tall mellom 0 og 255
   // Gir samme array med tall for hver kjøring
	
   // sort(data, data + arraySize);
   // sorterter data-arrayet
   
   // Skriver ut de 10 første verdiene
   for (c = 0; c < 10; c++)
     cout << data[c] << "\n";
   
   // Legger sammen alle tall større enn 127
   long sum = 0;
   
   // Ytre løkke for at det skal ta litt tid...
   for (i = 0; i < 100000; ++i)
     {
        // Indre løkke
        for (c = 0; c < arraySize; ++c)
           {
             if (data[c] > 127)
             sum += data[c];
           }
     }
   
   cout << "sum = " << sum << "\n";
}
```

Deretter kompileres `C++` programmet og kjøres på en Linux-maskin:

```
$ g++ b.cpp
$ time ./a.out 
103
198
105
115
81
255
74
236
41
205
sum = 314931600000
Real:17.095 User:17.096 System:0.000 100.00%
```

Kommandoen `time` tar tiden på programmet som kjøres og gir som resultat at programmet har brukt 17.096 sekunder CPU-tid og at det har brukt CPU-en hele tiden (100%). Utskriften av de 10 første tallene viser at verdiene kommer i en tilfeldig rekkefølge og at de er over og under 127, slik at if-testen vil slå til en gang i blant og i gjennomsnitt ca halvparten av gangene.

Deretter gjøres en enkelt endring på koden ved at kommentartegnet foran linjen

```
sort(data, data + arraySize);
```

fjernes, slik at data-arrayet blir sortert før programmet kjører de to løkkene. Dette vil endre rekkefølgen for når if-testen slår til og dataene adderes til sum-variabelen, men det vil skje nøyaktig like mange ganger og som vi ser blir også summen nøyaktig den samme:

```
0
0
0
0
0
0
0
0
0
sum = 314931600000
Real:6.285 User:6.280 System:0.000 99.91%
```

Utskriften av de første 10 elementene viser at data-arrayet er sortert og starter med alle 0-verdiene. Men det overraskende er at denne kjøringen går mer en dobbelt så fort og nesten bare tar en tredjedel av tiden til den første kjøringen. Og dette til tross for at nøyaktig de samme instruksjonene blir utført i begge tilfeller og det samme regnestykket gir samme resultat. Hva kan dette skyldes?

---

## 6.4 Meltdown

* Et hardware-sikkerhetshull funnet i 2018
* Rammet Intel, ARM og IBM-prosessorer
* Meltdown utnytter at både koden som sjekker om prosessen kan lese fra RAM og lesingen fra RAM delvis utføres
* Meltdown kan dermed lese data fra andre prosesser som er cache't men ennå ikke fjernet pga feil branch
* Spectre brukte lignende metoder til å lese passord og sensitive data
* Betegnet som sikkerhets-katastrofe
* Både CPU design og operativsystemer ble endret for å hindre Meltdown og Spectre i å virke

---

## 6.5 Viktig å huske fra datamaskinarkitektur

På veien videre er det viktigste å huske fra datamaskinarkitektur at alt CPU-en gjør er å slavisk utføre maskininstruksjoner en for en i en evigvarende løkke; ihvertfall til maskinen skrus av. Legg også merke til at det ikke er noen en til en forbindelse mellom instruksjoner i høynivåkode og maskinkode. En linje kode i høynivåspråk fører ofte til mange maskininstruksjoner i det kompilerte programmet.

---

## 6.6 OS historie

Det er nyttig å vite litt om historien til noen av de mest brukte operativsystemene.

---

## 6.6.1 Microsoft Desktop-OS

**MS-DOS**: 1981, 16-bit

**Windows**: 1.0 i 1985, 3.0 i 1990, GUI på toppen av DOS

**Windows 95**: Noe 32-bit kode, mye 16-bit Intel assembler,DOS-filsystem, bruker DOS til å boote

**Windows 98**: essensielt som 95, desktop/Internett integrert

**Windows Me**: essensielt som 98, mer multimedia og nettverk support

**Windows 2000**: Første (ikke så vellykkede) forsøk med Desktop OS basert på NT (5.0).

**Windows XP**: Oktober 2001, Desktop-OS som kombinerer NT 5.1 kode med Win 9x. Home edition: 1 CPU, XP Professional: 2CPU-er, logge inn utenfra, 32 og 64 bit

**Windows Vista**: januar 2007. Kernel NT 6.0, Booter raskere, bedre filsøk, Ingen suksess.

**Windows 7**: oktober 2009, kjernen er Windows NT 6.1, PowerShell 2.0 default, 7 editions, Service Pack 1

**Windows 8**: oktober 2012, NT 6.2, Start Screen, touch screen, USB 3.0, Windows Store, Windows RT for ARM

**Windows 8.1**: oktober 2013, NT 6.3

**Windows 10**: July 2015, NT 10.0(!), Microsoft Edge, virtual desktops, native Ubuntu bash shell(samarbeid med Canonical) gjennom Windows Subsystem for Linux

**Windows 11**: October 2021, NT 10.0(!), ikke lenger støtte for 32-bit x86 CPUs, Internet Explorer ikke inkludert

*Intels første 32-bit maskin var 386 fra 1985. 
Generelt problem før XP: Windows er bakover-kompatibelt til DOS, alle Win-prosesser kan ødelegge 
for kjernen og ta ned OS.*

---

## 6.6.2 Microsoft Server-OS

**NT 3.1**: 1993 32-bit, skrevet fra scratch i C (lite assembler), David Cutler (VAX-VMS designer), mye bedre sikkerhet og stabilitet enn Windows. 3.1 millioner linjer kode.

**NT 4.0**: 1996, Samme GUI som Win-95, 16 millioner linjer, portabelt `->` alpha, PowerPC

**Windows 2000**: NT 5.0, opp til 32 CPU'er, features fra Win-98, Plug and Play, `\winnt\system32\ntoskrnl.exe`. 29 millioner linjer. *MS-DOS borte, men 32-bits kommando-interface med samme funksjonalitet.*

**Windows Server 2003**: bygger på 2000 server, NT 5.2, design med tanke på .NET: web, XML, C#, 32 og 64 bit, SP1, SP2, R2 i 2006

**Windows Server 2008**: februar 2008, felles basis med Vista, første OS med PowerShell, Kan installeres som **Server core** og styres fra CLI (Command Line Interface), Hyper-V virtualisering

**Windows Server 2008 R2**: oktober 2009, NT 6.1 (som Win 7), PowerShell 2.0 default, kun 64 bit

**Windows Server 2012**: september 2012, NT 6.2 (som Win 8), cloud computing, oppdatert Hyper-V, nytt filsystem: ReFS

**Windows Server 2012 R2**: oktober 2013, NT 6.3 (som Win 8.1)

**Windows Server 2016**: september 2016, NT 10.0, Windows Defender, nano server: uten gui, fjernstyres med PowerShell

**Windows Server 2019**: oktober 2018, NT 10.0, Windows Admin Center

**Windows Server 2022**: August 2021, NT 10.0.2

---

## 6.6.3 Unix operativsystemer

Dagens Unix-versjoner har utviklet seg fra to som dominerte rundt 1980:

* system V (AT&T Bell Labs)
* BSD (University of California at Berkely )

De fleste av dagens varianter er bygd på SVR4 som er en blanding. Følgende er kommersielle 64 bit Unix-OS for RISC-prosessorer som var dominerende i server-markedet et stykke inn på 2000-tallet:

| OS | Eier | hardware |
|---|----|--------|
| AIX | IBM | RS6000, Power |
| Solaris | Sun | Sparc, intel-x86 |
| HP-UX | Hewlett-Packard | PA-RISC, Itanium(IA-64) |
| Tru64 UNIX(Digital Unix) | HP(Compaq(DEC)) | Alpha |
| IRIX | Silicon Graphics | SGI |

Oracle stanset vidreutviklingen av Solaris, det største av Unix-operativsystemene, i 2017. Idag er det x86 servere som dominerer og de fleste med Linux. Frie Unix-kloner for mange plattformer:

| OS | hardware |
|---|--------|
| FreeBSD | x86, Alpha, Sparc |
| OpenBSD | (sikkerhet) x86, Alpha, Sparc, HP, PowerPC, mm |
| NetBSD | x86, Alpha, Sparc, HP, PowerPC (Mac), PlayStation, mm |
| Darwin | (basis for Mac OS X og iOS, kjernen, XNU, bygger på FreeBSD og Mach 3 microkernel) , intel x86, ARM, PowerPC |
| Linux | x86, Alpha, Sparc, HP, PowerPC, PlayStation 3, Xbox, stormaskin, mm |

---

## 6.6.4 Interrupts (avbrytelser)

* Signal fra hardware
* CPU-en avbrytes for å håndtere signalet
* Lagrer adressen til neste instruksjon på stack og hopper til interrupt-rutinen
* Hvert interrupt-nr (IRQ) har sin rutine

---

## 6.7 Singletasking OS

Basis for flerprosess-systemer.

---

## 6.7.1 Internminne-kart

*Stack: brukes bl. a. til å lagre adressen som skal returneres til ved subrutinekall.*

---

## 6.8 Multitasking-OS

*For å lage et system som kan kjøre n programmer samtidig, må vi få en enprosess maskin til 
å se ut som n maskiner.*

*Bruker software til å fordele tid mellom n programmer og å dele ressurser; minne, disk, skjerm etc. 
OS-kjernen utfører denne oppgaven.*

Samtidige prosesser må tildeles hver sin del av minne:

Illustrasjon:
Minnekart for et multitasking system

---

## 6.9 Multitasking

Multitasking gjør at man kan kjøre flere programmer samtidig selvom man bare har en CPU. I prinsippet er CPU-en meget enkel på den måten at den gjør en og en maskinistruksjon av gangen. Som for eksempel å legge sammen to tall, å sammenligne to bit-strenger (1010001101101110 = 1010001100101110?) eller å lagre en streng med binære tall i internminnet(RAM). Et multitasking operativsystem får det til å se ut som om mange programmer kan kjøre samtidig ved å dele opp tiden i små biter (timeslices) og la hver prosess som kjører få en bit CPU-tid (typisk et hundredels sekund) av gangen i et køsystem (såkalt Round Robin kø). Metoden som alle moderne OS bruker er Preemptive multitasking. Metoden består i at en hardware timer (klokke) jevnlig sender et interrupt-signal som gjør at første OS-instruksjon legges inn i CPU-en. Dermed unngås det at vanlige brukerprosesse tar over kontrollen. OS lar hver prosess etter tur bruke CPU-en i et kort tidsintervall. Alle prosesser ser da ut til å kjøre samtidig. Når OS switcher fra prosess P1 til prosess P2 utføres en såkalt Contex Switch (kontekst svitsj).

Illustrasjon:
Prosessene P1, P2 og P3 kjører samtidig under et multitasking OS. En 
Context Switch utføres hver gang en prosess gis CPU-tid. Typisk tid for context-switch: 0.001 ms (ms = millisekunder = tusendels sekund). Timeslice = 10 ms for Linux på Intel.

---

## 6.10 PCB -Process Control Block

Process Control Block (PCB) er Prosessens tilstandsbeskrivelse: prioritet, prosessormodus, minne, stack, åpne filer, I/O, etc. PCB inneholder bl. a. følgende:

* CPU registre
* pekere til stack
* prosesstilstand (sleep, run, ready, wait, new, stopped)
* navn (PID)
* eier (bruker)
* prioritet (styrer hvor mye CPU-tid den får)
* parent prosess
* ressurser (åpne filer, etc.)

---

## 6.11 Timesharing og Context Switch

CPU-scheduling = å fordele CPU-tid mellom prosessene = Time Sharing Metoden som alle moderne OS bruker er Preemptive multitasking med en Round Robin kø. OS lar hver prosess etter tur bruke CPU-en i et kort tidsintervall (timeslice). Alle prosesser ser da ut til å kjøre samtidig. Når OS switcher fra prosess P1 til prosess P2 utføres en Contex Switch.

Illustrasjon:
Prosessene P1, P2 og P3 kjører samtidig under et multitasking OS. En 
Context Switch utføres hver gang en prosess gis CPU-tid. Typisk tid for context-switch: 0.001 ms. Timeslice = 10 ms for Linux på Intel.

*All PCB-info må lagres i en Context Switch -> tar tid  -> systemoverhead*

Illustrasjon:
CPU info lagres i PCB ved en Context Switch

---

## 6.12 Multitasking i praksis, CPU-intensive programmer

Et program som oversetter kildekode til maskinkode (kompilator) eller et program som hele tiden regner med tall, vil bruk så mye CPU-tid som det klarer å få tak i. Prosesser som kjører slike programmer kalles CPU-intensive. De fleste vanlige programmer som browsere, tekstbehandlingsprogrammer, tengeprogram etc. bruker lite CPU og det er dette som gjør at multitasking av hundretalls samtidige prosesser går helt greit uten at brukeren oppfatter datamaskinen som treg. Vi skal nå se hva som skjer når vi kjører flere instanser av et mulititasking program på systmer med en eller flere CPU'er.

Programmet vi bruker er et lite shell-script som står i en løkke og regner og regner. Da vil det hele tiden ha behov for CPU-en. Siden prosessen aldri har behov for å vente på data fra disk, tastatur eller andre prosesser, kan den regne uten stans. Programmet heter `regn` og ser slik ut:

```
#! /bin/bash

# regn (bruker CPU hele tiden)

(( max = 100000 ))
(( i = 0  ))
(( sum = 0  ))

echo $0 : regner....
while (($i < $max))
do
        (( i += 1 ))
        (( sum += i  ))
done
echo $0, resultat: $sum
```

---

## 6.13 Multitasking eksempel

*Bare rene regneprosesser bruker CPU hele tiden. Vanlige prosesser
  venter mye på I/O (Input/Output fra disk, nettverk etc.) og
  multitasking gir da mer effektiv utnyttelse av CPU.*

Illustrasjon:
Prosessene A og B kjørt med single og multitasking

---

## 6.14 CPU-intensiv prosess på system med èn CPU

Med kommandoen `lscpu` kan man hente ut mye nyttig informasjon om cpu og cache:

```
user@chokeG7:~$ lscpu 
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
Address sizes:       40 bits physical, 48 bits virtual
CPU(s):              1
On-line CPU(s) list: 0
Thread(s) per core:  1
Core(s) per socket:  1
Socket(s):           1
NUMA node(s):        1
Vendor ID:           AuthenticAMD
CPU family:          15
Model:               65
Model name:          Dual-Core AMD Opteron(tm) Processor 2216
Stepping:            3
CPU MHz:             2400.114
BogoMIPS:            4800.22
Hypervisor vendor:   Xen
Virtualization type: full
L1d cache:           64K
L1i cache:           64K
L2 cache:            1024K
NUMA node0 CPU(s):   0
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt rdtscp lm 3dnowext 3dnow rep_good nopl cpuid extd_apicid pni cx16 x2apic hypervisor lahf_lm cr8_legacy 3dnowprefetch vmmcall
```

Dette viser at denne Linux-maskinen har èn enkelt 64-bits CPU med en klokkefrekvens på 2.4 GHz. Utskriften viser også at dette er en virtuell maskin, man kan se at den er virtualisert med Xen utifra de to linjene

```
Hypervisor vendor:   Xen
Virtualization type: full
```

Videre kan man se størrelsen på L1 og L2 cache. En rask og tydelig oversikt kan man få med kommandoen `lstopo` :

```
lstopo --no-io
```

som gir følgende figur

Illustrasjon:
CPU-topologi generert av lstopo den virtuelle maksinen chokeG7.

Vi starter en instans av programmet `regn` som er CPU-intensivt og bruker så mye CPU det kan få:

```
mroot@chokeG7:~$ ./regn 
./regn, resultat: 3125001250000
```

Samtidig startes `top` og man kan se at prosessen med PID (Process ID) 18908 forsyner seg grovt av CPU-en og klarer å karre til seg 99.3% av CPU-tiden. Verdien som vises er gjennomsnittsverdien for de siste 3 sekunder.

```
top - 14:32:39 up 10 days, 23:56,  2 users,  load average: 0,09, 0,12, 0,05
Tasks:  74 total,   1 running,  73 sleeping,   0 stopped,   0 zombie
%Cpu(s):  0,0 us,  0,7 sy,  0,0 ni, 99,0 id,  0,0 wa,  0,0 hi,  0,0 si,  0,3 st

PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                    
18908 mroot     20   0    9504   3244   3008 R  99,3   0,7   0:07.16 regn                                       
18903 mroot     20   0   16668   4668   3536 S   0,3   1,0   0:00.04 sshd
```

Vi starter så en instans til av programmet som regner i vei, uavhengig av den første. Da ser vi at OS fordeler CPU-en likt mellom de to prosessene og de får i underkant av 50% hver av CPU-tiden.

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND                                    
18912 mroot     20   0    9504   3224   2988 R  49,8   0,7   0:13.14 regn                                       
18913 mroot     20   0    9504   3312   3080 R  49,8   0,7   0:12.84 regn
```

Dette betyr at reelt sett er det til enhver tid bare en prosess som kjører, men det oppleves som om de kjører samtidig fordi OS deler opp tiden i små biter(1-10 hundredels sekunder) og lar dem bruke CPU-en annenhver gang. Husk at for en prosess er ett hundredels sekund lang tid, den kan rekke å utføre millioner av maskininstruksjoner på den tiden.