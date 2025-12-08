## 1.2 Hva er Linux?

* Linux er et operativsystem = et stort og komplisert program som styrer en datamaskin
* Linux-kjernen laget av Linus Torvalds i 1991
* GNU/Linux er et mer korrekt navn
* Mest brukt som server OS
* Linux er et Unix-OS, andre er Mac OS X, FreeBSD, BSD, Solaris, AIX
* Unix ble laget av Ken Thompson og Dennis Ritchie i 1969
* Viktig del av Unix-filosofien: Sette sammen mange små programmer på mange måter

---

## 1.3 Linux

* Åpen kildekode, Linux-kjernen er GPL
* Det finnes mange distribusjoner av Linux, i alle størrelser.
* Små: i IP-kameraer, Mobiltelefoner(Android), Routere, switcher
* Store: Ubuntu/Debian, Red Hat/Fedora/Centos, SUSE/openSUSE
* GUI med vinduer og pek-og-klikk (for de som trenger det)

---

## 1.4 Linux-fordeler

* Gratis og åpen kildekode
* Naturlig del av åpen kildekode-prosjekter
* Sikkerhet
* Stabilitet

---

## 1.5 Hvor brukes Linux?

* Desktop/laptop: 1.5%
* Web servere: 70%
* Public Cloud: Amazon EC2 92% (Totalt: AWS 41%, Microsoft Azure 29%)
* Smartphone/nettbrett: Android 70%, iOS 24% (Unix basert)
* Supercomputere: 100% av de 500 største

---

## 1.6 Hva er et shell?

* kommandobasert verktøy
* tar imot kommandoer fra tastatur
* *Grensesnitt mot Linux-kjernen*

Illustrasjon:
Linux-kommandoene sendes til shellet som er et skall rundt Linux-kjernen. Shellet 
sørger for at oppdraget det får blir utført ved å gjøre et sett av systemkall til kjernen.

---

## 1.7 Hvorfor shell/kommandolinje?

*Tidligere gikk all kommunikasjon med et Linux-system gjennom et shell.* [1](footnode.html#foot98)

* Stor frihetsgrad; "Alt" er mulig å gjøre
* **Kompliserte oppgaver kan løses effektivt, ved å sette sammen mange små Linux-program; sort, grep, sed, cp, mv**
* *et programmeringsspråk: shell-script som kombinerer Linux-kommandoer; systemprogrammering*
* Vanskelig å automatisere og replikere en lang sekvens av pek og klikk
* Mye brukt i Linux automatisering, Cloud, Docker, Kubernetes, Git, osv

---

## 1.8 Innlogging

Hver bruker på et Linux-system har

* entydig brukernavn
* passord

Oversikt over alle brukere på systemet ligger i filen

* /etc/passwd

og de krypterte passordene ligger i filen

* /etc/shadow

Kan ikke leses av vanlige brukere, kun av *root* (superuser)

Passordet settes/endres på OsloMet via web.

---

## 1.9 Linux filsystem

Filer er et helt sentralt Linux-begrep. *Alle data lagres som filer og strømmer av 
data fra tastatur og andre devicer blir behandlet som om de var filer.*

Illustrasjon:
Et typisk Linux-filtre

---

## 1.10 Hvordan man flytter seg i et Linux-filtre

| Linux-kommando | Virkning |
|--------------|--------|
| $ pwd | gir mappen/katalogen man står i (Print Working Directory) |
| $ cd home | change directory til “home” (kun fra /) |
| $ cd /etc | flytter til /etc |
| $ cd .. | flytter en mappe opp |
| $ cd ../.. | flytter to mapper opp |
| $ cd | går til hjemmemappen |
| $ ls -l | viser alt som finnes i mappen |

---

## 1.11 Å lage et shell-script

```
$ jed script.sh
```

Illustrasjon:
script.sh i jed

* `#! --> nå kommer et script`
* `/bin/bash --> skal tolkes av /bin/bash`
* Rettigheter må settes slik at filen er kjørbar (x)

```
[os]studssh:~$ script.sh
-bash: ./script.sh: Permission denied

[os]studssh:~$ ls -l script.sh
-rw-r--r-- 1 os student 37 2010-01-06 20:23 script.sh

 [os]studssh:~$ chmod 700 script.sh

[os]studssh:~$ ls -l script.sh
-rwx------ 1 os student 37 2010-01-06 20:23 script.sh

 [os]studssh:~$ script.sh
 Linux studssh 2.6.24-26-generic #1 SMP Tue Dec 1 18:37:31 UTC 2009 i686 GNU/Linux
tmp
/iu/cube/u4/os/mappe
total 4
drwxr-xr-x 2 os student 4096 2010-01-04 12:11 tmp

 [os]studssh:~$
```

---

## 1.12 Filbehandling (Viktig!)

"Alt" i Linux er filer; *vanligvis ASCII-filer.*

| Linux-kommando | resultat |
|--------------|--------|
| $ ls | lister filer/mapper i mappen der du står |
| $ ls -l | ekstra info |
| $ ls -a | lister “skjulte” filer (.fil) |
| $ ls /etc | lister alt i /etc |
| $ mkdir mappe | lager en mappe |
| $ cat fil1 | skriv innhold til skjermen |
| $ touch fil2 | lag en tom fil med navn “fil2”/oppdaterer tidsstempel hvis den fins |
| $ jed fil3.txt | editer en fil med navn fil3.txt. Rask og effektiv editor som også kan brukes fra putty. |
| $ emacs fil4.txt | editer en fil med navn fil4.txt. Mer omfattende GUI-editor. |
| $ cp fil1 fil2 | kopierer fil1 til fil2 |
| $ cp -i fil1 fil2 | Spørr om fil2 skal overskrives |
| $ mv fil1 fil2 | Endrer navn fra fil1 til fil2 |
| $ mv fil2 /tmp | Flytter fil2 til /tmp |

---

## 1.13 Spesielle mapper

| betegnelse | Mappe |
|----------|-----|
| . | den du står i |
| .. | den over |
| ../.. | den over den igjen |
| ~ | Din hjemmemappe |

Bruk av ~:

```
$ echo ~
/iu/nexus/ud/haugerud
$ cat ~/.bashrc  (skriver din .bashrc til skjermen.)
$ echo ~haugerud
/iu/nexus/ud/haugerud
$ cd ~/www       {# gå til din hjemmesidemappe.}
```