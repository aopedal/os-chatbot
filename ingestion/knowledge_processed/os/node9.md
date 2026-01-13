## 8.1.2 Vaffel-video

[Video som demonstrerer multitasking av forelesning og vaffelrørelaging](https://os.cs.oslomet.no/os/vaffel.mp4)

---

## 8.3 Hvorfor kan ikke en prosess bruke to CPU-er?

Det ville vært ønskelig om et vilkårlig program kjøres fire ganger så raskt på en maskin med en quadcore prosessor(4 CPU'er på en brikke) som på en maskin med en enkelt CPU av samme type. Men det gjør generelt et program ikke, det bruker like lang tid om det har fire prosessorer, for det klarer bare å utnytte en prosessor av gangen. Slik at man bare får en gevinst av de fire prosessorene om man har flere programmer som kjører samtidig.

For å undersøke hvorfor det er slik, ser vi på assemblerkoden for et program som regner ut Fibonacci-rekken, 1 1 2 3 5 8 13 21 34 55 ..... I denne rekken er neste tall summen av de to foregående. Assemblerkode ligger tett opp til maskinkode, det er en litt mer lesbar utgave av maskininstruksjoner og kan sees på som den koden som CPU-en utfører en for en:

```
1. mov 1, %ax    # %ax = 1
2. mov 1, %bx    # %bx = 1
3. add %ax, %bx  # %bx = %bx + %ax
4. add %bx, %ax  # %ax = %ax + %bx
5. jmp 3
```

Etter hver runde i denne evige løkken, vil ax og bx være siste og nest siste ledd i Fibonacci-rekken som er regnet ut. I instruksjon 3 settes bx lik summen av de to og i nummer 4 settes ax lik summen av de to og dermed har vi kommet to stepp videre i beregningen. Vi ser at det ikke er mulig for et operativsystem å fordele bergningene i en slik algoritme på flere CPU'er. Neste ledd i beregningen avhenger av det forrige og det tar uforholdsmessig lang tid å flytte verdier av registre fra en CPU til en annen. I dette tilfellet lar ikke algoritmen seg naturlig dele opp i separate bergningsdeler og da vil det også være vanskelig for en programmerer å dele opp beregningen i flere prosesser for å utnytte flere prosessorer. Følgende eksempel som regner ut summen er det i prinsippet letter å dele opp eller parallellisere som det kalles:

```
1. mov 2001, %ax
2. mov 1, %bx
3. mov 0, %cx
3. add %bx, %cx   # %cx += %bx
4. inc %bx        # %bx++
5. cmp %bx %ax    
6. jne 3          # Hopp til linje 3 hvis %bx ikke er lik 2001
```

Etter dette programmet er avsluttet vil registreret cx være lik . Det er lett å se at denne algoritmen i prinsippet kan deles i to. En CPU kan regne ut og en annen CPU kan regne ut og så legger man sammen svarene til slutt. Men poenget er at operativsystemet ikke har noen anelse om hva som foregår i et vilkårlig program. Det bare sørger for at prosessene får utført sine instruksjoner. Derfor er det programmereren som eksplisitt må skrive programmet slik at det kjøres som to uavhengige prosesser for at det skal kunne utnytte flere CPU'er. En annen løsning er at programmet inneholder flere tråder(threads) som kan kjøres på hver sin CPU, dette kommer vi tilbake til senere. Threads i denne sammenhengen har ikke noe med hyperthreads å gjøre, disse threads styres av OS og ikke av prosessoren. Det har også blitt utviklet kompilatorer som til en viss grad klarer å parallelisere kode. Men operativsystemet kan ikke gjette seg til hva programmet gjør og kan derfor ikke på egenhånd få en enkelt prosess til å utnytte flere prosessorer.

Moderne spillkonsoller inneholder ofte mange CPU'er, XBOX 360 har tre og Playstation 3 har åtte CPU'er. For å kunne utnytte disse må spill-programmen som kjøres på dem skrives slik at de kan utnytte alle prosessorene. Programmererne deler da opp oppgavene i uavhengige deler slik at de kan beregnes hver for seg. Dette kalles å parallellisere koden. Tidligere var dette bare viktig i såkalte clustere satt sammen av mange datamaskiner, men med dagens utvikling hvor etterhvert alle datamakiner har flere CPU'er er dette viktig for alle programmer.

---

## 8.4 Samtidige prosesser

To prosesser (tasks) må ikke ødelegge for hverandre:

* skrive til samme minne
* kapre for mye CPU-tid
* få systemet til å henge

Beste løsning:

All makt til OS = Preemptive multitasking

**Linux, Windows, Mac**: Preemptive multitasking, *"Preemptive"= rettighetsfordelende. Opprinnelig betydning: Preemption = Myndighetene fordeler landområde.*

**Windows 3.1**: Cooperative multitasking, prosessene samarbeider om å dele på CPU-en. *En prosess kan få hele systemet til å henge.*

---

## 8.5 Prosessor modus

Alle moderne prosessorer har et modusbit [5](footnode.html#foot1251) som kan begrense hva som er lov å gjøre. Modusbit switcher mellom bruker og priviligert modus. Dette kalles også protection hardware og er nødvendig for å kunne kjøre multitasking.

* Bruker modus: User mode. begrenset aksess av minne og instruksjoner; må be OS om tjenester.
* Priviligert modus: Kernel mode. Alle instruksjoner kan utføres. Alt minne og alle registre kan aksesseres.

Se avsnittet Protection Hardware i 1.5.7 i Tanenbaum. Se også bruken av hjelm som hardware protection senere i forelesning.

---

## 8.6 Hvordan kan OS effektivt kontrollere brukerprosesser?

**Problem:**: OS kan ikke tillate en prosess/bruker å ta kontroll over maskinen. Men hvis OS skal kontrollere hver instruksjon en bruker-prosess utfører (emulering) gir det meget stor systemoverhead.

**Effektiv løsning:**: OS bruker en hardware timer til å gi et begrenset tidsintervall til en brukerprosess og switcher til brukermodus og laster inn 1. brukerinstruksjon. Når tiden er ute, hopper CPU til OS-kode og OS overtar. Hver eneste CPU får sine individuelle timer-interrupt, slik at OS tar over kontrollen med jevne intervaller; typisk hvert hundredels skund.

---

## 8.7 Bruker/Priviligert minne-kart

Det er helt vesentlig at operativsystemet har støtte fra hardware for å kunne kontrollere at vanlige programmer ikke skriver til vilkårlige deler av internminnet. Det varierer hvor stor del av de forskjellige operativsystemene som finnes som ligger i kjernen, det vil si, ligger i den priviligerte delen av minnet som kun kan nås i priviligert prosessormodus.

Illustrasjon:
Modusbit må switches til priviligert modus for å kunne kjøre kode 
fra priviligert del av minne (OS-kjernen). Deler av OS ligger utenfor kjernen og kan 
kjøres fra brukermodus.

---

## 8.8 Systemkall

Anta at en vanlig bruker utfører Linux-kommandoen `ls` . En slik kommando ber om å lese noe som ligger på harddisken og er da nødt til å få hjelp av OS-kjernen for brukerprogrammer har aldri direkte aksess til eksterne enheter. Programmet `ls` inneholder derfor bl. a. systemkallet `readdir()` som ber kjernen om å lese hva en katalog inneholder. Før kjernekoden kjøres, må modus-bit settes til kernel. Men hvis det fantes en instruksjon SWITCH_TO_KERNELMODE, ville et program i usermodus kunne gjøre denne instruksjonen og deretter få fri tilgang til systemet. Hvordan løses dette dilemmaet: sette modusbit til kernel og deretter være sikker på at det kun er kjernekode som kjøres?

OS må igjen ha hjelp fra hardware i form av en spesiell instruksjon, trap, som i samme operasjon switcher modussbit til kernel og hopper til ett av flere predefinert steder i minnet hvor det ligger kode for systemkall, som vist i figur 56 . Det er da ikke mulig å switche til kernelmodus og kjøre vilkårlig kode etterpå for vanlige brukerprogrammer. Etter systemkallet er utført, switcher OS modusbit til brukermodus og returnerer til der i koden systemkallet ble utført.

På Linuxinstallasjoner der kildekoden er med, inneholder filen `syscall_table_32.S` (med path /usr/src/linux-source-3.2/arch/x86/kernel e.l.) som er en del av kildekoden for Linux som Linus Torvalds har skrevet, som definerer hver av de 348 Linux-systemkallene. Den tilsvarende filen for 4.4 kjernen heter

```
linux-source-4.4.0/arch/x86/entry/syscalls/syscall_32.tbl
```

og har 376 systemkall. I tillegg finnes det noen spesifikke systemkall for 64 bits prosessorer.

Illustrasjon:
Trap-instruksjonen sørger for at en brukerprosess ikke kan oppnå full kontroll 
over en maskin ved å switche til kernelmodus.

Illustrasjon:
Fig 1-17 fra Tanenbaum

Illustrasjon:
Fig 1-18 fra Tanenbaum

Illustrasjon:
Fig 1-23 fra Tanenbaum

---

## 8.9 Prioritet i Linux-scheduling

Alle mulititasking operativsystem bruker en hardware timer til å dele opp tiden i små enheter. Med faste intervall vil denne timeren sende et interrupt til CPU-en som gjør at den hopper til operativsystemet-kode for dette intertuptet. Linux-kjernen deler tiden opp i ticks eller jiffies som vanligvis varer i 10 millisekunder eller ett hundredels sekund. Dette er tiden som går mellom hver gang hardwaretimeren sender et interrupt. Denne hardwaretimeren er faktisk programmerbar, slik at OS-kjernen kan sette verdien for denne når maskinen booter. Det har variert litt hva som har vært standard lengde på en Linux-jiffie, men i det siste har det vært 10 ms. I noen tidligere versjoner var det 2.5 ms. Det er mulig å konfigurere Linux kjerneversjon 2.6 til å bruke jiffie-lengde 10, 2.5 og 1 ms.

* Tiden deles i epoker
* Hver prosess tildeles et time-quantum målt i et helt antall jiffies som legges i variabelen counter. F. eks. 20 i enheter av ticks = 10 ms = timer-intervall
* OS kjører Round Robin-scheduling. Prosessen som kjører mister ett tick (counter reduseres med en) for hvert timer-tick.
* For hvert timer-tick sjekkes det om kjørende prosess har flere ticks, counter > 0
* Hvis counter > 0 fortsetter prosessen, hvis ikke kalles schedule() som velger en ny
* Epoken er over når alle prosesser har brukt opp sin tid (counter = 0)
* Antall ticks som deles ut før hver epoke bestemmes av prioriteten og lagres i en variabel med navn 'priority'
* En vanlig brukerprosess kan senke sin egen prioritet
* Prioritet kan dermed endres dynamisk (har en prosess brukt mye CPU, kan den f. eks. få nedsatt prioritet)
* Gjennomsnittlig time-quantum for 2.4 kjernen var ca 210 ms
* Gjennomsnittlig time-quantum for 2.6 kjernen var ca 100 ms

---

## 8.10 need resched

Linux 2.6 kjernen deler dynamisk prosessene inn i 140 forkjellige prioritetsklasser. Hver prioritetsklasse tilsvarer et antall tildelte ticks i starten av en epoke. Hver gang scheduleren kalles, velges prosessen som har høyest prioritet og den kjører til den har brukt opp alle sine tildelte ticks. Deretter kalles scheduleren på nytt. Men hvis det i løpet av epoken kommer et interrupt, for eksempel fra tastaturet, vil et flagg `need_resched` bli satt og scheduler på grunn av dette kjøres etter neste timer-tick. En interaktiv prosess vil få mange ticks hver epoke og komme i en høy prioritetsklasse. Dermed vil den alltid velges før CPU-intensive prosesser etter en context switch. Men om ikke `need_resched` ble satt ved et interrupt fra for eksempel tastaturet, ville den interaktive prosessen som skulle hatt og prosessert dette tegnet måtte vente helt til en kjørende CPU-intensiv prosess var ferdig med alle sine tick i en epoke, før den slapp til etter en contex switch. At `need_resched` settes gjør at det skjer en context switch med en gang ved neste timer tick og interaktive prosesser får dermed en mye bedre responstid.

---

## 8.11 Simulering av hvordan man ved hjelp av et operativsystem kan holde forelesning og lage vaffelrøre samtidig

I år (2025) vil denne simuleringen gjennomføres i levende live i PH170 onsdag 12. mars og ikke bare som videopptak slik som under pandemien.

[Video som demonstrerer multitasking av forelesning og vaffelrørelaging](https://os.cs.oslomet.no/os/vaffel.mp4)

*Når en datamaskin skal kjøre to prosesser samtidig, må den strengt skille mellom oppgavene 
de to gjør og fordele CPU-ressurser mellom de to. Et menneske er relativt dyktig til å gjøre 
to ting samtidig, men om man f. eks. skal forelese og lage vaffelrøre samtidig, kan det være nyttig (vel.....) 
å ha et program (operativsystem) som systematisk fordeler hjernebruken. Nedenfor følger instruksjoner for 
vaffelrøre, forelesning samt et styringsprogram som illustrerer hvordan et OS gjør scheduling.
Sidene nedenfor kan sammenlignes med internminnet på en maskin og hardware utfører 
instruksjoner herfra i en evig løkke.*

```
Operativsystem, data 
mem[1] = OST1  # timer
mem[2] = OSM1  # I/O melk

Operativsystem, kode 
OSI1 stack = PC                      # I = Interrupt. Hjelm!
OSI2 disableInterrupts
OSI3 JMP mem[IRQ]

OSM1 legg melk i buffer              # M = melk
OSM2 set needResched
OSM3 enableInterrupts
OSM4 switch to user modus            # Ta av hjelm
OSM5 PC = stack

OST1 updateCounterCurrentProcess        # T = timer kall 
OST2 If(countersum == 0) 
        counter = priority;  JMP OSS1   # ny epoke
OST3 If(counter == 0) 
        removeFromReadyList; JMP OSS1   # Call scheduler   
OST4 if(! needResched)
        switch to user modus            # Ta av hjelm
        PC = stack

OSS1 Les Ready List                     # S = scheduler
OSS2 Velg prosess
OSS3 if(ny prosess) 
            Context Switch  
            OSS3a  stack -> OldPCB.PC   # Lagre gammel PCB
            OSS3b  NyPCB.PC -> Stack    # Laste ny PCB
OSS4 Sett på timer                      # ringer om ett minutt = tick/jiffie
OSS5 enableInterrupts
OSS6 switch to user modus               # Ta av hjelm
OSS7 PC = stack

OSmelk1 stack = PC    
OSmelk2 disableInterrupts
OSmelk3 hent melk                    # Be I/O melkemannen om melk
OSmelk4 block prosess                # Fjern fra Readylist
OSmelk5 JMP OSS1                     # Call scheduler

OSegg1 stack = PC    
OSegg2 disableInterrupts
OSegg3 knus egg
OSegg4 enableInterrupts
OSegg5 switch to user modus          # Ta av hjelm
OSegg6 PC = stack
```

Vaffelprosess (V) med PCB (Process Control Block, process descriptor)

```
PCB
counter  0
priority 3
PC V1

V1  100g sukker
V2  100g mel
V3  visp
V4  blandet?
V5  JMPNB V3  (Jump Not Blandet)
V6  syscall trap OSmelk1
V7  1 dl melk
V8  Visp
V9  blandet
V10 JMPNB V8
V11 syscall trap OSegg1 
V12 Visp
V13 blandet?
V14 JMPNB V12
V15 JMPNOK V6
```

Forelesningsprosess. Siden den har prioritet 2, får den i snitt kjøre litt mindre enn vaffelprosessen.

```
PCB
counter  0
priority 2
PC F1

F1 Utviklingen av Linux
F2 Linux ble utviklet av datastudenten
F3 Linus Torvalds på en hybel i Helsinki 
F4  år   Versjon brukere kodelinjer
F5  1991  0.01   1       10K
F6  1992  0.96   1000    40K
F7  1994  1.0    100.000 170K
F8  1996  2.0    1.5M    400K
F9  1999  2.2    10M     1M
F10 2001  2.4    20M     3.3M
F11 2003  2.6    25M     5.9M 
F12 2009  2.6.32 ?       9.7M 
F13 2010  2.6.36 ?      10.9M 
F14 2011  3.0    ?      11.9M 
F15 2012  3.3    59M    12.3M 
F16 2015  4.0    ?      15.5M 
F17 2017  4.10   89M    17.0M
F18 2019  4.19   ?      17.3M
```

```
Operativsystem, data} 
ready list: F, V
needResched
stack:                               # Prosessen det ble hoppet fra

CPU-registre} 
PC Program Counter
(pekes på av kulepenn)

IRQ:
```

*Operativsystemet opererer i priviligertmodus og bruker derfor sykkelhjelm. Når vaffelrøre 
prosessen stoppes må hvilken instruksjon den har kommet til lagres i PCB, slik at prosessen 
fortsetter fra der den slapp neste gang. Deretter leses ready-list. Hvis forelesningen ikke er 
ferdig, står den der og adressen til neste instruksjon er lagret i denne prosessens PCB. 
OS oppdaterer Ready list, setter på timer, switcher til bruker modus og legger neste F-instruksjon 
i PC. Forelesningen fortsetter til timeren ringer og scheduler kalles på nytt. Ved ønske om å knuse egg 
(som er for risikofylt for at en vanlig bruker kan gjøre det) må vaffelprosessen gjøre et systemkall (OSegg). 
Da switches modus, systemkallet utføres, modus switches tilbake og vaffelprosessen kan fortsette.
counter minskes med en for hver gang timeren ringer for den prosessen som kjøres. Når alle countere er null er en epoke over 
og en ny innledes ved at alle countere blir satt lik prosessenes prioritet.*

[Video som demonstrerer multitasking av forelesning og vaffelrørelaging](https://os.cs.oslomet.no/os/vaffel.mp4)

---

## 8.12 Dagens faktum: Linux

*Linux er nå snart 32 år gammelt:*

```
> From: torvalds@klaava.Helsinki.FI (Linus Benedict Torvalds)
> Newsgroups: comp.os.minix
> Summary: small poll for my new operating system
> Date: 25 Aug 91 20:57:08 GMT
> 
> Hello everybody out there using minix -
> 
> I'm doing a (free) operating system (just a hobby, won't be big and
> professional like gnu) for 386(486) AT clones.  This has been brewing
> since april, and is starting to get ready.  I'd like any feedback on
> things people like/dislike in minix, as my OS resembles it somewhat
> (same physical layout of the file-system (due to practical reasons)
> among other things). 
> 
> I've currently ported bash(1.08) and gcc(1.40), and things seem to work. 
> This implies that I'll get something practical within a few months, and
> I'd like to know what features most people would want.  Any suggestions
> are welcome, but I won't promise I'll implement them :-)
> 
>               Linus (torvalds@kruuna.helsinki.fi)
```

Linux ble utviklet av Linus Torvalds (f. 1969) på en hybel i Helsinki.

| år | Versjon | brukere | kodelinjer |
|---|-------|-------|----------|
| 1991 | 0.01 | 1 | 10K |
| 1992 | 0.96 | 1000 | 40K |
| 1994 | 1.0 | 100.000 | 176K |
| 1995 | 1.2 | 500.000 | 311K |
| 1996 | 2.0 | 1.5M | 400K |
| 1999 | 2.2 | 10M | 1M |
| 2001 | 2.4 | 20M | 3.3M |
| 2003 | 2.6 | 25M | 5.9M |
| 2009 | 2.6.32 | ? | 9.7M |
| 2010 | 2.6.36 | ? | 10.9M |
| 2011 | 3.0 | ? | 11.9M |
| 2012 | 3.3 | 59M | 12.3M |
| 2015 | 4.0 | ? | 15.5M |
| 2017 | 4.10 | 89M | 17.0M |
| 2019 | 4.19 | ? | 17.3M |
| 2022 | 5.16 | ? | 22.6M |
| 2024 | 6.7.8 | ? | ? |

Torvalds leder fortsatt utviklingen av kjernen. Linux kildekode er fri, GNUs public licence, GPL. Tusenvis av programmerere fra hele verden har bidratt til prosjektet. En Eu-studie fra 2006 anslår at det ville koste 882M euro å utvikle 2.6.8-kjernen på nytt fra bunnen av.