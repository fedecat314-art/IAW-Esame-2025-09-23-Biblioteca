**Introduzione alle Applicazioni Web \- Appello del 22/09/2025**

# Progetto d’esame

# **MODALITÀ D’ESAME**

L’esame di Introduzione alle Applicazioni Web consta di due parti, strettamente collegate ed entrambe obbligatorie:

1. Progettazione e realizzazione individuale di un’applicazione web.
2. Dimostrazione e discussione orale sul progetto.

La valutazione dei progetti e la dimostrazione/orale riguarderà il materiale consegnato prima dell’appello. La dimostrazione e la breve discussione orale inerente il progetto è da svolgersi secondo il calendario che sarà reso disponibile qualche giorno prima dell’appello, previa registrazione all’appello stesso.

La discussione riguarderà le scelte di progettazione (layout, struttura del codice, struttura del DB, ecc.) nonché le scelte implementative e funzionali adottate.

# **DESCRIZIONE E REQUISITI**

Il progetto consiste in un’applicazione web che deve soddisfare alcuni requisiti tecnici, stilistici e funzionali, dettagliati in seguito.

L’applicazione web dovrà utilizzare le tecnologie illustrate e sperimentate durante il corso.

## Requisiti logistici

- Il progetto deve essere realizzato individualmente.
- Non è prevista né accettabile una consegna (parzialmente o totalmente) in comune con un altro studente del corso.
- Il progetto deve essere consegnato secondo le tempistiche riportate nell’ultima pagina di questo documento.
- Non è prevista né accettabile una consegna in ritardo.

## Requisiti tecnici

L’applicazione web deve rispettare i seguenti requisiti tecnici:

- Utilizzo di HTML5 e CSS3, avvalendosi se necessario di framework esterni come Bootstrap, ma personalizzandone lo stile tramite regole create ad-hoc.
- Utilizzo di Flask e di SQLite (come database relazionale), per il back-end.
- Utilizzo di Flask-Login per la gestione dell’autenticazione.

Inoltre:

- L’applicazione web deve avere un target di dispositivi ben preciso (desktop, mobile oppure tablet), a scelta degli studenti, eventualmente supportando la modalità responsive.
- Eventuali form utilizzati nel progetto devono essere **validati** sia nel front-end che nel back-end, come spiegato durante il corso.
- Il progetto consegnato deve essere interamente testabile dal docente e deve funzionare sulle ultime versioni di Chrome (111+) e Firefox (110+).
- Il codice sorgente deve essere ben scritto e corredato di opportuni commenti laddove necessario.
- Tutte le tecnologie elencate in precedenza devono essere integrate in maniera coesa e uniforme all’interno di un’unica applicazione web.

**Extra:**

- Fare il deploy dell’applicazione web su PythonAnywhere ([https://www.pythonanywhere.com/](https://www.pythonanywhere.com/)).

## Requisiti stilistici

L’applicazione web deve rispettare i seguenti requisiti stilistici:

- Utilizzo di tag HTML in maniera semantica (per esempio, non tutto è un \<div\>).
- No tag HTML deprecati.
- Non utilizzare dichiarazioni CSS inline, mantenendo cioè le regole CSS separate dalla struttura semantica del HTML.

Inoltre, l’applicazione web deve essere sufficientemente “usabile”.

## Descrizione (requisiti funzionali)

Si vuole creare un’applicazione web per la gestione di una **biblioteca digitale**. Per semplicità, l’applicazione sarà dedicata a un solo mese di attività. L’applicazione deve supportare due tipi di utenti registrati: i **lettori** e il **bibliotecario**.

I lettori possono esplorare il catalogo dei libri disponibili e prenotarne il prestito. Per poter prenotare, è necessario che il lettore sia registrato ed effettuare il login. Il login/registrazione richiede un campo univoco (ad esempio, l’email). La gestione del prestito è simulata all’interno dell’applicazione e non prevede l’integrazione con sistemi reali.

Il bibliotecario, anch’esso autenticato tramite login, potrà gestire il catalogo della biblioteca. In particolare, potrà inserire nuovi libri e gestire le copie disponibili. Al momento della registrazione di un nuovo prestito, il sistema dovrà impedire che venga superato il numero di copie disponibili. I dati di un libro (titolo, autore, genere, ecc.) possono essere modificati liberamente finché non è stato registrato alcun prestito. Un libro può essere eliminato dal catalogo solo se nessuna copia è attualmente in prestito.

Ogni libro presente nel sito dovrà avere associate le seguenti informazioni obbligatorie:

- Titolo
- Autore
- Genere
- Anno di pubblicazione
- Breve descrizione
- Copertina/immagine
- Numero di copie disponibili

Ogni copia sarà prestabile per un massimo di 14 giorni. I lettori potranno prenotare al massimo 3 libri contemporaneamente. Una prenotazione può essere annullata dal lettore fino a 24 ore prima dell’inizio del prestito. Una volta esaurite le copie disponibili, non sarà più possibile effettuare nuove prenotazioni per quel titolo.

Nella homepage dell’applicazione, **tutti gli utenti** (registrati o meno) vedranno una versione breve del catalogo, ordinato per autore o titolo in ordine alfabetico. Tramite appositi filtri, sarà possibile esplorare i libri anche in base al **genere** o **all’anno di pubblicazione**.

Cliccando su un libro, sarà possibile visualizzare tutte le informazioni dettagliate e le copie disponibili.

Una volta effettuata una prenotazione, i libri appariranno nellaLIBR pagina profilo del lettore, dove saranno riportati il titolo, la data di inizio prestito e la data di restituzione prevista.

Anche il bibliotecario avrà una propria pagina profilo, in cui potrà visualizzare l’elenco dei prestiti attivi e le statistiche dei prestiti effettuati per ciascun libro. Inoltre, potrà gestire le prenotazioni attive, ad esempio annullando prestiti non ancora iniziati.

Il bibliotecario può navigare il sito come i lettori, ma non può prenotare libri. Un lettore non può diventare bibliotecario. Gli utenti non registrati possono esplorare liberamente il catalogo, ma non possono inserire libri né prenotarne il prestito.

**Nota:** alla consegna, l’applicazione web dovrà contenere almeno **5 utenti registrati** (1 bibliotecario e 4 lettori), almeno **10 libri inseriti**, e prestiti programmati per l’intero mese (almeno 2 nuovi prestiti attivi per settimana, di cui almeno uno ancora modificabile perché non ancora iniziato). Devono inoltre essere presenti prestiti per almeno **due generi diversi**. I nomi utente e le password di questi account dovranno essere forniti ai docenti per la verifica.

---

🔥 Si incoraggia a esprimere pienamente la propria creatività nella **scelta dei libri, del nome della biblioteca, del tema e degli altri dettagli**, per realizzare un progetto originale e personalizzato\!

# **ISTRUZIONI PER LA CONSEGNA DEL PROGETTO**

La consegna del progetto deve avvenire tramite lo strumento “**Consegna Elaborati**” presente nella pagina del corso sul *Portale della Didattica*, entro le **23:59 del 22 Settembre 2025**.

La consegna dovrà contenere in un unico archivio (.zip):

- Codice sorgente dell’applicazione web realizzata, incluse:
  - eventuali dipendenze (in un file come requirements.txt), immagini, …
  - file SQLite contenente il database
- Un documento di testo (.md o .txt) contenente:
  - le credenziali degli utenti;
  - eventuali istruzioni per provare l’applicazione web;
  - se è stato fatto, l’indirizzo a cui l’applicazione web è visibile dopo il deploy.





  