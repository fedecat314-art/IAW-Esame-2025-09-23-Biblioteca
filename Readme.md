# Esame 23/09/2025

[https://elite.polito.it/teaching/01dxu-iaw/esame](https://elite.polito.it/teaching/01dxu-iaw/esame)

[https://docs.google.com/document/d/1hfIPLSzTydxGo3tHkihwoihi2OgvVviWKSeFmlMpGpw/edit?usp=sharing](https://docs.google.com/document/d/1hfIPLSzTydxGo3tHkihwoihi2OgvVviWKSeFmlMpGpw/edit?usp=sharing)

## Development

Apri la cartella nel terminale e scrivi `python -m venv .venv`

Attiva l'ambiente virtuale con `.venv\Scripts\Activate.ps1`

Per aprire VSCode aprire il file `*.code-workspace`

Installa le dipendenze con: `pip install -r requirements.txt`

Per aprire il database aprire il file `biblioteca.sqbpro`

Per le operazioni sul database c'è lo script `initialize_db.py`. Per utilizzarlo, eseguire il comando `python initialize_db.py` nel terminale. 
Permette di fare:

1. Crea struttura del database (tabelle)
2. Popola database con dati predefiniti
3. Inizializza utenti predefiniti
4. Elimina tutte le tabelle
5. Svuota tutte le tabelle (mantiene struttura)
6. Reset contatori auto-incremento
7. Visualizza conteggio record
8. Crea backup del database
9. Ripristina database da backup
10. Inizializzazione completa (crea + popola + utenti)

pip freeze > requirements.txt
flask run --debug

## Design

### DB

- **Utenti**:
  - id
  - nome utente
  - nome
  - cognome
  - email
  - password
  - ruolo (lettore/bibliotecario)
  - pfp
  
  ```sql
  CREATE TABLE "users" (
    "id" INTEGER NOT NULL UNIQUE,
    "username" TEXT NOT NULL UNIQUE,
    "name" TEXT NOT NULL,
    "surname" TEXT NOT NULL,
    "email" TEXT NOT NULL UNIQUE,
    "password" TEXT NOT NULL,
    "role" INTEGER NOT NULL,
    "pfp" TEXT,
    PRIMARY KEY("id" AUTOINCREMENT)
  )
  ```

- **Libri**:
  - id (PK)
  - titolo
  - autore
  - genere
  - anno_pubblicazione
  - descrizione
  - copertina (path/URL immagine)
  - copie_totali
  - copie_disponibili

  ```sql
  CREATE TABLE "books" (
    "id" INTEGER NOT NULL UNIQUE,
    "title" TEXT NOT NULL,
    "author" TEXT NOT NULL,
    "genre" INTEGER NOT NULL,
    "publication_year" INTEGER NOT NULL,
    "description" TEXT,
    "cover" TEXT,
    "total_copies" INTEGER NOT NULL,
    "available_copies" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("genre") REFERENCES "genres"("id")
  )
  ```

- **Prestiti**:
  - id (PK)
  - user_id (FK → users)
  - book_id (FK → books)
  - data_inizio
  - data_fine_prevista
  - data_restituzione (null se non ancora restituito)
  - stato (prenotato (0), attivo (1), restituito (2), annullato (3))
  
  ```sql
  CREATE TABLE "loans" (
    "id" INTEGER NOT NULL UNIQUE,
    "user_id" INTEGER NOT NULL,
    "book_id" INTEGER NOT NULL,
    "start_date" TEXT NOT NULL,
    "due_date" TEXT NOT NULL,
    "return_date" TEXT,
    "status" INTEGER NOT NULL,
    PRIMARY KEY("id" AUTOINCREMENT),
    FOREIGN KEY("user_id") REFERENCES "users"("id"),
    FOREIGN KEY("book_id") REFERENCES "books"("id")
  )
  ```

- **Generi**
  - id (PK)
  - nome
  
  ```sql
  CREATE TABLE "genres" (
    "id" INTEGER NOT NULL UNIQUE,
    "name" TEXT NOT NULL UNIQUE,
    PRIMARY KEY("id" AUTOINCREMENT)
  )
  ```

## Utenti disponibili

### Bibliotecari (nome utente - password)

- **Bibliotecario 1**: librarian - Admin2025!
- **Bibliotecario 2**: chapterfan - Leggi2025!

### Lettori (nome utente - password)

- **Lettore 1**: bookworm - Plan2025!
- **Lettore 2**: storyseeker - Books2025!
- **Lettore 3**: booklover - Fan2025!
- **Lettore 4**: avid_reader - Storie2025!
- **Lettore 5**: pageturner - Novels2025!
- **Lettore 6**: bibliophile - 2025Books!
- **Lettore 7**: noveladdict - Read2025!

## Indirizzo pubblico



## Repository Github

pagine app

home: libri nuovi/più letti + breve catalogo RICONTROLLA CAROSELLI con responsive
catalogo: tutti i libri + filtri
profilo: utente/bibiotecario gestione prestiti
      profilo utente: visualizzazione pronotazioni (max 3 libri) + bottone per restituire subito il libro
      profilo bibliotecario: visualizzazione prestiti attivi, stats libri, gestione prenotazioni, gestione libri (aggiungi/togli dal catalogo)

login FATTO
sign up FATTO
dettaglio libro SISTEMARE
nuova prenotazione: form per scegliere data di inizio/fine prestito (mag 14 gg)
modifica prenotazione

foto libro-titolo-autore

completa pagine

se si prova a prenotare senza login/accesso fare modale o simile che ti dice di fare l'accesso o l'account

passo 2:
dao + app.py (metti tutti dati in return + logiche varie)





DA FARE:

sistemare la pagina del profilo utente/bibliotecario FATTO
aggiungere logica a tutte le pagine FATTO
nella prenotazione aggiungere nota nel modale FATTO
nel catalogo aggiungere inizio descrizione nelle cards
sistemare e far funzionare filtri e barra ricerca FATTO
in book aggiungere descrizione + logica prenotazione (far rilevare prenotazione + data riconsegna) FATTO
ricorda di inserire il max di libri  FATTO
annullamento prenotazione almeno 24 ore prima dell'inizio FATTO
inserire data inizio/fine prestito nella sezione profilo lettore FATTO





TEST:
1984, gatsby, da vinci, cent'anni, metamorfosi
fiction, fiction, mistery, fiction, fiction


DA FARE ASSOLUTAMENTE (21/09)
sistemare password per signup che non funziona FATTO
sistemare return
passata la data di fine prestito segnare come restituito???? quando il prestito inzia devo far cambiare status da 0 a 1
fare descrizione che si ferma a metà e poi apri e vedi tutto
evitare di superare numero di copie disponibili  FATTO (?)


TECNICAMENTE BACKEND FINITO



POSSIBILI NOMI: digital tales, 


DESCRIZIONE HERO: 
1) Benvenuti nella nostra Biblioteca Digitale
La tua porta d’accesso a un mondo infinito di conoscenza, cultura e intrattenimento. La nostra biblioteca digitale offre una vasta collezione di libri, riviste, documenti storici e risorse multimediali, comodamente accessibili ovunque e in qualsiasi momento. Che tu sia uno studente, un ricercatore o un appassionato lettore, qui troverai materiale aggiornato e di qualità, con strumenti intuitivi per facilitare la ricerca e la lettura. Scopri il piacere di leggere senza confini, esplora nuovi argomenti e arricchisci il tuo sapere con un semplice click.

2) Benvenuto nella nostra Biblioteca!
Un luogo accogliente dove puoi scoprire libri, riviste, film e tanto altro, da sfogliare, leggere e prendere in prestito. Qui troverai uno spazio tranquillo per studiare, incontrare amici o partecipare a eventi e attività pensate per tutte le età. Che tu sia un lettore appassionato o semplicemente curioso, la nostra biblioteca è pronta ad accoglierti con tante risorse e tanta voglia di condividere storie e conoscenza. Vieni a trovarci, la cultura ti aspetta!

3) Benvenuto nella nostra Biblioteca!
Un luogo dove ogni passione trova il suo spazio: dai romanzi avvincenti ai testi universitari, dai manuali tecnici alle opere di ogni genere. Qui puoi sfogliare, leggere e prendere in prestito tantissimi libri, in un ambiente accogliente e tranquillo, ideale per studiare, approfondire o semplicemente lasciarti ispirare. La nostra biblioteca è pensata per tutti: studenti, professionisti, appassionati e curiosi. Vieni a scoprire il piacere della lettura e della conoscenza, ti aspettiamo con tante risorse e un sorriso!

4) Benvenuti nella nostra Biblioteca
La nostra biblioteca rappresenta un punto di riferimento culturale e formativo, offrendo una vasta collezione di volumi che spaziano dalla narrativa ai testi universitari e tecnici, fino a opere di ogni genere e disciplina. In un ambiente accogliente e silenzioso, mettiamo a disposizione degli utenti risorse di qualità per lo studio, la ricerca e l’approfondimento personale. Rivolta a studenti, professionisti e appassionati di lettura, la nostra struttura si impegna a favorire la diffusione della conoscenza e della cultura, promuovendo l’accesso libero e consapevole al sapere. Vi invitiamo a visitare la biblioteca per scoprire tutte le opportunità che offre.

pensare a colori + font + OCCHIO ALLE DIMENSIONI PER RESPONSIVE
