import sqlite3

from utils.logger import get_logger
from utils.vars import DB_PATH, ROOT_PATH



logger = get_logger()


def get_all_loans():
    """
    Restituisce tutti i prestiti

    Returns:
        list: Lista di dizionari contenenti i dettagli dei prestiti
    """

    query = "SELECT * FROM loans"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query)
    loans = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": loan[0], "user_id": loan[1], "book_id": loan[2], "start_date": loan[3], "due_date": loan[4], "return_date": loan[5], "status": loan[6]} for loan in loans]


def get_loan_by_id(loan_id: int):
    """
    Restituisce un genere dato il suo ID

    Parameters:
        loan_id (int): ID del genere

    Returns:
        dict: Dizionario contenente i dettagli del genere, o None se non trovato
    """

    query = "SELECT * FROM loans WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (loan_id,))
    loan = cursor.fetchone()
    cursor.close()
    conn.close()

    if loan:
        return {"id": loan[0], "user_id": loan[1]}

    return None


def get_loans_by_user(user_id: int):
     
    query = "SELECT * FROM loans WHERE user_id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    loans_by_user = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"id": loan[0], "user_id": loan[1], "book_id": loan[2], "start_date": loan[3], "due_date": loan[4], "return_date": loan[5], "status": loan[6]} for loan in loans_by_user]


def get_loans_count_by_book(book_id: int):

    """
    Restituisce per ogni libro il numero di prestiti in corso o scaduti (non restituiti).
    """
    query = """
    SELECT book_id, COUNT(*) as loans_count
    FROM loans
    WHERE (status = 1 OR status = 2 OR (due_date < DATE('now') AND return_date IS NULL)) AND book_id = ?
    GROUP BY book_id
    """

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (book_id,))
    loans_count_by_book = cursor.fetchall()
    cursor.close()
    conn.close()

    return [{"book_id": loan[0], "loans_count": loan[1]} for loan in loans_count_by_book]


def get_loans_by_book(book_id: int):
    """
    Restituisce tutti i prestiti di un libro, con tutti i dettagli.
    """
    query = "SELECT * FROM loans WHERE book_id = ?"
    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (book_id,))
    loans_by_book = cursor.fetchall()
    cursor.close()
    conn.close()
    return [
        {
            "id": loan[0],
            "user_id": loan[1],
            "book_id": loan[2],
            "start_date": loan[3],
            "due_date": loan[4],
            "return_date": loan[5],
            "status": loan[6]
        }
        for loan in loans_by_book
    ] 


def max_loans(user_id: int):
    """
    Restituisce il numero di prestiti attivi (in corso o prenotati) di un utente.
    """
    query = """
    SELECT COUNT(*) FROM loans
    WHERE user_id = ? AND status IN (0, 1)
    """
    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (user_id,))
    count = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return count


def loan_dismiss(loan_id: int):
    
    query = """
        UPDATE loans
        SET status = 3
        WHERE id = ?
        """
    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (loan_id,))
    conn.commit()
    cursor.close()
    conn.close()


def new_loan(user_id: int, book_id: int, start_date: str, due_date: str):
    """
    Crea un nuovo prestito

    Parameters:
        user_id (int): ID dell'utente
        book_id (int): ID del libro
        start_date (str): Data di inizio del prestito (YYYY-MM-DD)
        due_date (str): Data di scadenza del prestito (YYYY-MM-DD)
    """

    query = """
    INSERT INTO loans (user_id, book_id, start_date, due_date, status)
    VALUES (?, ?, ?, ?, 0)
    """

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (user_id, book_id, start_date, due_date))
    conn.commit()
    cursor.close()
    conn.close()


def loan_update_status(loan_id: int, new_status: int):
    """
    Aggiorna lo stato di un prestito

    Parameters:
        loan_id (int): ID del prestito
        new_status (int): Nuovo stato del prestito
    """

    query = "UPDATE loans SET status = ? WHERE id = ?"

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        query,
        (
            new_status,
            loan_id,
        ),
    )
    conn.commit()
    cursor.close()
    conn.close()


def return_loan(loan_id: int):
    """
    Segna un prestito come restituito

    Parameters:
        loan_id (int): ID del prestito
        return_date (str): Data di restituzione (YYYY-MM-DD)
    """

    query = """
    UPDATE loans 
    SET status = 2 
    WHERE id = ?"""

    conn = sqlite3.connect(ROOT_PATH + DB_PATH)
    cursor = conn.cursor()
    cursor.execute(query, (loan_id,))
    conn.commit()
    cursor.close()
    conn.close()