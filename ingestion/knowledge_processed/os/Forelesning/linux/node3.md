## 2.3 Manualsider og apropos

For å finne ut hvordan en viss kommando (f. eks. date) virker, kan man slå opp i manualsiden med

```
$ man date
```

Manualsiden er vanligvis for lang til å vises på en side. Du kan manøvrere deg nedover en side av gangen ved å taste space. Man søker ved å taste `/søkeord` og så taste "n" fortløpende for flere forekomster. Tast "q" for å avslutte.

Apropos: finner kommandoer relatert til et emne.

```
haugerud@studssh:~$ apropos compare
[ (1)                - check file types and compare values
bcmp (3)             - compare byte sequences
bzcmp (1)            - compare bzip2 compressed files
bzdiff (1)           - compare bzip2 compressed files
cg_diff (1)          - compares two Cachegrind output files
cmp (1)              - compare two files byte by byte
comm (1)             - compare two sorted files line by line
diff (1)             - compare files line by line

haugerud@studssh:~$ man diff
DIFF(1)                                                User Commands                                                DIFF(1)

NAME
       diff - compare files line by line

SYNOPSIS
       diff [OPTION]... FILES

DESCRIPTION
       Compare FILES line by line.

       Mandatory arguments to long options are mandatory for short options too.

       --normal
              output a normal diff (the default)
      -i, --ignore-case
              ignore case differences in file contents
```

*Alt som er listet i [] er opsjoner som kan men ikke må tas med. Tast "q" for å avslutte.*

```
studssh$ diff -i fil1 fil2
```

Og et google-søk med 'linux command line' eller 'linux bash' og det du ønsker å finne gir ofte raskt det du leter etter.

---

## 2.4 Tidsbesparende triks i et Linux-shell

Det finnes mange smarte knep som gjør inntasting av shell-kommandoer enklere. Bla tilbake i tidligere kommandoer og rediger dem med piltastene og trykk TAB-tasten for å finne mulige forlengelser av det du har skrevet inn.

* Tidligere kommandoer kan gjentas og endres med piltaster og vanlig editering
* , editere en tidligere kommando, og utføre den på nytt med Enter
* `$ exit` og CTRL-d avslutter et shell.
* Bruk Ctrl-C Hvis du skal stoppe et program som går i et shell

Man kan søke bakover i tidligere kommandoer ved å taste CTRL-r og så fortløpende det man søker etter, "mitt" i eksempelet under:

```
(reverse-i-search)`': 
(reverse-i-search)`mitt': mv mitt.sh new
```

Generelt kan man få skallet til å komplettere filnavn og kommandoer ved å trykke på TAB-tasten. Skal man f.eks. flytte til mappen kjempelangtnavn:

```
$ cd kj [TAB]
$ cd kjempelangtnavn
```

*Hvis du også har en mappe der du står som heter kjiipt, piper det etter TAB*

```
$ cd kj [TAB] [TAB]
kjempelangtnavn/ kjiipt/   
$ cd kje [TAB]
$ cd kjempelangtnavn
$ loc [TAB]
local      locale     localedef  locate     lockfile
```

Du kan også bruke TAB-tasten til å komplettere kommandoer du skal utføre. Skriver du

```
$ net
```

og så trykker TAB-tasten to ganger vil du få alle kommandoer som begynner på "net".

```
$ net
net         netcat      netkit-ftp  netstat
```

tast en "s" og TAB igjen og "netstat" fullføres av shellet.

Se mer om dette og andre tips under 'Nyttige tips om bruk av Linux' under Linux-help ikonet på kurs-siden.

Hvis du kjører Linux med grafisk brukergrensesnitt vil i noen tilfeller kopiering og lignende være litt anderledes enn i andre systemer:

* Copy = Merk område med venstre musetast
* Paste = høyre musetast (putty) eller midtre musetast(linux)
* Windows varianten: cut=CTRL-x copy=CTRL-c og paste=CTRL-v virker i de fleste nyere GUI-applikasjoner

---

## 2.5 Linux-shellscript

* Samling av kommandolinjer
* program som utføres linje for linje
* Kompileres ikke

|   |   |
|---|---|
| + | Raskt å lage. |
| + | Fint for små oppgaver. |
| - | Langsomt i forhold til kompilert kode. |
| - | Mangler avanserte datastrukturer. |
| - | Kryptisk syntaks |
| - | Vanskelig å feilsøke/debugge |

En meget nyttig måte å teste ut bash-script på er å bruke -x parameteren. Kjør scriptet ditt, som heter f. eks. mittscript, slik:

```
$ bash -x mittscript
$ bash -x mittscript
+ '[' -f /etc/passwd ']'
+ echo Bra
Bra
og hver kommando som utføres blir skrevet til skjermen.
```

---

## 2.6 Absolutt og relativ path

En path (bane) til en mappe eller en fil angis alltid absolutt eller relativt til posisjonen man er i filtreet. Absolutt path begynner alltid med / som er rot-mappen som alle de andre henger på.

```
$ pwd
   /
$ cd home
$ pwd
   /home
$ cd etc               <----- Relativ path
bash: cd: etc: No such file or directory
$ cd /etc              <----- Absolutt path
```

| Alt I: Relativ path | AltII: Absolutt path |
|-------------------|--------------------|
| Fra / | Fra hvor som helst |
| $ cd usr | $ cd /usr/bin |
| $ cd bin | $ pwd |
| $ pwd | /usr/bin |
| /usr/bin |  |
| Begynner ikke med / | Begynner med / |

Illustrasjon:
Mappen /usr/bin i filtreet.

---

## 2.7 Mer filbehandling

| Linux-kommando | resultat |
|--------------|--------|
| $ tree | viser den underliggende mappe-strukturen |
| $ sudo apt-get install tree | Installerer programmet tree om det ikke finnes fra før |
| $ mv dir1 dir2 | flytter mappen dir1 til mappen dir2 |
| $ cp /bin/c* /tmp | Kopier alt som begynner på c i /bin til /tmp |
| $ cp -R dir1 dir2 | Kopier dir1 med undermapper til dir2 |

Illustrasjon:
mv av hele mapper

Illustrasjon:
cp -R av hele mapper

---

## 2.8 Sletting av filer og mapper

NB! Fjernes for godt (ingen undelete)

| Linux-kommando | resultat |
|--------------|--------|
| $ rm fil1 | sletter fil1 (umulig å få tilbake) |
| $ rmdir Mappe | kun tom mappe |
| $ rm -R Mappe | sletter mappe og alle undermapper. Farlig |
| $ rm -i fil2 | ber om bekreftelse først |

---

## 2.9 Enda mer filbehandling

| Linux-kommando | resultat |
|--------------|--------|
| $ locate noe | finner alle filer og mapper med navn som inneholder tekststrengen “noe” |
| $ find tmp -name fil.txt | finner alt under tmp med navn som inneholder fil.txt |
| $ find . -name "*fil*" | finner alt under mappen du står som inneholder strengen "fil" i navnet |
| $ more fil1 | skriv til skjerm; en side av gangen |
| $ grep group /etc/passwd | skriv til skjerm alle linjer som inneholder strengen group |
| $ wc -l /etc/passwd | tell antall linjer i /etc/passwd |
| $ grep group /etc/passwd | wc -l | tell antall linjer som inneholder strengen group |

---

## 2.10 Lovlige filnavn

Alle tegn untatt / er lov// unngå spesielle tegn som æ,ø,å og mellomrom *for de 
må spesialbehandles (som "en fin fil")* Bruk A-Z a-z 0-9 _ .

* fil1
* fil1.txt
* Index.html
* VeldigLangeFilnavn.help
* fil2.ver3.tekst

Linux er case-sensitiv. **fil1 er IKKE den samme filen som FIL1** .

---

## 2.11 Prosesser

* `ps`
* `ps aux`
* `ps aux | grep root`
* `man ps`
* `top`

---

## 2.12 Linux-maskiner

* Hver Linux-maskin kalles en "host" (vert)
* Flere brukere kan logge inn og bruke samme host samtidig.
* Hver host har et navn: studssh (Linux, fil og www-server), rex (desktop), etc.
* Entydig adresse som kan nås fra hele verden krever domenenavn i tillegg: studssh.cs.oslomet.no, login.uio.no

Man kan logge inn fra hvorsomhelst i verden til en annen maskin:

```
ssh os@studssh.cs.oslomet.no
os@studssh.cs.oslomet.no's password:
[os]studssh:~$
```

Når man logger inn med ssh (Secure Shell) krypteres alt som sendes.

---

## 2.13 Orientering: Hvem, hva, hvor

| Linux-kommando | Gir deg |
|--------------|-------|
| $ whoami | brukernavn |
| $ hostname | maskin-navn |
| $ uname | Operativsystem (Linux, Solaris,.....) |
| $ uname -a | OS, versjon, etc. |
| $ who | hvem som er logget inn |
| $ type chmod | hviklet program kjøres med chmod? |
| $ history | tidligere kommandoer |

---

## 2.14 Symbolske linker til filer (symbolic links)

```
$ ln -s fil1 fil2
$ ls -l
-rw-------   1 haugerud drift             20 Sep  4 18:44 fil1
lrwxrwxrwx   1 haugerud drift              4 Sep  4 18:43 fil2 -> fil1
$ cat fil2
Denne teksten står i fil1
```

---

## 2.15 Symbolske linker til mapper

Ved å lage en link til en mappe kan man lage en snarvei i filtreet.

```
$ pwd
/home/min/dir1
$ ln -s /usr/bin mbin
$ ls -l
lrwxrwxrwx   1 haugerud drift              8 Sep  4 19:02 mbin -> /usr/bin
```

Illustrasjon:
Symbolsk link fra mbin til /usr/bin

```
$ cd mbin
$ ls
822-date                giftopnm                    nawk                  rcsmerge
Esetroot                giftrans                    ncftp                 rdist
.......etc.......            # alle filene i /usr/bin
$
$ pwd
/home/min/dir1/mbin          # /bin/pwd gir path relativt til linken
$ type pwd
pwd is a shell builtin       # kommandoen pwd er bygd inn i bash
$ /bin/pwd                   # /bin/pwd gir absolutt path til der du er
/usr/bin
$ cd ..
$ pwd
/home/min/dir1               # ikke /usr
```

---

## 2.16 Filrettigheter

Alle filer tilhører en bruker og en gruppe av brukere. For hver mappe og fil kan eieren sette rettighetene for

* brukeren filen tilhører (seg selv)
* gruppen filen tilhører
* alle andre

```
$ ls -l
-rwxrw-r--   1 haugerud drift           7512 Aug 30 14:20 fil.exe
```

|   |   |
|---|---|
| - | fil (d = mappe, l = link) |
| rwx | fileier sine rettigheter (r = read, w = write, x = executable) |
| rw- | gruppens rettigheter (kan lese og skrive) |
| r- - | alle andre sine rettigheter (kan bare lese filen) |
| 1 | antall hard links |
| haugerud | eiers brukernavn |
| drift | gruppen som filen tilhører (definert i /etc/group) |
| 7512 | antall byte |
| Aug 30 14:20 | tidspunkt filen sist ble endret |
| fil.exe | filnavn |

For mapper betyr x at man har tilgang til mappen. Er ikke x satt, kan man ikke gå dit. Og da kan man heller ikke liste filer der eller kopiere noe dit.

---

## 2.17 Hvordan forstå filrettigheter

Rettighetene til eier, gruppe og andre er representert med kun tre bit. Dette begrenser hvor mange forskjellige rettigheter man kan ha, samtidig gjør det det enkelt å representere rettighetene som tall og å regne ut rettigheter i hodet. Dette gjør man på følgende måte:

* kjørerettigheter = 1
* skriverettigheter = 2
* leserettigheter = 4

Ved hjelp av disse tallene (og tallet 0) kan vi telle fra 0 til 7 ved å kombinere dem på forskjellige måter. F.eks:

* Kjørerettigheter + leserettigheter = 5
* Kjøre + lese + skrive = 7 (maks)
* skrive og kjøre, men ikke lese = 3

---

## 2.18 Endre filrettigheter

Numerisk endring av filrettigheter:

```
$ chmod 644 fil.txt <- gir rw-r--r--
$ chmod -R 755 dir  <- gir rwxr-xr-x til dir og alle filer og mapper under dir
```

Tallene betyr:

| rwx | octal | tekst |
|---|-----|-----|
| 000 | 0 | - - - |
| 001 | 1 | - - x |
| 010 | 2 | - w - |
| 011 | 3 | - w x |
| 100 | 4 | r - - |
| 101 | 5 | r - x |
| 110 | 6 | r w - |
| 111 | 7 | r w x |

For mapper: Rettighet x (execute) gir tilgang til mappen.

Illustrasjon:
Man må ha tilgangsrettighet (x) til alle
  mappene i path for å kunne lese en fil (her: se et web-bilde i /home/www/bilder). Alternativt:

```
$ chmod a+xr fil.txt <- gir read og execute til alle (a)
$ chmod g-w fil.exe  <- fratar gruppen skriverettigheter
```

u = user, g = group, o = other, a = all (både u, g og o)

---

## 2.19 umask

Kommandoen `umask` setter hva som skal være standard rettigheter for nye filer og mapper.

```
$ umask
0022
$ mkdir dir
$ touch fil
$ ls -l
total 1
drwxr-xr-x  2 haugerud drift 512 Aug 30 23:52 dir
-rw-r--r--  1 haugerud drift   0 Aug 30  2006 fil
```

`umask` er en 'maskering'. For hver brukergruppe settes rettighet '111 minus mask' for mapper og '110 minus mask' for filer. Bit som er satt i mask, settes alltid til null.

```
$ umask 027
$ mkdir dir2
$ touch fil2
$ ls -l
total 2
drwxr-x---  2 haugerud drift 512 Aug 30 23:53 dir2
-rw-r-----  1 haugerud drift   0 Aug 30  2006 fil2
```

Det er ikke så viktig å vite detaljene i hvordan umask virker, for man kan raskt teste ut hva resultatet blir om man har en viss forståelse. Slik beregnes rettighetene:

| For mappe | 7 = 111 | 7 = 111 | 7 = 111 |
|---------|-------|-------|-------|
| minus mask | 0 = 000 | 2 = 010 | 7 = 111 |
| resultat | 7 = 111 | 5 = 101 | 0 = 000 |
| rettighet | 7 = r w x | 5 = r - x | 0 = - - - |

og for filer

| For fil | 6 = 110 | 6 = 110 | 6 = 110 |
|-------|-------|-------|-------|
| minus mask | 0 = 000 | 2 = 010 | 7 = 111 |
| resultat | 6 = 110 | 4 = 100 | 0 = 000 |
| rettighet | 6 = r w - | 4 = r - - | 0 = - - - |

---

## 2.QA Spørsmål

**Gir skriverettighet leserettighet?**

Har man automatisk leserettigheter hvis man har skriverettighet? Svar: Nei, r, w og x settes uavhengig av hverandre. Men `-w-` (kun skriverettigheter) brukes i praksis aldri.

**Kan man sette bare skriverettigheter på en fil?**

Ja. chmod 200 fil Da kan man skrive til filen, men ikke lese den.

**Hvilke rettigheter trenger man for å kunne slette en fil?**

w, skriverettigheter.

**Kan man slette en fil man selv ikke har skriverettigheter til?**

Ja, om man har skriverettigheter til mappen den ligger i, men man får en advarsel og blir spurt først. Det samme gjelder en fil med ingen rettigheter, 000.

**Hva skjer med eierskapet om man kopierer en annens fil?**

Da blir man selv eier til den kopierte filen.