## 6.3 root og sudo

På den virtuelle Linux-serveren, som egentlig er en ekstra isolert Docker container, dere har blitt tildelt i os-gruppene har dere rettigheter til å gjøre alt dere måtte ønske, som å installere programmer og lage nye brukere. Husk at Linux-VMene har offentlig IP og dermed kan bli utsatt for hacker-angrep fra hele verden.

Root er administratorbrukeren på Linux, som har alle rettigheter på systemet. For å bli root kan man logge inn direkte med root-passordet. Alternativt kan man logge inn med en vanlig bruker-konto og så bli root ved hjelp av kommonadoen `sudo su` hvis man er tildelt rettigheter for å gjøre dette.

På Linux-VM vil du som den vanlige group-brukeren for eksempel ikke få lov til å se på shadowfilen:

```
$ whoami
group50
$ cat /etc/shadow
cat: /etc/shadow: Permission denied
```

Men fordi group-brukeren er en såkalt sudo-user som har root-rettigheter om han ønsker det, kan han likevel se shadow-filen med kommandoen

```
sudo cat /etc/shadow
[sudo] password for group50:
```

etter å ha skrevet inn sitt vanlige passord. Det er også mulig for en sudo-user å få opp et root-shell ved å gjøre

```
sudo su
```

Man bør være forsiktig med å jobbe fra et root-shell, siden man da lettere glemmer at man har de allmektige root-rettighetene som potensielt kan føre til store feilgrep.

Om man jobber i et miljø med virtuelle maskiner og kontainere, noe som blir mer og mer vanlig, er ikke det å unngå å være logget på som root like viktig som før. Om man gjør et stort feilgrep, kan man raskt bygge en ny VM eller bare starte en ny kontainer. Ihvertfall så lenge man har backup av alle data som man hadde på serveren. Og det er viktig: ta alltid backup av script og lignende filer som dere har på Linux-VM.

---

## 6.4 Brukere

En bruker på et UNIX/Linux system består av følgende:

* En linje i filen /etc/passwd som inneholder bl.a
  * Bruker id - UID. Må være unik.
  * Brukernavn
  * Hjemmekatalog
* En linje i filen /etc/shadow som inneholder en hash av passordet
* En hjemmekatalog (vanligvis i /home)
* Eventuelle gruppemedlemskap i filen
* /etc/group

Man kan lage nye bruker med kommandoen adduser eller useradd . Sistnevnte er kun anbefalt dersom man skal legge til en bruker via et script eller lignende. Kommandoen adduser fungerer mer interaktivt og passer best for å legge til en og en bruker. Den kan brukes slik

```
group60@os60:~$ sudo adduser s123456
```

for å legge til brukeren `s123456` .

For å legge denne brukeren til sudo-gruppen slik at den blir en sudo-bruker, kan gjøres med

```
group60@os60:~$ sudo addgroup s123456 sudo
```

Et UNIX/Linux system har vanligvis en del brukere i tillegg til de "menneskelige" brukerne. Den mest kjente av dem er root, som har UID 0. De øvrige brukerne representerer tjenester som ikke bør kjøre som brukeren root av risikohensyn. Eksempler på slike brukere er nobody, sshd og sys. Dersom man installerer flere tjenester på et system, f.eks en webserver, vil man sansynligvis få opprettet de tilsvarende brukerne automatisk.

---

## 6.5 Grupper

* gruppe av brukere
* Definert i /etc/group
* må defineres av root

```
$ groups haugerud                   # lister gruppene haugerud er med i
 $ chgrp studgruppe fil.txt      # fil.txt tilhører nå studgruppe
 $ chmod 770 fil.txt             # alle rettigheter til alle i studgruppe
 $ sudo adduser s123456 studgruppe # Gjør s123456 til medlem av studgruppe
```

Man kan lage en ny gruppe med `addgroup` :

```
mroot@os50:~$ sudo addgroup newgroup
[sudo] password for mroot: 
Adding group `newgroup' (GID 1003) ...
Done.
mroot@os50:~$ grep newgroup /etc/group
newgroup:x:1003:
```

---

## 6.6 Rettighetsprinsipper i Linux/UNIX miljøer

Følgende regler gjelder mellom brukere:

* Alle prosesser/programmer som startes av en bruker vil være eid av den brukeren og filrettigheter vil være i forhold til eierskapet. Unntaket er kommandoen su som forandrer bruker og tjenester som forandrer status på seg selv, f.eks sshd (startes som root, men blir til sshd kort tid etter).
* Brukere kan kun sende signaler til sine egne prosesser (f.eks med kommandoen kill). Unntak er root.
* Brukere kan kun forandre på rettighetene til filer som de eier selv. Unntak er root.
* Brukere kan ikke "gi" filer til andre brukere ved å forandre hvem som er eier av filen med kommandoen chown. Root kan.
* Brukere KAN forandre hvilken gruppe som eier en fil med kommandoen chgrp, men KUN til grupper som den selv er medlem av. Root kan uansett.
* Brukere kan ikke lage nye brukere. Bare root kan det.

Det finnes to måter å bli root på. Den ene er å bruke kommandoen su , som ber deg om root sitt EGET passord. Denne metoden er mest kjent. I de nyeste versjonene av Linux er det blitt mer vanlig å bruke sudo, som gir rettigheter til vanlige brukere dersom de kan autentisere seg. Man må vanligvis være medlem av en spesiell gruppe for å få lov til å kjøre kommandoen sudo su , som ber brukeren om sitt eget passord istedefor root sitt passord.

Det er også mulig å logge seg rett på systemet som root dersom man har root passordet. Det er derimot ikke anbefalt av følgende årsaker:

* Alt den brukeren gjør vil bli gjort med root-rettigheter.
* Ved å bruke su eller sudo su kan vi se i logfilene HVEM som ble root. Denne typen informasjon kan være veldig viktig når man vil finne ut hva som har skjedd (og hvem som skal få skylden).
* Root skal kun brukes når man har behov for det, og ikke behandles som en normal bruker/person.

---

## 6.7 ssh-copy-id

Det kan være nyttig å kunne logge inn med ssh på andre servere uten å måtte skrive passord hver gang. Sikkerhetsmessig kan dette også være en fordel, da man kan velge å kun tillate innlogging ved hjelp av ssh-nøkler og dermed unngå alle brute-force ssh-angrep. Først må man lage ssh-keys:

```
group1@os1:~$ ssh-keygen 
Generating public/private rsa key pair.
Enter file in which to save the key (/home/group1/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/group1/.ssh/id_rsa.
Your public key has been saved in /home/group1/.ssh/id_rsa.pub.
group1@os1:~$
```

Deretter kan man med ssh-copy-id (som kopierer over id_rsa.pub) sørge for at man senere kan logge inn uten passord:

```
group1@os1:~$ ssh-copy-id group49@os49.vlab.cs.oslomet.no
group49@os49.vlab.cs.oslomet.no's password: 

group1@os1:~$ ssh group49@os49.vlab.cs.oslomet.no
Linux os49 2.6.32-5-xen-amd64 #1 SMP Fri Feb 5 17:48:36 UTC 2016 x86_64
group49@os49:~$
```

Man kan deretter også utføre kommandoer direkte på andre servere:

```
group1@os1:~$ ssh group49@os49.vlab.cs.oslomet.no whoami;hostname
group49
os1
group1@os1:~$ ssh group49@os49.vlab.cs.oslomet.no "whoami;hostname"
group49
os49
```

---

## 6.8 Root aksess til server med sudo-rettigheter

Hvis man har en bruker på en server som har sudo-rettigheter, har man vanligvis ikke mulighet til å logge seg inn med ssh direkte til root-brukeren på serveren. Det er mulig å sette det opp, men det er sikrere og vanlig å skru av muligheten for å logge inn som root med passord. Man kan derfor heller ikke overføre ssh-nøkler med ssh-copy, men det er likevel mulig å sette opp ssh-key innlogging for root. Det som behøves er at nøkkelen også legges i root sin `.ssh` -mappe. Det er viktig å forsikre seg om at root faktisk har en mappe `/root/.ssh` og en enkel måte å sørge for at den blir opprettet (om den ikke har blitt opprettet tidligere) med riktige rettigheter er å kjøre `ssh-keygen` som root:

```
# ssh-keygen
```

og taste return på alle spørsmål.

Hvis du allerede har satt opp innlogging til din vanlige bruker på serveren, i dette eksempelet til group60@os60, kan du nå overføre nøkkelen derfra slik som dette:

```
group60@os60:~$ sudo cp .ssh/authorized_keys /root/.ssh
```

Hvis mappen `/root/.ssh` ikke eksisterer fra før blir den laget som en fil og da vil innlogging ikke virke. Dermed skal du kunne logge inn også som root fra den serveren, f.eks. studssh, som du satte opp ssh-key innlogging fra til group60 i utgangspunktet. Når man overfører sin offentlige nøkkel til en annen server på denne måten, er det en enveis-innlogging. Det vil ikke være mulig å gå tilbake til serveren man kom fra med denne nøkkelen. Men man må passe godt på sin private nøkkel ( `id_rsa` ) for om andre får tilgang til den, kan de logge seg inn til de serverene som du har overført den offentlige nøkkelen til ( `id_rsa.pub` ). Når du logger deg på en server med ssh-key, er det din private nøkkel ( `id_rsa` ) som brukes til å autentisere deg (bevise at det er deg).

---

## 6.9 Bakgrunnsjobber og screen

Hvis man ønsker å sette igang en jobb i et terminalvindu og la det stå og jobbe selvom man selv logger ut, kan man bruke screen. Da kan man senere logge seg inn på nytt til samme host og så koble seg opp til terminalvinduet som ligger i bakgrunnen. Man installerer screen og starter en ny screen-session med

```
$ sudo apt update -y 
$ sudo apt install screen
$ screen
Screen version 4.03.01 (GNU) 28-Jun-15

$ uname
Linux
$ ./loop.sh
loop nr 1
loop nr 2
loop nr 3
loop nr 4
```

og dermed får man et terminalvindu som ser ut som et helt vanlig terminalvindu. Her kan man kjøre kommandoer og for eksempel sette igang en jobb som loop-jobben over. Når man så kobler seg fra dette screen-vinduet med CTRL-a CTRL-d, kommer man tilbake til shellet hvor man kjørte kommandoen screen.

```
$ screen
[detached from 9833.pts-0.os1]
$
```

Så kan man logge ut og inn igjen(eventuelt fra et helt annent sted) og liste alle screen-sessions med

```
$ screen -ls
There are screens on:
	9833.pts-0.os1	(14. feb. 2017 kl. 18.15 +0100)	(Detached)
	2216.compile	(13. feb. 2017 kl. 09.01 +0100)	(Detached)
	923.pts-1.os1	(13. feb. 2017 kl. 08.57 +0100)	(Detached)
3 Sockets in /var/run/screen/S-group1.

$
```

Så kan man koble seg til den screen man ønsker seg med

```
$ screen -r pts-0.os1
```

og man vil se at jobben har fortsatt å kjøre i terminalvinduet når man var logget ut.

```
group1@os1:~$ ./loop.sh
loop nr 1
loop nr 2
loop nr 3
loop nr 4
loop nr 5
loop nr 6
loop nr 7
loop nr 8
loop nr 9
loop nr 10
```

Om man ønsker å se om man er inne i en screen og vise hvilken det er, kan man oppnå det med

```
$ echo $STY
9833.pts-0.os1
```

For å gi navn til en screen kan man starte den med

```
$ screen -S compile
```

og den listes med navn som vist over i eksempelet med `screen -ls` . Om man fra screen-vinduet taster CTRL-d (uten CTRL-a foran) vil screen-prosessen drepes. På samme måte som om man drepte den med kill. For å scrolle opp og ned må man bruke kommandoen `CTRL-a ESC` og så opp og ned piltaster. `ESC` igjen for å avslutte scrolling.

Om man leser manual-siden for screen, finner man kommandoer man trenger i litt mer spesielle tilfeller, men dette er alt man behøver for enkel bruk.

---

## 6.9.1 Å dele en screen med samme bruker

Hvis to personer er logget inn på samme Linux-server med samme bruker, kan de enkelt dele en felles screen der begge kan utføre kommandoer og dermed jobbe sammen. Først må en av dem lage en ny screen med opsjonene `-d -m` som gjør at man lager en screen men ikke kobler seg til den:

```
screen -d -m -S felles
```

Deretter kan begge koble seg til med

```
screen -x felles
```

og de vil begge kunne utføre kommandoer og se hva den andre gjør.

---

## 6.9.2 Bakgrunnsjobber og screen

Screen er også et fint verktøy å bruke for å sette igang batch-jobber som potensielt kan bruke lang tid på å bli ferdig og som kan finne på å skrive til både stderr og stdout. Det siste kan være problematisk om man har koblet seg opp med ssh for å starte jobbene, uten å sørge for å redirigere stderr og stdout. Default skriver de da tilbake til terminalen ssh-tilkoblingen kom fra og da kan hele jobben crashe om disse tilkoblingene ikke lenger finnes fordi du har logget ut. Forøvrig er følgende en sikker metode å sette igang en bakgrunnsjobb på en annen maskin med ssh:

```
ssh haugerud@studssh.cs.oslomet.no '/home/haugerud/back.sh </dev/null >/home/haugerud/backup.log 2>&1 &'
```

Legg merke til at både stdin, stdout og stderr er tatt hånd om, slik at alle koblinger til ssh-kanalen er brutt. I tillegg er jobben (back.sh) avsluttet med &, slik at den legges i bakgrunnen. I tillegg brukes full path for å sikre at det ikke er noen avhengighet av PATH. Dermed vil denne fortsette å kjøre i bakgrunnen etter at man logger seg ut fra shellet som startet jobben med ssh. Alternativt kunne man startet jobben fra en screen-session, som ville stått og tatt i mot eventuell output. Men da kunne man potensielt fått problemer om serveren som kjører screen hadde gått ned.

---

## 6.10 scp

`scp` (secure copy) kopierer filer mellom maskiner og sender alt kryptert:

```
mroot@os50:~$ scp haugerud@rex.cs.oslomet.no:~/www/regn .
haugerud@rex.cs.oslomet.no's password: 
regn                                                       100%  194   123.7KB/s   00:00    
mroot@os50:~$
```

Meget nyttig og mye brukt for sikker filoverføring. Hvis man er på studssh og vil overføre en fil r.sh derfra, kan man gjøre det med

```
haugerud@studssh:~$ scp r.sh mroot@os50.vlab.cs.oslomet.no:
mroot@os50.vlab.cs.oslomet.no's password: 
r.sh                                                        100%   39     0.0KB/s   00:00
```

Med opsjonen -r kan man overføre mapper(inkludert undermapper):

```
haugerud@studssh:~$ ls -l nymappe/
total 16
-rwxr-xr-x 1 haugerud drift 34 jan.   8 10:17 mitt.sh
-rwxr-xr-x 1 haugerud drift 39 jan.   8 10:10 r.sh
-rw-r--r-- 1 haugerud drift 24 jan.   8 10:09 tomfil
haugerud@studssh:~$ scp -r nymappe mroot@os50.vlab.cs.oslomet.no:
mroot@os50.vlab.cs.oslomet.no's password: 
tomfil                                                     100%   24     0.0KB/s   00:00    
r.sh                                                       100%   39     0.0KB/s   00:00    
mitt.sh                                                    100%   34     0.0KB/s   00:00
```

---

## 6.11 Backup med rsync og cron-tab

Når man har satt opp passord-løs innlogging med ssh-keys som vist over, er det enkelt å sette opp systematisk backup. Anta man ønsker å ta backup av /home/group1 på en os-VM. Det kan man nå gjøre med

```
scp -r /home/group1/ haugerud@studssh.cs.oslomet.no:/home/haugerud/kopiavos1
```

og hele mappen og alle undermapper blir kopiert over. Men når man gjør det på nytt en gang til, vil alle filer kopieres over enda en gang. Linux-kommandoen `rsync` gjør det samme, men den kopierer bare over filer som har endret seg fra gang til gang:(Gjør først `$ sudo apt install rsync` )

```
rsync -a /home/group1/ haugerud@studssh.cs.oslomet.no:/home/haugerud/rsynckopiavos1
```

Når man lager en ny fil eller gjør en endring, er det bare dette som kopieres over neste gang. Den enkleste måten å få dette til å bli en daglig rutine(eventuelt hver time) er å bruke `cron` . På Linux-VM må cron først insatlleres med

```
group100@os100:~$ sudo apt install cron
```

Om man kjører

```
crontab -e
```

får man opp en fil som man kan bruke til å kjøre jobber til visse tider på døgnet. Følgende linje i crontab

```
# Edit this file to introduce tasks to be run by cron.
#
# m h  dom mon dow   command

30 1 * * * /home/group1/bin/rsyncStudssh.sh
```

fører til at scriptet kjører hver natt kl 01.30. Hvis man bytter ut tallet 1 med *, vil scriptet `rsyncStudssh.sh` kjøres 30 minutter etter hver hele time. Forkortelsene i linjen over forklarer syntaksen i crontab:

|   |   |
|---|---|
| m | minute |
| h | hour |
| dom | day of month |
| mon | month |
| dow | day of week |

På siden [crontab.guru](https://crontab.guru) er det enkelt å teste ut hva forskjellige crontab-koder gir.

Om man har root aksess kan man også legge script i mappene definert i `/etc/crontab` :

```
group1@os1:~$ cat /etc/crontab 
# /etc/crontab: system-wide crontab
# Unlike any other crontab you don't have to run the `crontab'
# command to install the new version when you edit this file
# and files in /etc/cron.d. These files also have username fields,
# that none of the other crontabs do.

SHELL=/bin/sh
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# m h dom mon dow user	command
17 *	* * *	root    cd / && run-parts --report /etc/cron.hourly
25 6	* * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.daily )
47 6	* * 7	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.weekly )
52 6	1 * *	root	test -x /usr/sbin/anacron || ( cd / && run-parts --report /etc/cron.monthly )
```

Script som for eksempel legges i `/etc/cron.hourly` vil kjøres 17 minutter over hver hele time.

---

## 6.12 wget

`wget` henter web (og ftp) sider fra kommandolinjen.

```
mroot@os50:~$ wget https://www.cs.oslomet.no/~haugerud/regn
--2018-02-25 22:29:42--  https://www.cs.oslomet.no/~haugerud/regn
```

På denne måten kan store nedlastninger kjøres i bakgrunnen. Opsjonen `-O -` sender output til STDOUT, slik at det kan brukes i en pipe.

```
wget -r https://www.gnu.org -o log.txt
```

Opsjonen `-r` henter hele web-stedet rekursivt (default dybde er 5). Med opsjonen `--mirror` og kjørt regelmessig, kan man opprettholde en mirror-site.

---

## 6.13 gzip,bzip2, tar og zip

`gzip` komprimerer en fil mens `gunzip` dekomprimerer den.

```
$ ll
-rw-r--r--    1 haugerud drift      130680 Oct  5 20:11 passwd
$ gzip passwd
$ ll
-rw-r--r--    1 haugerud drift       39093 Oct  5 20:11 passwd.gz
$ gunzip passwd.gz
$ ll
-rw-r--r--    1 haugerud drift      130680 Oct  5 20:11 passwd
```

De nyere `bzip2` og `bunzip2` gjør det samme, er ikke like raskt, men komprimerer bedre.

```
$ bzip2 passwd
$ ll
-rw-r--r--    1 haugerud drift       29246 Oct  5 20:11 passwd.bz2
$ bunzip2 passwd.bz2
```

Kommandoen `tar` pakker en hel mappestruktur til en enkelt fil.

```
$ tar cf dir.tar dir  # Pakker alt ned i dir.tar, c = create
$ tar xf dir.tar      # Pakker alt opp, lager dir, x = extract
```

Man kan kjøre `gzip` på en tar fil, men det er enklere å gjøre alt på en gang:

```
$ tar cfz dir.tgz dir  # Pakker alt ned i dir.tar, c = create, z = gzip
$ tar xfz dir.tgz      # Pakker alt opp, lager dir, x = extract, z = gzip
$ tar cfz ob1.tgz snort.bash info.bash # Pakker de to filene i ob1.tgz
$ tar cfj dir.tbz dir  # j = bzip2
```

Man kan gjøre det samme med kommandoen `zip` som kan kjøre på mange plattformer og er kompatibel med windows sin `PKZIP` .

```
$ zip -r dir.zip dir  # -r = rekursivt i mappen dir
$ unzip dir.zip
```

*tar cfz komprimerer noe mer:*

```
-rw-------    1 haugerud drift      728780 Sep 27 00:58 forelesning.tgz
-rw-------    1 haugerud drift     1086314 Sep 27 01:00 forelesning.zip
```

---

## 6.14 awk (ward)

Syntaks: awk 'awk program' fil

```
$ ps u
haugerud 23419  0.0  0.1  2032 1268 pts/1    S    09:07   0:00 -bash

$  ps aux | awk '/haugerud/ {print $2}'
23419
4396
4397
$  ps aux | awk '/haugerud/ {print $2,$11}'
23419 -bash
4403 ps
4404 awk
$  ps aux | awk '{if ($1 == user) {print $2}}' user=`whoami`
23419
4416
4417
$ awk -F: '{ if ($1 == "haugerud") {print $NF}}' /etc/passwd
/bin/bash
```

---

## 6.QA Spørsmål

**Hvordan fjerne et alias?**

Svar: med unalias: `unalias move`