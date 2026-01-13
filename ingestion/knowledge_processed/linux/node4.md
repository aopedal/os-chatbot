## 3.3 Dagens faktum: UNIX' opprinnelse

Linux er en åpen kildekode variant av operativsystemet UNIX som opprinnelig ble skrevet i PDP-7 assembler av Ken Thompson i 1969 ved AT&T Bell Laboratories. Han gjorde det for å kunne kjøre spillet "space travel" på minicomputeren PDP-7 (9 Kbyte internminne). Thompson lagde senere programmeringsspråket B og var også med å lage språket Go mens han jobbet hos Google. Progrmmeringsspråket C ble laget av Dennis Ritchie rundt 1970 for å kunne skrive UNIX i et plattformuavhengig språk; noe som ble gjort i 1973. UNIX og C hadde stor betydning for utviklingen av dataindustrien.

Illustrasjon:
Ken Thompson(foran) og Dennis Ritchie ved en PDP-11.

---

## 3.4 Shell-variabler

*I et Linux-shell finnes det systemvariabler som $HOME, $PATH, $PS1, $CLASSPATH og mange
andre som systemet og mange applikasjoner som f. eks. Jbuilder bruker. En bruker kan også definere
sine egne lokale variabler med selvlagde variabelnavn.
Det er vanlig, men ikke påkrevet å bruke små bokstaver i
variabelnavnet til lokale variable.*

```
$ os=Linux
$ dato='Thu Jan 25'
```

Det må *ikke* være mellomrom før og etter =. Variabler refereres til med et $-tegn foran navnet:

```
$ echo $os
Linux
$ echo $dato
Thu Jan 25
```

Navnet kan avgrenses med

```
$ echo $osfrelst

$ echo ${os}frelst
Linuxfrelst
```

*Kommandoer for å liste og fjerne variabler:*

```
$ set         # Lister alle definerte variabler og funksjoner
$ unset os    # Fjerner definisjonen av os
```

---

## 3.5 Globale shell-variabler

I utgangspunktet er shell-variabler lokale og bare kjent i det shellet de har blitt definert. Man kan gjøre variabler globale med kommandoen `export` :

```
$ date='30. januar'
$ os=Linux
$ export os
$ export nyglobal='ny global verdi'
```

Variabelene `$os` og `nyglobal` er nå globale og vil arves av nye shell som startes, men det vil ikke `$date` :

```
$ bash
$ echo $os
Linux
$ echo $nyglobal
ny global verdi
$ echo $date
```

men som vi ser kjenner det nye shellet ikke til variabelen `$date` , den er lokal og bare kjent i shellet den ble definert i.

* vanlig å skrive globale variabler med store bokstaver
* kalles ofte ENVIRONMENT varibler ($HOME, $PATH, $EDITOR, $CLASSPATH)
* leses av programmer som ønsker å vite default editor, classpath, etc
* Globale variabler kan listes med `export`
* Variabler kan defineres direkte som globale i bash: `$ export os=Linux`
* Kommandoen `$ env` lister alle definerte globale variabler

---

## 3.6 Hvor ligger alle kommandoene egentlig? Svar: PATH

*$PATH er en global variabel som inneholder en streng med alle mapper 
(separert med kolon) som shellet leter i for å finne kjørbare filer når et 
  kommandonavn tastes inn til shellet*

```
studssh$ echo $PATH
/opt/bin:/local/iu/bin:/local/gnu/bin:/local/bin:/usr/X11R6/bin:/usr/bin:/bin:.:
studssh$ type ls              # type gir hvilket program shellet starter
ls is /bin/ls
```

*Når du taster inn*

```
$ ls
```

*leter bash igjennom alle mappene i $PATH etter en fil med navn ls helt til 
det finner en i den nest siste (/bin) og kjører den.* Hvis du gjør PATH tom:

```
$ PATH=""
```

vil shellet ikke finne vanlige kommandoer som `mv` og `ls` fordi mappen `/bin` ikke er med i `$PATH` .

---

## 3.7 Prosesser

Hver gang vi starter et program lager Linux en uavhengig prosess: $ emacs Starter vi fra et shell, venter shellet på at programmet skal bli ferdig. $emacs& $ Dette starter emacs som en bakgrunnsprosess

|   |   |
|---|---|
| kommando | virkning |
| $ ps | Lister shellets prosesser |
| $ ps aux (eller -Al) | Alle prosesser |
| $ top | Dynamisk ps -aux |
| $ kill 1872 | Drep prosess med PID 1872 |
| $ kill -9 1872 | Forsert drap av 1872 |
| $ time mittScript.bash | Måler tidsforbruket |

---

## 3.8 Apostrofer

*I bash brukes 3 forskjellige typer apostrofer ', ` og " som alle 
  har forskjellig betydning:*

```
$ dir=mappe

$ echo 'ls $dir'      ' -> Gir eksakt tekststreng
ls $dir

$ echo "ls $dir"      " -> Variabler substitueres; verdien av $dir skrives ut.
ls mappe

$ echo `ls $dir`      ` -> utfører kommando!
fil1 fil2 fil.txt
```

Huskeregel

```
'  ->  /  -> Linux    -> vet hva man får
`  ->  \  -> Windows -> aner ikke hva man får
```

Et mer robust alternativ når en kommando skal utføres:

```
echo $(ls $dir)
```

Dette gir også mer lesbar kode. I tillegg kan man ikke ha uttrykk med apostrofer inni hverandre:

```
rex$ line=`grep `whoami` /etc/passwd`
Usage: grep [OPTION]... PATTERN [FILE]...
Try 'grep --help' for more information.
bash: /etc/passwd: Permission denied
```

Men dette går fint med `$()` syntaksen:

```
rex$ line=$(grep $(whoami) /etc/passwd)
rex$ echo $line
haugerud:x:5999:9002:Hårek Haugerud,,,:/home/haugerud:/bin/bash
```

Så generelt anbefales det å bruke denne. Om man prøver følgende uttrykk med apostrofer inni hverandre:

```
haugerud@studssh:~/mappe$ var=`/bin/ls `pwd` `
```

Det vil si, det ga ingen feilmeldinger. Men om man ser nøyere på hva resultatet ble

```
haugerud@studssh:~/mappe$ echo $var
fil.txtpwd
haugerud@studssh:~/mappe$ pwd
/iu/nexus/ua/haugerud/mappe
haugerud@studssh:~/mappe$ ls
fil.txt
```

så ser vi at de ikke fungerte som ønsket. Igjen er det bedre å bruke `$()` konstruksjonen:

```
haugerud@studssh:~/mappe$ var=$(/bin/ls $(pwd))
haugerud@studssh:~/mappe$ echo $var
fil.txt
```

---

## 3.9 Tilordne output fra kommando til en variabel

```
$ mappe=`pwd`
$echo $mappe
/iu/nexus/ud/haugerud
$ tall=`seq 5 10`
$ echo $tall
5 6 7 8 9 10
```

Anbefalt alternativt:

```
$ mappe=$(pwd)
$ tall=$(seq 5 10)
$ echo $tall
5 6 7 8 9 10
$ tall=$(echo {5..10})
$ echo $tall
5 6 7 8 9 10
```

---

## 3.10 Omdirigering (viktig!)

*Den store fleksibiliteten det gir å kunne dirigere datastrømmer til og 
fra filer og programmer har alltid vært en sentral og nyttig egenskap ved Linux* .

De fleste Linux programmer og kommandoer har alltid tre åpne kanaler:

|   |   |   |   |   |
|---|---|---|---|---|
| nummer | navn | fullt navn | funksjon | default |
| 0 | stdin | standard in | input kanal | fra tastatur |
| 1 | stdout | standard out | output kanal | til skjerm |
| 2 | stderr | standard error | kanal for feilmelding | til skjerm |

Dataene som strømmer inn og ut av disse kanalene (streams) kan omdirigeres til og fra filer og programmer.

Illustrasjon:
Linux datakanaler

---

## 3.10.1 Omdirigering til og fra filer

Eks: stdout for echo er terminal.

```
$ echo hei
hei
$ echo hei > fil1
$ cat fil1
hei
$ echo hei2 >> fil1
$ cat fil1
hei
hei2
```

|   |   |
|---|---|
| omdirigering | virkning |
| > fil.txt | omdirigerer stdout til fil.txt. Overskriver |
| >> fil.txt | legger stdout etter siste linje i fil.txt |
| >& fil.txt | sender også stderr til fil.txt |
| 2> err.txt | sender stderr til err.txt |
| 2> /dev/null | stderr sendes til et 'sort hull' og forsvinner |
| > fil.txt 2> err.txt | stdout -> fil.txt stderr -> err.txt |
| find / -name passwd 2>&1 | grep -v Permission | sender stderr til samme kanal som stdout |
| prog < fil.txt | sender fil til stdin for program |

Flere eks:

```
$ ehco hei
ehco: Command not found
$ ehco hei >& fil1
$ cat fil1
ehco: Command not found
$ echo hei > fil1 2> err.txt   # Sender error til err.txt
$ mail haugerud < fil1
```

Konstruksjonen `2>&1` betyr: send stderr til samme kanal som stdout. Man limer da stderr-kanalen til kommandoen på samme linje inn i stdout-kanalen. I eksempelet over vil det føre til at man kan grep'e på både stdout og stdin fra find. Uten `2>&1` ville man bare kunne grep'e på stdout. Denne konstruksjonen kan også brukes som alternativ til `>&` , kommandoen

```
ls /tmp/finnesikke > fil.txt 2&>1
```

vil sende stderr til fil.txt (men må stå etter `>` ).

Konstruksjonen `1>&2` betyr: send stdout til samme kanal som stderr. Inne i et script vil

```
echo "Error!" 1>&2
```

sende feilmeldinger til stderr, slik programmer vanligvis gjør. Vanligvis sender echo output til stdin, men `1>&2` gjør at stdout istedet sendes til stderr.

---

## 3.11 Omdirigering til og fra kommandoer; pipes

*En pipe  er et data-rør som leder et programs stdout til et annent programs stdin.* Uten pipe:
```
$ ps aux > fil
$ more fil
```

Med pipe:
```
$ ps aux | more
```

*Dette gjør at man kan kombinere alle Linux-kommandoene på en rekke måter. Noen eksempler:*
```
$ ps aux | grep haugerud | more
$ cat /etc/passwd | sort > fil.txt
$ sort /etc/passwd > fil.txt 
$ ps aux | awk '{print $1}' | sort | uniq | wc -l
$ ps -eo user | sort | uniq | wc -l
```

*Forklaring til det siste eksempelet: ps -eo user gir bare brukernavnet i ps-listingen. sort sorterer listen med brukernavn alfabetisk. uniq fjerner 
identiske linjer, men kun de som kommer etter hverandre, derfor sort først. 
wc -l returnerer antall linjer. En slik 
'pipeline' gir dermed antall brukere som kjører prosesser på maskinen.*

Illustrasjon:
Øverst: ps -aux | more. Nederst:  cat /etc/passwd | sort > fil.txt.

---

## 3.12 Piping standard error

Når man setter en pipe etter en kommando, er det bare stdout som sendes dit. Men ved hjelp av konstruksjonen `|&` sender man også stderr videre:

```
$ ehco hei | grep found
No command 'ehco' found, did you mean:
 Command 'echo' from package 'coreutils' (main)
ehco: command not found
$ ehco hei |& grep found
No command 'ehco' found, did you mean:
ehco: command not found
```

Finnes det en annen måte å gjøre det samme på?

---

## 3.13 Sub-shell

Konstruksjonen `(kommando;kommando)` gir et såkalt subshell. Da startes et nytt shell og man mottar den samlede output til stdout og stderr i shellet som kjører kommandoen. Det kan f.eks. brukes til å slå sammen output fra to filer:

```
$ cat > fil1
en
to
tre
$ cat > fil2
tre
to
fire
$ sort fil2
fire
to
tre
```

Hvis man ønsker å skrive ut de to filene med en kommando, kan man gjøre

```
$ cat fil2;cat fil1
tre
to
fire
en
to
tre
```

Men anta at man ønsker å sortere output fra de to filene; da kan man prøve følgende:

```
cat fil1;cat fil2 | sort
en
to
tre
fire
to
tre
```

Men det som skjer er at bare fil2 blir sortert. Om man lager et sub-shell

```
$ (cat fil1;cat fil2)
en
to
tre
tre
to
fire
```

vil output fra dette subshellet samlet sendes til sort:

```
$ (cat fil1;cat fil2) | sort
en
fire
to
to
tre
tre
```

og man oppnår det man ønsket.

---

## 3.14 source

|   |
|---|
| $ emacs change |
| #! /bin/bash |
| cd /usr/bin |
| pwd |

```
$ pwd
/
$ change
/usr/bin
$ pwd
/
```

Når scriptet change kjøres, starter en ny prosess; et nytt shell som utfører

```
cd /usr/bin
```

og avsluttes. All shell-info blir da borte (variabler og posisjon i filtreet).

Illustrasjon:
Når et script kjøres startes et helt nytt shell. Alt som 
har skjedd i dette shellet blir borte når scriptet avsluttes (exit utføres selvom det ikke 
står eksplisitt på slutten av scriptet).

Kommandoen `source` utfører linje for linje i argumentfilen uten å starte noe annent shell.

```
$ pwd
/
$ source change
/usr/bin
$ pwd
/usr/bin
```

I Bash er `.` og `source` ekvivalent:

```
$ . change   # samme som $ source change
```

---

## 3.15 Kommandoer brukt under forelesningen

[Kommandoer](https://www.cs.oslomet.no/~haugerud/os/Forelesning/forelesningsKommandoer/Fri07.02.2020.html)