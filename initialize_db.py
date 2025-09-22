import os
import sqlite3
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash

from utils.vars import DB_PATH, ROOT_PATH


table_schemas = [
    """
    CREATE TABLE IF NOT EXISTS "users" (
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
    """,
    """
    CREATE TABLE IF NOT EXISTS "genres" (
        "id" INTEGER NOT NULL UNIQUE,
        "name" TEXT NOT NULL UNIQUE,
        PRIMARY KEY("id" AUTOINCREMENT)
    )
    """,
    """
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
    """,
    """
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
    """,
]

table_names = [
    "users",
    "genres",
    "books",
    "loans"
]

default_users = [
    ("librarian", "Marco", "Rossi", "marco.rossi@example.com", "Admin2025!", "", 1),
    (
        "chapterfan",
        "Laura",
        "Bianchi",
        "laura.bianchi@example.com",
        "Leggi2025!",
        "images/pfp/2.webp",
        1,
    ),
    ("bookworm", "Paolo", "Verdi", "paolo.verdi@example.com", "Plan2025!", "", 0),
    (
        "storyseeker",
        "Sara",
        "Neri",
        "sara.neri@example.com",
        "Books2025!",
        "images/pfp/4.webp",
        0,
    ),
    ("booklover", "Luca", "Romano", "luca.romano@example.com", "Fan2025!", "", 0),
    (
        "avid_reader",
        "Elena",
        "Ferrari",
        "elena.ferrari@example.com",
        "Storie2025!",
        "images/pfp/6.webp",
        0,
    ),
    (
        "pageturner",
        "Andrea",
        "Marino",
        "andrea.marino@example.com",
        "Novels2025!",
        "images/pfp/7.webp",
        0,
    ),
    (
        "bibliophile",
        "Chiara",
        "Costa",
        "chiara.costa@example.com",
        "2025Books!",
        "",
        0,
    ),
    (
        "noveladdict",
        "Matteo",
        "Rizzo",
        "matteo.rizzo@example.com",
        "Read2025!",
        "",
        0,
    ),
]

default_genres = [
    "Fiction",
    "Non-Fiction",
    "Science Fiction",
    "Fantasy",
    "Mystery",
    "Thriller",
    "Romance",
    "Horror",
    "Biography",
    "Self-Help",
    "Cookbook",
    "Graphic Novel",
]

default_books = [
    ("1984", "George Orwell", 1, 1949, "Scritto nel 1948 e pubblicato l'anno successivo, 1984 ritrae un futuro immaginario in cui dominano il totalitarismo, la falsificazione, l'annullamento dell'identità individuale e la perdita della memoria storica, viziata e corrotta dai mezzi d'informazione. La vicenda è ambientata in una Londra situata in uno dei tre grandi superstati in cui è diviso il mondo: l'Oceania. Gli altri due, l'Eurasia e l'Estasia, completano il quadro degli stati di polizia che dominano la terra in perenne conflitto. Come nelle più subdole guerre, le tensioni che ne derivano vengono sfruttate per mantenere inalterate le strutture sociali e per dare l'illusione che lo scopo primario sia la protezione dei cittadini. A questo valgono i sacrifici dei combattenti, che si immolano per preservare il benessere della società. Nello stato dell'Oceania l'ideologia dominante è il Socing, ossia il \"Socialismo Inglese\", rappresentato ai vertici del sistema dal Grande Fratello, una figura quasi leggendaria che nessuno ha mai visto, se non nei manifesti di cui è tappezzata la città. Quella di 1984 è una realtà in cui la volontà è totalmente annichilita e l'umanità sembra sopravvivere solo nel protagonista Winston, forse l'ultimo della sua specie. In questo contesto un grande interrogativo sorge al lettore: quando l'individuo non esiste più, e nessuno è più certo dell'autenticità dei propri pensieri, è ancora possibile distinguere la menzogna dalla verità?", "images/covers/book_1.jpg", 5, 5),
    ("Il buio oltre la siepe", "Harper Lee", 2, 1960, "Romanzo gotico del Sud", "images/covers/book_2.jpg", 3, 3),
    ("Il grande Gatsby", "F. Scott Fitzgerald", 1, 1925, "Tragedia americana", "images/covers/book_3.jpg", 4, 4),
    ("Moby Dick", "Herman Melville", 3, 1851, "Romanzo d'avventura", "images/covers/book_4.jpg", 2, 2),
    ("Orgoglio e pregiudizio", "Jane Austen", 4, 1813, "Romanzo rosa", "images/covers/book_5.jpg", 6, 6),
    ("Il giovane Holden", "J.D. Salinger", 1, 1951, "Romanzo di formazione", "images/covers/book_6.jpg", 4, 4),
    ("Il nome della rosa", "Umberto Eco", 5, 1980, "Giallo storico", "images/covers/book_7.jpg", 3, 3),
    ("La coscienza di Zeno", "Italo Svevo", 1, 1923, "Romanzo psicologico", "images/covers/book_8.jpg", 2, 2),
    ("Cent'anni di solitudine", "Gabriel García Márquez", 1, 1967, "Realismo magico", "images/covers/book_9.jpg", 5, 5),
    ("Il signore degli anelli", "J.R.R. Tolkien", 4, 1954, "Fantasy epico", "images/covers/book_10.jpg", 4, 4),
    ("Dracula", "Bram Stoker", 8, 1897, "Romanzo horror", "images/covers/book_11.jpg", 3, 3),
    ("La fattoria degli animali", "George Orwell", 1, 1945, "Satira politica", "images/covers/book_12.jpg", 4, 4),
    ("Il codice Da Vinci", "Dan Brown", 5, 2003, "Thriller", "images/covers/book_13.jpg", 6, 6),
    ("La strada", "Cormac McCarthy", 1, 2006, "Romanzo post-apocalittico", "images/covers/book_14.jpg", 2, 2),
    ("Il piccolo principe", "Antoine de Saint-Exupéry", 1, 1943, "Fiaba filosofica", "images/covers/book_15.jpg", 5, 5),
    ("Il ritratto di Dorian Gray", "Oscar Wilde", 1, 1890, "Romanzo gotico", "images/covers/book_16.jpg", 3, 3),
    ("La metamorfosi", "Franz Kafka", 1, 1915, "Racconto surreale", "images/covers/book_17.jpg", 4, 4),
    ("Il gabbiano Jonathan Livingston", "Richard Bach", 1, 1970, "Romanzo ispirazionale", "images/covers/book_18.jpg", 2, 2),
    ("Il diario di Anna Frank", "Anna Frank", 2, 1947, "Memorie storiche", "images/covers/book_19.jpg", 3, 3),
    ("V per Vendetta", "Alan Moore e David Lloyd", 12, 1988, "Graphic Novel distopica", "images/covers/book_20.jpg", 4, 4),
]

default_loans = [
    # Settimana 1 (1-7 settembre)
    (3, 1, "2025-09-02", "2025-09-16", None, 1),  # attivo
    (4, 2, "2025-09-03", "2025-09-17", None, 1),  # attivo
    (5, 3, "2025-09-05", "2025-09-19", None, 0),  # prenotato

    # Settimana 2 (8-14 settembre)
    (6, 4, "2025-09-09", "2025-09-23", None, 1),  # attivo
    (7, 5, "2025-09-10", "2025-09-24", None, 1),  # attivo
    (3, 6, "2025-09-12", "2025-09-26", None, 0),  # prenotato

    # Settimana 3 (15-21 settembre)
    (4, 7, "2025-09-15", "2025-09-29", None, 1),  # attivo
    (5, 8, "2025-09-16", "2025-09-30", None, 1),  # attivo
    (6, 9, "2025-09-18", "2025-10-02", None, 0),  # prenotato

    # Settimana 4 (22-28 settembre)
    (7, 10, "2025-09-22", "2025-10-06", None, 1),  # attivo
    (3, 11, "2025-09-23", "2025-10-07", None, 1),  # attivo
    (4, 12, "2025-09-25", "2025-10-09", None, 0),  # prenotato

    # Prestiti extra su generi diversi e altri libri
    (5, 13, "2025-09-04", "2025-09-18", None, 1),  # attivo
    (6, 14, "2025-09-11", "2025-09-25", None, 1),  # attivo
    (7, 15, "2025-09-17", "2025-10-01", None, 1),  # attivo
    (3, 16, "2025-09-24", "2025-10-08", None, 0),  # prenotato
    (4, 17, "2025-09-26", "2025-10-10", None, 1),  # attivo
    (5, 18, "2025-09-28", "2025-10-12", None, 1),  # attivo
    (6, 19, "2025-09-29", "2025-10-13", None, 0),  # prenotato
    (7, 20, "2025-09-30", "2025-10-14", None, 1),  # attivo
]


def ensure_db_directory():
    """Assicura che la directory del database esista"""
    os.makedirs(os.path.dirname(ROOT_PATH + DB_PATH), exist_ok=True)
    return os.path.exists(os.path.dirname(ROOT_PATH + DB_PATH))


def check_db_exists():
    """Verifica se il database esiste"""
    return os.path.exists(ROOT_PATH + DB_PATH)


def create_database_structure():
    """
    Crea la struttura del database come definita nel README
    """
    ensure_db_directory()

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    tables_created = 0
    for schema in table_schemas:
        try:
            cursor.execute(schema)
            tables_created += 1
        except Exception as e:
            print(f"Errore durante la creazione della tabella: {e}")

    conn.commit()
    cursor.close()
    conn.close()

    if tables_created == len(table_schemas):
        print("Tutte le tabelle create con successo")
        return True
    else:
        print(f"Create {tables_created}/{len(table_schemas)} tabelle")
        return False


def initialize_default_data():
    """
    Inizializza il database con i dati predefiniti
    """
    if not check_db_exists():
        print("Database non trovato. Crea prima la struttura del database.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    success = True

    # Generi
    try:
        cursor.execute("SELECT COUNT(*) FROM genres")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                "INSERT INTO genres (name) VALUES (?)",
                [(genre,) for genre in default_genres],
            )
            print("Generi inizializzati con successo")
        else:
            print("La tabella genres contiene già dati, inizializzazione saltata")
    except Exception as e:
        conn.rollback()
        print(f"Errore durante l'inizializzazione dei generi: {e}")
        success = False

    # Libri
    try:
        cursor.execute("SELECT COUNT(*) FROM books")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """INSERT INTO books 
                (title, author, genre, publication_year, description, cover, total_copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                default_books,
            )
            print("Libri inizializzati con successo")
        else:
            print("La tabella books contiene già dati, inizializzazione saltata")
    except Exception as e:
        conn.rollback()
        print(f"Errore durante l'inizializzazione dei libri: {e}")
        success = False

    # Prestiti
    try:
        cursor.execute("SELECT COUNT(*) FROM loans")
        if cursor.fetchone()[0] == 0:
            cursor.executemany(
                """INSERT INTO loans 
                (user_id, book_id, start_date, due_date, return_date, status)
                VALUES (?, ?, ?, ?, ?, ?)""",
                default_loans,
            )
            print("Prestiti inizializzati con successo")
        else:
            print("La tabella loans contiene già dati, inizializzazione saltata")
    except Exception as e:
        conn.rollback()
        print(f"Errore durante l'inizializzazione dei prestiti: {e}")
        success = False

    conn.commit()
    cursor.close()
    conn.close()

    if success and not initialize_default_users():
        print("Errore durante l'inizializzazione degli utenti.")
        success = False

    return success


def initialize_default_users():
    """
    Crea gli utenti di default nel database.
    """
    if not check_db_exists():
        print("Database non trovato. Crea prima la struttura del database.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM users")
    users_count = cursor.fetchone()[0]

    if users_count > 0:
        print(
            f"Ci sono già {users_count} utenti nel database. Inizializzazione utenti saltata."
        )
        cursor.close()
        conn.close()
        return True

    os.makedirs(f"{ROOT_PATH}static/images/pfp", exist_ok=True)

    insert_query = """
    INSERT INTO users (username, name, surname, email, password, pfp, role)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    inserted_users = 0
    success = True

    try:
        for user in default_users:
            username, name, surname, email, plain_password, pfp, role = user

            password_hash = generate_password_hash(plain_password, method="scrypt")

            cursor.execute(
                insert_query,
                (
                    username.lower(),
                    name,
                    surname,
                    email.lower(),
                    password_hash,
                    pfp,
                    role,
                ),
            )
            inserted_users += 1

        conn.commit()
        print(f"Inizializzati {inserted_users} utenti di default con successo")

    except Exception as e:
        conn.rollback()
        print(f"Errore durante l'inizializzazione degli utenti: {e}")
        success = False

    finally:
        cursor.close()
        conn.close()

    return success


def drop_tables():
    """
    Elimina tutte le tabelle del database
    """
    if not check_db_exists():
        print("Database non trovato.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF")

    success = True
    for table_name in reversed(table_names):
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"Tabella {table_name} eliminata con successo")
        except Exception as e:
            print(f"Errore durante l'eliminazione della tabella {table_name}: {e}")
            success = False

    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    cursor.close()
    conn.close()

    return success


def truncate_tables():
    """
    Svuota tutte le tabelle del database mantenendo la struttura
    """
    if not check_db_exists():
        print("Database non trovato.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = OFF")

    success = True
    for table_name in reversed(table_names):
        try:
            cursor.execute(f"DELETE FROM {table_name}")
            print(f"Tabella {table_name} svuotata con successo")
        except Exception as e:
            print(f"Errore durante lo svuotamento della tabella {table_name}: {e}")
            success = False

    cursor.execute("PRAGMA foreign_keys = ON")

    conn.commit()
    cursor.close()
    conn.close()

    return success


def reset_auto_increment():
    """
    Resetta i contatori di auto-incremento per tutte le tabelle
    """
    if not check_db_exists():
        print("Database non trovato.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    success = True
    for table_name in table_names:
        try:
            cursor.execute(f"DELETE FROM sqlite_sequence WHERE name='{table_name}'")
            print(f"Contatore auto-incremento per {table_name} resettato con successo")
        except Exception as e:
            print(f"Errore durante il reset del contatore per {table_name}: {e}")
            success = False

    conn.commit()
    cursor.close()
    conn.close()

    return success


def count_records():
    """
    Conta il numero di record in ogni tabella
    """
    if not check_db_exists():
        print("Database non trovato.")
        return False

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()

    print("\nNumero di record per tabella:")
    print("-" * 40)

    for table_name in table_names:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"{table_name}: {count} record")
        except Exception as e:
            print(f"{table_name}: Errore - {e}")

    print("-" * 40)

    cursor.close()
    conn.close()
    return True


def backup_database():
    """
    Crea un backup del database
    """
    if not check_db_exists():
        print("Database non trovato.")
        return False

    backup_dir = "db/backup"
    os.makedirs(backup_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{backup_dir}/biblioteca_backup_{timestamp}.db"

    try:
        with open(ROOT_PATH + DB_PATH, "rb") as src, open(backup_path, "wb") as dst:
            dst.write(src.read())

        print(f"Backup creato con successo: {backup_path}")
        print(f"Backup creato: {backup_path}")
        return True
    except Exception as e:
        print(f"Errore durante la creazione del backup: {e}")
        return False


def restore_database():
    """
    Ripristina un backup del database
    """
    backup_dir = "db/backup"

    if not os.path.exists(backup_dir):
        print("Directory di backup non trovata.")
        return False

    backups = [
        f
        for f in os.listdir(backup_dir)
        if f.startswith("biblioteca_backup_") and f.endswith(".db")
    ]

    if not backups:
        print("Nessun backup trovato.")
        return False

    print("\nBackup disponibili:")
    for i, backup in enumerate(backups, 1):
        print(f"{i}. {backup}")

    choice = input(
        "\nSeleziona il numero del backup da ripristinare (0 per annullare): "
    )

    try:
        choice = int(choice)
        if choice == 0:
            return False
        if choice < 1 or choice > len(backups):
            print("Scelta non valida.")
            return False

        selected_backup = backups[choice - 1]
        backup_path = f"{backup_dir}/{selected_backup}"

        if check_db_exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            pre_restore_backup = f"{backup_dir}/pre_restore_{timestamp}.db"
            with open(ROOT_PATH + DB_PATH, "rb") as src, open(
                pre_restore_backup, "wb"
            ) as dst:
                dst.write(src.read())
            print(f"Backup pre-ripristino creato: {pre_restore_backup}")

        with open(backup_path, "rb") as src, open(ROOT_PATH + DB_PATH, "wb") as dst:
            dst.write(src.read())

        print(f"Database ripristinato dal backup: {selected_backup}")
        print(f"Database ripristinato con successo dal backup: {selected_backup}")
        return True
    except ValueError:
        print("Input non valido.")
        return False
    except Exception as e:
        print(f"Errore durante il ripristino del backup: {e}")
        return False


def print_menu():
    """
    Stampa il menu principale
    """
    print("\n" + "=" * 60)
    print("BIBLIOTECA DATABASE MANAGER".center(60))
    print("=" * 60)

    print("\nOPERAZIONI DISPONIBILI:")
    print("1. Crea struttura del database (tabelle)")
    print("2. Popola database con dati predefiniti")
    print("3. Inizializza utenti predefiniti")
    print("4. Elimina tutte le tabelle")
    print("5. Svuota tutte le tabelle (mantiene struttura)")
    print("6. Reset contatori auto-incremento")
    print("7. Visualizza conteggio record")
    print("8. Crea backup del database")
    print("9. Ripristina database da backup")
    print("10. Inizializzazione completa (crea + popola + utenti)")
    print("0. Esci")

    print("\nStato database:", end=" ")
    if check_db_exists():
        print("PRESENTE ✓")
    else:
        print("NON PRESENTE ✗")


def main():
    """
    Funzione principale interattiva
    """
    while True:
        print_menu()

        choice = input("\nSeleziona un'operazione [0-10]: ")

        if choice == "1":
            print("\nCreazione struttura del database...")
            if create_database_structure():
                print("Struttura del database creata con successo!")
            else:
                print("Si sono verificati errori durante la creazione della struttura.")

        elif choice == "2":
            print("\nPopolamento database con dati predefiniti...")
            if initialize_default_data():
                print("Database popolato con successo!")
            else:
                print("Si sono verificati errori durante il popolamento del database.")

        elif choice == "3":
            print("\nInizializzazione utenti predefiniti...")
            if initialize_default_users():
                print("Utenti inizializzati con successo!")
            else:
                print(
                    "Si sono verificati errori durante l'inizializzazione degli utenti."
                )

        elif choice == "4":
            confirm = input(
                "\nATTENZIONE: Questa operazione eliminerà tutte le tabelle e i dati.\nSei sicuro di voler procedere? (s/n): "
            )
            if confirm.lower() == "s":
                if drop_tables():
                    print("Tutte le tabelle sono state eliminate con successo!")
                else:
                    print(
                        "Si sono verificati errori durante l'eliminazione delle tabelle."
                    )

        elif choice == "5":
            confirm = input(
                "\nATTENZIONE: Questa operazione svuoterà tutte le tabelle.\nSei sicuro di voler procedere? (s/n): "
            )
            if confirm.lower() == "s":
                if truncate_tables():
                    print("Tutte le tabelle sono state svuotate con successo!")
                else:
                    print(
                        "Si sono verificati errori durante lo svuotamento delle tabelle."
                    )

        elif choice == "6":
            if reset_auto_increment():
                print("Contatori auto-incremento resettati con successo!")
            else:
                print("Si sono verificati errori durante il reset dei contatori.")

        elif choice == "7":
            count_records()

        elif choice == "8":
            if backup_database():
                print("Backup completato con successo!")
            else:
                print("Si sono verificati errori durante la creazione del backup.")

        elif choice == "9":
            if not restore_database():
                print("Ripristino annullato o non riuscito.")

        elif choice == "10":
            print("\nInizializzazione completa del database...")

            success = True

            print("1. Creazione struttura...")
            if not create_database_structure():
                print("Errore durante la creazione della struttura!")
                success = False

            if success:
                print("2. Popolamento dati predefiniti...")
                if not initialize_default_data():
                    print("Errore durante il popolamento dei dati!")
                    success = False

            if success:
                print("\nInizializzazione completa terminata con successo!")
            else:
                print("\nL'inizializzazione completa ha incontrato errori.")

        elif choice == "0":
            print("\nUscita dal programma. Arrivederci!")
            break

        else:
            print("\nScelta non valida. Riprova.")

        input("\nPremi INVIO per continuare...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperazione interrotta. Uscita dal programma.")
        sys.exit(0)
