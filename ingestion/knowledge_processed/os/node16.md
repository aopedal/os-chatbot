## 15.2 Disker

En harddisk består av et antall plater av et magnetisk materiale. For hver plate er det et lese/skrive-hode som kan lese/skrive bits ved å måle magnetisering/magnetisere platene. De fleste disker lagrer data på begge sider av platene og har derfor lese/skrive-hode over og under.

Illustrasjon:
Overflaten av en plate på innsiden av en harddisk. Lesehodet flyttet posisjon mens bildet ble tatt og kan derfor sees i to posisjoner.

[Denne linken](
https://commons.wikimedia.org/wiki/File:HardDisk1.ogv  
) viser en video av en åpen harddisk mens den kjører.

Illustrasjon:
Tversnitt av en harddisk. En typsik rotasjonshastighet er 
7200 rpm (rounds per minute).

---

## 15.2.1 Sektor

Det området som lesehodet dekker under en rotasjon, kalles en track og en track er delt opp i sektorer. En sektor er

* grunnenhet for disker
* vanligvis på 512 bytes
* minste enhet som kan leses/skrives til.

Illustrasjon:
Hver plateoverflate er delt inn i tracks og sektorer. Den delen av en track som ligger 
innenfor en sektor, er den minste enheten det lagres data på og den er vanligvis på 512 bytes. Noen ganger brukes begrepet sektor om alle tracks i en retning på disken.

---

## 15.2.2 Sylinder

En sylinder er samlingen av alle tracks fra alle platene i disken som ligger i samme avstand fra sentrum.

Illustrasjon:
En sylinder defineres som samlingen av tracks på alle overflater i samme avstand fra sentrum. 
Sylinder nummer 39 er derfor samlingen av alle track nr. 39 på begge sider av alle platene. Adressen til den minste lesbare enheteten, en sektor, er derfor gitt ved tre parametre [leshode, track, sektornummer]. Når OS vil lese noe fra disk, sendes en forespørsel med disse tre tallene.

---

## 15.3 Partisjoner

En disk-partisjon defineres som et antall sylindere som ligger fysisk samlet etter hverandre. For eksempel kan man bestemme at alle sylindere fra og med nummer 150 til og med 672 skal utgjøre en partisjon. Dette er den største enheten man deler inn en disk i. Under Windows er det vanlig ha en stor partisjon som utgjør hele disken, mens det under Linux er vanlig å dele inn disken i flere partisjoner. Monteringspunkter i filsystemet kan da tildeles bestemte partisjoner slik at for eksempel alt som ligger under `/home` legges på partisjon nummer 3 på disken.

Illustrasjon:
En partisjon består av et antall sylindre som ligger etter hverandre. Noen av fordelene med partisjoner er:

* Hvis man har en egen partisjon for brukeres filer og partisjonen som OS ligger på blir ødelagt eller OS av andre grunner må installeres på nytt, vil man kunne beholde partisjonen med brukerfiler.
* Hvis man bare har en disk, kan man likevel ha forskjellige filsystemer og dermed forskjellige OS på den samme disken når den er delt i partisjoner.
* Mindre partisjoner og dermed mindre filsystemer er noe hurtigere enn å ha alt på en partisjon.
* Filsystemene på partisjoner kan tilpasses dataene som skal ligge der. For eksempel stor cluster-størrelse til videofilmer.

---

## 15.4 SSD (Solid State Drive)

* Basert på flash-minne som i minnepinner og har ingen bevegelige deler
* Tåler rystelser bedre og er lydløs
* Rask random aksesstid, 0.1 ms mot 5-10 ms for roterende disker
* Dyrere enn tradisjonelle disker og mindre kapasitet

---

## 15.5 Filsystemer

Før en ny disk kan tas i bruk må den formatteres. Dette er en lavnivå organisering av disken som vanligvis gjøres på fabrikken der den deles inn i sektorer, som for de fleste harddisker er på 512 byte. Når dette er gjort kan disk-controlleren lese og skrive til disse sektorene. Når man senere bruker software til å formattere en disk, er dette en høynivå formattering som setter disken tilbake til slik den var når den var ny, og i tillegg gjør operasjoner som å legge inn en boot-sektor. Før operativsystemet og applikasjoner kan ta disken i bruk må det så lages et filsystem på disken. Det finnes mange forskjellige filsystemer, NTFS er det vanligste på Windows, tidligere var FAT det vanligste. På Linux er filsystemet ext3 det vanligste. Hvis disken er inndelt i flere partisjoner, kan det lages forskjellige filsystemer på de forskjellige partisjonene. Fra Windows kan man ikke uten videre lese og skrive til partisjoner med ext3, men fra Linux kan man lese og skrive til parisjoner med FAT og NTFS.

Filsystemet tar utganspunkt i den miste enheten som kan leses fra eller skrives til, sektoren som typisk er på 512 bytes. Den viktigste oppgaven til filsystemet er å fordele mapper og filer på diskens sektorer og holde orden på hvor alt ligger. I de fleste tilfeller er en sektor for liten til å være en optimal størrelse for inndelingen av en disk og filsystemet deler derfor disken inn i større blokker (Linux: blocks, Windows: clustere). Størrelsen på blokkene må bestemmes når filsystemet lages og fordeler og ulemper ved store/små blokker må da veies mot hverandre.

* Store blokker
  * Lese og skrive går hurtig, større sammenhengende områder
  * En liten fil vil bruke unødvendig mye plass
  * Bra til store filer, bilder og video
* Små blokker
  * Små filer bruker mindre diskplass
  * Større filer kan risikere å bli spredt rundt på disken
  * Lese og skrive store filer går da saktere
  * Bra hvis filsystemet skal inneholde mange små filer

---

## 15.5.1 Tabell over filenes blokker

Alle filsystemer har en oversikt over hvilke blokker enhver fil på systemet består av. Når en fil lages, vil den om mulig lagres på sammenhengende blokker. Når filene øker vil den dynamisk tildeles flere blokker, men da kan det være at det ikke er plass ved siden av de opprinnelige blokkene og filen må spres på flere områder av disken.

Illustrasjon:
Filsystemet holder oversikt over hvilke blokker en fil består av. Blokkstørrelsen er 2KByte i dette 
eksempelet. Bare hele blokker kan allokeres til en fil, slik at all plassen ikke utnyttes når filstørrelsen ikke eksakt går opp 
når man deler på filstørrelsen.

---

## 15.5.2 Fragmentering

En oppdeling av filer rundt om kring på disken som resultat av dynamisk allokering når filer vokser, kalles fragmentering og den blir ofte ganske omfattende på disker som er mye i bruk og hvor det meste av plassen blir brukt. Under Windows kan man defragmentere disken med Disk Defragmenter. Det må da være minst 15% ledig plass og prosessen kan ta lang tid. For Linux ext-filsystemer finnes det ikke noen innebygd defragmenterer, men det finnes slike verktøy som kan installeres.

Illustrasjon:
Når en fil slettes vil det oppstå huller på disken og dette vil føre til enda større grad av fragmentering.

---

## 15.5.3 Sletting av filer

Når en fil slettes, vil de fleste filsystemer bare slette informasjonen om filene og hvilke blokker som tilhører filene og ikke slette innholdet av blokkene. Dermed kan man med applikasjoner som autopsy eller ved å se på et disk-image direkte med en hex-editor finne igjen hele eller deler av en slettet fil. Det finnes egne applikasjoner som brukes til å slette filer bedre ved å skrive over innholdet av filene med nuller eller tilfeldige bit. Selvom man gjør en slik operasjon flere ganger, kan man med måleinstrumenter som er enda mer nøyaktige enn standard lese/skrive-hoder finne ut hva som opprinnelig var skrevet. Et eksempel på dette kan sees i Fig. 86 .

Illustrasjon:
Rester etter data som er overskrevet på en harddisk.

Bildet er hentet fra boken Forensic Discovery av Farmer og Venema som er tilgjengelig [online](https://www.porcupine.org/forensics/forensic-discovery/) .

---

## 15.6 Lage et Linux ext3 filsystem

Først må man lage en tom fil av den størrelse man ønsker på image't.

```
haugerud@lap:~/disk/mount$ dd if=/dev/zero of=minfil bs=8M count=1
1+0 records in
1+0 records out
8388608 bytes (8,4 MB, 8,0 MiB) copied, 0,00784602 s, 1,1 GB/s
```

Dette lager en 8 MiB fil med null-tegn (ASCII tegn nummer null). Deretter kan man bygge et filsystem på denne filen:

```
haugerud@lap:~/disk/mount$ mkfs -t ext3 minfil
mke2fs 1.44.1 (24-Mar-2018)
Discarding device blocks: done                            
Creating filesystem with 8192 1k blocks and 2048 inodes

Allocating group tables: done                            
Writing inode tables: done                            
Creating journal (1024 blocks): done
Writing superblocks and filesystem accounting information: done
```

Deretter kan dette image't monteres i filsystemet på helt samme måte som om det var en disk:

```
haugerud@lap:~/disk/mount$ sudo mount minfil /mnt
[sudo] password for haugerud: 
haugerud@lap:~/disk/mount$ cd /mnt/
haugerud@lap:/mnt$ ls -l
total 12
drwx------ 2 root root 12288 april 27 00:10 lost+found
```

Tidligere måtte man eksplisitt bruke opsjonen -o loop for å montere en fil, men det fungerer nå uten å spesifisere det.

---

## 15.7 NTFS

Windows NT File System er Windows NT/XP/7/8/10 sitt eget filsystem men også FAT16 og FAT32 støttes.

* Deler inn disken i clustere
* Clusterstørrelse på 512 bytes, 1 KiB, 2 KiB, 4 KiB og opp til maks 64 KiB
* 4 KiB clustere er default for disker på 2GiB eller mer
* Clusterne adresseres med 64 bits pekere
* Komprimering
* Cluster størrelse på mer enn 4 KiB kan ikke komprimeres og brukes vanligvis ikke
* Kryptering
* Alle endringer i filsystemet logges (men ikke endringer av data)
* Raskt å rekonstruere filsystemet ved disk-crash

---

## 15.7.1 Volum

* Et volum består av en eller flere clustere
* Kan omfatte deler(partisjoner) av en disk, en hel disk, eller flere disker
* Filsystemet defineres for dette volumet
* Maksimum antall clustere i et volum er , 16TiB med 4KiB clustere

---

## 15.7.2 Master File Table(MFT)

Den viktigste filen i et NTFS-volum er MFT selv.

* Filen MFT består av 16 records med metadata og deretter en record for hver fil og mappe
* Hver fil har en 1KB record som inneholder all informasjon om filen som attributter
* Eksempler på atributter: tidsstempler, filnavn, data eller peker til hvor clusterene med data ligger
* Hvis plass lagres begynnelsen av dataene i MFT record'en
* Små filer kan lagres i sin helhet i MFT record'en
* Hvis det ikke er plass til pekere til alle clusterne, lages det en peker til en ny MFT-record
* Rettigheter ble tidligere lagret i hver fil-record: hvem er eier, hvem kan lese, skrive, aksessere
* Rettigheter lagres nå i en av de 16 MFT metatdatafilene, $Secure
* OS-kjernen behandler en fil som et objekt

Illustrasjon:
Figure 11-41 i Tanenbaum.

Illustrasjon:
Figure 11-42 i Tanenbaum.

---

## 15.7.3 Linux-partisjoner

Eksempelet under er informasjon som gis når man velger p for print fra menyen etter at man som root har kjørt kommandoen `fdisk /dev/hda` på en linux PC:

```
Disk /dev/hda: 61.4 GB, 61492838400 bytes
255 heads, 63 sectors/track, 7476 cylinders
Units = cylinders of 16065 * 512 = 8225280 bytes

   Device Boot      Start         End      Blocks   Id  System
/dev/hda1   *           1         608     4883728+  83  Linux
/dev/hda2             609         624      128520   82  Linux swap / Solaris
/dev/hda3             625        2537    15366172+  83  Linux
/dev/hda4            2538        7476    39672517+   5  Extended
/dev/hda5            2538        6500    31832766   83  Linux
/dev/hda6            6501        7476     7839688+  83  Linux
```

Den første partisjonen tildeles navnet `/dev/hda1` og består av alle sylinderne fra 1 til og med sylinder nummer 608. Hver sylinder er på 8225280 bytes og denne partisjonen er derfor på bytes bytes = 4.66 GBytes. Alternativt sier output at denne partisjonen består av 4883728 blocks med størrelse 1024 bytes. Partisjon nr. 2 er en liten swap-partisjon på 16 sylindre og totalt 126 MByte. Den fjerde partisjonen er spesiell. Det kan bare lages fire såkalte primære partisjoner og om man skal ha flere enn fire må den fjerde lages som en extended partisjon som inneholder de resterende. `/dev/hda4` inneholder ikke data, men definerer området på disken som utgjør partisjon 5 og 6. Linux-kommandoen `df` viser hvordan filsystemet er montert på partisjonene.

for SATA og SCSI-disker heter disk-devicet vanligvis `/dev/sda` og kommandoen `fdisk /dev/sda` på en linux PC kan gi:

```
Disk /dev/sda: 298,1 GiB, 320072933376 bytes, 625142448 sectors
Units: sectors of 1 * 512 = 512 bytes
Sector size (logical/physical): 512 bytes / 512 bytes
I/O size (minimum/optimal): 512 bytes / 512 bytes
Disklabel type: dos
Disk identifier: 0xcb46d2fa

Device     Boot     Start       End   Sectors   Size Id Type
/dev/sda1  *         2048 591679487 591677440 282,1G 83 Linux
/dev/sda2       591681534 625141759  33460226    16G  5 Extended
/dev/sda5       591681536 625141759  33460224    16G 82 Linux swap / Solaris
```

og heads, tracks og cylinders er ikke lenger nevnt.

```
[root]@rex$ df
Filesystem           1K-blocks      Used Available Use% Mounted on
/dev/hda1              4806904   4223584    339136  93% /
/dev/hda3             15124900  13790960    565632  97% /lokal
/dev/hda5             31333024  22349088   7392300  76% /mysql
/dev/hda6              7716496   2785908   4538604  39% /mln
```

Alt som ligger under `/lokal` i filsystemet vil fysisk ligge på partisjon nummer 3. Tilsvarende for partisjon 5 og 6. Resten av filsystemet, alt annent under `/` ligger på 1. partisjon. Neste disk vil het `/dev/hdb` og på samme måte kan denne deles inn i partisjoner og andre deler av filsystemet kan monters på disse partisjonene.

---

## 15.8 Windows-partisjoner

Om man deler opp en disk under Windows, tildeles hver partisjon bokstaver, C, D, E etc. Bokstavene A og B er tradisjonelt satt av for to diskett-stasjoner. Om man har flere disker kan hele denne eller deler av den om man lager flere partisjoner, tildels andre bokstaver. På Windows XP kan man Ved å kjøre programmet `Diskpart` se på og endre partisjoneringen av diskene:

```
C:\>Diskpart

Microsoft DiskPart version 1.0
Copyright (C) 1999-2001 Microsoft Corporation.
On computer: DIRAC

DISKPART> list disk

  Disk ###  Status      Size     Free     Dyn  Gpt
  --------  ----------  -------  -------  ---  ---
  Disk 0    Online        75 GB      0 B
  Disk 1    Online        75 GB    54 GB
```

Denne PC-en har to disker og ved å velge en av diskene kan man se hvilke partisjoner den inneholder:

```
DISKPART> select disk 0

Disk 0 is now the selected disk.

DISKPART> detail disk

WDC WD800BB-32BSA0
Disk ID: 3E423E41
Type   : IDE
Bus    : 0
Target : 0
LUN ID : 0

  Volume ###  Ltr  Label        Fs     Type        Size     Status     Info
  ----------  ---  -----------  -----  ----------  -------  ---------  --------
  Volume 2     C                NTFS   Partition     39 GB  Healthy    System
  Volume 3     F                       Partition     35 GB  Healthy
```

Vi ser at disken er delt i to omtrent like store partisjoner, at den første heter C, er systemdisken og har filsystemet NTFS. Den andre heter F og på denne er det ennå ikke lagd noe filsystem.

---

## 15.9 Disk controller og DMA

Et multitasking OS vil fortløpende ha behov for å lese data fra mange forskjellige steder på en disk. Siden disken snurrer rundt er det ikke opplagt hva som er den hurtigste måten å lese for eksempel 20 forskjellige slike forespørsler. En forespørsel består typisk av tre tall; [leshode, track, sektornummer]. Å flytte lesehodet til nærmeste neste track som skal leses er en mulighet, å la leshodet flytte seg hele veien fra innerst til ytterst og plukke opp forespøsler underveis er en annen. OS må velge en slik algoritme for å hente inn data. På moderne disker utføres slike algoritmer av mikroprosessoren som sitter på diskens egen disk controller. Tidligere tok OS seg direkte av lesingen av data og administreringen av disken, men det ordner nå disk controlleren.

Før var det også vanlig at OS detaljstyrte skrivingen av data fra disken til internminnet. Dette krevet veldig mange interrupts hver gang det komm inn data fra disken og derfor bruker moderne systemer DMA (Direct Memory Access) som avlaster denne jobben for CPU-en. Dette er vanligvis en egen chip knyttet til systembussen med en egen liten mikroprosessor og tillatelse fra CPU til å skrive direkte til minnet. CPU kan dermed be DMA om en større eller mindre lese eller skriveoperasjoner og DMA vil administrere kopieringen mellom disk og internminnet. Først når alle dataene er på plass sender DMA et interrupt til CPU som forteller at kopieringen er fullført. DMA brukes også for lesning av data fra andre enheter som CD-spiller, USB-devicer etc.

Også for I/O enheter som harddisker som er svært langsomme sammenlignet med internminnet, er det nyttig å bruke cache. I internminnet er det satt av plass til disk-cache, slik at mest mulig av det som er lest i det siste meelomlagres og kan hentes ut mye hurtigere om det kommer en ny forespørsel.

Illustrasjon:
DMA kommuniserer med disk-controlleren og sørger for at det OS ønsker blir kopiert mellom 
harddisken og internminnet.

---

## 15.10 ATA/IDE, SATA og SCSI

Det finnes flere interface-standarer eller grensesnitt-typer for harddisker. De varierer i pris og ytelse. ATA/IDE er billigst og brukes til standard PC'er. SATA er ATA's arvtager, har høyere ytelse og brukes også noe av server. SCSI og SAS er dyrere og brukes av servere som krever høy ytelse.

---

## 15.10.1 ATA/IDE

Den tidligste versjonen av denne grensessnitt-standaren ble på slutten av åttitallet kjent som IDE, Integrated Drive Electronics, fordi disk-controlleren ble plassert på selve disken. Etterhvert ble det offisielle navnet på standarden ATA (Advanced Technology Attachment).

* Den billigste teknologien
* Brukes i standard desktop PC'er og laptoper
* Kalles ofte PATA (Parallell ATA) eter at SATA (Serial ATA) ble innført
* Overføringshastigheter opp til 100 MB/s
* Kan ha inntil 2 disker på samme kabel (master og slave)

Illustrasjon:
ATA/IDE kabel

---

## 15.10.2 SATA

* Serial ATA, raskere og bedre enn ATA, men omtrent samme pris
* Introdusert i 2003, har tatt over for ATA
* Må ha SATA-kontroller på hovedkortet eller egen SATA-kontroller
* Overføringshastigheter opp til 300 MB/S (SATA2/SATA-300)
* Bruker samme metode (8B/10B encoding) som ethernet til å sende data
* En disk per kabel

Illustrasjon:
SATA-kontakter på hovedkort

Illustrasjon:
SATA-kabel

---

## 15.10.3 SCSI

* SCSI = Small Computer Systems Interface
* Interface-standard fra 1986 for disker, CD-ROM etc.
* Mer selvstendige disker enn ATA-disker, kan ha mange disker i serie på samme kabel
* Generelt raskere, mer robuste og dyrere enn ATA
* SCSI mest brukt i servere som krever høy disk-ytelse
* Overføringshastigheter opp mot 640 MB/s (Ultra-640 SCSI)
* SAS, Serial Attached SCSI, enda hutigere, bedre og dyrere enn parallell SCSI
* SAS støtter SATA devicer

Illustrasjon:
SCSI-kabel

---

## 15.11 KiB, MiB og GiB

Benenvninger som KB og MB er ikke alltid entydge, KB kan bety både bytes og 1000 bytes. Den opprinnelige SI [6](footnode.html#foot2354) -definisjonen av prefiksene er den helt korrekte og sier at K = 1000, M = 1000.000, G = 1000.000.000, etc. Vanlig praksis når det for eksempel gjelder RAM er at 128MB betyr 128 bytes. Men hvis en harddisk-produsent oppgir at en disk er på 300 GB, betyr det at den er bytes og et OS vil da typisk rapportere den som en disk med kapasitet på 279.4 GB. For å ordne opp i dette og flere lignende tilfeller av flertydighet definerte i 1999 International Electrotechnical Commission (IEC) nye binære prefikser kibi-, mebi-, gibi- og tilhørende symboler Ki, Mi, Gi. Disse prefiksene symboliserer potenser av 2 slik at Ki , Mi og Gi . I 2005 ble dette en IEEE [7](footnode.html#foot2358) -standard.

| Navn | Symbol | Verdi | Eksempel |
|----|------|-----|--------|
| kilo | K |  |  |
| mega | M |  |  |
| giga | G |  |  |
| tera | T |  |  |
| kibi | Ki |  | 100 KB = 97.6 KiB |
| mebi | Mi |  | 100 MB = 95.4 MiB |
| gibi | Gi |  | 100 GB = 93.1 GiB |
| tebi | Ti |  | 100 TB = 90.9 TiB |

Et disk-eksempel viser at produsenten Seagate bruker SI-benvening og sier at en disk er på 160 GB. På første figur ser man at Linux fdisk bruker samme benevning og 1 GB = 1 milliard bytes.

Illustrasjon:
fdisk viser 160 GB Derimot viser XP's Disk Managment at disken er på 149.05 GB og bruker altså 1 GB = bytes = 1.08 milliarder bytes.

Illustrasjon:
XP viser 149.05 GB

Partisjoneringsverktøyet GParted som brukes under Ubuntu-installasjon, rapporterer disk-størrelser i GiB, slik at det er helt entydig hva som menes. Men fortsatt er MiB og GiB relativt sjelden i bruk.

Illustrasjon:
GParted viser at en 160 GB disk er på 149.05 GiB.

---

## 15.12 Sammenligning av overføringshastigheter på minne-enheter

| enhet | Hastighet (MBit/s) |
|-----|------------------|
| Serial Infrared (SIR) | 0.115 |
| Bluetooth 1.1 | 0.7 |
| Medium Infrared (MIR) | 0.5-1 |
| CD-ROM, 1x | 1.2 |
| Bluetooth 2.0 | 2.1 |
| Fast IR | 4 |
| Wireless IEEE 802.11b | 5.5-11 |
| 10 MBit Ethernet | 10 |
| DVD-ROM, 1x | 11.1 |
| USB 1.0 | 12 |
| Bluetooth 4.0 | 25 |
| Bluetooth 5 | 50 |
| Wireless IEEE 802.11g | 54 |
| CD-ROM, 52x | 62.4 |
| 100 MBit Ethernet | 100 |
| Wireless IEEE 802.11n | 150 |
| DVD-ROM, 16x | 177.3 |
| FireWire IEEE 1394 400 | 400 |
| Blu-ray Disk 12x | 432 |
| USB 2.0 | 480 |
| Wireless IEEE 802.11ac | 500 |
| FireWire 800 | 800 |
| Gigabit Ethernet | 1,000 |
| PATA 133 | 1,064 |
| SATA2 300 | 2,400 |
| Ultra-320 SCSI | 2,560 |
| FireWire 3,200 | 3,200 |
| SATA3 | 4,800 |
| USB 3.0 | 5,000 |
| Ultra-640 SCSI | 5,120 |
| Wireless IEEE 802.11ad | 6,750 |
| 10 Gigabit Ethernet | 10,000 |
| USB 3.1 | 10,000 |
| Thunderbolt 1 | 10,000 |
| SAS 3 | 12,000 |
| SATA 3.2 | 16,000 |
| Thunderbolt 1 | 20,000 |
| Thunderbolt 3 | 40,000 |
| 40 Gigabit Ethernet | 40,000 |
| 100 Gigabit Ethernet | 100,000 |
| InfiniBand | 100,000 |

Til sammenligning noen typiske tall for krav til overføringshastigheter for film i forskjellige kvaliteter:

| hastighet | kvalitet |
|---------|--------|
| 2-3 Mbit/s | VHS |
| 8-12 Mbit/s | DVD |
| 36 Mbit/s | Blueray |
| 4-25 Mbit/s | HD-TV/4K |

I motsetning til hva som er vanlig i mange andre sammenhenger, betyr her prefikset M en million. Altså betyr Mbit/s ikke bit/s = 1.048.576 bit/s. Bruken av slike prefiks er diskutert i forrige avsnitt.

---

## 15.12.1 Sammenligning av disker

Her er et eksempel på hver av disktypene med priser hentet fra komplett.no. Men husk at ytelsestallene er hentet fra produsentene.

| Type | Kapasitet | hastighet | Søketid | Rotasjon | Buffer | Produsent | pris |
|----|---------|---------|-------|--------|------|---------|----|
| SATA-600 | 1 TB | 600 MBps | 8.5 | 7200 rpm | 64MB | Seagate | 528 |
| SAS | 2 TB | 1200 MBps | 4.16 | 7200 rpm | 128 MB | Seagate | 1,675 |
| SSD | 120 GB | 600 MBps |  |  |  | Kingston | 578 |
| SSD | 240 GB | 600 MBps |  |  |  | Corsair | 1,049 |
| SSD | 2TB GB | 600 MBps |  |  | 2 GB | Samsung | 6,699 |

I 2012 så det slik ut:

| Type | Kapasitet | hastighet | Søketid | Rotasjon | Buffer | Produsent | pris |
|----|---------|---------|-------|--------|------|---------|----|
| SATA-600 | 1 TB | 600 MBps |  | 7200 rpm | 32MB | Seagate | 795 |
| SAS | 1 TB | 600 MBps |  | 7200 rpm | 64 MB | Seagate | 1.395 |
| SAS | 600 MB | 600 MBps |  | 15000 rpm | 16 MB | Seagate | 3.695 |
| SSD | 60 GB | 300 MBps |  |  |  | Corsair | 799 |
| SSD | 240 GB | 600 MBps |  |  |  | Corsair | 1,999 |

Og for enda et par år tidligere så det slik ut:

| Type | Kapasitet | hastighet | Søketid | Rotasjon | Buffer | Produsent | pris |
|----|---------|---------|-------|--------|------|---------|----|
| ATA-133 | 320 GB | 133 MBps | 8.5 ms | 7200 rpm | 8 MB | Hitachi | 795 |
| SATA-300 | 320 GB | 300 MBps | 8.5 ms | 7200 rpm | 16 MB | Hitachi | 795 |
| Ultra320 SCSI | 300 GB | 320 MBps | 4.7 ms | 10000 rpm | 8 MB | Seagate | 5.750 |
| SAS | 300 GB | 300 MBps | 3.5 ms | 15000 rpm | 16 MB | Seagate | 8.995 |

---

## 15.13 RAID

Mens utviklingen av hastigheten til prosessorer, cache og delvis RAM har gått raskt, har utviklingen av hastigheten til harddisker vært langsom. En måte å forbedre ytelsen på når det begynner å bli vanskelig å få hver enklet enhet til å gå raskere, er å bruke flere enheter i parallell. Utviklingen av multicore prosessorer er et eksempel på dette. For disker kalles teknologien som gjør dette RAID (Redundant Array of Independent Disks). Man bruker da flere like disker til å øke hastigheten man kan hente data og man kan også bruke et slikt oppsett til redundans; dobbel lagring av data slik at man ikke mister data om en disk blir ødelagt.

**RAID 0**: Minst to disker. Striper diskene. Ingen redundans. Hurtigere å lese.

**RAID 1**: Minst to disker. Dupliserer dataene. Hurtigere å lese. Kan fortsatt lese alt om en disk ryker.

**RAID 3**: Minst tre disker. Parallell aksess, veldig små striper, ned til en byte. Paritet lagres på en ekstra disk. Om en disk ryker kan informasjonen hentes ut fra de som er igjen. Optimalt høy overføringshastighet, men kun en forespørsel kan behandles av gangen.

**RAID 4**: Minst tre disker. Paritet lagres på en ekstra disk. Store striper, sektor eller blocks. Om en disk ryker kan informasjonen hentes ut fra de som er igjen. Kan behandle flere forespørsler samtidig. Bra for servere som får mange forespørsler.

**RAID 5**: Minst tre disker. Paritet lagres fordelt på diskene. Store striper, sektor eller blocks. Om en disk ryker kan informasjonen hentes ut fra de som er igjen.

RAID kan implementeres i software, det vil si av OS, eller i hardware ved en dedikert RAID-controller på hovedkortet. RAID 0, 1 og 5 er implementert i Windows 2003 server.

---

## 15.13.1 Ytelse

Ved såkalt striping av diskene økes ytelsen ved både lesing og skriving av filer. Dette fordi en stor fil deles i striper som fordeles på diskene. Innholdet av en stor fil vil være fordelt på alle diskene og data kan både leses fra og skrives til diskene i parallell og da går det mye raskere.

---

## 15.13.2 Paritet

Hvis man har en samling bits (for eksempel en byte, 8 bit) som har verdi en eller null, kan man telle antall enere. Hvis antall enere er like (0, 2, 4, , har samlingen av bits like paritet. Hvis antall enere er odde (1, 3, 5, ), sier vi at samlingen av bits har odde paritet. Dette kan brukes til en meget enkel feilsjekking, hvis man sender et antall bit over et nettverk og pariteten har endret seg på veien, kan man konkludere med at minst ett bit må ha endret verdi. I et RAID kan man ta et bit fra hver data-disk i RAID'et, regne ut pariteten og skrive den til en egen paritetsdisk. Hvis en av diskene i RAID'et crasher og alle dataene for denne disken går tapt, kan man bruke dataene på paritetsdisken for å finne ut verdien på de tapte bit'ene. Hvis pariteten for de igjenværende diskene er den samme som den lagrede pariteten, har en null gått tapt. Hvis pariteten for de igjenværende diskene er forskjellig fra den lagrede pariteten, har en ener gått tapt. Dermed kan hver bit på den tapte disken gjenskapes. I RAID 3 er stripene små, ned til en byte. I RAID 4 og 5 er stripene et antall sektorer. I begge tilfeller er prinsippet for redundans det samme. Bergningen av paritet må gjøres når det skrives til diskene. Det kan gjøres hurtig, fordi XOR-porter kan regne ut paritet i paralell for 32 eller 64 bit av gangen, for henholdsvis 32 og 64 bits prosessorer. Det finnes også hardware-RAID, egne enheter som gjør disse paritetsberegningene og styrer RAID'et uavhengig av prosessoren.

---

## 15.13.3 Eksempel på paritetsberegning

Anta at vi i et RAID 3 striper disken bit for bit og bruker 5 disker. Disken med paritet lagrer da den samlede pariteten for bit'ene for de 4 andre diskene; en ener om antallet er odde og en null om antallet er like:

| disk 1 | disk 2 | disk 3 | disk4 | paritets-disk |
|------|------|------|-----|-------------|
| 0 | 1 | 0 | 1 | 0 |
| 1 | 0 | 1 | 1 | 1 |
| 0 | 0 | 1 | 1 | 0 |
| 1 | 1 | 0 | 0 | 0 |
| 0 | 0 | 1 | 0 | 1 |
| 1 | 1 | 1 | 1 | 0 |

Hvis nå for eksempel den 2. disken crasher og alle dataene fra den blir borte, vil RAID'et se slik ut:

| disk 1 | disk 2 | disk 3 | disk4 | paritets-disk |
|------|------|------|-----|-------------|
| 0 |  | 0 | 1 | 0 |
| 1 |  | 1 | 1 | 1 |
| 0 |  | 1 | 1 | 0 |
| 1 |  | 0 | 0 | 0 |
| 0 |  | 1 | 0 | 1 |
| 1 |  | 1 | 1 | 0 |

Hvordan kan man nå trylle frem igjen dataene på den ødelagte disk2 og legge dem inn på en ny disk? Vi ser da at dataene fra denne disken kan trylles frem igjen ved å bruke paritetsdisken og reglene nevnt over: Hvis pariteten for de igjenværende diskene er den samme som den lagrede pariteten, har en null gått tapt. Hvis pariteten for de igjenværende diskene er forskjellig fra den lagrede pariteten, har en ener gått tapt. Prøv selv!