## 5.2 Passord-kryptering

Alle brukere på en Linux server har en linje i /etc/passwd. For eksempel:

```
rex:~$ grep haugerud /etc/passwd
haugerud:x:285:1001:Hårek Haugerud,,,:/home/haugerud:/bin/bash
```

Tidligere stod det en hash av passordet der istedet for x i andre kolonne. Denne hashen er en kryptert versjon av passordet og ligger nå i `/etc/shadow` og kan bare leses av root. Det er kun hashen som lagres og dette gjør at man kan logge inn på en datamaskin uten at passordet er lagret i klartekst noe sted. Om en slik liste med passord i klartekst blir lekket, ville det vært katastrofe. Men det er også alvorlig om en liste med passord-hasher blir fritt tilgjengelig.

```
rex:~$ sudo grep haugerud /etc/shadow
[sudo] passord for haugerud: 
haugerud:$6$WXQf3H3AUREz8y$IRYwxMcpK/aTX4oF.xEJrol.Va7cjGY4V.93wkKCc3Tcd9JV0mPIPjyqBuljB3UPw6.VPJx/ymiCJlxsk5lBv.:17835:0:99999:7:::
```

Hashen kan (med rett 'salt') genereres med kommandoen `mkpasswd` :

```
rex:~$ mkpasswd -m sha-512 -S WXQf3H3AUREz8y
Passord: 
$6$WXQf3H3AUREz8y$IRYwxMcpK/aTX4oF.xEJrol.Va7cjGY4V.93wkKCc3Tcd9JV0mPIPjyqBuljB3UPw6.VPJx/ymiCJlxsk5lBv.
```

Hvilken kryptografisk hashing-metode som er brukt kan sees av de første tegnene i hashen:

| Første tegn | Algoritme |
|-----------|---------|
| To tegn | DES (13 totalt) |
| $1$ | md5 |
| $5$ | sha256 |
| $6$ | sha512 |

Saltet er de etterfølgende tegnene frem til $-tegnet. Dette saltet gjør det vanskeligere å bruke enkelte brute force metoder som rainbow tables for å cracke passord om man kjenner en hash for et passord. Ved login skjer følgende:

* Man taster passord
* Login-shellet krypterer passordet
* Sjekker mot /etc/shadow
* Hvis likt login

Illustrasjon:
Passordkryptering

For 4 år siden lå alle bruker-hashene i `/etc/shadow` , men nå autentiseres den som logger seg inn på studssh ved hjelp av PAM (pluggable authentication module) mot AD (Active Directory) sentralt på OsloMet.

---

## 5.2.1 Hashing-algoritmer

Med `mkpasswd` kan man velge hvilken hashing-metode man vil bruke:

```
$ mkpasswd -m help
Available methods:
des	standard 56 bit DES-based crypt(3)
md5	MD5
sha-256	SHA-256
sha-512	SHA-512
```

Dette er enveisalgoritmer som for et gitt passord generere en entydig lengre streng av tegn. DES var tidligere standard, men ble så avløst av MD5 som er noe bedre, og nå er sha-512 standard metode for Linux. De samme prinsippene gjelder for Windows-innlogging, der lagres hash-strengene i SAM-databasen på en lokal Windows-maskin eller på en sentral server i Active Directory. Tidligere var LM-hash(DES) standard, men den ble etterhvert avløst av NTLM-hash(MD5) og etterhvert av kraftigere algoritmer som AES(Advanced Encryption Standard).

---

## 5.2.2 Passord-cracking

Hvis man har tilgang til shadowfilen på Linux eller SAM-databasen på Windows, kan et crack-program kryptere alle ord og kombinasjoner av ord i en ordbok og sammenligne med de krypterte passordene. Hvis ett av de riktige passordene velges, vil det avsløres ved at det gir en av hashene. Slike program kan teste hundretusner av passord per sekund, slik at passord fra ordbøker veldig raskt kan knekkes. Jo lengre passordene er og jo flere tegn som brukes i passordene, desto mer tidkrevende er det for passord-cracker program å teste ut alle mulige kombinasjoner.

Hvis man går ut ifra 52 tegn (a-z og A-Z), 10 tall og 32 spesialtegn, har man totalt 94 mulige tegn i et passord. Og om man har en kraftig GPU-server kan man regne ut en million hasher i sekundet for algortimer som sha512, mange flere for enklere algortimer. For åtte tegn i passordet er det eller 218 billioner mulige kombinasjoner. For å finne hash'ene for alle mulige kombinasjoner, tar det da i underkant av 7 år om man regner ut en million hash i sekundet. Tid for forskjellige lengder av passord er vist i følgende tabell:

| Lengde | tid (36 tegn) | tid (62 tegn) | tid (94 tegn) |
|------|-------------|-------------|-------------|
| 4 | 1.7 sekunder | 15 sekunder | 78 sekunder |
| 6 | 36 minutter | 16 timer | 192 timer |
| 8 | 32 dager | 6.9 år | 193 år |
| 10 | 116 år | 26.6 tusen år | 1.7 millioner år |

Til sammenligning er det ca en million ord i en norsk ordbok som tar med alle varianter av norske ord, slik at det kun tar ett sekund å finne et passord som er med i en ordbok om man kjenner hashen for passordet.

Man ser at lengden på passordet er veldig viktig for hvor raskt det kan være å gjette ved hjelp av et brute force angrep på en hash. I tillegg hjelper det at store bokstaver og spesialtegn tas med.

---

## 5.3 find

Denne kommandoen kan brukes til å finne filer på systemet. Det er mulig å spesifisere en rekke kriterier. Ønsker man å finne alle filer (og mapper) i hjemmekatalogen som har filendelse c, kan man bruke

```
haugerud@studssh:~$ find ~ -name "*.c"
/iu/nexus/ua/haugerud/os/funk.c
/iu/nexus/ua/haugerud/os/old/main.c
/iu/nexus/ua/haugerud/os/old/sum.c
```

For å finne alle filer og mapper som ble endret mer nylig enn 4 februar 2019 kl 19:55, kan man gjøre

```
haugerud@studssh:~$ find . -newermt "4 Feb 2019 19:55"  -ls 
     9714      4 drwxr-xr-x  20 haugerud drift        4096 feb.  5 10:28 .
    29479      4 -rw-------   1 haugerud drift         318 feb.  5 10:28 ./.Xauthority
    29374      4 -rw-r--r--   1 haugerud drift          10 feb.  5 20:07 ./fil
```

der `-ls` gir en mer detaljert listing. Tilsvarende kan man finne alle filer som har blitt endret mellom to tidspunkt med

```
haugerud@studssh:~$ find . -type f -newermt "29 Jan 2019 19:55" ! -newermt "29 Jan 2019 22:55" -ls 
    29422      4 -rwx------   1 haugerud drift          56 jan. 29 22:40 ./mappe/arg.sh~
    29423      4 -rwx------   1 haugerud drift          58 jan. 29 22:42 ./mappe/arg.sh
```

hvor `-type f` gir kun filer.

---

## 5.4 sed

Kommandoen sed kan brukes til å bytte ut forekomster av ord i setninger:

```
echo dette er en test | sed s/test/fisk/
echo test og test | sed s/test/fisk/
echo test og test | sed s/test/fisk/g
```

---

## 5.5 sort

I tillegg til at man kan sende output fra en Linux-kommando inn til input for en annen, kan man også legge til en rekke opsjoner. På denne måten kan man få til veldig mye med enlinjers sammensatte kommandoer. Manualsiden til sort avslører at opsjonen -k gjør at man kan velge hvilken kolonne man vil sortere med hensyn på, mens -n gjør at man sorterer numerisk slik følgende eksempel viser. Utgangspunktet er filen `biler` som ser slik ut:

```
$ cat biler
student bmw 500000
haugerud berlingo 150000
kyrre elbil 90000
```

Denne filen kan man nå sortere som man ønsker med de rette opsjoner.

---

## 5.5.1 Sortert alfabetisk

```
$ sort biler
haugerud berlingo 150000
kyrre elbil 90000
student bmw 500000
```

---

## 5.5.2 Sortert alfabetisk etter andre kolonne

```
$ sort -k 2 biler
haugerud berlingo 150000
student bmw 500000
kyrre elbil 90000
```

---

## 5.5.3 Sortert numerisk etter tredje kolonne

```
$ sort -n -k 3 biler
kyrre elbil 90000
haugerud berlingo 150000
student bmw 500000
```

Default sender sort output til shellet, hvis man ønsker at reaultatet skal lagres i en fil må man be om det

```
sort -n -k 3 biler > sortertFil
```

---

## 5.6 head og tail

Hvis man ønsker å se kun de 6 første linjene av en utgave av passordfilen på studssh sortert etter femte kolonne kan man bruke `head` for å få til det:

```
studssh:~$  sort -t: -k 5 /etc/passwd | head -n 6
aasej:x:2748:1001:Aase Jenssen:/iu/nexus/uc/aasej:/bin/bash
s137153:x:2603:100:Aasmund Solberg:/iu/cube/u2/s137153:/bin/bash
s103726:x:1089:100:Abdi Farah Ahmad:/iu/cube/u3/s103726:/bin/false
s133988:x:1695:100:Abdi Hassan Abdulle:/iu/cube/u2/s133988:/bin/bash
s123860:x:1090:100:Abdinasir Omar Kahiye:/iu/cube/u2/s123860:/bin/bash
s141546:x:3449:100:Abdiqadir Said Jama:/iu/cube/u3/s141546:/bin/false
```

Legg merke til at `-t:` gjør at tegnet : betraktes som skilleledd mellom kolonnene. Evalueringen av en slik pipeline går fra venstre til høyre så hvis man istedet ønsker å se en sortert utgave av de 6 første linjene, får man det med:

```
studssh:~$ head -n 6 /etc/passwd | sort -t: -k 5 
bin:x:2:2:bin:/bin:/bin/sh
daemon:x:1:1:daemon:/usr/sbin:/bin/sh
games:x:5:60:games:/usr/games:/bin/sh
root:x:0:0:root:/root:/bin/bash
sync:x:4:65534:sync:/bin:/bin/sync
sys:x:3:3:sys:/dev:/bin/sh
```

Kommandoen `tail` gir i motsetning til `head` de siste linjene. En spesielt nyttig bruk av `tail` er for å se på slutten av log-filer. Hvis man i tillegg tilføyer opsjonen -f vil man kontinuerlig følge med på om det kommer nye linjer til logfilen, for eksempel slik:

```
sudo tail -f /var/log/auth.log
```

---

## 5.7 cut

Cut brukes til å klippe ut deler av linjer. Cut leser fra standard input. En vanlig anvendelse er å klippe ut enkelte kolonner fra en tabell.

```
$cat /etc/passwd | cut -d: -f2 | tail -n 4
group16
mroot
noob
munin
```

Her "pipes" innholdet i /etc/passwd til cut, som bruker : som kolonneskille (gitt ved -d:) og som klipper ut kolonne 2 (gitt ved -f2). Dette pipes videre til head, som viser de fire nederst linjene.

```
$cat /etc/passwd | cut -c -3 | tail -n 4
gro
mro
noo
mun
```

Med switchen -c angir vi at vi ønsker å klippe ut "`characters"'. Med - , der er et tall, klipper vi ut bare de første tallene. - tar tegnene fra tegn og ut linja, - tar alle tegnene mellom tegn og .

---

## 5.8 Input fra bruker

```
#!/bin/bash 

echo -en "svar: \a" # -n dropper linjeskift
read answer
echo "Du svarte $answer"
```

opsjonen `-e` muligjør bruk av kontrolltegn som `\a` , som gir ett pip.

---

## 5.9 Lese filer og output med while og read

Veldig ofte ønsker man å gå igjennom og prosessere en fil eller tekstoutput fra en kommando linje for linje. Da kan while brukes til å lese input og read til å behandle linje for linje, som i skriptet read.sh:

```
#! /bin/bash

i=0
while read LINE 
do
   (( i++ ))
   echo "Linje nr $i: $LINE"
done
```

read leser linje for linje fra STDIN slik at

```
$ read.sh < /etc/passwd
```

vil lese passordfilen. `read LINE` returnerer 0 (alt OK) helt til EOF og da stopper while.

IFS kan endre hvordan `read` leser inn dataene og filen kan også sendes til `read` inne i scriptet::

```
#! /bin/bash

#haugerud:x:285:102:Hårek Haugerud:/iu/nexus/ud/haugerud:/bin/bash
IFS=:
while read brnavn x ID GR NAVN HOME SHELL 
do
   echo "$brnavn: $NAVN"
done < /etc/passwd
```

`read` leser fra STDIN og dit kan linjene også sendes med en pipe:

```
#! /bin/bash

#haugerud 16662  0.0  0.1  2256 1280 pts/2    S    12:52   0:00 /bin/bash

# Sender all output fra ps aux til \verb+read+:
ps aux |  
   while read bruker PID x x x x x x x x prog
   do
      if [ "$bruker" = "haugerud" ]
      then
         echo "ProsessID = $PID $prog"
      fi
   done
```

---

## 5.10 Arrays

Et array kan i bash fylles inn med elementer uten å deklarere arrayet først:

```
linux:~$ tall[0]=null
linux:~$ tall[1]=en
linux:~$ tall[2]=to
linux:~$ tall[3]=tre
```

Den mest naturlige måten å skrive ut et array-element på fungerer ikke:

```
linux:~$ echo $tall[1]
null[1]
linux:~$ echo $tall[2]
null[2]
linux:~$ echo ${tall[2]}
to
```

Men man må legge inn et sett med krøll-parenteser rundt elementnanvnet for å få skrevet ut. Man kan også definere et array ved å skrive inn strenger innenfor en parentes adskilt av mellomrom:

```
$ tall=(null en to tre)
$ echo ${tall[to]}
null
$ echo ${tall[2]}
to
$ tall[4]=fire
$ echo ${#tall[@]} # Antall elementer
5
$ echo ${tall[@]} # Alle verdier
null en to tre fire
$ echo ${!tall[@]} # Index
0 1 2 3 4
$ for t in ${!tall[@]}
> do
> echo "Tall nr $t er ${tall[$t]}"
> done
Tall nr 0 er null
Tall nr 1 er en
Tall nr 2 er to
Tall nr 3 er tre
Tall nr 4 er fire
```

---

## 5.11 Et vanlig problem med pipe til while og read

Et naturlig forsøk på å sende output til en while-read løkke er følgende(se avsnittet nedenfor om hvordan man lager et array):

```
#! /bin/bash
i=0
ps aux | awk '{print $2}' |
while read pid
do
   (( i++ ))
   pidArr[$i]=$pid
done 
echo Antall elementer: ${#pidArr[@]}
```

men om man kjører dette, får man følgende resultat:

```
$ ./pipe.sh
Antall elementer: 0
```

Dette skyldes at når den kommer etter en pipe vil while-konsturksjonen startes i en annen prosess og variabler som blir laget i denne prosessen (arrayet i eksempelet over) vil forsvinne når while-prosessen avsluttes. Dette kan løses ved å sende en fil direkte til konstruksjonen eller mellomlagre output fra pipe'n i en fil:

```
#! /bin/bash
ps aux | awk '{print $2}' > tmp.txt
i=0
while read pid
do
   (( i++ ))
   pidArr[$i]=$pid
done < tmp.txt
echo Antall elementer: ${#pidArr[@]}
```

Da vil ønsket resultat oppnås:

```
$ ./pipe.sh
Antall elementer: 742
```

Med den spesielle konstruksjon `<(kommando)` er det også mulig å direkte sende output fra `kommando` til while-read løkken som om det var en fil:

```
#! /bin/bash
i=0
while read pid
do
   (( i++ ))
   pidArr[$i]=$pid
done < <(ps aux | awk '{print $2}')
echo Antall elementer: ${#pidArr[@]}
```

Det gir samme ønskede resultat, dataene blir lagret i arrayet og kan brukes etter at løkken er fullført. Konstruksjon `<(kommando)` kalles "Process Substitution".

---

## 5.12 Assosiative array

Assosiative array har, istedet for tall, tekst-strenger som indeks. Et assosiativ array må deklareres før bruk i bash:

```
$ declare -A mann
$ mann[eva]=adam
$ mann[kari]=per
$ mann["Gunn Kari"]="Per Olav"
$ echo ${#mann[@]}
3
$ echo ${mann[@]}
adam Per Olav per
$ echo ${!mann[@]}
eva Gunn Kari kari
$ for k in "${!mann[@]}"
> do
> echo "$k sin mann er ${mann["$k"]}"
> done
eva sin mann er adam
Gunn Kari sin mann er Per Olav
kari sin mann er per
```

---

## 5.13 funksjoner

En funksjon (function) brukes nesten på samme måte som et selvstendig script. Må inkluderes først i scriptet.

```
#!/bin/bash 

 users()         #deklarasjon av funksjon 
 { 
         date    #skriver ut dagens dato 
         who  # Må ha linjeskift før }
 } 

 users  # kall paa en funksjon; ETTER deklarasjon
```

---

## 5.14 funksjoner og parametre

Parametre overføres som til bash-script. Og som for script kan kun exit-verdier (tall) returneres, men med return og ikke exit.

```
#!/bin/bash 

 findUser()         #deklarasjon av funksjon
 {
    echo "funk-arg: $*"
    local bruker # Lokal variabel
    bruker=$1    # 1.u argument, dette er en lokal $1, uavhengig av den $1
                 # som er 1. argument til hovedscriptet
    funn=$(grep ^$bruker /etc/passwd)
    if [ "$funn" ]
    then
        return 0 # Alt ok
    fi
    return 1
 }

# Hovedprog 'user.sh', syntaks: $ user.sh bruker1 bruker 2 .....
echo "Script-arg: $*"
for user in $*
do
   echo -e "\nLeter etter $user" # -e tillater \n
   findUser $user    # $user blir $1 i prosedyren
   if [ $? = 0 ]     # Returnverdi fra findUser i $?
   then
      echo "$user finnes"
      echo $funn          # $funn er global
   else
      echo "$user finnes ikke"
   fi
done

echo -e "\nScript-arg: $*"

#BUG: $ user.sh haug -> slår til på linjen haugerud i /etc/passwd
# Kan bruke 'while read'-konstruksjon for å trekke ut brukernavn fra linjene
```

*Funksjoner kan også defineres direkte i et terminalvindu, men forsvinner når shellet avsluttes. 
Man kan lagre egne funskjoner i en fil, f. eks. funk.bash og inkludere funskjonene i flere script 
ved å starte scriptene med som følger:*

```
#! /bin/bash

. funk.bash  # Alternativt 'source funk.bash' I begge tilfeller tilsvarer 
             # det å taste inn all koden i filen funk.bash inn i 
             # begynnelsen av dette scriptet
```

---

## 5.15 Signaler og trap

En prosess kan stoppes av andre prosesser og av kjernen. Det gjøres ved å sende et signal. Alle signaler bortsett fra SIGKILL ( `kill -9` ) kan stoppes og behandles av bash-script med kommandoen `trap` . Følgende script kan bare stoppes ved å sende ( `kill -9` ) fra et annent shell.

```
#! /bin/bash

# Definisjoner fra 
# /usr/src/linux-headers-3.13.0-106/arch/x86/include/uapi/asm/signal.h

#define SIGHUP          1       /* Hangup (POSIX).  */
#define SIGINT          2       /* Interrupt (ANSI).  */
#define SIGKILL         9       /* Kill, unblockable (POSIX).  */
#define SIGTERM         15      /* Termination (ANSI).  */
#define SIGTSTP         20      /* Keyboard stop (POSIX).  */

trap 'echo -e "\rSorry; ignores kill -1 (HUP)\r"' 1
trap 'echo -e "\rSorry; ignores kill -15 (TERM)\r"' 15
trap 'echo -e "\rSorry; ignores CTRL-C\r"' 2
trap 'echo -e "\rSorry; ignores CTRL-Z\r"' 20
trap 'echo -e "\rSorry; ignores kill - 3 4 5\r"' 3 4 5
trap 'echo -e "\rCannot stop kill -9\r"' 9

while [ true ]
do
   echo -en "\a quit? Answer y or n: "
   read answer
   if [ "$answer" = "y" ]
        then break
   fi
done
```

---

## 5.16 Oversikt over shell-typer

*Det finnes mange forskjellige typer shell og det shellet som nå er mest brukt i
             Linux-distribusjoner og som brukes her ved OsloMet  
er bash (vi skiftet fra tcsh i 2001). 
Det er en forbedring og utvidelse av det originale Linux-shellet Bourne Shell (sh)*

| Bourne-shell type | C-shell type |   |   |
|-----------------|------------|---|---|
| sh | Bourne-shell, Det opprinnelige Linux-shell | csh | C-shell, C-syntaks |
| bash | Bourne-again-shell, forbedret sh | tcsh | forbedret csh, bedre interaktivt |
| ksh | Korn-shell, utvidet sh, mye fra csh |  |  |

* De fleste Linux/Linux system-script er skrevet i Bourne-shell, `/bin/sh`
* Bourne-again-shell (bash), er default Linux-shell
* bash kan kjøre alle Bourne-shell script
* bash er Free Software Foundation's (FSF) Linux-shell

Under Linux:

```
haugerud@studssh:~$ ls -l /bin/sh
lrwxrwxrwx 1 root root 4 feb.  19  2014 /bin/sh -> dash
```

Debian Almquist shell (dash) er et mindre og hurtigere shell enn bash. Det ligger nærmere det originale Bourne-shell og har for Ubuntu blitt brukt som Bourne-substitutt siden 2006.

---

## 5.17 Oppstartsfiler

Hver gang et nytt terminalvindu (f. eks. xterm) startes, startes bash og du får et prompt som du kan taste inn kommandoer ved. Hver gang bash startes leses en konfigurasjonsfil som ligger øverst i brukerens hjemmemappe og heter `.bashrc` . Alle kommandoer som står der blir utført. Hver gang du logger inn, utføres kommandoene i `/etc/profile` og `~/.bash_profile` .

Et nytt shell startes hver gang

* man logger inn på en maskin (ssh, telnet)
* et nytt terminalvindu åpnes (xterm)
* et nytt shell startes eksplisitt($ bash)

Shellet utfører først kommandoer i noen oppstartsfiler:

* `/etc/profile` ved hver innlogging, systemfil
* `~/.bash_profile` ved hver innlogging
* `/etc/bash.bashrc` for hvert nytt shell, men ikke ved innlogging, systemfil
* `~/.bashrc` for hvert nytt shell, men ikke ved innlogging

*I disse filene kan f. eks. definisjoner av shell-variabler og alias'er legges.*

Eksempel på innhold:

```
PS1="\h:\w$ "
alias move=mv
alias cp="cp -i"
```

Legges dette i `~/.bashrc` vil `move` alltid bety `mv` og promptet blir:

```
$ bash                 
studssh:~/www/os$ exit    
exit                   
$ source ~/.bashrc     
studssh:~/www/os$
```

`source` starter **ikke** et nytt shell, men utfører alt i det eksisterende shellet.