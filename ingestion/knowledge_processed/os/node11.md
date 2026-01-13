## 10.3 Å kjøre Java, C og bash-programmer under forskjellige OS

Utgangspunktet er det samme "Hello world!" programmet skrevet i C, Java og Bash. Vi skal prøve å kjøre disse på tre systemer:

* Operativsystemet Linux kjørt på en vanlig PC med Intel Pentium prosessor som kun forstår X86 maskin-instruksjoner
* Operativsystemet Windows kjørt på den samme Intel-PC-en
* Operativsystemet Solaris kjørt på en Sun Sparcstation 20 med en sparc-prosessor som kun forstår Sparc maskin-instruksjoner

Idag er Sun og sparc-prosessor en utdøende rase og det finnes ikke så mange av dem lenger. Men det er et eksempel på en datamaskinarkitektur som er helt forskjellig fra x86 og Sparc CPUer var tidligere veldig mye i bruk i Unix-servere. Nå har dette markedet i stor grad blitt tatt over av Linux- og Windows-servere som stort sett kjører på Intel og AMD CPUer med x86-arkitektur.

---

## 10.3.1 Hello.java

Dette Java-programmet ser slik ut

```
$ cat Hello.java
class Hello
{ 
    public static void main(String args[])
    {
        System.out.println("Java: Hello world!");
    }
}
```

og som de to andre, skriver det bare ut en linje til skjermen. For å kjøre dette programmet må det kompileres og vi gjør det på Linux-maskinen:

```
$ javac Hello.java
```

da lages det en binær fil med navn `Hello.class` som inneholder såkalt bytekode. Denne koden er instruksjoner til en såkalt Java Virtual Machine (JVM) som er et program som kjører bytekoden og får det underliggende systemet til å utføre det denne koden sier skal gjøres. For hvert operativsystem er det en egen JVM som sørger for dette slik som vi ser i figuren:

Illustrasjon:
Java er plattformuavhengig og samme Hello.class fil kan kjøres på alle de tre plattformene.

Dermed kan `Hello.class` filen som ble kompilert på en Linux-maskinen faktisk kjøre på alle de tre plattformene. Enheten OS + Hardware blir ofte omtalt som en plattform. På grunn av dette sier vi at Java er plattformuavhengig. Det samme er også Perl og C#, deres kompilerte kode kjøres av virtuelle maskiner.

---

## 10.3.2 hello.c

Dette programmet ser slik ut

```
cube$ cat hello.c
#include <stdio.h>
main()
{
    printf("c: Hello world!\n");
}
```

For å kjøre dette programmet må det kompileres og vi gjør det på Linux-maskinen:

```
$ gcc hello.c
```

da lages det en binær fil med navn `a.out` som inneholder maskin-instruksjoner og deler av disse kan lastes inn og kjøres direkte på CPU-en til plattformen den er kompilert på. Nå har vi kompilert programmet på en X86-prosessor og da vil `a.out` inneholde X86-instruksjoner som på assembler-form kan se ut som f. eks. `mov %eax,%ebx` og henviser til registrene denne CPU-en har. Kompilatoren oversetter direkte fra kildekode til maskinkode. Assembly er et språk i mellom disse, men som ligger svært nær maskinkoden, og som gjør at vi enkelt kan se nøyaktig hva maskinkoden gjør. For å få kjørbar kode som er veldig kompakt og eller gjør nøyaktig det vi ønsker, er det mulig å skrive programmer direkte i assembly og så få en assembler til å oversette dette til maskinkode og dermed et kjørbart program.

Ved hjelp av reverse engineering kan man prøve å se hva binærkoden til et kompilert program (ofte kalt objekt-kode) inneholder. Programmet `objdump` er en disassembler som oversetter maskinkoden til en for mennesker mer leselig assembly-kode. Dette er det motsatte av hva en assembler gjør.

```
Linux$ objdump -d a.out 

8048278:       83 ec 04                     sub    $0x4,%esp
 804827b:       e8 00 00 00 00          call   8048280 <_init+0xc>
 8048280:       5b                      pop    %ebx
 8048281:       81 c3 d8 12 00 00       add    $0x12d8,%ebx
 8048287:       8b 93 fc ff ff ff       mov    -0x4(%ebx),%edx
```

Dette er bare et lite utsnitt av koden og det sentrale i vår sammenheng er at dette er instruksjoner fra det såkalte X86-instruksjonssettet som alle vanlige Intel og AMD-prosessorer bruker.

Dermed kan det umulig gå bra å kjøre `a.out` på en Sparc-prosessor, for den forstår overhode ikke maskin-instruksjonene som blir gitt. Det er rett og slett helt gresk for Sparc-prosessoren. Den forstår bare Sparc-instruksjoner som er et helt annent instruksjonessett som vi kan se hvis vi kompilerer programmet og dumper objekt koden under Solaris:

```
Solaris$  gcc a.out
Solaris$  objdump -d a.out
   10440:       e0 03 a0 40     ld  [ %sp + 0x40 ], %l0
   10444:       a2 03 a0 44     add  %sp, 0x44, %l1
   10448:       9c 23 a0 20     sub  %sp, 0x20, %sp
   1044c:       80 90 00 01     tst  %g1
```

Dette ligner, men instruksjonene er delvis forskjellige og definsjonene av hvilke bit-strenger som betyr en bestemt instruksjon eller et bestemt register er helt forskjellige.

I tillegg inneholder `a.out` kode som ber Linux-operativsystemet om å skrive ut til skjermen og dette er spesielle systemkall som er helt spesifikke for Linux og som andre OS ikke forstår. Dermed går det heller ikke å kjøre dette programmet på Windows-maskinen, selvom maskin-instruksjonene er de samme, alle er hentet fra X86-instruksjonssettet.

Illustrasjon:
C er ikke plattformuavhengig og samme a.out fil kan ikke kjøres på alle de tre plattformene. Som vi ser i figuren er det kun på plattformen programmet er kompilert at det kan kjøres og vi sier at C er plattformavhengig. Om vi skal kjøre dette programmet på de to andre plattformen, må det kompileres på nytt med en C-kompilator på både Windowsmaskinen og på Solaris-maskinen. På Windows kan det gjøres for eksempel med tinyCC (tcc), eller med en komersiell kompilator som Visual C++. På Solaris finnes det som regel en C-kompilator, det er vesentlig for Unix-maskiner. Da lages det instruksjoner som snakker med det rette OS'et og som inneholder de rette maskininstruksjonene, slik som i figuren.

Illustrasjon:
C-programmet må kompileres på hver av de tre plattformene, først da kan de kjøres.

---

## 10.3.3 hello.bash

Dette programmet ser slik ut

```
cube$ cat hello.bash
#! /bin/bash
echo "bash: Hello world!"
```

og er avhengig av at shellet bash er installert på plattformen det skal kjøres. Dette programmet tolker da linje for linje og utfører den. Dette er delvis analogt til Java, bortsett fra at mellomleddet med å kompilere og lage bytekode er fjernet. Programmet bash erstatter JVM og kjører koden. Dermed er også bash-script plattformuavhengig. Tidligere var det ikke mulig å kjøre bash på Windows, men i de siste årene har Microsoft samarbeidet mye med Ubuntu og det er nå mulig å aktivere et fullverdig bash-shell i Windows. Men det er ikke aktivert som default.

---

## 10.4 Test av C, Java, Python og bash på 5 plattformer

I forelesningen ble et Python 'Hello world' program testet i tillegg til de tre språkene beskrevet over. De fem forskjellige plattformene som var involvert i testen var de følgende.

* Linux Ubuntu 18.04, Intel Xeon, Java 11 Python 3.6 (HP laptop)
* MacOS X Darwin Kernel, Intel Core Duo, Java 6 (1.6) Python 2.6 (Gammel MacBook Pro)
* Linux Ubuntu 16.04, AMD Opteron, Java 8 (1.8) Python 2.7 (Dell server med 48 CPUer)
* Linux Ubuntu 20.04, ARM Neoverse-N1, Java 14 Python 3.8 (Amazon EC2, London)
* Windows server 2019, Intel Xeon CPU, Java 8 (1.8) Python 3.9 (Amazon EC2, London)

Utganspunktet varr at alle programmene ble kompilert og kjørt på den førstnevnte HP-laptopen som kjører Ubuntu 18.04. Kompileringen av programmene ble gjort med

```
gcc hello.c
javac Hello.java
```

og kjøringen med

```
./a.out
java Hello
python hello.py
bash hello.bash
```

---

## 10.5 Threads (tråder)

* prosess = At en kokk lager en porsjon middag i et kjøkken
* CPU = kokk
* ressurser = kjøkken, matvarer, oppskrift
* thread/tråd = den sammenhengende serien av hendelser som skjer når kokken lager en porsjon

Når porsjonen er ferdig er porsessen avsluttet. Alternativer:

* To uavhengige prosesser = to kjøkken, kokken løper frem og tilbake og lager en porsjon i hvert kjøkken. Følger en oppskrift i hvert kjøkken(men oppskriften er den samme).
* En prosess med to threads = Ett kjøkken, kokken bytter på å jobbe med de to porsjonene og lager to porsjoner fra samme oppskrift med felles ressurser for de to porsjonene.

Med en tradisjonell prosess kan kun en kokk jobbe i et kjøkken og der lage kun en porsjon. Ønsker man å lage flere porsjoner, så må man lage flere kjøkken. Innfører man tråder kan flere kokker jobbe i samme kjøkken med flere porsjoner på en gang.

---

## 10.6 Definisjoner av threads

* den sammenhengende rekken av hendelser/instruksjoner som utføres når et program kjøres
* "tråden" som følges når et program utføres
* Lettvekts prosess

Programmereren (og ikke OS) vet hva som skal gjøres. Han kan detaljstyre threads til å samarbeide om oppgaver som skal utføres.

Illustrasjon:
Single og multithreading

Figur 64 viser for en single threaded prosess hvordan programmet gjennom å utføre instruksjoner beveger seg igjennom koden og også frem og tilbake og til RAM. Om man tegner opp denne bevegelsen får man en enkelt "tråd" som beveger seg rundt og illustrerer hvordan programmet kjøres. Om man kjører et program flere ganger, kan det følge forskjellige tråder hvis for eksempel input er forskjellig fra gang til gang. Hvis man kjører en prosess som kan ha flere tråder kan man istedet for å kjøre et program tre ganger, kjøre tre tråder samtidig inne i den samme koden. Den høyre delen av figuren viser en multi threaded prosess hvor tre instanser av samme program kjører samtidig og følger hver sin tråd under utførelsen. Det meste av koden kan deles med de andre trådene, men alle data som er spesielle for den enkelte kjøringen må lagres hver for seg, slik som PCB for tråden. For eksempel vil disse tre trådene hele tiden ha forskjellige verdier i registerene og de vil kunne gjøre kall til forskjellige metoder. Dermed må de ha hver sin stack definert i RAM (hvor metode-kallene og metode-variabler lagres) og de må ha sine helt egne verdier i registerene som lagres i PCB når de ikke kjører. Den vanligste måten for operativsystemet å schedulere tråder er å betrakte dem som uavhengig enheter slik at tre tråder innen samme prosess kan kjøre på tre forskjellige CPUer.

---

## 10.7 Fordeler med threads

**Ressursdeling**: Flere tråder eksisterer innenfor samme prosess. Deler på kode, data og delvis PCB.

**Respons**: Interaktive applikasjoner kan ha en tråd med høy prioritet som kommuniserer med brukere og lavprioritettråder som gjør grovarbeid.

**Effiktivitet**: Tar mindre tid å lage nye threads og mindre tid å context-switche mellom threads. Kan typisk ta 30x så lang tid å lage en ny prosess som å lage en ny thread. Context switch kan ta 5x så lang tid.

**Multiprosessor**: Hver tråd kan tildeles en egen CPU.

**Felles variabler**: Ofte nyttig med felles minne for prosesser, men det er tungvint å sette opp. Dette er trivielt for threads.

---

## 10.8 Java-threads

For å lage Java-threads må man arve klassen Thread. Viktige Thread-metoder:

**start()**: Allokerer minne, stack etc. og kaller run().

**run()**: Her uføres jobben tråden skal gjøre.

**yield()**: Tråden gir fra seg CPU-en.

**setPriority()**: Setter thread-prioritet. Min = 1, Max = 10, default = 5.

**sleep(ms)**: Tråden sover i ms millisekunder

---

## 10.8.1 Prioritet

Vanligvis scheduleres to Java-tråder av OS, etter en-til-en modellen slik at de to trådene kjører uavhengig av hverandre og samtidig. Dette kalles native threads. Det finnes implementasjoner hvor Java kjører en prosess og schedulerer trådene selv, såkalte green-threads. jdk1.1 var implementert slik på Linux.

Det går ikke klart frem av spesifikasjonene for JVM (Java Virtual Machine) hvordan prioritet skal implementeres og her kan det være forskjeller.

---

## 10.8.2 Java på Linux

```
$ emacs Calc.java&
$ javac Calc.java   # Calc.class lages; bytecode
$ java Calc         # Starter JVM (Java Virtual Machine) som kjører byte-koden
```

---

## 10.8.3 Variabler

Variabler som blir definert som static vil være felles for alle trådene. Andre vil kun kunne brukes av den enkelte tråd.

```
static int count;
   int id;
```

I eksempelet oppdateres `count` av begge trådene, mens det eksisterer en `id` for hver tråd.

Illustrasjon:
Deklareres en variabel som static blir den felles for alle tråder.

---

## 10.9 Java thread eksempel: Calc.java

```
import java.lang.Thread;

class CalcThread extends Thread
{
   static int count = 0;
   int id;

   CalcThread()
        {
         count++;
         id = count;
        }

   public void run()
        {
         System.out.println("Thread nr." + id + " is starting");
         System.out.println("Thread nr." + id + " calculated " + work());
        }

   private float work()
        {
         int i,j;
           float res = 0;
            System.out.println("Thread nr." + id + " calculating");
            for(j = 1;j < 5;j++)
                {
                    for(i = 1;i < 30000000;i++)
                        {
                            res += 1.0/(1.0*i*i);
                        }
                     System.out.println("Thread nr." + id + " calculating" + j);
                }
         return(res);
        }
}

class Calc
{
   public static void main(String args[])
   {
    System.out.println("Starts two threads !\n");
    CalcThread s = new CalcThread();
    System.out.println("Thread s has id " + s.id + "\n");
    s.start(); // Allokerer minne og kaller s.run()

    CalcThread s2 = new CalcThread();
    System.out.println("Thread s2 has id " + s2.id + "\n");
    s2.start();
    System.out.println("s2 started !\n");

    }
}
```

Kjører man dette programmet på en maskin med to CPU'er, vil de to trådene kunne kjøre på hver sin CPU og dermed utnytte ressursene optimalt. Et java-program med en tråd vil kun kunne utnytte en av CPU-ene.