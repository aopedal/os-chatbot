## 11.3 Mange samtidige Java-tråder

Man kan starte et gitt antall tråder med

```
.
.
.
    static double saldo[] = new double[5000000]; // Felles array. 5M*8 byte = 40MByte
.
.
.
       int threads = 20;
       CalcThread tr[] = new CalcThread[threads];
       System.out.println("Starts " +threads + " threads !\n");

       for(k = 0;k < threads;k++)
           {
               tr[k] = new CalcThread();
               System.out.println("Thread has id " + tr[k].id + "\n");
               tr[k].start();
           }
```

Dette vil lage en prosess med mange tråder. Med top på Linux så dette tidligere ut som 20 uavhengige prosesser, selvom de egentlig var tåder. På en Linux host med to CPU'er ser det idag slik ut:

```
PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND                              
 4448 haugerud  20   0  246m  59m  15m S  199  2.9   0:16.19 java
```

Legg merke til at prosessen bruker 199% CPU, det skyldes at de 20 trådene tilsammen bruker så mye CPU ved at de av OS-kjernen scheduleres på begge CPU-ene. Om man taster H får man se alle trådene:

```
PID USER      PR  NI  VIRT  RES  SHR S %CPU %MEM    TIME+  COMMAND                                   
 4458 haugerud  20   0  246m  59m  15m R 10.8  2.9   0:59.51 java                                      
 4466 haugerud  20   0  246m  59m  15m R 10.8  2.9   0:59.38 java                                      
 4450 haugerud  20   0  246m  59m  15m R 10.5  2.9   0:59.60 java                                      
 4454 haugerud  20   0  246m  59m  15m R 10.5  2.9   0:59.54 java                                      
 4465 haugerud  20   0  246m  59m  15m R 10.5  2.9   0:59.34 java                                      
 4455 haugerud  20   0  246m  59m  15m R 10.2  2.9   0:59.53 java                                      
 4459 haugerud  20   0  246m  59m  15m R 10.2  2.9   0:59.49 java                                      
 4460 haugerud  20   0  246m  59m  15m R 10.2  2.9   0:59.49 java                                      
 4451 haugerud  20   0  246m  59m  15m R  9.9  2.9   0:59.58 java                                      
 4461 haugerud  20   0  246m  59m  15m R  9.6  2.9   0:52.16 java                                      
 4467 haugerud  20   0  246m  59m  15m R  9.3  2.9   0:52.01 java                                      
 4452 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.18 java                                      
 4456 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.18 java                                      
 4462 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.14 java                                      
 4463 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.13 java                                      
 4464 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.13 java                                      
 4468 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.08 java                                      
 4469 haugerud  20   0  246m  59m  15m R  9.0  2.9   0:52.01 java                                      
 4453 haugerud  20   0  246m  59m  15m R  8.7  2.9   0:52.22 java                                      
 4457 haugerud  20   0  246m  59m  15m R  8.7  2.9   0:52.15 java
```

Det ser ut som det er 20 prosesser som bruker 59MByte hver, men de deler i virkeligheten på et stort felles array, `saldo[]` . Legg merke til at hver tråd har sin egen PID. Det er slik OS-kjernen ser trådene, de scheduleres som selvstendige enheter og får like mye CPU hver. Hvis man i top taster f og velger

```
TPGID   = Tty Process Grp Id  
nTH     = Number of Threads
```

vil man se at dette er PID for den opprinnelige prosessen som startet alle de andre trådene, tråd nummer 21 i listingen nedenfor:

```
PID USER      PR  NI    VIRT    RES    SHR S %CPU %MEM     TIME+ COMMAND          TPGID nTH 
 7617 haugerud  20   0 8241296  60408  16644 R 43,9  0,4   1:30.37 java              7586  40 
 7623 haugerud  20   0 8241296  60408  16644 R 41,6  0,4   1:29.58 java              7586  40 
 7624 haugerud  20   0 8241296  60408  16644 R 41,6  0,4   1:31.18 java              7586  40 
 7607 haugerud  20   0 8241296  60408  16644 R 41,3  0,4   1:31.09 java              7586  40 
 7622 haugerud  20   0 8241296  60408  16644 R 41,3  0,4   1:30.59 java              7586  40 
 7619 haugerud  20   0 8241296  60408  16644 R 40,3  0,4   1:32.93 java              7586  40 
 7625 haugerud  20   0 8241296  60408  16644 R 40,3  0,4   1:32.86 java              7586  40 
 7606 haugerud  20   0 8241296  60408  16644 R 39,9  0,4   1:31.49 java              7586  40 
 7614 haugerud  20   0 8241296  60408  16644 R 39,9  0,4   1:30.02 java              7586  40 
 7615 haugerud  20   0 8241296  60408  16644 R 39,9  0,4   1:30.50 java              7586  40 
 7620 haugerud  20   0 8241296  60408  16644 R 39,9  0,4   1:30.47 java              7586  40 
 7609 haugerud  20   0 8241296  60408  16644 R 38,9  0,4   1:31.44 java              7586  40 
 7610 haugerud  20   0 8241296  60408  16644 R 38,9  0,4   1:30.85 java              7586  40 
 7611 haugerud  20   0 8241296  60408  16644 R 38,3  0,4   1:30.66 java              7586  40 
 7613 haugerud  20   0 8241296  60408  16644 R 38,0  0,4   1:30.76 java              7586  40 
 7616 haugerud  20   0 8241296  60408  16644 R 38,0  0,4   1:30.37 java              7586  40 
 7608 haugerud  20   0 8241296  60408  16644 R 37,3  0,4   1:30.91 java              7586  40 
 7618 haugerud  20   0 8241296  60408  16644 R 37,3  0,4   1:29.09 java              7586  40 
 7621 haugerud  20   0 8241296  60408  16644 R 37,3  0,4   1:29.92 java              7586  40 
 7612 haugerud  20   0 8241296  60408  16644 R 37,0  0,4   1:30.44 java              7586  40 
 7586 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7587 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.06 java              7586  40 
 7588 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7589 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7590 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7591 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7592 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7593 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7594 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7595 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7596 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:16.10 java              7586  40 
 7597 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7598 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7599 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7600 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.02 java              7586  40 
 7601 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.02 java              7586  40 
 7602 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7603 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.02 java              7586  40 
 7604 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.00 java              7586  40 
 7605 haugerud  20   0 8241296  60408  16644 S  0,0  0,4   0:00.05 java              7586  40
```

Og hvis man taster H igjen, er det bare denne prosessen man ser som bruker nesten 800% CPU, siden serveren har 8 CPU'er i dette tilfellet.

```
PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND     TPGID nTH 
 7586 haugerud  20   0 8241296  60548  16644 S 790,4  0,4  86:37.05 java       7586  40
```

---

## 11.4 Java threads-eksempel: Prioritet

En Java-tråd kan tilordnes prioritet med `setPriority()` . Eksempelet under viser også at en tråd selv kan endre sin prioritet. Når en tråd med høyere prioritet starter er meningen at den skal ta over CPU fra tråder med lavere prioritet, eventuelt gis mer CPU-tid. Men dette er ikke et absolutt krav i spesifikasjonen og praksis viser at dette ikke er tilfelle for alle JVM'er.

Om man hadde kjørt programmet i eksempelet med tråder implementert i user-space, ville OS ikke vært involvert i scheduleringen. Med Java green-threads (jdk1.1) startes først tråd 1 med prioritet 5 og tråd 2 med prioritet 10. Tråd 2 "sover" i 3 sekunder, så i starten kjører tråd 1 alene. Når tråd 2 våkner, tar den fullstendig over CPU-en og utfører `work()` helt til den setter sin egen prioritet til 1. Da tar tråd 1 over igjen til den er helt ferdig og til slutt fullføres tråd 2.

Kjøres det samme med native-threads, som er implementert i alle nyere JVM'er, vil trådene scheduleres av OS-kjernen og dermed timeslices og kjøre samtidig. På Linux vil prioriteten i praksis ikke ha noen innflytelse, trådene kjøres samtidig og deler likt på CPU, uansett hva prioriteten settes til. Dette skjer også om trådene tvinges til å kjøre på samme CPU med taskset. Det ville vært mulig å bruke `nice` til å implementere prioritet i en Linux JVM, men man har valgt å ikke gjøre det som default siden dette ikker er et absolutt krav i spesifikasjonen for JVM-implementasjonen. Se ukeoppgavene om hvordan man kan få prioritet til å virke under Linux.

Under Windows vil trådene både timeslice og resprektere prioriteten, men i så stor grad at threads med lavere prioritet nesten ikke slipper til. Og denne prioriteringen skjer kun hvis trådene deler samme CPU. Om det er flere CPUer tilgjengelig, kjører trådene på hver sin CPU og får like mye CPU-tid hver. Moralen er: Java Threads er ikke plattformuavhengig og avhengig av hvordan JVM i samarbeid med det underliggende OS schedulerer trådene.

```
import java.lang.Thread;

class PriorThread extends Thread
{
   static int count = 0;
   int id,mil;
   int max = 400000000;
   
   PriorThread(int millisek)
	{
	 count++;
	 id = count;
	 mil = millisek;
	}

   public void run()
	{
	 try {sleep (mil);} catch (Exception e) {}	 	 
	 System.out.println("Thread nr." + id + " med prioritet " + getPriority() + " starter");
	 System.out.println("Thread nr." + id + " regnet ut " + work()+ "\n");
	 if(id == 2)
	    {
	    setPriority(1);
	    System.out.println("\nEndrer prioritet for Thread nr." + id + ". Prioritet er nå "+getPriority()+"\n");
	    }
	 System.out.println("Thread nr." + id + " regnet ut " + work()+ "\n");
	}

   private float work()
	{
	 int i,j;
	 float res = 0;
	 for(j=1;j<=8;j++)
	     {
		 for(i = 1;i < max;i++)
		     {
			 res += 1.0/(1.0*i*i);
		     }
		 System.out.println("Thread nr." + id + " avsluttet work(" + j + ")");
	     }
	 return(res);
	}
}

class Prior
{
   public static void main(String args[])
   {
    System.out.println("\nStarter to threads!\n");
    PriorThread s1 = new PriorThread(1);
    s1.start();
    s1.setPriority(5);
    System.out.println("Default prioritet er " + s1.NORM_PRIORITY + " for en thread");
    System.out.println("Max er " + s1.MAX_PRIORITY + " og min er " + s1.MIN_PRIORITY + "\n");

    PriorThread s2 = new PriorThread(0);
    s2.setPriority(10);
    s2.start();  
   }
}
```

---

## 11.5 Prior.java kjørt på Linux

Man ser av kjøringen under at selvom man tvinger trådene til å dele samme CPU, har ikke prioriteten noen effekt:

```
rex:~/threads$ taskset -c 0 java Prior

Starter to threads!

Default prioritet er 5 for en thread
Max er 10 og min er 1

Thread nr.2 med prioritet 10 starter
Thread nr.1 med prioritet 5 starter
Thread nr.1 avsluttet work(1)
Thread nr.2 avsluttet work(1)
Thread nr.1 avsluttet work(2)
Thread nr.2 avsluttet work(2)
Thread nr.1 avsluttet work(3)
Thread nr.2 avsluttet work(3)
Thread nr.1 avsluttet work(4)
Thread nr.2 avsluttet work(4)
Thread nr.1 avsluttet work(5)
Thread nr.2 avsluttet work(5)
Thread nr.1 avsluttet work(6)
Thread nr.2 avsluttet work(6)
Thread nr.1 avsluttet work(7)
Thread nr.2 avsluttet work(7)
Thread nr.2 avsluttet work(8)
Thread nr.1 avsluttet work(8)
Thread nr.1 regnet ut 13.15576

Thread nr.2 regnet ut 13.15576

Endrer prioritet for Thread nr.2. Prioritet er nå 1

Thread nr.1 avsluttet work(1)
Thread nr.2 avsluttet work(1)
Thread nr.1 avsluttet work(2)
Thread nr.2 avsluttet work(2)
Thread nr.2 avsluttet work(3)
Thread nr.1 avsluttet work(3)
Thread nr.2 avsluttet work(4)
Thread nr.1 avsluttet work(4)
Thread nr.2 avsluttet work(5)
Thread nr.1 avsluttet work(5)
Thread nr.2 avsluttet work(6)
Thread nr.1 avsluttet work(6)
Thread nr.2 avsluttet work(7)
Thread nr.1 avsluttet work(7)
Thread nr.2 avsluttet work(8)
Thread nr.2 regnet ut 13.15576

Thread nr.1 avsluttet work(8)
Thread nr.1 regnet ut 13.15576
```

---

## 11.6 Prior.java kjørt på Windows 10

Kjører man PriorThread-eksempelet under Windows, på en maskin med kun en CPU, vil prioriteten tas hensyn til, men tråd med høyere prioritet tar da over nesten all CPU-tiden og slipper ikke den andre tråden til:

```
PS C:\Users\os\threads> java Prior

Starter to threads!

Default prioritet er 5 for en thread
Max er 10 og min er 1

Thread nr.2 med prioritet 10 starter
Thread nr.2 avsluttet work(1)
Thread nr.2 avsluttet work(2)
Thread nr.1 med prioritet 5 starter
Thread nr.2 avsluttet work(3)
Thread nr.2 avsluttet work(4)
Thread nr.2 avsluttet work(5)
Thread nr.2 avsluttet work(6)
Thread nr.2 avsluttet work(7)
Thread nr.2 avsluttet work(8)
Thread nr.2 regnet ut 13.15576

Thread nr.1 avsluttet work(1)
Thread nr.1 avsluttet work(2)

Endrer prioritet for Thread nr.2. Prioritet er nå 1

Thread nr.1 avsluttet work(3)
Thread nr.1 avsluttet work(4)
Thread nr.1 avsluttet work(5)
Thread nr.1 avsluttet work(6)
Thread nr.1 avsluttet work(7)
Thread nr.1 avsluttet work(8)
Thread nr.1 regnet ut 13.15576

Thread nr.1 avsluttet work(1)
Thread nr.1 avsluttet work(2)
Thread nr.1 avsluttet work(3)
Thread nr.1 avsluttet work(4)
Thread nr.1 avsluttet work(5)
Thread nr.1 avsluttet work(6)
Thread nr.1 avsluttet work(7)
Thread nr.1 avsluttet work(8)
Thread nr.1 regnet ut 13.15576

Thread nr.2 avsluttet work(1)
Thread nr.2 avsluttet work(2)
Thread nr.2 avsluttet work(3)
Thread nr.2 avsluttet work(4)
Thread nr.2 avsluttet work(5)
Thread nr.2 avsluttet work(6)
Thread nr.2 avsluttet work(7)
Thread nr.2 avsluttet work(8)
Thread nr.2 regnet ut 13.15576
```

Man ser at når thread nr. 2 endrer prioritet, kjører thread nr. 1 to runder før thread nr 2 får tid til å skrive ut sin kommentar om at prioriteten er senket.

Kjører man eksemplet med mange tråder, kan man på Windows taskmanager se hvor mange tråder JVM bruker. For å få til det må man høyreklikke på en av kolonne-navnene og be om at thread-kolonnen vises. I utganspunktet bruker Windows JVM 10 tråder. Hvis man starter 20 egne tråder viser dermed Taskmanager 30 tråder.

---

## 11.7 Blokkerende systemkall

Den viktigste årsaken til at man i det hele tatt begynte med threads var såkalte blokkerende I/O requests. Blokkerende betyr at applikasjonen som ber om I/O blir satt på vent av operativsystemet til resultatet fra I/O operasjonen returnerer. Blokkerende I/O forespørsler kan for eksempel være å lese fra en fil eller fra tastaturet. Programmet kan da ikke kjøre videre før det får resultatet. Generelt leder forespørsler om I/O til systemkall og disse er da blokkerende eller ikke-blokkerende systemkall. Eksempler på blokkerende systemkall:

* read/write
* wait
* sleep

De to første er alltid blokkerende, mens read og write kan bli gjort til nonblocking ved å bruke buffere og ordninger som sender signaler når lesingen/skrivingen er ferdig. Ikke blokkerende systemkall:

* getpid
* gettimeofday
* setuid

Dette er systemkall som ikke trenger å vente på I/O, andre prosesser eller noe annent for å fullføre. Uansett vil et systemkall føre til en trap til OS-kjernen.

---

## 11.8 Thread-modeller

Det finnes tre hovedmetoder for hvordan et operativsystem skedulerer threads. De tre metodene er forskjellige med hensyn på hvor uavhengig av hverandre trådene skeduleres.

Illustrasjon:
Thread-modeller i OS-kjernen

**en til mange**: Alle trådene skeduleres som en prosess, en enhet. Java: green-threads, JVM sørger selv for skedulering; ingen multitasking. Default på gamle versjoner av Linux(Debian) og Solaris.

**en til en**: Den mest brukte modellen. Hver tråd skeduleres uavhengig av de andre. Windows Java-threads, Linux native Java-threads, Linux Posix-threads (pthreads)

**mange til mange**: Tråder skeduleres uavhengig om de ikke er for mange. Kjernen kan begrense antall tråder i RR-køen. Solaris, Digital Unix, IRIX pthreads

Et operativsystem som bruker en-til-mange metoden vil behandle en prosess som inneholder mange tråder akkurat som en prosess med bare en tråd. Den gir prosessen biter av CPU-tid som alle andre prosesser og bryr seg ikke om at prosessen egentlig består av flere tråder. Det gjør at tråd-programmet selv må sørge for skedulering. En måte å gjøre dette på er at trådene kaller på `yield()` for å signalisere til de andre trådene at den er ferdig med sin del av jobben. Alternativt kan tråd-programmet selv lag en round robin schedulering som fordeler tid mellom trådene. For Java green-threads, som var default metode i de første Java-versjonene, var det JVM som selv sørget for skedulering. Hvis man i en slik versjon av Java setter igang to tråder, vil de ikke jobbe annen hver gang som man ville forvente, men første tråd kjøre til den er ferdig og så vil trå nummer to ta over.

De aller fleste av dagens operativsystemer bruker en-til-en metoden hvor det er en kjerne-tråd for hver bruker-tråd. Det betyr ikke at det for hver bruker-prosess er en egen prosess eller tråd i kjernen, men at kjernen for hver tråd har lagret data som registerverdier, program counter, tilstand, tråd-ID, prioritet og så videre og skedulerer hver tråd uavhengig av de andre trådene. For prosesser med bare en tråd, har kjernen lagret disse dataene i en tabell som inneholder informasjon om alle prosessene som kjører. For prosesser som har flere tråder, har kjernen for hver av disse en tabell som inneholder data for de individuelle trådene. Når operativsystemets scheduler skal velge hvilken tråd den skal kjøre på en CPU, velger den mellom alle tilgjengelige tråder, uavhengig av hvilken prosess de tilhører og uavhengig av hvor mange tråder hver prosess har. OS-kjernen fordeler CPU-tid jevnt mellom alle trådene og ikke mellom prosessene. En prosess som har veldig mange tråder vil derfor få mer CPU-tid enn en prosess med få tråder.

---

## 11.9 Synkronisering

Samtidige prosesser som deler felles ressurser/data må synkroniseres .

* prosesser må ikke endre felles data samtidig
* en prosess bør ikke lese felles data mens en annen endrer dem
* en prosess må kunne vente på (f. eks. resultater fra) en annen prosess

Distribuerte systemer mer og mer vanlig. Synkronisering er da essensielt.

---

## 11.10 Serialisering

Prosesser/tråder som aksesserer felles data må serialiseres; jobbe en av gangen på felles data. Problemstillingen kalles **Race Condition** (konkurranse om felles ressurser). *Brukeren må selv serialisere sine prosesser. OS legger mulighetene til rette.*

---

## 11.10.1 Eksempel: To web-prosesser som skriver ut billetter

Anta at man kan kjøpe billetter på en web-side. På web-serveren starter det da opp en prosess for hver bruker som bestiller en billett. Disse prosessene er helt uavhengige, bortsett fra at de har en felles variabel `LedigeBilletter` som er antall ledige billetter. Koden prosessene kjører kan se omtrent slik ut:

```
if(LedigeBilletter > 0){
   LedigeBilletter--;
   SkrivUtBillett();
}
```

Dette fungerer greit når bare en slik prosess kjøres av gangen, men det kan oppstå problemer hvis de kjører samtidig(husk at `LedigeBilletter` er en felles variabel):

| P1-kode | P2-kode | LedigeBilletter |
|-------|-------|---------------|
| if(LedigeBilletter > 0){ |  | 1 |
| —Context Switch | if(LedigeBilletter > 0){ | 1 |
|  | LedigeBilletter—; | 0 |
|  | SkrivUtBillett(); | 0 |
|  | } | 0 |
| LedigeBilletter—; | Context Switch— | -1 |
| SkrivUtBillett(); |  | -1 |
| } |  | -1 |

En Context Switch kan forekomme når som helst og hvis den skjer rett etter at P1 har sjekket at `(LedigeBilletter > 0)` , men før den har senket verdien med en, vil P1 og P2 skrive ut den samme (og siste) billetten til to forskjellige kunder. Dette er opplagt galt. Prosessene må serialiseres, slik at denne kodebiten (som kalles et kritisk avsnitt) gjøres av en prosess av gangen.

---

## 11.10.2 Eksempel: to prosesser som oppdaterer en felles variabel

Det er viktig å huske at en linje høynivåkode ofte oversettes til mange linjer makinkode. Dermed kan en Race Condition oppstå selv inni en kodelinje, fordi en Context Switch kan oppstå mellom to hvilke som helst maskininstruksjoner. CPU-en ser kun maskininstruksjoner og aner ikke noe om høynivåkoden som ligger bak. Anta at to prosesser P1 og P2 kjører følgende høynivåkode som oppdaterer en konto:

| P1-kode | P2-kode |
|-------|-------|
| static int saldo; | static int saldo; |
| . | . |
| . | . |
| . | . |
| saldo = saldo - mill; | saldo = saldo + mill; |

*Variabelen saldo er da en felles variabel begge kan endre.*

**Problem**: Hva skjer om OS switcher fra P1 til P2 mens P1 ufører `saldo = saldo - mill` ?

**Hvorfor?**: Prosessen utfører maskinkode, linje for linje, og kan bli avbrutt etter en instruksjon.

| P1 | P2 |
|---|---|
| saldo = saldo - mill; | saldo = saldo + mill; |
| mov saldo,%ax | mov saldo,%ax |
| mov mill,%bx | mov mill,%bx |
| sub %bx,%ax | add %bx,%ax |
| mov %ax,saldo | mov %ax,saldo |

Anta at P1 blir Context switchet etter å ha utført `mov mill,\%bx` og P2 overtar. Og videre at saldo er 5 til å begynne med og mill er 1. Følgende skjer, sett fra prosessoren:

| Prosess som kjører | Instruksjon (IR) | %ax | %bx | saldo |
|------------------|----------------|---|---|-----|
| P1 | mov saldo,%ax | 5 | 0 | 5 |
| P1 | mov mill,%bx | 5 | 1 | 5 |
| OS | Context switch | 0 | 0 | 5 |
| P2 | mov saldo, %ax | 5 | 0 | 5 |
| P2 | mov mill,%bx | 5 | 1 | 5 |
| P2 | add %bx,%ax | 6 | 1 | 5 |
| P2 | mov %ax,saldo | 6 | 1 | 6 |
| OS | Context switch | 5 | 1 | 6 |
| P1 | sub %bx,%ax | 4 | 1 | 6 |
| P1 | mov %ax,saldo | 4 | 1 | 4 |

Når P2 er ferdig vil P1 bruke den gamle saldoverdien 5 og sluttresultatet blir saldo = 4. Det burde ha blitt saldo = 5 og en mill er borte!! Konklusjon: må serialisere aksess til felles data!

---

## 11.11 Kritisk avsnitt

To prosesser P1 og P2 kjører:

| P1-kode | P2-kode |
|-------|-------|
| static int saldo; | static int saldo; |
| . | . |
| . | . |
| . | . |
| saldo = saldo - mill; | saldo = saldo + mill; |

Utregningen av saldo er et kritisk avsnitt i koden til P1 og P2. Et kritisk avsnitt **må fullføres** av prosessen som utfører det uten at andre prosesser slipper til; prosessene må serialiseres.

---

## 11.12 Kritisk avsnitt: Java-eksempel

Anta at to tråder samarbeider om et felles int-variabel saldo. Den ene tråden øker en million ganger saldo med 1, mens tråd nummer to minker verdien av saldo med en million ganger. Koden kan se slik ut:

```
// Kompileres med  javac NosynchThread.java
// Run: java NosynchThread

import java.lang.Thread;

class SaldoThread extends Thread
{
    static int MAX = 1000000; // En million
    static int count = 0;
    public static int saldo; // Felles variable, gir race condition
    int id; 
    
    SaldoThread()
    {
        count++;
        id = count;
    }
    
    public void run()
    {
	System.out.println("Tråd nr. "+ id +", med prioritet " + getPriority() + " starter");
	updateSaldo();
    }
    
    private void updateSaldo()
    {
	int i;
	if(id == 1) 
	{
	    for(i = 1;i < MAX;i++) 
	    {
		saldo++;
	    }
	}
	else      
	{
	    for(i = 1;i < MAX;i++)
	    {
	        saldo--;
	    }
	}
	System.out.println("Tråd nr. " + id + " ferdig. Saldo: " + saldo);
    }
}

class NosynchThread extends Thread
{
   public static void main (String args[])
   {
       int i;
       System.out.println("Starter to tråder!");

       SaldoThread s1 = new SaldoThread();
       SaldoThread s2 = new SaldoThread();
       s1.start();
       s2.start();

       try{s1.join();} catch (InterruptedException e){}
       try{s2.join();} catch (InterruptedException e){}

       System.out.println("Endelig total saldo: " +SaldoThread.saldo);
   }
}
```

*Her stod det inntil 14 april 2024 i koden  public synchronized void updateSaldo() men det var trolig fra
en test; det hjelper ikke å bruke synchronized slik, se mer om dette i neste forelesning. I videoen er koden korrekt
presentert, uten synchronized.*

Man skulle tro at saldo dermed ender opp som 0, men en kjøring kan gi noe slikt som:

```
rex:~/threads/nosync$ java NosynchThread 
Starter to tråder!
Tråd nr. 2, med prioritet 5 starter
Tråd nr. 1, med prioritet 5 starter
Tråd nr. 2 ferdig. Saldo: -7831
Tråd nr. 1 ferdig. Saldo: -4892
Endelig total saldo: -4892
```

eller

```
rex:~/threads/nosync$ java NosynchThread 
Starter to tråder!
Tråd nr. 1, med prioritet 5 starter
Tråd nr. 2, med prioritet 5 starter
Tråd nr. 1 ferdig. Saldo: 8055
Tråd nr. 2 ferdig. Saldo: 3727
Endelig total saldo: 3727
```

Altså flere tusen feil og varierende resultat fra gang til gang. Dette skyldes at trådenes lesning og lagring av den felles variabelen ikke er synkronisert.

---

## 11.12.1 Årsaken: race conditions

Ser man på bytekoden som kjøres vil den delen av updateSaldo() som legger til 1 se slik ut

```
\normalsize
$ javap -private -c SaldoThread
 -private for å vise alle metoder, ellers vises ikke updateSaldo()
.
.
      17: getstatic     #17                 // Field saldo:I
      20: iconst_1
      21: iadd
      22: putstatic     #17                 // Field saldo:I
.
.
```

og tilsvarende del av koden for subtraksjon ser slik ut

```
40: getstatic     #17                 // Field saldo:I
      43: iconst_1
      44: isub
      45: putstatic     #17                 // Field saldo:I
```

JVM er en stack-maskin og getstatic laster verdien fra saldo på stacken før iadd øker verdien med en. Til slutt lagres verdien på stacken med putstatic. Årsaken til regnefeilene er at trådene når som helst kan context switches og om det skjer mellom getstatic og putstatic, vil regneoperasjonen bli usynkroniserte og trådene overser deler av hverandres regneoperasjoner.

---

## 11.13 Race condition med C, to pthreads og én instruksjon

Vi så i eksempelet med Java-tråder at instruksjonen

```
saldo++;
```

faktisk ikke utføres av en enkelt Java bytecode-instruksjon, men av flere. Dermed vil det selvom trådene kjører på samme CPU kunne skje en context switch rett etter at verdien på saldo er lastet inn og før verdien er lagret igjen. Når den andre tråen så går inn og leser verdien på saldo vil den bruke den ikke oppdaterte verdien og en race condition oppstår. Sluttresultatet vil avhenge av hvilken tråd som leser verdien først og vil dermed være forskjellig for hver gang programmet kjøres. Men hva om det faktisk bare var en enkelt instruksjon som blir utført i det kritiske avsnittet? Kan det også da oppstå en race condition?

For å undersøke det lager vi et ligenende program hvor vi bruker en enkelt assembly-instruksjon for å forsikre oss om at det kun er en enkelt instruksjon som utføres og at kompilatoren ikke lager maskinkode som involverer flere instruksjoner. Tråder er ikke inkludert som default i C, men man kan introdusere tråder ved hjelp av pthreads-biblioteket. Koden nedenfor viser et C-program som lager to tråder som begge oppdaterer en felles variabel med navn `svar` . I dette tilfellet øker begge tråder verdien til variabelen like mange ganger og dermed vet vi at verdien må bli det dobbelte av det hver tråd øker med hvis det ikke inntreffer en race condition.

```
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>

int svar = 0;

extern void enlinje();

void *inc() 
{
   printf("Starter; svar verdi: %d\n", svar);
   
   for (int i = 0; i < 10000000; i++) 
     {
	enlinje();
     }
   
   printf("Avslutter; svar verdi: %d\n", svar);
}

int main()
{
           pthread_t thread1, thread2;
      
          /* Lager uavhengige threads som utfører inc-funksjonen */
      
           pthread_create( &thread1, NULL, inc,NULL);
           pthread_create( &thread2, NULL, inc, NULL);
      
           /* Venter med join til begge tråder er ferdige */
      
           pthread_join( thread1, NULL);
           pthread_join( thread2, NULL); 
      
           printf("Main avslutter; svar verdi: %d\n", svar);
           exit(0);
}
```

I første omgang skriver vi enlinje-funksjonen med vanlig C-kode i en fil med navn `en.c` , alt den gjør er å øke verdien av den felles variabelen `svar` med en:

```
void enlinje()
{
   extern int svar;
   svar++;
}
```

Når vi så kompilerer og kjører programmet på følgende måte:

```
rex:~/threads/lock$ gcc -pthread thread.c en.c
rex:~/threads/lock$ ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 629979
Avslutter; svar verdi: 10026464
Avslutter; svar verdi: 12261597
Main avslutter; svar verdi: 12261597

rex:~/threads/lock$ ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 204229
Avslutter; svar verdi: 7132793
Avslutter; svar verdi: 10668956
Main avslutter; svar verdi: 10668956

rex:~/threads/lock$ ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 114562
Avslutter; svar verdi: 9936660
Avslutter; svar verdi: 10127784
Main avslutter; svar verdi: 10127784
```

ser vi at en race condition oppstår fordi svaret blir forskjellig for hver gang og avhenger av rekkefølgen de to trådene oppdaterer variabelen. At svaret er litt over 10 millioner er forenlig med det som skjer hvis begge henter ut verdien 1 omtrent samtidig og øker den til 2 og så skriver tilbake omtrent samtidig, vil den totale økningen være 1, mens den burde vært 2. Når trådene fortsetter slik uten å samarbeide, vil ca halvparten av økningene med 1 forsvinne. Men kan dette skyldes at kompilatoren lager maskinkode som involverer flere instruksjoner? Ja, det kan være årsaken (å undersøke om det virkelig er tilfelle at kompilatoren lager flere linjer, overlates til en av ukens oppgaver). For å være helt sikker på at enlinje-funksjonen kun utfører en enkelt insturksjon, erstatter vi `en.c` med assembly-filen `minimal.s` :

```
.globl	enlinje
enlinje:
	incl svar(%rip)
	ret
```

Når vi nå kompilerer og kjører er vi sikker på at det kun er en enkelt instruksjon som oppdaterer variabelen `svar` , den blir ikke lagret i et register først. Likevel, når vi kompilerer og kjører oppstår det fortsatt en race condition:

```
rex:~/threads/lock$ gcc -pthread thread.c minimal.s 
rex:~/threads/lock$ ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 748235
Avslutter; svar verdi: 7065807
Avslutter; svar verdi: 10768013
Main avslutter; svar verdi: 10768013
```

Dette skyldes at de to trådene kjører på hver sin CPU og at det ikke er noen koordinering CPUene imellom om å vente på hverandre når en variabel skal hentes fra RAM. Men hva om man tvinger begge trådene til å kjøre på samme kjerne eller CPU? Da bør vel en race condition avverges? Det kan testes ved å starte prosessen med taskset, den vil tvinge prosessen og alle dens tråder til å kjøre på samme CPU. Og ganske riktig, da løses problemet:

```
rex:~/threads/lock$ taskset -c 0 ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 3258051
Avslutter; svar verdi: 17614192
Avslutter; svar verdi: 20000000
Main avslutter; svar verdi: 20000000

rex:~/threads/lock$ taskset -c 0 ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 3348312
Avslutter; svar verdi: 17502515
Avslutter; svar verdi: 20000000
Main avslutter; svar verdi: 20000000
```

Uansett hvor mange ganger man kjører dette, vil det gi riktig resultat. Dette er fordi en enkelt maskininstruksjon fullføres før en context switch skjer, dermed vil et kritisk avsnitt alltid fullføres før neste tråd tar over.

En mer genrell løsning består i å legge til maskininstruksjonen `lock` rett før oppdateringen av `svar` :

```
.globl	enlinje
enlinje:
        lock
	incl	svar(%rip)
	ret
```

Denne instruksjonen låser minnebussen slik at ingen andre prosesser får bruke den før den selv har utført neste instruksjon. Dermed løses problemet:

```
rex:~/threads/lock$ ./a.out 
Starter; svar verdi: 0
Starter; svar verdi: 116546
Avslutter; svar verdi: 19886202
Avslutter; svar verdi: 20000000
Main avslutter; svar verdi: 20000000
```

Dette er en metode å løse race condition problemer på, i neste forelesning ser vi på denne og andre metoder. Forøvrig bruker programmet tre ganger så lang tid på å kjøre når man bruker `lock` . Dette er fordi det tar mye ekstra tid å synkronisere prosessene, de må vente på hverandre når minnebussen låses.