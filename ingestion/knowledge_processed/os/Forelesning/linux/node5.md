## 4.3 Shell-programmering

Vi kan lage script som er

* nye kommandoer
* oppstartsprogrammer/program som gjør systemarbeid
* innstallasjonsprogrammer
* daemons; prosesser som alltid går i bakgrunnen og utfører tjenester.

`$mittprog&` vil fortsette å kjøre etter logout.

Når du skriver script:

* begynn med et skjelett (som f. eks. kun behandler argumentene) og få det til å virke
* utvid med en detalj av gangen; test for hver gang
* test små deler med copy&paste til et kommandovindu

Debugging:

* `bash -x mittscript` viser hva som skjer
* Legg inn linjer som `echo "Har nå kommet hit"`

Feilmeldinger fra bash er ofte kryptiske og misvisende, så det er vanskelig å finne feil i et stort script.

---

## 4.4 if-test

```
if test1
then
   kommando1
elif test2
then 
   kommando2
else
   kommando3
fi
```

---

## 4.5 if-eksempel; fil-testing

```
#! /bin/bash

fil=$1
if [ -f "$fil" ]
 then
   echo $fil er en fil
elif [ -d "$fil" ]; then
   echo $fil er en mappe
else
   echo $fil er hverken fil eller mappe
fi
```

*Man må ha mellomrom før og etter [ og før ] i 
if-testene. Semikolon adskiller generelt to kommandoer på samme måte som et linjeskift.*

Følgende script prøver å teste om det ikke er gitt noe argument:

```
#! /bin/bash

argument1=$1
if [ $argument1 = "" ]
then
        echo "Ingen argumenter"
fi
```

Men det gir en feilmelding når det kjøres uten argumenter

```
$ ./script
./script: line 5: [: =: unary operator expected
```

fordi det ikke er anførselstegn rundt $argument1 og da ser bash en linje som ser ut som `if [  = "" ]` og gir feilmelding. Analogt vil testen `if [ -f ]` alltid slå til. Bruk derfor alttid anførselstegn rundt det som skal testes, slik at det blir en tom streng og dermed syntaktisk riktig om variabelen du tester ikke eksisterer eller er tom.

---

## 4.6 Flere filtester og sammenligning

| Filtest | Sann hvis |
|-------|---------|
| -L fil | fil er en link |
| -r fil | fil er lesbar |
| -w fil | fil er skrivbar |
| -e fil | fil eksisterer |
| -x fil | fil er eksekverbar |
| s1 = s2 | strengene s1 og s2 er like |
| s1 != s2 | strengen s1 og s2 er forskjellige |
| x -eq y | heltallene x og y er like |
| x -lt y | x er mindre enn y 2 |
| x -gt y | x er større enn y |
| t1 -a t2 | Logisk og - sann hvis t1 OG t2 er sanne |
| t1 -o t2 | Logisk eller - sann hvis t1 ELLER t2 er sanne |

---

## 4.7 Logiske operatorer

| Operator | betydning |
|--------|---------|
| ! | logisk NOT |
| -a | logisk AND |
| -o | logisk OR |

---

## 4.8 for-løkke

```
for variable in list
do
  kommandoer
done
```

*hvor  list er en liste av ord adskilt av mellomrom. F. eks. gir*

```
for var in h1 h2 h3
do
   echo $var
done
```

til output

```
h1
h2
h3
```

Info om nøkkelord som `for`

```
haugerud@studssh:~$ type for
for is a shell keyword
```

kan man få med

```
haugerud@studssh:~$ help for
for: for NAME [in WORDS ... ] ; do COMMANDS; done
    Execute commands for each member in a list.
```

Eksempler på `list` eller WORDS:

* `$(ls)`
* `$(cat fil)`
* `*`
* `dir/*.txt`
* `$filer # ( filer="fil1 fil2 fil3")`

*En liste splittes med mellomrom. Variabelen IFS (Internal Field Separator)  kan
settes om man ønsker å splitte på et annet tegn. Det skjer ved at 
IFS-tegnet byttes ut med mellomrom når verdien av en shellvaribael 
benyttes.
Den må fjernes med unset 
om man ønsker å splitte på mellomrom igjen.*

```
$ var=fil1:fil2:fil3
$ echo $var
fil1:fil2:fil3
$ IFS=:
$ echo $var
fil1 fil2 fil3
$ for fil in $var
> do
> echo $fil
> done
fil1
fil2
fil3
```

Å bruke kolon til å splitte er nyttig om man ønsker å løpe igjennom PATH eller en linje i passordfilen. Med noen opsjoner til cat, kan man se hva som skjuler seg bak $IFS:

```
haugerud@studssh:~$ echo "$IFS" | cat -vet
 ^I$
$
```

Dette betyr at IFS splitter på de tre tegnene <space><tab><newline>, noe man kan se i bash sin manual-side om man søker på IFS.

Fra og med bash versjon 2.0 kan man også skrive vanlige for-løkker med en syntaks som ligner mer på Java:

```
for (( i=1;i < 30;i++ ))
do 
   echo $i
done
```

---

## 4.9 Break og Continue

Break og Continue kan brukes mellom do og done til å avbryte for og while løkker:

**continue**: Fortsett med neste runde i for/while løkke.

**break**: Avslutt for/while løkke; hopp til etter done

**break n**: Hopp ut n nivåer

---

## 4.10 Numerikk

Tungt å bruke `expr` som er eneste alternativ i Bourne-shell:

```
a=`expr $a + 1`               # increment a
a=`expr 4 + 10 \* 5`          # 4+10*5
```

Enklere innenfor (( )) for da kan Java-syntaks for numerikk brukes(men bare i bash 2.x).

```
$ (( x = 1 ))
$ echo $x
1
$ (( x += 1))
$ echo $x
2
$ (( total = 4*$x + x )) # Virker med x uten $ foran!
$ echo $total
10
```

Den numeriske testen

```
if ((x < y))
```

er et Bash 2.x alternativ til

```
if [ $x -lt $y ]
```

Den beste løsningen er å bruke syntaksen med doble paranteser, (( )), selvom syntaksen (for å være bakoverkompatibel) er litt uvanlig.

---

## 4.11 Script og argumenter

Argumenter blir lagret i spesielle variabler. Kjøres scriptet argscript.bash med tre argumenter: $ argscript.sh fil1 fil2 fil3 vil følgende variabler bli satt:

| variabel | innhold | verdi i eksempelet |
|--------|-------|------------------|
| $* | hele argumentstrengen | fil1 fil2 fil3 |
| $# | antall argumenter | 3 |
| $1 | arg nr 1 | fil1 |
| $2 | arg nr 2 | fil2 |
| $3 | arg nr 3 | fil3 |

---

## 4.12 Argumenter i for-løkke og exit-verdier.

```
$ cat forarg
#!/bin/bash 

if [ $# -lt 1 ]
then
   echo No arguments
   exit 1             # Avsluttet scriptet
fi

for arg in $*
do
  echo $arg was an argument
done

echo total number: $#

$ forarg hei du
hei was an argument
du was an argument
total number: 2
$ echo $?
0
$ forarg 
No arguments
$ echo $?
1
```

Variabelen `$?` inneholder exit-verdien til programmet/kommandoen som sist ble utført. Det finnes andre variabler som er definert, som de to følgende:

```
echo "PID = $$, navn: $0"
```

---

## 4.13 while

syntaks:

```
while test
do
     kommandoer
done
```

Eksempel; alternativ måte å behandle argumenter: *bedre hvis "strenger med mellomrom" er blant argumentene*

```
#! /bin/bash

while [ $# -gt 0 ]  # Så lenge det er noe i $*
do
        echo "arg: $1"
        shift          # skyver ut $1 og legger neste argument i $1
done
```

Deamon-eksempel

```
#! /bin/bash

while [ "true" ]  # evig løkke; en streng er alltid 'sann'
do
        echo "Running $0, a process with PID $$"
        sleep 5   # sover i 5 sekunder
done
```

---

## 4.14 /proc - et vindu til kjernen

Linux tilbyr oss en enkel måte å undersøke tilstanden til operativsystemet på. Det finnes nemlig en mappe /proc som egentlig ikke finnes på harddisken, men som likevel inneholder “filer” som vi kan lese innholdet fra. Hver gang vi åpner en av filene i /proc, kjøres en metode i kjernen som skriver ut innholdet der og da. Man får altså et øyeblikksbildet av hva som skjer. Her er en liste over interessante filer og mapper i /proc:

* cpuinfo
* meminfo
* interrupts
* Hver prosess har en egen mappe som har samme navnsom prosessens PID. Spennende filer i en slik mappe kan være:
  * status - Navn og status på prosessen
  * stat - Teller prosessorbruk, minnebruk osv. se `man proc'
* uptime
* version
* net/