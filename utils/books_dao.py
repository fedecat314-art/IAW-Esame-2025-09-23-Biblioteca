import sqlite3

from utils.logger import get_logger
from utils.vars import DB_PATH, ROOT_PATH

import random


logger = get_logger()


def get_all_books():
    """
    Restituisce tutti i generi musicali

    Returns:
        list: Lista di dizionari contenenti i dettagli dei generi musicali
    """

    query = "SELECT * FROM books"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    books = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "genre": book[3],
            "publication_year": book[4],
            "description": book[5],
            "cover": book[6],
            "total_copies": book[7],
            "available_copies": book[8],
        }
        for book in books
    ]


def get_random_books(n):

    books = get_all_books()
    random_books = random.sample(books, n)

    return random_books


def get_most_read_books(n):

    query = """ 
    SELECT books.*, COUNT (loans.id) as loancount
    FROM books
    JOIN loans ON books.id=loans.book_id
    GROUP BY books.id 
    ORDER BY loancount DESC
    LIMIT ?
    """
    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (n,))
    most_read_books = cursor.fetchall()
    cursor.close()
    conn.close()

    return [
        {
            "id": most_read_book[0],
            "title": most_read_book[1],
            "author": most_read_book[2],
            "genre": most_read_book[3],
            "publication_year": most_read_book[4],
            "description": most_read_book[5],
            "cover": most_read_book[6],
            "total_copies": most_read_book[7],
            "available_copies": most_read_book[8],
        }
        for most_read_book in most_read_books
    ]


def get_book_by_id(book_id: int):
    """
    Restituisce un libro dato il suo ID

    Parameters:
        book_id (int): ID del libro

    Returns:
        dict: Dizionario contenente i dettagli del libro, o None se non trovato
    """

    query = "SELECT * FROM books WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (book_id,))
    book = cursor.fetchone()
    cursor.close()
    conn.close()

    if book:
        return {
            "id": book[0],
            "title": book[1],
            "author": book[2],
            "genre": book[3],
            "publication_year": book[4],
            "description": book[5],
            "cover": book[6],
            "total_copies": book[7],
            "available_copies": book[8],
        }

    return None


def update_total_copies(book_id: int, new_total: int):
    """
    Aggiorna il numero di copie totali di un libro

    Parameters:
        book_id (int): ID del libro
        new_copies (int): Nuovo numero di copie totali
    """

    query = "UPDATE books SET total_copies = ? WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        query,
        (
            new_total,
            book_id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def remove_book(book_id: int):

    query = "DELETE FROM books WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (book_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_book(
    title: str,
    author: str,
    genre: int,
    publication_year: int,
    description: str,
    cover: str,
    total_copies: int,
):
    """
    Aggiunge un nuovo libro al database

    Parameters:
        title (str): Titolo del libro
        author (str): Autore del libro
        genre (int): ID del genere del libro
        publication_year (int): Anno di pubblicazione del libro
        description (str): Descrizione del libro
        cover (str): URL della copertina del libro
        total_copies (int): Numero totale di copie del libro
    """

    query = "INSERT INTO books (title, author, genre, publication_year, description, cover, total_copies, available_copies) VALUES (?, ?, ?, ?, ?, ?, ?, ?)"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        query,
        (
            title,
            author,
            genre,
            publication_year,
            description,
            cover,
            total_copies,
            total_copies,
        ),
    )
    conn.commit()
    book_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return book_id


def update_book_cover(book_id: int, new_cover: str):
    """
    Aggiorna la copertina di un libro

    Parameters:
        book_id (int): ID del libro
        new_cover (str): Nuovo URL della copertina
    """

    query = "UPDATE books SET cover = ? WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (new_cover, book_id))
    conn.commit()
    cursor.close()
    conn.close()


def decrease_book_available_copies(book_id: int):
    """
    Aggiorna il numero di copie disponibili di un libro

    Parameters:
        book_id (int): ID del libro
        new_copies (int): Nuovo numero di copie disponibili
    """

    query = "UPDATE books SET available_copies = available_copies - 1 WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query,(book_id,))
    conn.commit()
    cursor.close()
    conn.close()


def increase_book_available_copies( book_id: int):
    """
    Aggiorna il numero di copie disponibili di un libro

    Parameters:
        book_id (int): ID del libro
        new_copies (int): Nuovo numero di copie disponibili
    """

    query = "UPDATE books SET available_copies = available_copies + 1  WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        query,
        (book_id,)
    )
    conn.commit()
    cursor.close()
    conn.close()


def update_book_details(book_id, title, author, genre, publication_year, description, total_copies):
    """
    Aggiorna i dettagli di un libro nel database

    Parameters:
        book_id (int): ID del libro da aggiornare
        title (str): Nuovo titolo del libro
        author (str): Nuovo autore del libro
        genre (int): Nuovo ID del genere del libro
        publication_year (int): Nuovo anno di pubblicazione del libro
        description (str): Nuova descrizione del libro
        total_copies (int): Nuovo numero totale di copie del libro
    """

    update_fields = []
    params = []

    if title is not None:
        update_fields.append("title = ?")
        params.append(title)

    if author is not None:
        update_fields.append("author = ?")
        params.append(author)

    if genre is not None:
        update_fields.append("genre = ?")
        params.append(genre)

    if publication_year is not None:
        update_fields.append("publication_year = ?")
        params.append(publication_year)
    
    if description is not None:
        update_fields.append("description = ?")
        params.append(description)
    
    if total_copies is not None:
        update_fields.append("total_copies = ?")
        params.append(total_copies)

    

    if not update_fields:
        return

    query = f"UPDATE books SET {', '.join(update_fields)} WHERE id = ?"
    params.append(book_id)

    try:
        conn = sqlite3.connect(ROOT_PATH + DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, tuple(params))
        conn.commit()
        cursor.close()
        conn.close()


    except Exception as e:
        logger.error(f"Errore durante l'aggiornamento del libro ID {book_id}: {e}")

