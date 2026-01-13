## 11.1 Windows PowerShell

Windows PowerShell er, som bash for Linux, både kommandolinje og scriptspråk for Windows og ble innført av Microsoft i 2006. Fra og med Windows 2008 Server og Windows 7 har PowerShell vært installert som default. Det finnes en rekke aliaser som gjør at man kommer veldig langt med å skrive vanlige bash kommandoer.

Det finnes fire kategorier kommandoer i PowerShell:

|   |   |
|---|---|
| Cmdlets | Tilsvarer bash shell builtins som pwd og echo (og er en del av shellet). De fleste kommandoer er Cmdlets. |
| Applications | Eksisterende Windowsprogrammer som ping og ipconfig. (tilsvarer /bin/mv) |
| Scripts | Tekstfiler med endelse .ps1 (også for PS versjon 2 og høyere), tilsvarer bash-script |
| Functions | Tilsvarer funksjoner i bash |

Operativsystemet Windows er i utgangspunktet objektorientert og konfigurasjonen er ikke basert på tekstfiler som i Linux, men på binære filer og databaser. Derfor må et kraftig Windows shell også være objektorientert og det er PowerShell. Som bash er PowerShell bygd opp av mange små programmer eller Cmdlets som gir en fleksibel måte å løse oppgaver på. Under Linux har vi sett at disse kommandoene kan settes sammen med pipes og omdirigering og det er da tekst som streames mellom kommandoene. PowerShell tar dette ett steg videre og sender hele objekter mellom Cmdlets med pipes.

---

## 11.1.1 Verdens korteste Hello World program

Hvis du har problemer med keyboard-tegn og norsk tastatur, kan du velge Settings Time & Language Region & Language norsk options og så legge til US keyboard. Så kan du switche mellom keyboard med Windows-tasten og space.

```
"Hello World!"
```

Lagrer man dette som en fil med for eksempel navnet `hello.ps1` har man laget verdens korteste Hello World program. PowerShell script må ha filendelse `ps1` . Det gjelder også for versjon 2 av PowerShell. Med tanke på script som lastes ned av virus og ormer er det i utgangspunktet ikke lov å kjøre script i det hele tatt fra PowerShell. Men hvis du setter

```
PS> set-executionPolicy remoteSigned
```

vil du kunne kjøre egne script. Men dette får du bare lov til å gjøre hvis du kjører PowerShell med "elevated privileges", det vil si som administrator. Det kan du få til ved å trykke Windows-tasten, skrive "PowerShell" og så høyreklikke og velge "Run as administrator".

Hvis PowerShell scriptet åpner et nytt vindu som umiddelbart forsvinner, slik at du ikke ser "Hello World!"-teksten, kan du finne noen mulige løsninger her: [powershell-window-disappears](https://stackoverflow.com/questions/1337229/powershell-window-disappears-before-i-can-read-the-error-message) .

---

## 11.2 To viktige kommandoer

De kanskje to viktigste kommandoene i powershell er de som gir deg hjelp: "Get-Command" gir liste over alle kommandoer og "Get-Help kommando" gir informasjon om kommandoene. Disse kan sammenliknes med "man" og "help" i bash.

```
Get-Command

CommandType     Name                                               Version    Source            
-----------     ----                                               -------    ------            
Alias           Add-ProvisionedAppxPackage                         3.0        Dism              
Alias           Apply-WindowsUnattend                              3.0        Dism              
Alias           Disable-PhysicalDiskIndication                     2.0.0.0    Storage           
Function        A:                                                                              
Function        Add-BCDataCacheExtension                           1.0.0.0    BranchCache       
Function        Add-BitLockerKeyProtector                          1.0.0.0    BitLocker         
Cmdlet          Read-Host                                          3.1.0.0    Microsoft.Power...
Cmdlet          Receive-DtcDiagnosticTransaction                   1.0.0.0    MsDtc             
...
```

Uten argument listes alle kommandoene

```
Get-Command ls

CommandType     Name                                               Version    Sourc
                                                                              e    
-----------     ----                                               -------    -----
Alias           ls -> Get-ChildItem                                                

CommandType     Name                            Definition
-----------     ----                            ----------
Alias           ls                              Get-ChildItem
```

Med kommando som argument listes informasjon om kommandoen.

```
Get-Help Get-ChildItem

NAME
    Get-ChildItem

SYNOPSIS
    Gets the items and child items in one or more specified locations.

SYNTAX
    Get-ChildItem [[-Path] <string[]>] [[-Filter] <string>] [-Exclude <string[]
...
```

For å få informasjon om alle kommandoer, må du først kjøre Update-Help som Administrator.

---

## 11.3 Likheter med bash

Det er definert en rekke alias som gjør at mange av de kjente bash-kommandoene kan brukes direkte i powershell. Dette gjør at en del bash-script lett kan oversettes. Her er noen av de vanligste, kommandoen `alias` gir alle som er definert:

```
set-alias cat        get-content
set-alias cd         set-location
set-alias cp         copy-item
set-alias history    get-history
set-alias kill       stop-process
set-alias ls         get-childitem
set-alias mv         move-item
set-alias ps         get-process
set-alias pwd        get-location
set-alias rm         remove-item
set-alias rmdir      remove-item
set-alias echo       write-output
```

I disse notatene er eksemplene hentet fra kjøring av PowerShell på en Windows-PC. Når dere gjør oppgaver, kan dere også kjøre eksemplene i pwsh-shellet på os-VMene. Men det er da viktig at man bruker de 'ekte' Cmdlet-ene som Get-Childitem og Get-Process og ikke ls og ps, fordi de sistnevnte da vil kjøre det underliggende Linux-kommandoene ls og ps og ikke PowerShell Cmdlet'ene. På eksamen i Inspera vil dere også kunne få tilgang til et slikt shell, så det er viktig å teste ut dette, selvom dere også bruker PowerShell i Windows.

---

## 11.3.1 Omdirigering

Omdirigering og pipes virker på samme måte som i bash. For eksempel er

```
PS> ls | sort > fil.txt
```

en gyldig powershell-kommando. Vanlig output og feilmeldinger er også delt på samme måte, slik at følgende virker som i bash:

|   |   |
|---|---|
| omdirigering | virkning |
| > fil.txt | omdirigerer stdout til fil.txt. Overskriver |
| >> fil.txt | legger stdout etter siste linje i fil.txt |
| Write-Error "oops" 2> $null | sender stderr til "/dev/null" |
| > fil.txt 2> err.txt | stdout -> fil.txt stderr -> err.txt |

Men som vi skal se senere er det ikke tekst som streames mellom Cmdlets, men hele objekter!

---

## 11.4 Variabler

Variabler lages som i PHP ved å sette et $-tegn foran navnet:

```
PS > $var = "min nye var"
PS > echo $var
min nye var
PS > $var
min nye var
```

Slike variabler er lokale. PowerShell er ikke så nøye på mellorom som bash, men teksstrenger må skrives innenfor apostrofer. Legg merke til at echo er overfløding, en tekststreng blir skrevet ut selvom du ikke skriver echo først.

Cmdlet'en Get-Variable (kan forkortes til gv) viser hvilke variabler som er definert, følgende viser et utdrag:

```
PS > Get-Variable

Name                           Value
----                           -----
MaximumErrorCount              256
MaximumVariableCount           4096
MaximumFunctionCount           4096
MaximumAliasCount              4096
null
false                          False
true                           True
PWD                            C:\Documents and Settings\group10\My Documents\ps
MaximumHistoryCount            4000
HOME                           C:\Documents and Settings\group10
PSVersionTable                 {CLRVersion, BuildVersion, PSVersion, PSCompatible...
PID                            3976
Culture                        nb-NO
ShellId                        Microsoft.PowerShell
PSHOME                         C:\WINDOWS\system32\WindowsPowerShell\v1.0\
ErrorView                      NormalView
NestedPromptLevel              0
OutputEncoding                 System.Text.ASCIIEncoding
CommandLineParameters          {}
args                           {}
PROFILE                        C:\Documents and Settings\group10\My Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1
var                            min nye var
dir                            mappe
```

---

## 11.5 Environmentvariabler

I tillegg finnes det et sett med environmentvariabler i namespace'et env: som kan listes ut med ls:

```
PS > ls env:
Name                           Value
----                           -----
Path                           C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32...
TEMP                           C:\DOCUME~1\group10\LOCALS~1\Temp
PATHEXT                        .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;....
USERDOMAIN                     IU-VM
PROCESSOR_ARCHITECTURE         x86
SystemDrive                    C:
APPDATA                        C:\Documents and Settings\group10\Application Data
windir                         C:\WINDOWS
TMP                            C:\DOCUME~1\group10\LOCALS~1\Temp
USERPROFILE                    C:\Documents and Settings\group10
ProgramFiles                   C:\Program Files
HOMEPATH                       \Documents and Settings\group10
COMPUTERNAME                   IU-VM
USERNAME                       group10
NUMBER_OF_PROCESSORS           1
PROCESSOR_IDENTIFIER           x86 Family 16 Model 4 Stepping 2, AuthenticAMD
SystemRoot                     C:\WINDOWS
ComSpec                        C:\WINDOWS\system32\cmd.exe
LOGONSERVER                    \\IU-VM
ALLUSERSPROFILE                C:\Documents and Settings\All Users
OS                             Windows_NT
HOMEDRIVE                      C:
```

Dette betyr at det for eksempel finnes en variabel $env:path

```
PS > $env:path
C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\system32\WindowsP
owerShell\v1.0\;C:\Program Files\OpenSSH\bin;C:\lcc\bin
```

Legg merket til at variabler og cmdlets ikke er case-sensitive som de er i bash. Tilsvarende kan man liste funksjoner og aliaser med `ls function:` og `ls alias:`

```
PS > $alias:pwd
Microsoft.PowerShell.Management\Get-Location
PS > & $alias:pwd

Path
----
C:\Documents and Settings\group10\My Documents\ps
```

Her ser vi at en & i starten av en linje gjør at innholdet av en streng kjøres. Nyttig om man må ha apostrofer rundt en path fordi den inneholder mellomrom.

---

## 11.6 Apostrofer

Apostrofer virker stort sett som i bash:

```
PS> $dir="mappe"

PS>  echo 'ls $dir'     #    ' -> Gir eksakt tekststreng
ls $dir

PS>  echo "ls $dir"     #    " -> Variabler substitueres; verdien av $dir skrives ut.
ls mappe

PS> echo "Filer: $(ls $dir)"        #  utfører kommandoen \verb+ls mappe+ inne i strengen
fil fil2.txt
```

---

## 11.7 Objekter og Get-Member

Det som virkelig gir ”Power” i PowerShell er at hele objekter sendes mellom Cmdlets. Dette gjør det veldig intuitivt og enkelt å trekke ut informasjon fra for eksempel lister av prosesser og filer. Og det geniale er at det kan gjøres på mer eller mindre samme måte uansett hvilke objekter vi ser på, objektene har bare litt andre egenskaper og metoder.

For eksempel returnerer en listing av filene i en mappe

```
PS > ls
Mode                LastWriteTime     Length Name
----                -------------     ------ ----
d----        02.03.2010     20:38            mappe
-a---        01.03.2010     12:26         73 ps.ps1
```

ikke bare tekst som viser filene i mappen slik som i bash. Egentlig returneres et array av objekter, ett for hver fil eller mappe. Om man ønsker kun et objekt for filen `ps.ps1` , kan man slik legge det i variabelen `$fil` :

```
PS > $fil = ls ps.ps1
```

Hvis man på kommandolinjen nå skriver `$fil.` kan man tabbe seg gjennom alle metoder og properties for dette objektet. En måte å vise alle på en gang, er å sende objektet til cmdlet'en `Get-Member` :

```
PS > $fil | Get-Member

   TypeName: System.IO.FileInfo

Name                      MemberType     Definition
----                      ----------     ----------
Mode                   CodeProperty System.String Mode{get=Mode;}
AppendText         Method          System.IO.StreamWriter AppendText()
Delete                  Method          System.Void Delete()
PSPath                NoteProperty System.String PSPath=Microsoft.PowerShel...
CreationTime       Property        System.DateTime CreationTime {get;set;}
DirectoryNam      Property        System.String DirectoryName {get;}
Extension             Property        System.String Extension {get;}
FullNa                 Property         System.String FullName {get;}
IsReadOnly          Property         System.Boolean IsReadOnly {get;set;}
LastAccessTime  Property         System.DateTime LastAccessTime {get;set;}
LastWriteTime    Property         System.DateTime LastWriteTime {get;set;}
Length                 Property         System.Int64 Length {get;}
Name                   Propertty        System.String Name {get;}
```

Bare et lite utvalg er vist over. Dermed kan man for eksempel få tak i tidspunktet filen sist ble aksessert, lest eller sett på:

```
PS > $fil.LastAccessTime
1. mars 2010 12:26:50
```

Dette tidspunktet er også et objekt, et System.DateTime objekt. På samme måte kan dette objektet tilordnes en variabel

```
PS > $date = $fil.LastAccessTime
```

Og denne kan vi lese ut metoder og egenskaper fra med `Get-Member` :

```
PS > $date | Get-Member
   TypeName: System.DateTime

Name                 MemberType     Definition
----                 ----------     ----------
AddHours             Method         System.DateTime AddHours(Double value)
IsDaylightSavingTime Method         System.Boolean IsDaylightSavingTime()
ToLongDateString     Method         System.String ToLongDateString()
ToLongTimeString     Method         System.String ToLongTimeString()
DayOfWeek            Property       System.DayOfWeek DayOfWeek {get;}
DayOfYear            Property       System.Int32 DayOfYear {get;}
Hour                 Property       System.Int32 Hour {get;}
Millisecond          Property       System.Int32 Millisecond {get;}
Minute               Property       System.Int32 Minute {get;}
Month                Property       System.Int32 Month {get;}
Second               Property       System.Int32 Second {get;}
TimeOfDay            Property       System.TimeSpan TimeOfDay {get;}
Year                 Property       System.Int32 Year {get;}
```

Igjen er bare et lite utvalg vist. Dermed kan man trekke ut disse egenskapene, for eksempel året:

```
PS > $date.year
2010
```

Det er også mulig å gjøre dette direkte uten å gå veien om et dato-objekt:

```
PS > $fil.LastAccessTime.year
2010
```

Man kan til og med trekke det ut direkte fra kommandoen som listet filen:

```
PS > (ls ps.ps1).LastAccessTime.year
2010
```

---

## 11.8 Undersøke typen til et objekt

Med get-member vil vi få listet opp alle egenskaper (properties) og metoder som er tilgjengelige på det aktuelle objektet. Dette er viktig informasjon, fordi det forteller oss hva vi kan gjøre med objektene.

```
PS C:\> ls | get-member

   TypeName: System.IO.FileInfo

Name                      MemberType     Definition
----                      ----------     ----------
...
Length                    Property       System.Int64 Length {get;}
Name                      Property       System.String Name {get;}
...
```

Øverst ser vi at typen til det som returneres fra ls er `System.IO.FileInfo` . Men vi ser bare typen til det siste elementet på denne måten. Kommandoen ls returnerer altså et array av FileInfo-objekter. Dette kan vi se ved å kalle metoden `GetType()` på returverdien slik:

```
PS C:\> (ls).getType()

IsPublic IsSerial Name                                     BaseType
-------- -------- ----                                     --------
True     True     Object[]                                 System.Array
```

For mer informasjon om de ulike typene, kan man søke dem opp på Microsofts dokumentasjonssider, https://msdn.microsoft.com/. Søker man for eksempel etter `System.Array` får man som første treff `Array Class` . Her finner du definisjonen av klassen og kodeeksempler i flere språk.

Om man kaller metoden getType for ett av elementene får man vite hva slags type dette er:

```
PS C:\> (ls)[1].getType()

IsPublic IsSerial Name                                     BaseType
-------- -------- ----                                     --------
True     True     FileInfo                                 System.IO.FileSystemInfo
```

---

## 11.9 ps

Når man istedet for å liste filer med ls lister prosesser med ps, gir dette også objekter.

```
PS > ps
Handles  NPM(K)    PM(K)      WS(K) VM(M)   CPU(s)     Id ProcessName
-------  ------    -----      ----- -----   ------     -- -----------
    194          6         3276           6012      49         1,20        4936  Adobe_Updater
    102          5         1156            360      32          0,28       1264   alg
    320          5         1528            908      22         1,28        696     csrss
```

Det som returneres fra ps er et array av prosessobjekter der første element er første prosess i listingen:

```
PS > $ps = ps
PS > $ps[0].name
Adobe_Updater
PS > $ps[0].id
4936
PS > $ps[1].name
alg
```

Lengden av dette arrayet vil da gi antall prosesser på maskinen:

```
PS > $ps.length
44
```

---

## 11.10 Foreach

Det er først når man bruker mulighetene objektorienteringen gir i script at PowerShell virkelig viser sin styrke:
```
foreach ($ls in ls *.ps1){
    $sum += $ls.length
}
$sum
```

eller i onelinere som dette:

```
ls | ForEach-Object {$sum += $_.Length}
```

Disse mulighetene vil bli utdypet i senere avsnitt.

---

## 11.11 Installasjon av programmer fra PowerShell

På samme måte som man installerer programmer i et Linux shell med apt-get, kan man installere programmer i PowerShell med Chocolatey; eller bare choco som kommandoen heter. Da må man først installere choco og det kan i PowerShell gjøres med:
```
wget -OutFile install.ps1 http://chocolatey.org/install.ps1
```

hvor `wget` er et alias for `Invoke-WebRequest` og virker på omtrent samme måte som i Linux. Etter å ha kjørt dette installasjons-scriptet, kan man installere annen programvare som ssh og scp med:

```
PS C:\> choco install openssh
```

og deretter bruke det fra PowerShell på samme måte som man bruker det fra bash i Linux.

---

## 11.12 Select-String, PowerShells svar på grep

For å gå igjennom et array av objekter, som for eksemple alle prosessene som listes med ps, er foreach en meget nyttig konstruksjon. Allikevel er det viktig å sjekke hva mer man kan gjøre med kommandoen ps, før man overkompliserer oppgaven. I bash bruker vi kommandoen

```
$ ps | grep power
```

for å finne alle prosesser med "power" i navnet. Vi har en funksjon i powershell som likner på grep, nemlig `select-string` eller kortversjonen `sls` . Men kommandoen `ps | select-string power` returnerer ikke helt det vi ønsker. Grunnen til dette er at kommandoen `ps` , i PowerShell, returnerer et array av objekter, og ikke en tekst. For å gjøre tilsvarende søk i PowerShell skriver man heller følgenede:

```
$ ps power*

Handles  NPM(K)    PM(K)      WS(K) VM(M)   CPU(s)     Id ProcessName
-------  ------    -----      ----- -----   ------     -- -----------
     48       2      764       2696    28     0,05   2752 poweroff
    257       5    28968      28196   135     0,47   5412 powershell
```

Her sender vi ordet power, med wildcardet *, til kommandoen ps, som er et alias for kommandoen get-process. Sjekk dette ved å skrive `get-command ps` . For detaljert informasjon om hva du kan gjøre med get-process, skriv `get-help get-process -detailed`

Fra Linux er vi vant til å velge ut linjer som inneholder et gitt ord med kommandoen `grep` . Det finnes ikke en helt tilsvarende PowerShell-kommando og ofte bruker man andre metoder for å oppnå det samme. Men det er mulig å bruke CmdLet'en `Select-String` som ligner:

```
ls | Select-String fil
```

er et forsøk på å velge alle linjer som inneholder ordet `fil` i ls-listingen. Men Select-String virker på objekter og går derfor inn i mapper i listingen og det virker ikke helt som ønsket. Ved å pipe output fra ls til Out-String gjøres objekt-strømmen om til vanlige strenger og man får det til å virke som i bash:

```
ls | Out-String -Stream | Select-String fil
```

Man må også ha med opsjonen `-Stream` til `Out-String` for at det skal virke.

---

## 11.13 Logiske operatorer

|   |   |
|---|---|
| Operator | Betydning |
| -lt | Less than |
| -gt | Greater than |
| -le | Less than or equal to |
| -ge | Greater than or equal to |
| -eq | Equal to |
| -ne | Not equal to |

|   |   |
|---|---|
| Operator | Betydning |
| -not | Not |
| ! | Not |
| -and | And |
| -or | Or |

Merk at i powershell kan vi bruke logiske operatorer rett i shellet. I bash vil `2 -lt 3` ikke returnere noen ting, fordi det er exit-verdien av denne kommandoen som indikerer om testen slo til eller ikke. I powershell er dette litt enklere:

```
PS > 2 -eq 3
False
PS > 2 -lt 3
True
PS > "hei" -eq "hei"
True
PS > -not ("hei" -eq "heia")
True
```

---

## 11.14 Windows script editor

En mulighet er å bruke Windows PowerShell ISE til å skrive PowerShell script. Da kan man få opp ett PowerShell vindu samtidig med et editor-vindu og kjøre scriptet ved å taste F5. Det finnes også mange generelle tekst-editorer for Windows som stort sett er GUI-baserte.

En annen mulighet er å installere `nano` med `choco install nano` og deretter bruke `nano` fra kommandolinjen slik som i et Linux shell.

---

## 11.15 Summere antall bytes i filer

Output fra PowerShell CmdLets er som vi har sett ikke bare tekst som i et bash-shell, men objekter. Dermed kan man ved hjelp av `foreach` gå igjennom alle objektene og trekke ut den informasjon man trenger:

```
foreach ($ls in ls *.ps1){
    $sum += $ls.length
}
$sum
```

Foreach er et alias for ForEach-Object, men når det står i starten av en setning, er det et PowerShell statement eller reservert ord, slik som if og for. Summasjon som inkluderer filer i alle undermapper får man med opsjonen -r til ls:

```
foreach ($ls in ls -r){
    if($ls.Extension -eq ".ps1"){
	$sum += $ls.length
    }
}
```

Egentlig er `ls -r` et alias for `Get-ChildItem -Recurse` .

---

## 11.16 Stoppe prosesser med et gitt navn: nkill.ps1

En stor fordel med at kommandoene gir objekter er at man kan bruke de samme metodene på mange forskjellige typer kommandoer, for eksempel på `ps` som er et alias for `Get-Process` :

```
$s = $args[0] # Første argument

foreach ($p in ps ){
   foreach ($name in $args){
      if ($p.name -eq $name){
         kill -whatif $p.id
      }
   }
}
```

Opsjonen `-whatif` til `kill` er nyttig for å teste ut hva som kommer til å skje hvis man kjører scriptet. Når scriptet virker som det skal, kan man fjerne `-whatif` . En tilsvarende oneliner kan lages slik:

```
ps | foreach {	if($_.name -eq "navn"){kill $_.id -whatif}}
```

---

## 11.17 PowerShell oneliner

Ofte kan man lage tilsvarende kraftige konstruksjoner med bare en enkelt kommandolinje, såkalte oneliners. For å gjøre det bruker man konstruksjoner som `ForEach-Object` og `Where-Object` og lage en indre løkke hvor hvert objekt behandles. Inne i en slik løkke vil den spesielle variabelen `$_` være en peker til objektet som er under behandling. Hele scriptet ovenfor kan lages som en oneliner slik:

```
ls | ForEach-Object {$sum += $_.Length}
```

Men man må på kommandolinjen passe på at variabelen nullstilles og hvis man i tillegg ønsker å skrive ut svaret kan man akkurat som i bash adskille kommandoer med semikolon:

```
$sum = 0; ls | ForEach-Object {$sum += $_.Length };$sum
```

Med Where-Object kan man velge ut objekter med spesielle egenskaper. For eksempel kan man plukke ut mapper fra en listing av filer og mapper på følgende måte:

```
ls | Where-Object  {$_.PSIsCointainer}
```

for `PSIsCointainer` er en TRUE/FALSE property som bare er sann for mapper. Where-Object kan kombineres med forEach-Object:

```
$sum = 0; ls | Where-Object  {$_.extension -eq ".txt"} | ForEach-Object {$sum += $_.Length };$sum
```

som legger sammen Length kun for filer med extension .txt.

---

## 11.18 Sort-Object og Select-Object

Med disse to CmdLets kan man sortere og velge ut objekter. For eksempel vil følgende oneliner sortere filer etter lengde, med de største først (descending) og deretter plukke ut de fire første:

```
ls | Sort-Object Length -des | Select-Object -First 4
```

---

## 11.19 DateTime

`DateTime` er en CmdLet som uten argumenter gir et objekt som inneholder dato og klokkeslett (DateTime) akkurat nå:

```
PS C:\> Get-Date
søndag 19. mars 2017 19.41.59
```

Man kan også lage DateTime objekter for et vilkårlig tidspunkt:

```
PS C:\> Get-Date -Year 2016 -Month 5 -Day 17  -Hour 17 -Minute 30 -Second 00
tirsdag 17. mai 2016 17.30.00

PS C:\> Get-Date "17/5 2007 17:30"
torsdag 17. mai 2007 17.30.00

PS C:\> Get-Date "17 May 2007 17:30"
torsdag 17. mai 2007 17.30.00
```

Med utgangspunkt i en variabel som inneholder et DateTime-objekt, kan man med `Get-Member` finne egenskaper og metoder objektet har og for eksempel bruke det til å lage en ny variabel ett døgn tilbake i tid.

```
PS C:\> $now = Get-Date
PS C:\> $now

søndag 19. mars 2017 19.44.26

PS C:\> $now | Get-Member

   TypeName: System.DateTime

Name                 MemberType     Definition
----                 ----------     ----------
Add                  Method         datetime Add(timespan value)
AddDays              Method         datetime AddDays(double value)
AddHours             Method         datetime AddHours(double value)

PS C:\> $yesterday = $now.AddDays(-1)
PS C:\> $yesterday

lørdag 18. mars 2017 19.44.26
```

Anta at du husker at du har laget eller endret noen filer på mandag 13 mars, men ikke husker hvor de ligger. Da kan man først lage et par DateTime variabler tidlig på dagen og sent på kvelden:

```
PS C:\> $mm = Get-Date "13/3 2017 08:00" # Mandag morgen
PS C:\> $mk = Get-Date "13/3 2017 22:00" # Mandag kveld
PS C:\> $mm.DayOfWeek
Monday
```

Den siste kommandoen dobbeltsjekker at den 13 var en mandag. Deretter kan man lage en oneliner som lister alle filer som har `LastWriteTime` i dette tidsrommet:

```
PS C:\Users\haugerud> ls -r | Where-Object {$_.LastWriteTime -gt $mm -and $_.LastWriteTime -lt $mk}

    Directory: C:\Users\haugerud

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
d-----       13.03.2017     17.05                .ssh
d-----       13.03.2017     18.28                mappe
-a----       13.03.2017     19.00              0 file6.txt
-a----       13.03.2017     10.38          13074 history13.03.2017

    Directory: C:\Users\haugerud\.ssh

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       13.03.2017     17.05            189 known_hosts

    Directory: C:\Users\haugerud\mappe

Mode                LastWriteTime         Length Name
----                -------------         ------ ----
-a----       13.03.2017     09.05            146 hello.ps1
-a----       13.03.2017     18.36             64 loop.ps1
-a----       13.03.2017     18.25            307 nkill.ps1
```

Hvis man sender output til `Format-Table` blir det litt ryddigere og man kan velge hvilke felt man ønsker å ha med:

```
ls -r | Where-Object {$_.LastWriteTime -gt $mm -and $_.LastWriteTime -lt $mk} | Format-Table LastWriteTime,fullName

LastWriteTime       FullName
-------------       --------
13.03.2017 17.05.18 C:\Users\haugerud\.ssh
13.03.2017 18.28.23 C:\Users\haugerud\mappe
13.03.2017 19.00.45 C:\Users\haugerud\file6.txt
13.03.2017 10.38.02 C:\Users\haugerud\history13.03.2017
13.03.2017 17.05.18 C:\Users\haugerud\.ssh\known_hosts
13.03.2017 09.05.03 C:\Users\haugerud\mappe\hello.ps1
13.03.2017 18.36.16 C:\Users\haugerud\mappe\loop.ps1
13.03.2017 18.25.18 C:\Users\haugerud\mappe\nkill.ps1
```

Hvis man ønsker en sortert liste på tidspunktet, må man sende objektene til sort (alias for Sort-Objekt) før man sender det til Format-Table:

```
ls -r | Where-Object {$_.LastWriteTime -gt $mm -and $_.LastWriteTime -lt $mk} | sort LastWriteTime | Format-Table LastWriteTime,fullName

LastWriteTime       FullName
-------------       --------
13.03.2017 09.05.03 C:\Users\haugerud\mappe\hello.ps1
13.03.2017 10.38.02 C:\Users\haugerud\history13.03.2017
13.03.2017 17.05.18 C:\Users\haugerud\.ssh
13.03.2017 17.05.18 C:\Users\haugerud\.ssh\known_hosts
13.03.2017 18.25.18 C:\Users\haugerud\mappe\nkill.ps1
13.03.2017 18.28.23 C:\Users\haugerud\mappe
13.03.2017 18.36.16 C:\Users\haugerud\mappe\loop.ps1
13.03.2017 19.00.45 C:\Users\haugerud\file6.txt
```