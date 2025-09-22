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
