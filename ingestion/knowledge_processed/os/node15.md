## 14.2 Dynamisk allokering

Et program kan be om at det settes av minnet til sine variabler før det starter, men det kan også be om at minne allokeres dynamisk. F. eks. vil et Java-statement

```
PCB = new process;
```

gjøre at denne plassen settes av i minnet først når programmet utfører det. Programmet tildeles page for page med minne. I C++ må man eksplisitt delete objekter som ikke er i bruk lenger for å frigjøre minne, JVM utfører dette automatisk (garbage collection). Den delen av et programs minne som inneholder variabler og data og som dynamisk kan øke og minke i størrelse, kalles ofte heap. Variabler i funskjoner/metoder som forsvinner og ikke kan brukes mer etter at kallet på funksjonen er ferdig, legges på stack.

---

## 14.3 VIRT, RES og SHR i top

Hvis man kompilerer og kjører følgendeC- program på en Linux-maskin, vil man kunne observere hvordan størrelsene VIRT, RES og SHR endrer seg.

```
#include <stdio.h>
#include <stdlib.h>

#define S 1024*1024

int staticArr[S];
int main()
{
   int i, size,d;

   printf("\nStørrelse: ");
   scanf("%d",&size);
   printf("Lager int  array med %d elementer\n",size);

   int *array = malloc(size * sizeof(int));
   
   printf("\nKlar til å bruke arrayet:");
   scanf("%d",&d);

   for(i=0;i < size;i++)
     {
	array[i] = i;
     }

   printf("\nVenter på å avslutte: ");
   scanf("%d",&size);
}
```

Programmet starter med å definere et statisk array med 1 M elementer som hver er på 4 byte, altså 4MiB. Både et slikt statisk array og et dynamisk array som lages med malloc() vil legges på heap.

Størrelsen VIRT er beskrevet slik i manualsiden for top:

```
VIRT  --  Virtual Memory Size (KiB)
          The total amount of virtual memory used by the task.  It includes all code, data and shared libraries
          plus pages that have been swapped out and pages that have been mapped but not used.
```

VIRT er altså all det internminnet som prosessen kan tenkes å bruke, men som ikke nødvendigvis ligger i RAM. Det som ikke ligger i RAM, ligger i SWAP-området på disken.

Hvis vi kjører programmet med bare ett element i arrayet, får vi

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                        
19924 haugerud  20   0    4352    652    584 S   0,0  0,0   0:00.00 a.out
```

mens hvis vi øker størrelsen til 1024*1024 som vist i koden over, kompilerer og kjøre på nytt, viser top:

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                        
25448 haugerud  20   0    8448    640    572 S   0,0  0,0   0:00.00 a.out
```

Og endringen i VIRT er 8448 - 4352 = 4096 og altså nøyaktig 4MiB = 4*1024*1024. Denne størrelsen er definert når programmet starter, men man kan dynamisk legge til mer internminnet som vist i koden over med funksjonen malloc. Hvis vi dynamisk legger til et nytt array med 1 M elementer

```
rex:~/mem/a$ ./a.out 

Størrelse: 1048576
Lager int  array med 1048576 elementer
```

vil vi se på top at VIRT øker

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                        
25448 haugerud  20   0   12548    640    572 S   0,0  0,0   0:00.00 a.out
```

og økningen er 12548 - 8448 = 4100 KiB som er som forventet ganske nøyaktig 4MiB.

Men som vi ser endres ikke RES i det hele tatt av dette og det er fordi disse array-elementene bare er allokert i det virtuelle minnerommet og ikke fysisk lastet inn i RAM. RES er definert på følgende måte:

```
RES  --  Resident Memory Size (KiB)
          The non-swapped physical memory a task is using.
```

RES er altså den delen av prosessens internminnet som akkurat nå ligger fysisk inne i RAM. Når vi lar programmet fortsette å kjøre og tilordne verdier til alle elementene i det dynamiske arrayet, gir top dette:

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND                                        
25448 haugerud  20   0   12548   5256   1276 S   0,0  0,0   0:00.00 a.out
```

Vi ser at RES øker med litt over 4MiB som først og fremst skyldes at hele arrayet nå lastes inn i RAM.

Størrelsen SHR er i top definert som

```
SHR  --  Shared Memory Size (KiB)
         The  amount  of shared memory available to a task, not all of which is typically resident.  It simply
         reflects memory that could be potentially shared with other processes.
```

SHR er den mengden av internminnet som det kan være mulig å dele med andre prosesser; merk den ligger ikke nødvendigvis i RAM nå.

---

## 14.4 Noen minne-begreper

**Soft miss**: page-referanse er ikke i TLB; må hentes fra internminnet

**Hard miss**: = page fault. En page mangler i minnet(og i TLB); må hentes fra disk

**Major fault**: = page fault. En page mangler i minnet(og i TLB); må hentes fra disk

**Minor fault**: = En page mangler i page-tabellen i RAM og må lages. Må IKKE hentes fra disk

**Dirty page**: En side som har blitt endret slik at den må skrives til disk om den må ut av minnet

**working set**: (Windows) Det sett av sider som en prosess har brukt nylig

**RES**: (Linux) De sider som nå er lastet inn (RESident) i fysisk RAM.

**Segment**: En logisk del av et programs minne, data, programtekst, stack-segmenter

**buffer cache**: Del av minnet som brukes som filsystem-cache

---

## 14.5 RAM-test

```
rex:~/mem/ramsmp-3.5.0$ ./ramsmp -b 1
RAMspeed/SMP (GENERIC) v3.5.0 by Rhett M. Hollander and Paul V. Bolotoff, 2002-09

8Gb per pass mode, 2 processes

INTEGER & WRITING         1 Kb block: 16376.46 MB/s
INTEGER & WRITING         2 Kb block: 17503.79 MB/s
INTEGER & WRITING         4 Kb block: 16018.84 MB/s
INTEGER & WRITING         8 Kb block: 17191.61 MB/s
INTEGER & WRITING        16 Kb block: 17629.32 MB/s
INTEGER & WRITING        32 Kb block: 17232.47 MB/s
INTEGER & WRITING        64 Kb block: 12087.30 MB/s
INTEGER & WRITING       128 Kb block: 10896.62 MB/s
INTEGER & WRITING       256 Kb block: 11532.74 MB/s
INTEGER & WRITING       512 Kb block: 11663.74 MB/s
INTEGER & WRITING      1024 Kb block: 12726.65 MB/s
INTEGER & WRITING      2048 Kb block: 6481.25 MB/s
INTEGER & WRITING      4096 Kb block: 2418.77 MB/s
INTEGER & WRITING      8192 Kb block: 2152.39 MB/s
INTEGER & WRITING     16384 Kb block: 2141.66 MB/s
INTEGER & WRITING     32768 Kb block: 2137.81 MB/s
```

[Intel Core Duo 6600](https://www.cpu-world.com/CPUs/Core_2/Intel-Core%202%20Duo%20E6600%20HH80557PH0564M%20%28BX80557E6600%29.html)

---

## 14.6 free

```
rex:~/www$ free -m
             total       used       free     shared    buffers     cached
Mem:          2011       1453        557          0         14        551
-/+ buffers/cache:        887       1123
Swap:         1937        683       1253
```

---

## 14.7 top

```
top - 01:50:33 up 78 days, 11:02, 35 users,  load average: 0.19, 0.51, 0.61
Tasks: 408 total,   1 running, 399 sleeping,   0 stopped,   8 zombie
Cpu(s):  0.8%us,  0.7%sy,  0.0%ni, 98.5%id,  0.0%wa,  0.0%hi,  0.0%si,  0.0%st
Mem:   2059344k total,  1501056k used,   558288k free,    14572k buffers
Swap:  1983988k total,   700372k used,  1283616k free,   565164k cached

  PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND                                                  
23123 haugerud  20   0  2676 1428  932 R    0  0.1   0:00.21 top                                                       
    1 root      20   0  2932 1232  792 S    0  0.1   0:30.41 init                                                      
    2 root      20   0     0    0    0 S    0  0.0   0:00.02 kthreadd                                                  
    3 root      RT   0     0    0    0 S    0  0.0   0:32.07 migration/0                                               
    4 root      20   0     0    0    0 S    0  0.0   0:35.21 ksoftirqd/0
```

---

## 14.8 Eksempler på minnebruk

```
#include <stdio.h>    

int array[200000000];
main(int argc, char *argv[]){
   int i,j;
   for(i = 0;i < 2000000;i++){
      j = i*100;
      array[i] = i;
   }
}
```

```
#include <stdio.h>    

int array[10000][10000];
main(int argc, char *argv[]){
   int i,j;
   for(i = 0;i < 10000;i++){
      for(j = 0;j < 10000;j++){
	 array[i][j] = 5;
      }
   }
}
```