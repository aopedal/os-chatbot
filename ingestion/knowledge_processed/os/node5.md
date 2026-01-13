## 4.2 Simulerings-CPU og RAM

I maskinkoden som summerer opp summen S = 1 + 2 + 3 ved hjelp av en løkke som er mulig å få til på grunn av branch-kontrollen, foregår alle beregninger inne i CPU-en. Det vil si at alle tallene først legges inn i registerne og at alle resultatene fra mellomregninger før man kommer frem til den endelige summen ligger i registerne lokalt i CPU. Slik er det for virkelige CPU-er laget av Intel og AMD også. Registerne er meget hurtige, men det er et begreneset antall man kan ha inne i en CPU. En alternativ lagringsplass for beregningsdata er internminne eller RAM. Her er det plass til Milliarder av bytes (8 bit) med data, men det tar omtrent ti ganger så lang tid å lagre noe i RAM. Det optimale er derfor å alltid bruke registre for å lagre midlertidige data, slik som den stadig økende summen i eksempelet vi ser på. Men hvordan høynivåkoden oversettes til maskinkode avgjøres av kompilatoren. Dette er et program som systematisk kan oversette alle mulige varianter av høynivåkode til maskinkode som utfører det som høynivåkoden ber om når det kompilerte programmet kjøres i en datamaskin. Detaljer som om beregningsdata skal lagres i registere eller i RAM, avgjøres av kompilatoren. Men som vi skal se senere er det mulig å be kompilatoren om å lage maskinkode som skal gå hurtigst mulig. Og hvis man gjør det når man kompilerer vil kompilatoren lage kode som lagrer alle mellomregninger i registerne og først skriver resultatene til variabler i RAM når beregningene er fullført.

Når man deklarerer variabler som for eksempel i et C-program på følgende måte

```
int sum=0;
int i;
```

vil det settes av 4 byte i RAM til denne variabelen og der initialiseres den til å ha verdien 0. RAM er ganske enkelt et enormt array av bytes som ligger etterhverandre. Den minste lagerenheten er en byte som består av 8 bit. At en integer skal være 32 bit er en konvensjon for programmeringsspråket C, men disse konvensjonene kan variere mellom forskjellige språk og også mellom forskjellige implementasjoner av C. Andre konvensjoner er at en long long int bruker 8 byte og at flytt-tall lagringsenhetene float og double er henholdsvis 32 og 64 bit lange.

---

## 4.3 C-programmering

Siden Dennis Ritchie på starten av 70-tallet laget programmeringsspråket C, har det vært tett knyttet til Unix-operativsystemer. De fleste Unix-programmer er skrevet i C og de fleste systemkall har korresponderende C-funksjoner med samme navn. Vi skal her bruke C-program som eksempler på høynivåkode og se hvordan de må kompileres til maskinkode for å kunne kjøres av en datamaskin.

---

## 4.3.1 hello.c

Et `Hello World` C-program ser slik ut:

```
/* filnavn: hello.c */

#include <stdio.h>

int main()
{
   printf("Hello world!\n");
}
```

Den første linjen inkluderer standard-biblioteket `stdio.h` som blant annet inneholder funksjoner for å kunne skrive til et terminal-vindu. Alle C-program har en main-funksjon. Den kan inneholde all koden eller inneholde kall til andre funksjoner. For å kunne kjøre et C-program, må det først kompileres til maskinkode og det kan man i et Linux-shell gjøre slik:

```
$ gcc hello.c
```

Det lages da maskinkode som lagres i en fil ved navn `a.out` . Den kan kjøres med

```
$ ./a.out
Hello world!
```

Filen `a.out` inneholder maskinkode i form av maskin-instruksjoner for en prosessor med såkalt x86-arkitektur som ble introdusert av Intel i 1978. Det finnes mange forskjellige CPU-arkitekturer, som ARM, SPARC og PowerPC, men x86 er den som nå brukes i nesten alle PCer og servere. Andre arkitekturer har andre maskin-instruksjoner og de kan derfor ikke kjøre maskinkode for x86, slik som innholdet i `a.out` . Maskinkode for Hello World er på mange tusen byte og den inneholder blant annet kode for å kommunisere med operativsystemet. Dette er nødvendig for eksempel for å kunne skrive ut noe. Man kan se på direkte på koden og følgende er deler av innholdet:

```
$ xxd a.out 
00000000: 7f45 4c46 0201 0100 0000 0000 0000 0000  .ELF............
00000010: 0200 3e00 0100 0000 3004 4000 0000 0000  ..>.....0.@.....
00000020: 4000 0000 0000 0000 d819 0000 0000 0000  @...............
00000030: 0000 0000 4000 3800 0900 4000 1f00 1c00  ....@.8...@.....

00000230: 0100 0000 0000 0000 2f6c 6962 3634 2f6c  ......../lib64/l
00000240: 642d 6c69 6e75 782d 7838 362d 3634 2e73  d-linux-x86-64.s
00000250: 6f2e 3200 0400 0000 1000 0000 0100 0000  o.2.............
00000260: 474e 5500 0000 0000 0200 0000 0600 0000  GNU.............

000005b0: f3c3 0000 4883 ec08 4883 c408 c300 0000  ....H...H.......
000005c0: 0100 0200 4865 6c6c 6f20 776f 726c 6421  ....Hello world!
000005d0: 0000 0000 011b 033b 3000 0000 0500 0000  .......;0.......
```

Deler av programmet inneholder data, som strengen `Hello world!` og andre deler inneholder maskin-instruksjoner. Disse tilsvarer på alle måter maskin-instruksjonene i den simulerte maskinen vi har sett på. Den hadde kun 8-bits instruksjoner, x86-instruksjoner er av variabel lengde mellom 8 og 48 bit. Etterhvert skal vi se på Assembly-kode og der korresponderer hver x86 assembly-instruksjon som ADD, MOV, CMP, JNE osv. til en bestem maskin-instruksjon. Dette er også helt tilsvarende som i CPU-simuleringen.

---

## 4.3.2 Et C-program som summerer

Tidligere oversatte vi høynivåkode, en for-løkke med summering, til maskinkode for den simulerte CPUen. Den prosessen vi da gjennomførte, er det samme som gcc-kompilatoren gjorde for C-programmet over. Følgende er et C-program vi kaller `sum.c` som utfører den samme beregningen. Vi kunne skrevet all koden i main-funksjonen, men lager en egen funksjon som vi kaller `sum()` for enklere å kunne analysere hva som skjer i denne spesielle kode-biten:

```
/* filnavn: sum.c */

#include <stdio.h>

int sum()
{
   int S=0,i;
   for(i=0;i<4;i++)
   {
      S = S + i;
   }
   return(S);
}

int main()
{
   int Sum;
   Sum = sum();
   printf("Sum = %d \n",Sum);
}
```

Variabler må deklareres i C. Hvis man ikke definerer funksjonen før main(), kan man få en warning fra gcc. Man kan kompilere og kjøre programmet med

```
$ gcc sum.c -o sum
$ ./sum
Sum = 6
```

Opsjonen `-o` brukes til å gi det kjørbare programmet et annet navn enn default verdi `a.out` .

---

## 4.3.3 Kompilering av C-funksjoner

Når programmet over kompileres, lages det først maskinkode av C-koden i `sum.c` og så linkes denne koden sammen med kode fra standard-biblioteket `stdio.h` til ferdig maskinkode som er klar til å lastes inn i RAM og kjøres. Det er også mulig å legge en C-funksjon i en egen fil og så kompilere den til en egen maskinkode-fil. Hvis vi kaller følgende fil `sumFunksjon.c`

```
/* filnavn: sumFunksjon.c */

int sum()
{
   int S=0,i;
   for(i=0;i<4;i++)
   {
      S = S + i;
   }
   return(S);
}
```

kan vi kompilere den med

```
$ gcc -c sumFunksjon.c -o funksjon
```

Opsjonen `-c` gir kompilatoren `gcc` beskjed om å ikke linke programmet, men bare kompilere det og legge maskinkoden i filen `funksjon` . Deretter kan vi lage en fil til som vi kan kalle `sumMain.c`

```
/* filnavn: sumMain.c */

#include <stdio.h>

extern int sum();

int main(void)
{
   int summ;
   summ = sum();
   printf("Sum = %d \n",summ);
   
}
```

så kan vi kompilere den med

```
$ gcc -c sumMain.c -o main
```

og lage en maskinkode-fil med navn `main` . Til slutt kan vi skjøte sammen og be kompilatoren om å linke disse to filene sammen til et kjørbart sum-program og kjøre det:

```
$ gcc funksjon main -o sum
$ ./sum
Sum = 6
```

Vi kunne gjort disse tre operasjonene, kompilering av de to programmen og linking, i en operasjon med

```
$ gcc sumFunksjon.c sumMain.c -o sum
```

men vi velger å gjøre det slik for å kunne erstatte beregningene i `funksjon` med Assembly-kode. Maskinkoden i `funksjon` tilsvarer den maskinkoden vi la inn i CPU-simuleringen, dermed kan vi i detalj sammenligne x86-Assembly med vårt eget assembly-språk for den simulerte CPUen.

---

## 4.4 Assembly

[Kompendiet i INF2270 datamaskinarkitektur på UiO](https://www.uio.no/studier/emner/matnat/ifi/INF2270/v16/pensumliste/kompendium-inf2270.pdf) inneholder nyttig informasjon, blan annet alle X86 instruksjonene. Forelesningsnotatene til Erik Hjelmås, OS-kompendium2018.pdf, som ligger under filer i Canvas, inneholder noen avsnitt om Assembly.

Det finnes mange andre gode kilder på nettet, blant annet denne [introduksjonen til Assembly.](https://www.cs.oberlin.edu/~bob/cs331/Notes%20on%20x86-64%20Assembly%20Language.pdf)

Vi skal ikke gå veldig dypt inn i x86-assembly, men ved hjelp av noen få av de tilgjengelige Assembly-instruksjonene skrive kode som tilsvarer noen enkel eksempler på høynivåkode.

Idag trenger vi bare å kjenne noen få assembly-instruksjoner som ligner på dem vi lagde for simulerings-CPU-en:

| Instruksjon | source | destination | resultat |
|-----------|------|-----------|--------|
| mov | s | d | verdien av s legges i d |
| add | s | d | d = d + s |
| cmp | s | d | sammenlign (compare) s og d |
| jne | label |  | Jump Not Equal, hvis s ulik d i forrige linje, hopp til label |

Her kan s være en konstant (et tall skrevet som $34 for tallet 34), et register ( `%rax, %rbx, %rcx, %rdx` ) eller en referanse til et sted i RAM. Det siste kan være definert som et variabelnavn eller på formen `-4(%rbp)` , som betyr fire byte fra starten av stack for programmet. Stack er et område i RAM der variabler for metoder lagres og rbp står for Register Base Pointer og peker på starten av stacken.

---

## 4.4.1 Summerings-funksjonen skrevet i Assembly

Følgende x86-Assembly kode utfører nøyaktig det samme som maskinkoden i filen `funksjon` i avsnittet over. Assemblerkode ligger svært tett opp til den maskinkoden som kjører i CPU-en man programmerer for og koden kan kun kjøre på CPUer som har nøyaktig den arkitekturen og dermed de maskininstruksjonene som koden inneholder. Nesten alle data som instruksjonene i maskinkode virker på er lagret i selve CPU-en og lagringsenhetene for disse dataene er registre. I vår simulerte CPU kalte vi registrene R0, R1, R2 og R3. I x86-arkitekturen finnes det fire generelle registre som er svært mye brukt i all Assembly-programmering og de kalles ax, bx, cx og dx. Opprinnelig ble disse betegnelsene brukt om 16-bits registre på den tiden dette var den vanlige størrelsen for en x86-CPU. Ganske snart økte størrelsen til 32-bit og disse registrene ble da betegnet eax, ebx, etc. En moderne 64-bits prosessor har 64-bits registre og de kalles rax, rbx, rcx og rdx og det er disse vi bruker i koden nedenfor. Når denne koden assembles til maskinkode, vil maskinkoden utføre den samme beregningen som maskinkoden i filen `funksjon` i forrige avsnitt som regner ut summen S.

Følgende kode utgjør Assembly-programmet `as.s` :

```
# filnavn: as.s

.globl sum 
# C-signatur:int sum ()

# 64 bit assembly

# b = byte (8 bit)
# w = word (16 bit, 2 bytes)
# l = long (32 bit, 4 bytes)
# q = quad (64 bit, 8 bytes)

# Opprinnelige 16bits registre: ax, bx, cx, dx
# ah, al 8 bit
# ax 16 bit
# eax 32 bit
# rax 64 bit

sum:                 # Standard

mov   $3, %rcx       # 3 -> rcx, maks i løkke
mov   $1, %rdx       # 1 -> rdx, tallet i økes med for hver runde
mov   $0, %rbx       # 0 -> rbx, variabelen i lagres i rbx
mov   $0, %rax       # 0 -> rax, summen = S 

# løkke
start: # label
add  %rdx, %rbx # rbx = rbx + rdx (i++) 
add  %rbx, %rax # rax = rax + rbx (S = S + i)
cmp  %rcx, %rbx # compare, er i = 3?
jne  start      # Jump Not Equal til start:

ret  # Verdien i rax returneres
```

Assembly-programmet `as.s` utfører nøyaktig det samme som C-programmet `sumFunksjon.c` listet øverst i avsnitt 4.3.3 .

Om vi sammenligner med summerings-koden for den simulerte CPU-en i avsnitt 3.7, vil man se at de åtte Assembly-linjene etter `sum:` tilsvarer linje for linje koden der (om man ser bort ifra linjen som inneholder `start:` . Registeret `%rcx` tilsvarer R0, `%rdx` tilsvarer R1, `%rbx` tilsvarer R2 og `%rax` tilsvarer R3. Vi har skrevet programmet slik at summen S lagres i nettopp registeret `%rax` fordi verdien som ligger i nettopp `%rax` er den verdien som returneres til main-funksjonen som utfører kallet på funksjonen `sum()` .

For å kunne kjøre funksjonen vi har skrevet i Assembly-programmet `as.s` må man be gcc-kompilatoren om å assemble den. Det kan man gjøre slik:

```
$ gcc -c as.s -o as
```

Dette gjør at gcc oversetter Assembly-koden til maskinkode og lagrer denne maskinkoden i filen `as` . Prosessen med å assemble Assembly-kode til maskinkode er mye enklere enn kompilering fordi det er en ganske enkel oversettelse som stort sett skjer linje for linje. For eksempel vil en linje som inneholder instruksjonen ADD ganske enkelt oversettes til oppcode som inneholder hvilket nummer instruksjonen ADD har i x86-arkitekturen etterfulgt av rett rekkefølge på registrene som er involvert. Helt på samme måte som vi gjorde med koden for den simulerte CPUen.

Til slutt kan man så linke maskinkoden i filen `as` sammen med main-maskinkoden for å få et kjørbart program:

```
$ gcc main as -o sum
$ ./sum
Sum = 6
```

på samme måte som med C-programmene, kunne man også gjort disse tre operasjonene, kompilering av main, assembly av `as.s` og linking av de to, i en operasjon:

```
$ gcc sumMain.c as.s -o sum
$ ./sum
Sum = 6
```

Man kunne også skrive hele hovedprogrammet i Assembly, men for å forenkle kodingen, har vi konsentrert oss om kun den koden som utføres av sum-funksjonen.

Et viktig poeng er at maskinkoden `as` laget fra Assembly funksjonelt sett utfører den samme beregningen som maskinkoden `funksjon` som kompilatoren lagde. Men det finnes mange mulige varianter av både Assembly-kode og maskinkode som utfører nøyaktig det som høynivåkoden sier skal gjøres. Men hva som er den optimale maskinkoden som både er raskest og tar minst plass, er langt fra opplagt. Veldig mye forsking og utvikling er blitt brukt på å lage kompilatorer som genererer best mulig maskinkode. Likevel kan gode Assembly-programmerer i noen tilfeller lage enda bedre kode enn en kompilator, spesielt om de har innsikt i nøyaktig hva som er hensikten med programmet.

---

## 4.5 Assembly-kode generert av en kompilator

Man kan også be en kompilator om å stoppe kompileringen før den assembler koden til maskinkode. Det kan man med gcc få til med opsjonen -S og den lager da en fil med filendelse s som innholder Assembly-kode som tilsvarer den maskinkoden den ville laget om man bare kompilerte med opsjonen -c.

```
$ gcc -S sumFunksjon.c
$ cat sumFunksjon.s
	.file	"sumFunksjon.c"
	.text
	.globl	sum
	.type	sum, @function
sum:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$0, -8(%rbp)
	movl	$0, -4(%rbp)
	jmp	.L2
.L3:
	movl	-4(%rbp), %eax
	addl	%eax, -8(%rbp)
	addl	$1, -4(%rbp)
.L2:
	cmpl	$3, -4(%rbp)
	jle	.L3
	movl	-8(%rbp), %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	sum, .-sum
	.ident	"GCC: (Ubuntu 5.4.0-6ubuntu1~16.04.5) 5.4.0 20160609"
	.section	.note.GNU-stack,"",@progbits
$
```