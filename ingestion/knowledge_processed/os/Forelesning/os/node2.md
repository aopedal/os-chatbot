## 1.2 Om kurset

* Kurset består av to relativt uavhengige deler
  * Operativsystemer(OS)
  * Praktisk bruk av operativsystemer (Linux/Windows/Docker)
* Foreleser: Hårek Haugerud, haugerud@oslomet.no, rom SG214, SG29
* Hver onsdag fra 8:30: Flipped classroom-forelesninger
* Videoer hvor alt fagstoff foreleses legges ut uken før
* All kursinfo: `https://www.cs.oslomet.no/~haugerud/os` og Canvas
* Viktig: Jobb med **oppgaver**!!
* grunnlag for valgfaget Nettverks- og systemadministrasjon
* grunnlag for OsloMet-mastergraden Cloud-based services and operations (tidligere Network and System administration)

---

## 1.3 Vesentlige mål for kurset

* Lære å bruke kommandolinje, inkludert script (Mest Linux og Docker, noe Windows)
* Lære hvordan en datamaskin virker på alle nivåer, fra transistorer og opp til operativsystemet

---

## 1.4 Pensumlitteratur

* To kompendier dekker pensum
  * os.pdf
  * linux.pdf
  * Versjonene fra 2024 ligger under filer på Canvas og under Forelesninger på kurs-siden
  * Kompendiene blir fortløpende oppdatert i løpet av semesteret med årets endringer
* Anbefalt støtteliteratur: Tanenbaum, Andrew S.: Modern operating systems : Global edition, 4th edition, 2014
* Omfattende og dyr, men en meget god bok

---

## 1.5 Eksamen

* 3 timers skriftlig Inspera eksamen (teller 100%)
* Ingen hjelpemidler tillatt
* Linux kommandolinje tilgjengelig under eksamen i Silurveien

---

## 1.6 Obligatoriske gruppe-innleveringer

* Uke-oppgavene som er markert som obligatoriske for hver uke samles opp og leveres ved hver innlevering.
* Alle obliger MÅ være godkjent for å kunne melde seg opp til eksamen

---

## 1.7 Obligatoriske individuelle innleveringer

Individuelle Multiple Choice tester med tidsbegrensning

* Utgår trolig i 2025
* 3 korte Multiple Choice tester (7-10 minutter)
* Trekkes tilfeldig fra en database av spørsmål
* Må svare riktig på minst 7 av 10 for å få godkjenning
* Hvis ikke MÅ studentassistent kontaktes. Hen går igjennom svarene og anbefaler hva som bør jobbes med og oppdaterer databasen slik at du får en ny sjanse

---

## 1.8 Nyttige personer

* Foreleser
* Studentassistenter, i øvingstimene
* Hedda Marie Westlin, heddamar@oslomet.no, Linux drift (data2500-server, etc)

---

## 1.9 Hva er et operativsystem (OS)?

Et OS er et software-grensesnitt mellom brukeren og en datamaskins hardware.

---

## 1.10 Hvor stort er et operativsystem?

Kildekoden til et moderne operativsystem som Linux eller Windows er på omtrent fem millioner linjer kode. Det tilsvarer omtrent 100 Tanenbaum-bøker som hver er på 1000 sider med 50 linjer pr side.

Så stor er alene kildekoden for selve operativsystemkjernen. Hvis man tar med GUI, biblioteker og annen nødvendig system software (som Windows explorer), blir størrelsen ti til tyve ganger større.

---

## 1.11 OS-definisjon

Forsøk på definisjon: OS er programvare hvis hensikt er:

|   |   |
|---|---|
| A | Gi applikasjonsprogrammer og brukere enhetlig, enklere og mer abstrakt adgang til maskinens ressurser |
| B | Administrere ressursene slik at prosesser og brukere ikke ødelegger for hverandre når de skal aksessere samme ressurser. |

Eksempler:

|   |   |
|---|---|
| A | filsystemet som gir brukerne adgang til logiske filer slik at brukerne slipper å spesifisere disk, sektor, sylinder, lesehode osv. |
| B | Et system som sørger for at brukerne ikke skriver over hverandres filer; fordeling av CPU-tid. |

---

## 1.12 Prinsippskisse av Linux

Illustrasjon:
Prinsippskisse for et IT-system. GNU/Linux distribusjonen er 
markert med stiplede linjer. API = Application Programming Interface.

GNU er en rekursiv forkortelse (høy nerdefaktor) og står for 'GNU's not Unix'. Bakgrunnen for begrepet GNU/Linux er at GNU-prosjektet som ble startet av Richard Stallmann i 1983. GNU sto bak mange av de veldig viktige delene som ligger utenfor kjernen, som shellet bash og kompilatoren gcc. Operativsystemkjernen kan for eksempel ikke gjøre så mye fornuftig hvis man ikke kan kompilere programmer slik at de kan kjøres. Det er fortsatt noen som bruker begrepet GNU/Linux når de omtaler operativsystemet Linux, men det vanligste er å bare si Linux. Og bruken av GNU/Linux kan sammenlignes med distribusjoner av Linux som Ubuntu og Red Hat. Disse distribusjonene gjør også en rekke tilpasninger og lager systemprogrammer som skal gjøre det enklere, bedre og sikrere å bruke Linux-kjernen.

---

## 1.13 Sentralt begrep: prosess

Prosess er et svært viktig Operativsystem-begrep.

---

## 1.13.1 Linux prosesser

```
21:49:07 up 7 days,  7:05,  2 users,  load average: 0.01, 0.02, 0.00
66 processes: 64 sleeping, 2 running, 0 zombie, 0 stopped
CPU states:   3.8% user,   2.4% system,   0.0% nice,  93.8% idle
Mem:    901440K total,   875496K used,    25944K free,    18884K buffers
Swap:   128516K total,     2252K used,   126264K free,   681000K cached

  PID USER     PRI  NI  SIZE  RSS SHARE STAT %CPU %MEM   TIME COMMAND
17938 root      11 -10 93532  10M  2000 S <   2.3  1.2   0:31 XFree86
18958 haugerud  17   0  8800 8800  7488 R     2.3  0.9   0:01 kdeinit
18788 haugerud  11   0  3548 3548  2572 S     0.7  0.3   0:03 artsd
19272 haugerud  12   0   956  956   748 R     0.3  0.1   0:00 top
    1 root       8   0   484  456   424 S     0.0  0.0   0:00 init
    2 root       9   0     0    0     0 SW    0.0  0.0   0:00 keventd
    3 root      19  19     0    0     0 SWN   0.0  0.0   0:00 ksoftirqd_CPU0
    4 root       9   0     0    0     0 SW    0.0  0.0   0:29 kswapd
    5 root       9   0     0    0     0 SW    0.0  0.0   0:00 bdflush
    6 root       9   0     0    0     0 SW    0.0  0.0   0:19 kupdated
  123 daemon     9   0   432  428   356 S     0.0  0.0   0:00 portmap
  130 root       9   0     0    0     0 SW    0.0  0.0   0:01 rpciod
  131 root       9   0     0    0     0 SW    0.0  0.0   0:00 lockd
  196 root       9   0   872  868   724 S     0.0  0.0   0:02 syslogd
  199 root       9   0  1092 1088   420 S     0.0  0.1   0:00 klogd
  204 root       9   0   700  700   604 S     0.0  0.0   0:00 rpc.statd
  209 root       9   0   944  940   628 S     0.0  0.1   0:06 inetd
  293 root       9   0  2076 1860  1608 S     0.0  0.2   0:02 sendmail
  314 root       8   0  1280 1224  1068 S     0.0  0.1   0:00 sshd
  319 root       9   0  3028 2208   596 S     0.0  0.2   0:00 xfs
  321 root       9   0  1968 1968  1748 S     0.0  0.2   0:00 ntpd
```

---

## 1.13.2 Windows XP prosesser

```
PS C:\Documents and Settings\mroot> ps

Handles  NPM(K)    PM(K)      WS(K) VM(M)   CPU(s)     Id ProcessName
-------  ------    -----      ----- -----   ------     -- -----------
    105       5     1176       3616    32     0,07   1212 alg
    342       5     1512       3180    22    20,56    688 csrss
    118       4     1056       2808    21     0,90    972 csrss
    144       3     1812       3548    21     0,44   1132 csrss
     76       4     1004       3684    30     0,05    376 ctfmon
     72       4      964       3452    30     0,02    460 ctfmon
     86       2     1420       2200   413     0,02   2032 cygrunsrv
    157       4     1952       6180    44     0,07   1776 DW20
    352      10     8772      14460    85     0,66    520 explorer
    362      10     8036      14856    84     0,75   1864 explorer
      0       0        0         28     0               0 Idle
    164       6     3168       4724    38     2,65   1040 logonui
    389       9     3908       2284    41     0,38    768 lsass
    276       9    27568      25488   140     1,68   2132 powershell
     79       3     1196       3576    34     0,02    232 rdpclip
    106       4     1392       4384    35     0,03   1800 rdpclip
    154       5     4348       5884    56     0,08   2080 rundll32
    356       8     3328       5116    35     1,24    756 services
     40       2      400       1504    11     0,01    248 shutdownmon
     31       1      152        412     3     0,04    616 smss
    120       5     3148       4780    41     1,23   1468 spoolsv
     86      23     2092       3428   413     0,05    488 sshd
    263       6     2908       5452    61     0,11    924 svchost
    239      13     1724       4248    34     0,31   1080 svchost
   1561      62    15192      25432   140     5,15   1168 svchost
     76       3     1308       3584    29     1,11   1264 svchost
    161       5     1492       3912    34     1,23   1372 svchost
```

---

## 1.13.3 Definisjon av prosess

Alternative definisjoner:

* Et program som kjører
* Arbeidsoppgavene en prosessor gjør på et program
* 
  * Et kjørbart program
  * Programmets data (variabler, filer, etc.)
  * OS-kontekst (tilstand, prioritet, prosessor-registre, etc.)
* Et programs ånd/sjel
    * I en analogi hvor programmet som kjører er et menneskes DNA, vil prosessen være hele livet et menneske lever:
    * **Program**: = DNA
    * **Prosess**: = livet
    * **Hardware**: = Organer/Universet/hus/mat/bygninger
    * **OS**: = staten/lovverket
    * **kill, Ctrl-C**: = drap
    * **root/Administrator**: = Gud
    * **CPU**: =Hjerne
    * **kriminalitet**: = Black hat hacking

---

## 1.14 Abstraksjon og hierarkier

*Disse begrepene som er illustrert i Figur 2 er generelt sett blant de viktigste innen all databehandling, og spesielt innen OS.*

Illustrasjon:
Abstraksjoner i et hierarki

---

## 1.14.1 Linux-eksempel på hierarki

*Med verktøyet Bourne Again-shell (bash):*

```
$ cat /etc/motd
```

Hjelpeprogrammet cat bruker flere systemkall for å skrive /etc/motd til skjermen. *Et C-program kan gjøre direkte kall til Linux-kjernen. 
F. eks. klargjør systemkallet open for å lese fra en fil:*

```
open("/etc/motd", O_RDONLY|O_LARGEFILE) = 3
```

Kommandoen cat betstår av en serie systemkall:

* open
* read
* close
* etc.

Hvilke systemkall et Linux-program gjør, kan man se med kommandoen strace :

```
$ strace cat /etc/motd
execve("/bin/cat", ["cat", "/etc/motd"], [/* 36 vars */]) = 0
uname({sys="Linux", node="rex", ...})   = 0
brk(0)                                  = 0x804d000
old_mmap(NULL, 4096, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANONYMOUS, -1, 0) = 0x40017000
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/etc/ld.so.preload", O_RDONLY)    = -1 ENOENT (No such file or directory)
open("/etc/ld.so.cache", O_RDONLY)      = 3
fstat64(3, {st_mode=S_IFREG|0644, st_size=67455, ...}) = 0
old_mmap(NULL, 67455, PROT_READ, MAP_PRIVATE, 3, 0) = 0x40018000
close(3)                                = 0
access("/etc/ld.so.nohwcap", F_OK)      = -1 ENOENT (No such file or directory)
open("/lib/libc.so.6", O_RDONLY)        = 3
read(3, "\177ELF\1\1\1\0\0\0\0\0\0\0\0\0\3\0\3\0\1\0\0\0\360^\1"..., 512) = 512
fstat64(3, {st_mode=S_IFREG|0755, st_size=1244688, ...}) = 0
old_mmap(NULL, 1254852, PROT_READ|PROT_EXEC, MAP_PRIVATE, 3, 0) = 0x40029000
old_mmap(0x40151000, 32768, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED, 3, 0x127000) = 0x40151000
old_mmap(0x40159000, 9668, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) = 0x40159000
close(3)                                = 0
munmap(0x40018000, 67455)               = 0
brk(0)                                  = 0x804d000
brk(0x806e000)                          = 0x806e000
brk(0)                                  = 0x806e000
fstat64(1, {st_mode=S_IFCHR|0600, st_rdev=makedev(136, 25), ...}) = 0
open("/etc/motd", O_RDONLY|O_LARGEFILE) = 3
fstat64(3, {st_mode=S_IFREG|0644, st_size=712, ...}) = 0
read(3, "Linux rex 2.6.1skas #3 SMP Mon A"..., 4096) = 712
write(1, "Linux rex 2.6.1skas #3 SMP Mon A"..., 712) = 712
read(3, "", 4096)                       = 0
close(3)                                = 0
close(1)                                = 0
exit_group(0)                           = ?
```

---

## 1.15 Datamaskinarkitektur

Operativsystemkjernen styrer maskinens hardware slik at programmene som skal kjøres kan få utført det de ønsker uten at de ødelegger for hverandre. For å forstå hvordan et operativsystem virker, må man derfor også ha noe forståelse for de grunnleggende delene av en datamaskin og ikke minst forstå datamaskinens hjerne, CPU-en.

---

## 1.16 Digitalteknikk og konstruksjon av kretser

Alle tall i en datamaskin er representert i det binære tallsystem med nuller og enere og fysisk representeres det med ingen eller positiv elektrisk spenning i forhold til jord. Ved å sette slike bit med verdi null eller en ved siden av hverandre, kan man velge å la dem representere binære tall. For eksempel vil 32 bit ved siden av hverandre kunne representere alle heltall fra 0 til 4 294 967 295. Når man har en slik definisjon av tall, kan man definere alt man trenger i en datamaskin, desimaltall, bokstaver (for eksempel ASCIII, 80 = P), eller pixler og farger i grafikk. Alt representeres med tall som igjen representeres binært med bit som er av eller på, representert ved 0 Volts spenning elle 5 Volts spenning. Et tall kan representeres med 4 bits som vist i figur 1.16 .

Illustrasjon:
Et fire bits tall representer ved ulike spenningsforskjeller

For å kunne lage en datamaskin må man kunne utføre logiske og matematiske operasjoner på slike samlinger av bit. For eksempel må man kunne sammenligne, addere, subtrahere, multiplisere, dividere og gjøre shift-operasjoner. For å få til dette må man lage elektriske kretser som utfører denne type operasjoner. Det må for eksempel være mulig å få en CPU til å legge sammen to tall og gi et resultat. Dette kan man få til ved digitale kretser også kalt logiske kretser. La oss først se på hva man trenger for å kunne addere sammen to tall.

---

## 1.17 Logiske porter og binær logikk

Alt CPU-en eller prosessoren i en datamaskin gjør er å manipulere på nuller og enere og ved hjelp av dette kan all verdens tenkelige beregninger utføres. Det teoretiske grunnlaget for manipulasjon av nuller og enere, binær logikk, ble utviklet på 1800-tallet. Ved hjelp av tre logiske operatorer, AND, OR og NOT, kan alle logiske beregninger utføres. Så ved å bygge disse tre logiske operatorene i hardware og i tillegg ha en enhet som kan lagre verdien 1 eller 0, har man alt som skal til for å bygge en datamaskin. En 0 blir representert ved ingen spenning og 1 ved for eksempel 5 Volts spenning. Så kan man ved hjelp av matematisk logikk konstruere en datamaskin som kan legge sammen, trekke fra og sammenligne binære tall og det er stort sett alt man trenger.

Den fysiske implementasjonen av AND, OR og NOT operatorene kalles porter, det kommer en eller to ledninger inn i den ene enden og går en ledning ut av den andre. Teoretisk fysikks store oppdagelse i det tyvende århundre, kvantemekanikken, la grunnen for halvlederteknologien og transistoren. I 1956 fikk Shockley, Bardeen og Brattain Nobelprisen i Fysikk for å konstruere transistoren som har gjort det mulig å lage slike porter ekstremt små. På en CPU-chip med noen få kvadratcentimeters overflate kan det være plass til 100 millioner slike porter og med ledninger mellom dem som er så tynne som 5 nanometer. Et hårstrå er til sammenligning 100 000 nm. De fysiske grenesene for hvor lite det er mulig å lage de integrert kretsene begynner å nærme seg og derfor klarer man ikke å øke klokkefrekvensen så hurtig som tidligere.

I Fig. 4 ser vi de tre grunnleggende portene og hvordan man kan sette dem sammen til mer kompliserte kretser.

Illustrasjon:
De tre grunnleggende logiske byggestenene i en prosessor, AND, OR og NOT-porter.

Logikken til disse operatorene og tilsvarende porter kan beskrives ved såkalte sannhetstabeller, ved binær logikk og ved å tegne portene som vist i følgende avsnitt.

---

## 1.17.1 AND

Sannhetstabell:

| A | B | Ut = |
|---|---|----|
| 0 | 0 | 0 |
| 0 | 1 | 0 |
| 1 | 0 | 0 |
| 1 | 1 | 1 |

Logisk AND-operator:

Illustrasjon:
Tegning av AND-port

---

## 1.17.2 OR

Sannhetstabell:

| A | B | Ut = |
|---|---|----|
| 0 | 0 | 0 |
| 0 | 1 | 1 |
| 1 | 0 | 1 |
| 1 | 1 | 1 |

Logisk OR-operator:

Illustrasjon:
Tegning av OR-port

---

## 1.17.3 NOT

Sannhetstabell:

| A | Ut = |
|---|----|
| 0 | 1 |
| 1 | 0 |

Logisk NOT-operator:

Illustrasjon:
Tegning av NOT port

I tegningen av OR-porten, betyr det for eksempel at hvis det kommer en spenning 0 inn på inngang A og en spenning 1 inn på inngang B, vil det gå en spenning 1 ut. Slike porter kan man så sette sammen til kompliserte kretser. Det er for eksempel ikke veldig mange porter som skal til for å bygge en krets som kan legge sammen to firebits tall, slik CPU-en omtalt nedenfor kan. Alle tall i en datamaskin er representert i det binære tallsystem med nuller og enere, eller som vi har sett, med ingen eller positiv elektrisk spenning.

I figurene ser man hvordan det er vanlig å tegne AND, OR og NOT-porter i krets-diagram.