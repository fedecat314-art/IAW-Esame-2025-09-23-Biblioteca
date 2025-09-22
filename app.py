# Route per aggiunta libro
from werkzeug.utils import secure_filename
import os

from datetime import datetime, timedelta

from PIL import Image
from utils.vars import ROOT_PATH

from utils import users_dao, books_dao, genres_dao, loans_dao
from utils.logger import get_logger, setup_logger
from utils.models import User

from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import date, datetime

from flask_login import (
    LoginManager,
    login_user,
    login_required,
    logout_user,
    current_user,
)
from werkzeug.security import generate_password_hash, check_password_hash


setup_logger()
logger = get_logger()


logger.info("Avvio dell'applicazione")

app = Flask(__name__)
app.config["SECRET_KEY"] = "O*nY)jDH92t1g2K"
app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=30)
app.config["REMEMBER_COOKIE_SECURE"] = True
app.config["REMEMBER_COOKIE_HTTPONLY"] = True

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_user = users_dao.get_user_by_id(user_id)

    if not db_user:
        return None

    user = User(
        id=db_user["id"],
        username=db_user["username"],
        password=db_user["password"],
        name=db_user["name"],
        surname=db_user["surname"],
        email=db_user["email"],
        pfp=db_user["pfp"],
        role=db_user["role"],
    )
    return user


@app.route("/")
def home():

    random_books = books_dao.get_random_books(5)
    most_read_books = books_dao.get_most_read_books(5)
    most_read_genres = genres_dao.get_most_read_genres(5)

    return render_template(
        "index.html",
        random_books=random_books,
        most_read_books=most_read_books,
        most_read_genres=most_read_genres,
    )


@app.route("/catalogue")
def catalogue():
    if not current_user.is_authenticated:
        flash("Accedi o registrati per visualizzare tutto il catalogo!", "warning")
        return redirect(url_for("home"))

    genre_id = request.args.get("genre")
    search = request.args.get("search")
    genres = genres_dao.get_all_genres()

    # Filtra i libri
    books = books_dao.get_all_books()
    if genre_id:
        books = [b for b in books if str(b["genre"]) == genre_id]
    if search:
        books = [
            b
            for b in books
            if search.lower() in b["title"].lower()
            or search.lower() in b["author"].lower()
        ]

    return render_template("catalogue.html", books=books, genres=genres)


@app.route("/book", methods=["GET", "POST"])
def book_redirect():
    if request.method == "POST":
        if current_user.role != 1:
            flash("Non autorizzato", "danger")
            return redirect(url_for("catalogue"))

        title = request.form.get("title")
        author = request.form.get("author")
        genre = request.form.get("genre")
        publication_year = request.form.get("publication_year")
        description = request.form.get("description")
        total_copies = request.form.get("total_copies")
        cover_file = request.files.get("cover")

        if (
            not title
            or not author
            or not genre
            or not publication_year
            or not description
            or not total_copies
            or not cover_file
        ):
            flash("Tutti i campi sono obbligatori", "danger")
            return redirect(url_for("catalogue"))

        # Salva temporaneamente la copertina
        temp_image_path = ""
        cover_file = request.files.get("cover")
        if cover_file and cover_file.filename:
            os.makedirs(f"{ROOT_PATH}static/images/uploads", exist_ok=True)
            os.makedirs(f"{ROOT_PATH}static/images/covers", exist_ok=True)
            img = Image.open(cover_file.stream)
            max_size = (600,1000)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            if img.mode in ("RGBA", "LA"):
                if "A" in img.mode:
                    img = img.convert("RGB")
                else:
                    background = Image.new("RGB", img.size, (255, 255, 255))
                    background.paste(img)
                    img = background
            elif img.mode != "RGB" and img.mode != "RGBA":
                img = img.convert("RGB")

            temp_filename = f"temp_{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
            temp_image_path = f"images/uploads/{temp_filename}"
            img.save(f"{ROOT_PATH}static/{temp_image_path}", "JPEG", quality=85)

        # Inserisci il libro nel database e ottieni l'id
        book_id = books_dao.add_book(
            title,
            author,
            int(genre),
            int(publication_year),
            description,
            "",  # cover temporaneamente vuota
            int(total_copies),
        )

        # Rinomina e salva la copertina definitiva
        if book_id and temp_image_path:
            final_filename = f"book_{book_id}.jpg"
            final_image_path = f"images/covers/{final_filename}"
            img = Image.open(f"{ROOT_PATH}static/{temp_image_path}")
            img.save(f"{ROOT_PATH}static/{final_image_path}", "JPEG", quality=85)
            try:
                os.remove(f"{ROOT_PATH}static/{temp_image_path}")
            except:
                pass
            # Aggiorna il percorso copertina nel database
            books_dao.update_book_cover(book_id, final_image_path)
        flash("Libro aggiunto con successo!", "success")
        return redirect(url_for("catalogue"))
    else:
        return redirect(url_for("catalogue"))


@app.route("/book/<int:id>", methods=["GET", "POST"])
def book(id: int):
    if request.method == "POST":
        if current_user.role == 1:
            action = request.form.get("action")

            if action == "delete":
                # check if book has active loans or reservations
                loan_book_specifico = loans_dao.get_loans_by_book(id)
                if any(loan["status"] in [0, 1] for loan in loan_book_specifico):
                    flash(
                        "Non puoi rimuovere un libro che ha prestiti attivi o prenotazioni.",
                        "danger",
                    )
                    return redirect(url_for("book", id=id))
                # rimuovi libro
                books_dao.remove_book(id)
                # rimuovi copertina
                try:
                    os.remove(f"{ROOT_PATH}static/images/covers/book_{id}.jpg")
                except:
                    pass
                flash("Libro rimosso con successo", "success")
                return redirect(url_for("catalogue"))

            if action == "update":

                book = books_dao.get_book_by_id(id)
                if not book:
                    flash("Libro non trovato", "danger")
                    return redirect(url_for("catalogue"))

                title = request.form.get("title")
                author = request.form.get("author")
                genre = request.form.get("genre")
                publication_year = request.form.get("publication_year")
                description = request.form.get("description")
                total_copies = request.form.get("new_total")
                cover_file = request.files.get("cover")

                if (
                    not title
                    or not author
                    or not genre
                    or not publication_year
                    or not description
                    or not total_copies
                ):
                    flash("Tutti i campi sono obbligatori", "danger")
                    return redirect(url_for("book", id=id))

                # Aggiorna copertina se è stata caricata una nuova immagine
                if cover_file and cover_file.filename:
                    os.makedirs(f"{ROOT_PATH}static/images/covers", exist_ok=True)
                    img = Image.open(cover_file.stream)
                    max_size = (600, 1000)
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                    if img.mode in ("RGBA", "LA"):
                        if "A" in img.mode:
                            img = img.convert("RGB")
                        else:
                            background = Image.new("RGB", img.size, (255, 255, 255))
                            background.paste(img)
                            img = background
                    elif img.mode != "RGB" and img.mode != "RGBA":
                        img = img.convert("RGB")

                    final_filename = f"book_{id}.jpg"
                    final_image_path = f"images/covers/{final_filename}"
                    # Sovrascrive sempre il file, anche se già esiste
                    img.save(f"{ROOT_PATH}static/{final_image_path}", "JPEG", quality=85)
                    # Aggiorna il percorso copertina nel database

                # Aggiorna gli altri dettagli del libro
                books_dao.update_book_details(
                    id,
                    title,
                    author,
                    int(genre),
                    int(publication_year),
                    description,
                    int(total_copies),
                )

                flash("Libro aggiornato con successo!", "success")
                return redirect(url_for("book", id=id))

        else:
            return redirect(url_for("catalogue"))

    else:
        # prendo libro da db per id
        book_specifico = books_dao.get_book_by_id(id)
        if not book_specifico:
            flash("Libro non trovato", "danger")
            return redirect(url_for("catalogue"))
        # prendo il genere da db per id corrispondente a quello del libro specifico
        genere = genres_dao.get_genre_by_id(book_specifico["genre"])
        # prendo il numero di prestiti totali del libro specifico
        loan_count_specifico = loans_dao.get_loans_count_by_book(book_specifico["id"])
        # prendo tutti i dati dei prestiti del libro specifico
        loan_book_specifico = loans_dao.get_loans_by_book(book_specifico["id"])

        return render_template(
            "book.html",
            book_specifico=book_specifico,
            genere=genere,
            loan_count_specifico=loan_count_specifico,
        )


# @app.route("/update_book/<int:id>", methods=["POST"])
# @login_required
# def update_book(id: int):
#     if current_user.role != 1:
#         flash("Non autorizzato", "danger")
#         return redirect(url_for("catalogue"))

#     book = books_dao.get_book_by_id(id)
#     if not book:
#         flash("Libro non trovato", "danger")
#         return redirect(url_for("catalogue"))

#     title = request.form.get("title")
#     author = request.form.get("author")
#     genre = request.form.get("genre")
#     publication_year = request.form.get("publication_year")
#     description = request.form.get("description")
#     total_copies = request.form.get("total_copies")
#     cover_file = request.files.get("cover")

#     if (
#         not title
#         or not author
#         or not genre
#         or not publication_year
#         or not description
#         or not total_copies
#     ):
#         flash("Tutti i campi sono obbligatori", "danger")
#         return redirect(url_for("update_book", id=id))

#     # Aggiorna copertina se è stata caricata una nuova immagine
#     if cover_file and cover_file.filename:
#         os.makedirs(f"{ROOT_PATH}static/images/uploads", exist_ok=True)
#         os.makedirs(f"{ROOT_PATH}static/images/covers", exist_ok=True)
#         img = Image.open(cover_file.stream)
#         max_size = (800, 800)
#         img.thumbnail(max_size, Image.Resampling.LANCZOS)
#         if img.mode in ("RGBA", "LA"):
#             if "A" in img.mode:
#                 img = img.convert("RGB")
#             else:
#                 background = Image.new("RGB", img.size, (255, 255, 255))
#                 background.paste(img)
#                 img = background
#         elif img.mode != "RGB" and img.mode != "RGBA":
#             img = img.convert("RGB")

#         final_filename = f"book_{id}.jpg"
#         final_image_path = f"images/covers/{final_filename}"
#         img.save(f"{ROOT_PATH}static/{final_image_path}", "JPEG", quality=85)
#         books_dao.update_book_cover(id, final_image_path)

#     # Aggiorna gli altri dettagli del libro
#     books_dao.update_book_details(
#         id,
#         title,
#         author,
#         int(genre),
#         int(publication_year),
#         description,
#         int(total_copies),
#     )

#     flash("Libro aggiornato con successo!", "success")
#     return redirect(url_for("book", id=id))


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        flash("Sei già autenticato", "info")
        return redirect(url_for("home"))

    # Se la richiesta è POST, significa che l'utente sta cercando di effettuare il login
    if request.method == "POST":
        utente_form = request.form.to_dict()

        if not utente_form["usernameoremail"] or not utente_form["password"]:
            flash("Nome utente/email e password sono obbligatori", "danger")
            return redirect(url_for("login"))

        identifier = utente_form["usernameoremail"].strip()
        password = utente_form["password"].strip()
        remember = "remember" in utente_form

        if "@" in identifier:
            utente_db = users_dao.user_from_email(identifier)
        else:
            utente_db = users_dao.user_from_nickname(identifier)

        if not utente_db or not check_password_hash(utente_db["password"], password):
            flash("Credenziali non valide", "danger")
            return redirect(url_for("login"))
        else:
            new_user = User(
                id=utente_db["id"],
                username=utente_db["username"],
                password=utente_db["password"],
                name=utente_db["name"],
                surname=utente_db["surname"],
                email=utente_db["email"],
                pfp=utente_db["pfp"],
                role=utente_db["role"],
            )

            login_user(new_user, remember=remember)
            flash("Accesso efettuato con successo", "success")
            return redirect(url_for("home"))

    # Se la richiesta è GET, significa che l'utente sta cercando di visualizzare la pagina di login
    else:
        return render_template("login.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        flash("Sei già autenticato. Esci prima di creare un nuovo account", "info")
        return redirect(url_for("home"))

    # Se la richiesta è POST, significa che l'utente sta cercando di registrarsi
    if request.method == "POST":
        utente_form = request.form.to_dict()

        if (
            not utente_form["username"]
            or not utente_form["name"]
            or not utente_form["surname"]
            or not utente_form["email"]
            or not utente_form["password"]
        ):
            flash("Tutti i campi sono obbligatori", "danger")
            return redirect(url_for("signup"))

        if "@" in utente_form["username"]:
            flash("Il nome utente non può contenere '@'", "danger")
            return redirect(url_for("signup"))

        utente_db_username = users_dao.user_from_nickname(utente_form["username"])
        utente_db_email = users_dao.user_from_email(utente_form["email"])

        if utente_db_username:
            flash("Nome utente già esistente", "danger")
            return redirect(url_for("signup"))
        elif utente_db_email:
            flash("Email già registrata", "danger")
            return redirect(url_for("signup"))
        else:
            username = utente_form["username"]
            name = utente_form["name"]
            surname = utente_form["surname"]
            email = utente_form["email"]
            password = generate_password_hash(utente_form["password"], method="scrypt")
            role = int(utente_form["role"])

            temp_image_path = ""
            immagine = request.files["profile_picture"]

            if immagine and immagine.filename:
                os.makedirs(f"{ROOT_PATH}static/images/uploads", exist_ok=True)
                os.makedirs(f"{ROOT_PATH}static/images/pfp", exist_ok=True)
                img = Image.open(immagine.stream)
                max_size = (500, 500)
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
                if img.mode in ("RGBA", "LA"):
                    if "A" in img.mode:
                        img = img.convert("RGBA")
                    else:
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(img)
                        img = background
                elif img.mode != "RGB" and img.mode != "RGBA":
                    img = img.convert("RGB")

                temp_filename = f"pfp_{datetime.now().strftime('%Y%m%d%H%M%S')}.webp"
                temp_image_path = f"images/uploads/{temp_filename}"
                img.save(
                    f"{ROOT_PATH}static/{temp_image_path}", "WEBP", quality=85, method=6
                )

            user_id = users_dao.new_user(
                username, name, surname, email, password, temp_image_path, role
            )

            if temp_image_path:
                final_image_path = f"images/pfp/{user_id}.webp"
                img = Image.open(f"{ROOT_PATH}static/{temp_image_path}")
                img.save(
                    f"{ROOT_PATH}static/{final_image_path}",
                    "WEBP",
                    quality=85,
                    method=6,
                )

                try:
                    os.remove(f"{ROOT_PATH}static/{temp_image_path}")
                except:
                    pass

                users_dao.update_user_pfp(user_id, final_image_path)

            flash(
                "Registrazione completata con successo. Ora puoi accedere.", "success"
            )
            return redirect(url_for("login"))

    # Se la richiesta è GET, significa che l'utente sta cercando di visualizzare la pagina di registrazione
    else:
        return render_template("signup.html")


@app.route("/logout")
@login_required
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("Logout efettuato con successo", "success")
        return redirect(url_for("home"))
    else:
        flash("Non sei autenticato", "warning")
        return redirect(url_for("login"))


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    if not current_user:
        flash("Utente non trovato", "danger")
        return redirect(url_for("home"))

    template_data = {
        "username": current_user.username,
        "name": current_user.name,
        "surname": current_user.surname,
        "email": current_user.email,
        "pfp": current_user.pfp,
    }
    current_date = date.today()
    template_data["current_date"] = current_date

    if current_user.role == 0:
        user_loans = loans_dao.get_loans_by_user(current_user.id)
        loans = []
        for loan in user_loans:
            book = books_dao.get_book_by_id(loan["book_id"])
            if not book:
                flash(f"Libro con ID {loan['book_id']} non trovato", "warning")
                return redirect(url_for("profile"))
            genre = genres_dao.get_genre_by_id(book["genre"])
            if not genre:
                flash(f"Genere con ID {book['genre']} non trovato", "warning")
                return redirect(url_for("profile"))
            loan["genre_name"] = genre["name"]
            loan["genre_id"] = genre["id"]
            loan["book_title"] = book["title"]
            loan["book_author"] = book["author"]
            loan["book_year"] = book["publication_year"]
            loan["book_desccription"] = book["description"]
            loan["book_cover"] = book["cover"]
            loan["book_total"] = book["total_copies"]
            loan["book_available"] = book["available_copies"]
            loan["start_date"] = datetime.strptime(
                loan["start_date"], "%Y-%m-%d"
            ).date()
            loan["due_date"] = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
            loan["show_warning"] = (loan["due_date"] - current_date).days <= 3 and loan[
                "status"
            ] == 1
            loans.append(loan)

        template_data["loans"] = loans

        # inserisci libri dello stesso genere in sezione consigliati
        catalogue = books_dao.get_all_books()
        recommended_books = []
        
        for book in catalogue:
            for loan in user_loans:
                if (
                    book["genre"] == loan["genre_id"]
                    and book["id"] != loan["book_id"]
                    and book not in recommended_books 
                    and loan['status'] == 2
                ):
                    recommended_books.append(book)

        # mostra solo i primi 6 consigliati
        template_data["recommended_books"] = recommended_books[:6]

    elif current_user.role == 1:
        loans_raw = loans_dao.get_all_loans()
        loans = []
        for loan in loans_raw:
            user = users_dao.get_user_by_id(loan["user_id"])
            if not user:
                flash(f"Utente con ID {loan['user_id']} non trovato", "warning")
                return redirect(url_for("profile"))
            book = books_dao.get_book_by_id(loan["book_id"])
            if not book:
                flash(f"Libro con ID {loan['book_id']} non trovato", "warning")
                return redirect(url_for("profile"))
            genre = genres_dao.get_genre_by_id(book["genre"])
            if not genre:
                flash(f"Genere con ID {book['genre']} non trovato", "warning")
                return redirect(url_for("profile"))
            loan["genre_name"] = genre["name"]
            loan["book_title"] = book["title"]
            loan["book_id"] = book["id"]
            loan["book_author"] = book["author"]
            loan["book_year"] = book["publication_year"]
            loan["book_desccription"] = book["description"]
            loan["book_cover"] = book["cover"]
            loan["book_total"] = book["total_copies"]
            loan["book_available"] = book["available_copies"]
            loan["user_id"] = user["id"]
            loan["user_username"] = user["username"]
            loan["user_name"] = user["name"]
            loan["user_surname"] = user["surname"]
            loan["user_email"] = user["email"]
            loan["user_pw"] = user["password"]
            loan["user_role"] = user["role"]
            loan["user_pfp"] = user["pfp"]
            loan["start_date"] = datetime.strptime(
                loan["start_date"], "%Y-%m-%d"
            ).date()
            loan["due_date"] = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()

            loans.append(loan)
        template_data["loans"] = loans

    return render_template("profile.html", **template_data)


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    current_password = request.form.get("current_password")
    if not current_password:
        flash("La password attuale è obbligatoria", "danger")
        return redirect(url_for("profile"))

    if not check_password_hash(current_user.password, current_password):
        flash("Password attuale non corretta", "danger")
        return redirect(url_for("profile"))

    name = request.form.get("name")
    surname = request.form.get("surname")
    email = request.form.get("email")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    if email and email != current_user.email:
        existing_user = users_dao.user_from_email(email)
        if existing_user and existing_user["id"] != current_user.id:
            flash("Email già in uso da un altro utente", "danger")
            return redirect(url_for("profile"))

    if new_password:
        if new_password != confirm_password:
            flash("Le password non corrispondono", "danger")
            return redirect(url_for("profile"))
        password_hash = generate_password_hash(new_password, method="scrypt")
    else:
        password_hash = current_user.password

    users_dao.update_user(
        current_user.id, name=name, surname=surname, email=email, password=password_hash
    )

    current_user.name = name
    current_user.surname = surname
    current_user.email = email
    current_user.password = password_hash

    flash("Profilo aggiornato con successo", "success")
    return redirect(url_for("profile"))


@app.route("/update_profile_picture", methods=["POST"])
@login_required
def update_profile_picture():
    pfp = request.files["profile_picture"]

    if pfp and pfp.filename:
        os.makedirs(f"{ROOT_PATH}static/images/pfp", exist_ok=True)
        img = Image.open(pfp.stream)
        max_size = (500, 500)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        if img.mode in ("RGBA", "LA"):
            if "A" in img.mode:
                img = img.convert("RGBA")
            else:
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img)
                img = background
        elif img.mode != "RGB" and img.mode != "RGBA":
            img = img.convert("RGB")

        file_ext = "webp"
        pfp_path = f"images/pfp/{current_user.id}.{file_ext}"
        img_path = f"{ROOT_PATH}static/" + pfp_path
        img.save(img_path, "WEBP", quality=85, method=6)
        users_dao.update_user_pfp(current_user.id, pfp_path)

        current_user.pfp = pfp_path

        flash("Immagine profilo aggiornata con successo", "success")
    else:
        flash("Nessuna immagine selezionata", "danger")

    return redirect(url_for("profile"))


@app.route("/new_loan/<int:book_id>", methods=["POST"])
@login_required
def new_loan(book_id: int):
    if request.method == "POST":
        action = request.form.get("action")
        if action == "new_loan":
            book_specifico = books_dao.get_book_by_id(book_id)
            if not book_specifico:
                flash("Libro non trovato", "danger")
                return redirect(url_for("catalogue"))
            

            data_inizio_str = request.form.get("dataInizio")
            if not data_inizio_str:
                flash("Devi inserire una data di inizio prestito valida.", "warning")
                return redirect(url_for("book", id=book_specifico["id"]))


            data_inizio = datetime.strptime(data_inizio_str, "%Y-%m-%d").date()
            data_fine = data_inizio + timedelta(days=14)


            # verifica validità date
            if data_inizio == "" or data_inizio < date.today():
                flash("Devi inserire una data di inizio prestito valida.", "warning")
                return redirect(url_for("book", id=book_specifico["id"]))

            elif data_inizio >= date.today():
                # verifica numero prestiti attivi utente
                n_loan_user = loans_dao.max_loans(current_user.id)
                if n_loan_user >= 3:
                    flash(
                        "Hai raggiunto il numero massimo di prestiti attivi (3).",
                        "warning",
                    )
                    return redirect(url_for("book", id=book_specifico["id"]))

                # se il libro che si vuole prenotare è già stato prenotato o preso in prestito dallo stesso utente in un periodo che si sovrappone alla prenotazione/prestito che si vuole fare, non si può procedere
                # prendo date del libro in prestito/prenotato dallo stesso utente
                loans = loans_dao.get_loans_by_book(book_specifico["id"])
                for loan in loans:
                    if current_user.id == loan["user_id"] and loan["status"] in [0, 1]:
                        loan_start_date = datetime.strptime(
                            loan["start_date"], "%Y-%m-%d"
                        ).date()
                        loan_due_date = datetime.strptime(
                            loan["due_date"], "%Y-%m-%d"
                        ).date()
                        if (
                            data_inizio <= loan_due_date
                            and data_fine >= loan_start_date
                        ):
                            flash(
                                "Hai già un prestito attivo o una prenotazione per questo libro.",
                                "warning",
                            )
                        return redirect(url_for("book", id=book_specifico["id"]))
                    # se il libro non è prenotato o in prestito dallo stesso utente, procedo
                    #elif current_user.id != loan["user_id"] or loan["status"] not in [0, 1,]:
                
                
                loans_dao.new_loan(
                    current_user.id,
                    book_specifico["id"],
                    data_inizio_str,
                    data_fine.strftime("%Y-%m-%d"),
                )
                # diminuisco il numero di copie disponibili del libro
                books_dao.decrease_book_available_copies(book_specifico["id"])
                flash("Prenotazione avvenuta con successo.", "success")

    return redirect(url_for("catalogue"))


@app.route("/dismiss_loan/<int:loan_id>", methods=["POST"])
@login_required
def dismiss_loan(loan_id: int):
    if request.method == "POST":
        action = request.form.get("action")
        if action == "dismiss_loan":

            if not current_user:
                flash("Utente non trovato", "danger")
                return redirect(url_for("home"))

            current_date = date.today()
            # utente
            if current_user.role == 0:
                loan = loans_dao.get_loan_by_id(loan_id)
                data_inizio = datetime.strptime(
                    loan["start_date"], "%Y-%m-%d"
                ).date()
                data_annullamento_user = data_inizio - timedelta(days=1)
                # annullamento della prenotazione se non è ancora iniziata (possibile solo se manca almeno 1 giorno all'inizio del prestito)
                if (
                    current_date <= data_annullamento_user
                    and loan["status"] == 0
                ):
                    loans_dao.loan_dismiss(loan["id"])
                    # update dello status nel db a 3 (annullato)
                    loans_dao.loan_update_status(loan["id"], 3)
                    # aumento il numero di copie disponibili del libro
                    books_dao.increase_book_available_copies(loan["book_id"])
                    flash("Prenotazione annullata con successo", "success")

                    return redirect(url_for("profile"))

                elif current_date > data_annullamento_user and loan["status"] == 0:
                    flash("Tempo limite per l'annullamento scaduto", "danger")
                    return redirect(url_for("profile"))

            # bibliotecario
            elif current_user.role == 1:
                loan = loans_dao.get_loan_by_id(loan_id)
                
                data_inizio = datetime.strptime(
                    loan["start_date"], "%Y-%m-%d"
                ).date()
                
                data_annullamento_bibliotecario = data_inizio + timedelta(days=1)
                
                logger.warning(current_date)
                logger.warning(data_annullamento_bibliotecario) 

                # annullamento del prestito se attivo ma non ancora ritirato (possibile solo se lettore non ha ritirato il libro dopo 2 giorno dall'inizio del prestito)
                if (
                    current_date >= data_annullamento_bibliotecario
                    and loan["status"] == 0
                ):
                    loans_dao.loan_dismiss(loan["id"])
                    # update dello status nel db a 3 (annullato)
                    loans_dao.loan_update_status(loan["id"], 3)
                    # aumento il numero di copie disponibili del libro
                    books_dao.increase_book_available_copies(loan["book_id"])
                    flash("Prenotazione annullata con successo", "success")

                    return redirect(url_for("profile"))
                else:
                    flash("Non puoi annullare questa prenotazione", "danger")
                    return redirect(url_for("profile"))

    return redirect(url_for("profile"))


@app.route("/return_loan/<int:loan_id>", methods=["POST"])
@login_required
def return_loan(loan_id: int):
    if request.method == "POST":
        action = request.form.get("action")
        if action == "return_loan":

            if not current_user:
                flash("Utente non trovato", "danger")
                return redirect(url_for("home"))

            current_date = date.today()
            # utente
            if current_user.role == 0:
                loan_user = loans_dao.get_loans_by_user(current_user.id)
                for loan in loan_user:
                    data_inizio = datetime.strptime(loan['start_date'],"%Y-%m-%d").date()
                    data_fine = datetime.strptime(loan["due_date"], "%Y-%m-%d").date()
                    # restituzione del libro se il prestito è attivo
                    if loan["status"] == 1 and loan["id"] == loan_id and data_inizio <= current_date <= data_fine:
                        loans_dao.return_loan(loan["id"])
                        # update dello status nel db a 2 (restituito)
                        loans_dao.loan_update_status(loan["id"], 2)
                        # aumento il numero di copie disponibili del libro
                        books_dao.increase_book_available_copies(loan["book_id"])
                        # calcolo dei giorni di ritardo
                        ritardo = (current_date - data_fine).days
                        if ritardo > 0:
                            flash(
                                f"Libro restituito con successo. Hai un ritardo di {ritardo} giorni.",
                                "warning",
                            )
                        else:
                            flash("Libro restituito con successo.", "success")

                        return redirect(url_for("profile"))


@app.route("/start_loan/<int:loan_id>", methods=["POST"])
@login_required
def start_loan(loan_id: int):
    if request.method == "POST":
        action = request.form.get("action")
        if action == "start_loan":

            if not current_user:
                flash("Utente non trovato", "danger")
                return redirect(url_for("home"))

            current_date = date.today()
            # utente
            if current_user.role == 0:
                loan_user = loans_dao.get_loans_by_user(current_user.id)
                for loan in loan_user:
                    data_inizio = datetime.strptime(loan['start_date'],"%Y-%m-%d").date()
                    data_fine = datetime.strptime(loan['due_date'],"%Y-%m-%d").date()
                    if loan['status'] == 0 and loan['id'] == loan_id and data_inizio <= current_date <= data_fine:
                        # aggiorna lo status a 1 (attivo)
                        loans_dao.loan_update_status(loan["id"], 1)

                        return redirect(url_for("profile"))
                    


                #    data_inizio = datetime.strptime(loan['start_date'],"%Y-%m-%d").date()
                #    # data ultima per ritirare il libro
                #    data_ultima = data_inizio + timedelta(days=1)
                    
                #    if loan["status"] == 0 and loan["id"] == loan_id and data_inizio <= current_date <= data_ultima:
                #        loans_dao.loan_update_status(loan["id"], 1)
                        


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
