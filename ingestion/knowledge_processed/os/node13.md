## 12.3 Mulige måter å takle kritiske avsnitt

|   |   |   |
|---|---|---|
| A | Skru av scheduler før kritisk avsnitt. P1 kode: disableInterupts(); saldo = saldo - mill; enableInterupts(); OK for en OS-kjerne, men for farlig for brukerprosesser; de kan ta over styringen. | disableInterupts(); saldo = saldo - mill; enableInterupts(); |
| disableInterupts(); saldo = saldo - mill; enableInterupts(); |  |  |
| B | Bruke en form for lås som gjør at bare en prosess av gangen har tilgang til felles data. MUTual EXclusion = MUTEX = gjensidig utelukkelse mest brukt mange implementasjoner |  |

---

## 12.3.1 Linux-eksempel

File-lock for Linux-mail: hvis filen

```
/var/mail/haugerud.lock
```

eksisterer, kan inbox ikke leses/skrives til. *Sendmail og andre mailprogram 
lager denne filen før de skriver/leser mail og fjerner den når de er ferdige.*

---

## 12.3.2 Windows-eksempel

Win 32 API'et har to funksjonskall

* EnterCriticalSection
* LeaveCriticalSection

som applikasjoner kan kalle før og etter et kritisk avsnitt.

---

## 12.4 Softwareløsning for P1/P2 med MUTEX

Trenger to funksjoner `GetMutex(lock)` og `ReleaseMutex(lock)` som gjør at en prosess av gangen kan sette en lock. Da kan problemet løses med:

```
GetMutex(lock);      // henter nøkkel
KritiskAvsnitt();    // saldo -= mill;
ReleaseMutex(lock);  // gir fra seg nøkkel
```

---

## 12.4.1 Software-mutex, forsøk 1

```
static boolean lock = false; // felles variabel

GetMutex(lock)
   {
   while(lock){} // venter til lock blir false
   lock = true;
   }
ReleaseMutex(lock)
   {
   lock = false;
   }
```

Dette burde sikre at to prosesser ikke er i kritisk avsnitt samtidig? Men hva om det skjer en Context Switch rett etter `while(lock){}` når P1 kjører?

Da rekker ikke P1 å sette lock til true og P2 kunne gå inn i kritisk avsnitt, switches ut og P1 kan gå inn i kritisk avsnitt samtidig! Altså er ikke denne metoden korrekt. Dette er vanskelig å løse med en algoritme, som forsøkene i ukens oppgaver viser. Men Peterson-algoritmen gir en elegant løsning.

---

## 12.5 Hardware-støttet mutex

I praksis brukes som oftest hardwarestøttede løsninger, for alle softwareløsninger innebærer mange instruksjoner i tillegg til busy-waiting, som koster CPU-tid. Et unntak er synkronisering av fler-CPU maskiner, SMP, symmetric multiprocessing og flerkjerneprosessorer. . Kan lages med en egen instruksjon **testAndSet** også kalt TSL(Test and Set Lock). Tester og setter en verdi i samme maskininstruksjon. Låser minne-bussen slik at ikke andre CPUer kan endre eller lese verdien. GetMutex() kan da implementeres med:

```
GetMutex(lock)
   {
    while(testAndSet(lock)) {}
   }
```

og en context switch kan ikke ødelegge siden testen og endringen av lock skjer i samme instruksjon.

---

## 12.6 X86-instruksjonen lock

En annen X86 maskininstruksjon er `lock` som vi så på i forrige uke og som hindret race condition når kritisk avsnitt kun består av en enkelt instruksjon . Den vil for neste instruksjon som utføres låse minnebussen slik at instruksjoner på andre CPUer ikke samtidig kan hente eller lagre noe i RAM. Dette sikrer at instruksjonen etter lock som utføres på en variabel i minne får avsluttet hele sin operasjon uten at RAM endres. Dermed avverges problemet ved at det kritiske avsnittet fullføres før noen andre tråder slipper til.

---

## 12.7 Semaforer

En semafor er en integer S som signaliserer om en ressurs er tilgjengelig. To operasjoner kan gjøres på en semafor:

```
Signal(S): S = S + 1;                 # Kalles ofte Up(), V()
Wait(S): while(S <= 0) {}; S = S - 1; # Kalles ofte Down(), P()
```

Signal og wait må være uninterruptible og implementeres med hardwarestøtte eller i kjernen for å være atomiske(umulige å avbryte).

**Binær semafor**: S = 0 eller 1 (som lock) (initialiseres til 1)

**Teller semafor**: S vilkårlig heltall (initialiseres til antall ressurser)

En semafor kan brukes slik til å takle et kritisk avsnitt(må da initialiseres til 1):

```
Wait(S);
KritiskAvsnitt();
Signal(S);
```

En semafor som er initialisert til S=1 og som ikke kan bli større enn 1, omtales ofte som en mutex.

---

## 12.7.1 Implementasjon av semafor i OS

Hvis en semafor implementeres i OS kan prosesser som venter legges i en egen kø, slik at de ikke bruker CPU mens de venter. Skjematisk sett kan implementasjonen gjøres slik:

```
Signal(S){
   S = S + 1;
   if(S <= 0){
      wakeup(prosess);
      # Sett igang neste prosess fra venteliste
   }
}
```

```
Wait(S){
   S = S - 1;
   if(S < 0){
      block(prosess);
      # Legg prosess i venteliste
   }
}
```

En mp4 demo kan sees på [denne web-siden](https://www.cs.oslomet.no/~haugerud/os/demoer/mutex.mp4) som viser hvordan en implementasjon semaforer kan brukes av operativsystemet.

En flash-demo det samme kan sees på [denne web-siden](https://www.cs.oslomet.no/~haugerud/os/demoer/swf/sema.swf) .

---

## 12.8 Bruk av semafor i kritisk avsnitt

Anta at semaforen S brukes til å beskytte en felles ressurs (variabel eller lignende) i et kritisk avsnitt. Prosess A og B må da kall Wait() før og Signal() etter kritisk avsnitt.

| PA | PB-kode |
|---|-------|
| A1 | B1 |
| A2 | Wait(S) |
| A3 | K1 |
| Wait(S) | K2 |
| K1 | K3 |
| K2 | Signal(S) |
| K3 | B2 |
| Signal(S) | B3 |
| A4 | B4 |

Slik beskyttes da det kritiske avsnittet (pilene angir Context Switch)

| A | B | S |
|---|---|---|
|  | B1 | 1 |
|  | Wait(S) | 0 |
|  | K1 | 0 |
| A1 |  | 0 |
| A2 |  | 0 |
| A3 |  | 0 |
| Wait(S) | OS legger A i kø | -1 |
|  | K2 | -1 |
|  | K3 | -1 |
|  | Signal(S) | 0 (A ut av kø) |
|  | B2 | 0 |
|  | B3 | 0 |
|  | B4 | 0 |
| K1 |  | 0 |
| K2 |  | 0 |
| K3 |  | 0 |
| Signal(S) |  | 1 |
| A4 |  | 1 |

---

## 12.9 Bruk av semafor til å synkronisere to prosesser

En semafor kan brukes til å synkronisere to prosesser. Anta prosess B (PB) må vente til prosess A (PA) er ferdig med noe i sin kode (kodelinje A3 i eksempelet), før den kan gå videre (med kodelinje B2 i eksempelet). Med en semafor S initialisert til 0, kan de da synkroniseres som følger:

| PA | PB-kode |
|---|-------|
| A1 | B1 |
| A2 | Wait(S) |
| A3 | B2 |
| Signal(S) | B3 |
| A4 | B4 |

PB kan ikke gjøre B2 før PA har satt S til 1. Pilene angir Context Switch. To mulige forløp. B når først fram:

| A | B | S |
|---|---|---|
| A1 |  | 0 |
| A2 |  | 0 |
|  | B1 | 0 |
|  | Wait(S) | -1 |
| A3 |  | -1 |
| Signal(S) |  | 0 |
| A4 |  | 0 |
|  | B2 | 0 |
|  | B3 | 0 |

A når først fram:

| A | B | S |
|---|---|---|
| A1 |  | 0 |
| A2 |  | 0 |
| A3 |  | 0 |
| Signal(S) |  | 1 |
| A4 |  | 1 |
|  | B1 | 1 |
|  | Wait(S) | 0 |
|  | B2 | 0 |
|  | B3 | 0 |

---

## 12.10 Tanenbaums bruk av semaforer

Semaforene som er omtalt i læreboka er de samme som omtalt her men Tanenbaum bruker betegnelsene up og down istedet for signal og wait. I tillegg blir semaforen ikke mindre enn null, den beholder verdien null om en prosess kaller wait, men prosessen blir satt i kø. Men når en annen prosess gjør signal vil prosessen som lå i kø vekkes og de to kallene nulle ut verdien på semaforen. I praksis blir effekten den samme. Men vår bruk av semaforen viser tydligere hvor mange som ligger i kø.

---

## 12.11 Låse-mekanismer brukt i Linux-kjernen

Linux-kjernen kan selv skru av og på interrupts for å sikre at korte kode-biter ikke blir avbrutt. Flere CPUer kan samtidig kjøre kjerne-kode, derfor er låser mye i bruk for å unngå at datastrukturer aksesseres samtidig.

**Atomiske operasjoner**: Operasjonen kan ikke interruptes, eksempel: `atomic_inc_and_test()`

**Spinlocks**: Mest brukt. For korte avsnitt. Bruker busy waiting.

**Semaforer**: Kjernen sover til semaforen blir ledig igjen om den er opptatt.

**Reader/Writer locks**: Samtidige prosesser kan lese, men bare en CPU av gangen kan skrive

---

## 12.12 Monitorer og Java synkronisering

Det viser seg at i praksis er det vanskelig å skrive korrekte programmer med semaforer. Programmeren er helt overlatt til seg selv og ett signal for mye vil ødelegge hele systemet. Derfor ble konseptet monitor laget. Dette er en del av et programmeringsspråk og kan sørge for at hele metoder eller deler av kode synkroniseres. Kun en monitor-metode kan kjøre av gangen og dermed sikres synkronisering på et høyere nivå.

Dette er implementert i Java som har et eget statement `synchronized` for å synkronisere bruken av felles variabler. Alle java-objekter har en egen monitor-lås, tilsvarende variabelen lock vi har brukt i tidligere eksempler.

Når man bruker statementet `synchronized()` må man derfor knytte det opp mot ett objekt og dermed bruke dette objektets lås. En integer verdi som variabelen `saldo` er ikke et objekt, i motsetning til for eksempel et array, og derfor lager vi et objekt som vi kaller `lock` for så å knytte `synchronized()` opp mot dette objektet:

```
public static int saldo;                  // Felles variable, gir race condition
    public static Object lock = new Object(); // Argumentet til synchronized må være et objekt
```

Dermed kan man gjøre `synchronized(lock)` rundt en kodeblokk

```
synchronized(lock)
                   {
                      saldo++;
                   }
```

hvor man synkronisere mot lock-objektets lås.

I praksis betyr det at om en tråd kjører instruksjoner inne i denne kodeblokken, vil andre tråder settes på vent om de prøver å kjøre det samme kodeavsnittet. Dette avsnittet er da et kritisk avsnitt. Det tilsvarer helt å kalle wait før og signal etter et kritisk avsnitt. Gjør man det med eksempelet fra forrige forelesning, tar beregningene lenger tid, men saldo blir 0 til slutt.

Ser man på java bytekoden, kan man se at koden som oppdaterer saldo da blir beskyttet i en monitor:

```
$ javap -private -c SaldoThread
 
      17: getstatic     #17                 // Field lock:Ljava/lang/Object;
      20: dup
      21: astore_2
      22: monitorenter
      23: getstatic     #18                 // Field saldo:I
      26: iconst_1
      27: iadd
      28: putstatic     #18                 // Field saldo:I
```

Man kan også definere hele metoder som synchronized. I Figure 2-35 i læreboka defineres i et eksempel metoden

```
public synchronized void insert(int val)
```

Dette forsikrer programmereren om at kun en tråd av gangen kan kjøre denne metoden.

En løsning på vårt problem kunne være å gjøre følgende:

```
private static synchronized void upSaldo()
     {
	saldo++;
     }

   private static synchronized void downSaldo()
     {
	saldo--;
     }
```

og bruke disse metodene istedet for å endre variabelen direkte. Da ville også koden bli threadsafe og alltid gi saldo lik null til slutt.

---

## 12.13 Message passing

En annen metode for å sikre serialisering som også virker i distribuerte systemer er message passing. Konkurrerende tråder eller prosesser synkroniseres da ved å sende signaler til hverandre. En ulempe ved dette er at det generelt ikke er like effektivt som semaforer og monitorer.

---

## 12.14 Dining Philosophers Problem

Dette er et klassisk synkroniseringsproblem og som ofte har blitt brukt for å demonstrere synkroniseringsteknikker som semaforer og monitorer. Fem filosofer sitter rundt et bord og har fem gafler på deling. Når filosofene ikke tenker spiser de, men de trenger to gafler for å kunne spise. Hvordan kan man skrive fem filosof-prosesser som kjører samtidig og samtidig unngå en situasjon hvor alle griper en gaffel og blir sittende og vente? Dette er en såkalt deadlock-tilstand, vranglås, og det må unngås når man har samtidige tråder.

Filosoftilstander:

* tenker (uten gafler)
* Spiser spaghetti med 2 gafler

Tar opp en gaffel av gangen.

**Problem**: Programmer en filosofprosess slik at 5 prosesser kan spise og tenke i tidsrom av varierende lengde og dele ressursene (gaflene) uten at deadlock (vranglås) kan oppstå.

Illustrasjon:
Fra Tanenbaum: Lunch time in the Philosophy Department.

---

## 12.15 Deadlock

To eller fler prosesser venter på hverandre, ingen kommer videre. Eks. 1: P1 venter på P2, P2 venter på P3 og P3 venter på P1 (sirkulær venting)

Eks. 2: Deadlock med to semaforer S1 og S2, initialisert til 1:

| PA | PB-kode |
|---|-------|
| Wait(S1) |  |
|  | Wait(S2) |
| Wait(S2) |  |
|  | Wait(S1) |
| . | . |
| . | . |
| . | . |
| Signal(S1) | Signal(S2) |
| Signal(S2) | Signal(S1) |

---

## 12.16 Kriterier for at deadlock kan oppstå

* Mutex: ressurser som ikke kan deles
* En prosess kan beholde sine ressurser mens den venter på andre.
* En prosess kan ikke tvinges til å gi opp sin ressurs (felles minne, disk, etc.)

Med 1, 2 og 3 oppfylt, kan deadlock oppstå ved sirkulær venting! Mulige løsninger:

* Forhindre. Internt i OS-kjernen må deadlock forhindres. Umulig å forhindre bruker-deadlock.
* Løse opp deadlock. Generelt vanskelig.
* Ignorere problemet (mest vanlig metode for et OS).

---

## 12.17 Tråder i Python

Global Interpreter Lock (GIL) er en mekanisme som brukes av CPython, den mest populære implementeringen av Python, for å sikre at kun én tråd utfører bytekodeinstruksjoner om gangen. Dette låser hovedinterpreterløkken, slik at tråder ikke kan utføre Python-bytecode parallelt, selv på en flertrådet prosessor.

import multiprocessing, gir en løsning som lar deg opprette prosesser, som hver har sin egen Python-interpreter og minneplass. Dette omgår GIL og lar deg utnytte flere CPU-kjerner.

Noen biblioteker som NumPy og Pandas er implementert i C og frigjør GIL under tunge beregninger. Dette kan tillate parallell utførelse av beregninger uten å være begrenset av GIL.

Hvis man kjører følgende kode på en server med flere CPUer, vil kun en av trådene kjøre av gangen:

```
import threading

class SaldoThread(threading.Thread):
    MAX = 200000000
    count = 0
    saldo = 0  # Felles variabel, gir race condition?

    def __init__(self):
        super().__init__()
        SaldoThread.count += 1
        self.id = SaldoThread.count

    def run(self):
        print(f"Tråd nr. {self.id} starter")
        self.update_saldo()

    def update_saldo(self):
        if self.id == 1:
            for _ in range(SaldoThread.MAX):
                SaldoThread.saldo += 1
        else:
            for _ in range(SaldoThread.MAX):
                SaldoThread.saldo -= 1
        print(f"Tråd nr. {self.id} ferdig. Saldo: {SaldoThread.saldo}")

class NosynchThread:
    @staticmethod
    def main():
        print("Starter to tråder!")

        s1 = SaldoThread()
        s2 = SaldoThread()
        s1.start()
        s2.start()

        s1.join()
        s2.join()

        print(f"Endelig total saldo: {SaldoThread.saldo}")

if __name__ == "__main__":
    NosynchThread.main()
```