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
    ("Il buio oltre la siepe", "Harper Lee", 2, 1960, "In una sonnolenta cittadina del profondo Sud degli Stati Uniti l'avvocato Atticus Finch è incaricato della difesa d'ufficio di un afroamericano accusato di aver stuprato una ragazza bianca. Riuscirà a dimostrarne l'innocenza, ma l'uomo sarà ugualmente condannato a morte. Questo, in poche righe, l'episodio centrale di un romanzo che da quando è stato pubblicato, oltre cinquant'anni fa, non ha più smesso di appassionare non soltanto i lettori degli Stati Uniti, ma quelli di tutti i paesi del mondo dove è stato tradotto. Non si esagera dicendo che non c'è americano che non l'abbia letto da bambino o da adolescente e che non l'abbia consigliato a figli e nipoti. Eppure non è un libro per ragazzi, ma un affresco colorito e divertente della vita nel Sud ai tempi delle grandi piantagioni di cotone, dei braccianti neri che le coltivavano, delle cuoche di colore che allevavano i figli dei discendenti delle grandi famiglie dell'Ottocento, della white trash, i \"bianchi poveri\" abbrutiti e alcolizzati; e anche, purtroppo, delle sentenze sommarie di giurie razziste e degli ultimi linciaggi americani della storia. Quale il segreto della forza di questo libro? La sua voce narrante, che è quella della piccola Scout, la figlia di Atticus, una Huckleberry Finn in salopette (dire \"in gonnella\" sarebbe inesatto, perché Scout è una maschiaccia impertinente e odia vestirsi da donna) che, ora sola ora in compagnia del fratello maggiore e del loro amico più caro (ispirato all'autrice dal suo amico d'infanzia Truman Capote), ci racconta la storia di Maycomb, Alabama, della propria famiglia, delle pettegole signore della buona società che vorrebbero farla diventare una di loro, di bianchi e neri per lei tutti uguali, e della vana battaglia paterna per salvare la vita di un innocente.", "images/covers/book_2.jpg", 3, 3),
    ("Il grande Gatsby", "F. Scott Fitzgerald", 1, 1925, "«Non si può ripetere il passato? Certo che si può!»\n«Il grande Gatsby» ovvero l\'età del jazz: luci, party, belle auto e vestiti da cocktail, ma dietro la tenerezza della notte si cela la sua oscurità, la sua durezza, il senso di solitudine con il quale può strangolare anche la vita più promettente. Il giovane Nick Carraway, voce narrante del romanzo, si trasferisce a New York nell\'estate del 1922. Affitta una casa nella prestigiosa e sognante Long Island, brulicante di nuovi ricchi disperatamente impegnati a festeggiarsi a vicenda. Un vicino di casa colpisce Nick in modo particolare: si tratta di un misterioso Jay Gatsby, che abita in una casa smisurata e vistosa, riempiendola ogni sabato sera di invitati alle sue stravaganti feste. Eppure vive in una disperata solitudine e si innamorerà insensatamente della cugina sposata di Nick, Daisy... Il mito americano si decompone pagina dopo pagina, mantenendo tutto lo sfavillio di facciata ma mostrando anche il ventre molle della sua fragilità. Proprio come andava accadendo allo stesso Fitzgerald, ex casanova ed ex alcolizzato alle prese con il mistero di un\'esistenza ormai votata alla dissoluzione finale.", "images/covers/book_3.jpg", 4, 4),
    ("Moby Dick", "Herman Melville", 3, 1851, "Un uomo e un mostruoso cetaceo si fronteggiano: è il conflitto più aspro, accanito e solitario mai immaginato, è la storia di ogni anima che si spinga a guardare oltre l'abisso. Moby Dick è un gigantesco capodoglio, candida fonte di orrore e meraviglia; Achab è un capitano che, ossessionato da follia vendicatrice, lo insegue fino all'ultimo respiro; Ismaele, un marinaio dall'oscuro passato imbarcato sulla baleniera Pequod, è il narratore e, forse, l'eroe della tragedia. Sullo sfondo, il ribollire sordo e terribile dell'oceano, il vociare cosmopolita dell'equipaggio, le descrizioni anatomiche delle balene e i puntuali resoconti di caccia. Così, pagina dopo pagina, i personaggi del dramma diventano i protagonisti di una nuova epica, con il fascino ambiguo e controverso di un destino contemporaneo. Con un saggio di Harold Bloom.", "images/covers/book_4.jpg", 2, 2),
    ("Orgoglio e pregiudizio", "Jane Austen", 4, 1813, "«Non aveva mai capito di amarlo tanto come ora, quando l'amore era vano.»"
    "Jane Austen è una delle poche, autentiche grandi scrittrici che hanno saputo fare breccia nei cuori e nelle menti di utti i lettori, senza eccezioni. Fra i suoi tanti capolavori, Orgoglio e pregiudizio (pubblicato nel 1813) è sicuramente il più popolare e amato: le cinque figlie dell'indimenticabile Mrs Bennet, tutte in cerca di un'adeguata sistemazione matrimoniale, offrono l'occasione per tracciare un quadro frizzante e profondo della vita nella campagna inglese di fine Settecento. I destini di Elizabeth, Jane, Mr Bingley e dell'ombroso Mr Darcy intrecciano un balletto irresistibile, una danza psicologica che getta luce sulla multiforme imprendibilità dell'animo umano, specie quando si trova alle prese con l'amore o qualcosa che all'amore somiglia.", "images/covers/book_5.jpg", 6, 6),
    ("Il giovane Holden", "J.D. Salinger", 1, 1951, "Il libro che ha sconvolto il corso della letteratura contemporanea influenzando l'immaginario collettivo e stilistico del Novecento.\nSono passati più di sessant'anni da quando è stato scritto, ma continuiamo a vederlo, Holden Caufield, con quell'aria scocciata, insofferente alle ipocrisie e al conformismo, lui e tutto quello che gli è cascato addosso dal giorno in cui lasciò l'Istituto Pencey con una bocciatura in tasca e nessuna voglia di farlo sapere ai suoi. La trama è tutta qui, narrata da quella voce spiccia e senza fronzoli. Ma sono i suoi pensieri, il suo umore rabbioso, ad andare in scena. Perché è arrabbiato Holden? Poiché non lo si sa con precisione, ciascuno vi ha letto la propria rabbia, ha assunto il protagonista a \"exemplum vitae\", e ciò ne ha decretato l'immenso successo che dura tuttora. Torna, in una nuova traduzione di Matteo Colombo, il libro che ha sconvolto il corso della letteratura contemporanea influenzando l'immaginario collettivo e stilistico del Novecento.", "images/covers/book_6.jpg", 4, 4),
    ("Il nome della rosa", "Umberto Eco", 5, 1980, "Un’opera preziosa che racconta il nostro tempo, il passato e le sue meraviglie di pietra e inchiostro. Milo Manara, maestro del fumetto classico contemporaneo, firma l’adattamento a fumetti di Il nome della rosa, capolavoro e best seller mondiale di Umberto Eco. Un libro unico che mette su carta tre distinti stili grafici che si intersecano inseguendo la perfezione visiva. Ciascuno racconta un aspetto del libro di Eco: le sculture, i rilievi dei portali e i marginalia meravigliosi e surreali che corredano i libri miniati della biblioteca; il romanzo di formazione di Adso, con la scoperta della sensualità e della Donna; la vicenda storica dei Dolciniani, i cui temi della povertà degli ultimi, la non omologazione, la diversità perseguitata e il dissenso sono cruciali anche oggigiorno. Il nome della rosa di Manara trova quindi spazio nell’operazione “matrioska” letteraria del libro di Umberto Eco, che è anche un libro sui libri che contengono altri libri e aprono ad altri mondi.", "images/covers/book_7.jpg", 3, 3),
    ("La coscienza di Zeno", "Italo Svevo", 1, 1923, "Rimasto incompreso per lungo tempo, \"La coscienza di Zeno\" è il più importante romanzo di Svevo e uno dei capolavori della letteratura italiana contemporanea. È il resoconto di un viaggio nell'oscurità della psiche, nella quale si riflettono complessi e vizi della società borghese dei primi del Novecento, le sue ipocrisie, i suoi conformismi e insieme la sua nascosta, tortuosa, ambigua voglia di vivere. L'inettitudine ad aderire alla vita, l'eros come evasione e trasgressione, il confine incerto tra salute e malattia divengono i temi centrali su cui si interroga Zeno Cosini in queste pagine bellissime che segnarono l'inizio di un modo nuovo di intendere la narrativa. Primo romanzo \"psicoanalitico\" della nostra letteratura, quest'opera rivoluzionaria seppe interpretare magistralmente le ansie, i timori e gli interrogativi più profondi di una società in cambiamento.", "images/covers/book_8.jpg", 2, 2),
    ("Cent'anni di solitudine", "Gabriel García Márquez", 1, 1967, "Da José Arcadio ad Aureliano Babilonia, dalla scoperta del ghiaccio alle pergamene dello zingaro Melquíades finalmente decifrate: cent'anni di solitudine della grande famiglia Buendía, i cui componenti vengono al mondo, si accoppiano e muoiono per inseguire un destino ineluttabile. Con questo romanzo tumultuoso che usa i toni della favola, sorretto da un linguaggio portentoso e da un'inarrestabile fantasia, Gabriel García Márquez ha saputo rifondare la realtà e, attraverso Macondo, il mitico villaggio sperduto fra le paludi, creare un vero e proprio paradigma dell'esistenza umana. In questo universo di solitudini incrociate, impenetrabili ed eterne, galleggia una moltitudine di eroi predestinati alla sconfitta, cui fanno da contraltare la solidità e la sensatezza dei personaggi femminili. Con la sua forza, il suo bagaglio di visioni e di prodigi, con la sua capacità di reinventare il mondo, Cent'anni di solitudine è il libro rivelazione che ha rivoluzionato il modo di narrare e ha aperto alla forma romanzo una nuova stagione di successi. Un capolavoro insuperato e insuperabile, un racconto tra i più amati di ogni tempo, un «romanzo ideale», secondo le parole dello stesso autore, «capace di rivoltare la realtà per mostrarne il rovescio».", "images/covers/book_9.jpg", 5, 5),
    ("Il signore degli anelli", "J.R.R. Tolkien", 4, 1954, "Il Signore degli Anelli è un romanzo d'eccezione, al di fuori del tempo: chiarissimo ed enigmatico, semplice e sublime. Dona alla felicità del lettore ciò che la narrativa del nostro secolo sembrava incapace di offrire: avventure in luoghi remoti e terribili, episodi d'inesauribile allegria, segreti paurosi che si svelano a poco a poco, draghi crudeli e alberi che camminano, città d'argento e di diamante poco lontane da necropoli tenebrose in cui dimorano esseri che spaventano solo al nominarli, urti giganteschi di eserciti luminosi e oscuri; e tutto questo in un mondo immaginario ma ricostruito con cura meticolosa, e in effetti assolutamente verosimile, perché dietro i suoi simboli si nasconde una realtà che dura oltre e malgrado la storia: la lotta, senza tregua, fra il bene e il male. Leggenda e fiaba, tragedia e poema cavalleresco, il romanzo di Tolkien è in realtà un'allegoria della condizione umana che ripropone in chiave moderna i miti antichi.", "images/covers/book_10.jpg", 4, 4),
    ("Dracula", "Bram Stoker", 8, 1897, "Fra le dense nebbie di una Londra fin de siècle e la misteriosa Transilvania, prende vita la vicenda del giovane avvocato Jonathan Harker, che deve recarsi in Transilvania per curare l'acquisto di un'abitazione londinese da parte di un anziano nobile del posto. In un crescendo di tensione e terrore, il giovane protagonista scoprirà il terribile segreto dell'uomo: il conte Dracula è un vampiro che si nutre di sangue umano! Scritto sotto forma di raccolta di lettere, articoli e brani dei diari dei protagonisti, come se si trattasse di un'inchiesta giornalistica, si succedono sanguinarie e terrificanti situazioni immerse in atmosfere cupe e misteriose.", "images/covers/book_11.jpg", 3, 3),
    ("La fattoria degli animali", "George Orwell", 1, 1945, "Una favola morale senza tempo che mette in guardia dal tremendo fascino del potere, valida oggi come nei giorni in cui è stata scritta.\nTutti gli animali sono uguali ma alcuni animali sono piú uguali degli altri. È questa l'amara lezione che le umane bestie della Fattoria Padronale imparano dopo aver detronizzato il fattore Jones, e aver instaurato il loro governo. In poco tempo infatti una grufolante élite, guidata dal maiale Napoleone, trova il modo di salire sullo stesso trono che prima era stato del fattore. Cosí gli altri animali scoprono che uguaglianza e libertà, in bocca a chi desidera il controllo assoluto, sono soltanto parole, e si ritrovano sotto il giogo di una nuova tirannia dal volto diverso ma identica alla precedente. Perché come è accaduto sempre nella Storia, e come continuerà ad accadere, a un potere immancabilmente se ne sostituisce un altro.", "images/covers/book_12.jpg", 4, 4),
    ("Il codice Da Vinci", "Dan Brown", 5, 2003, "Un thriller denso di enigmi e colpi di scena, che ha conquistato milioni di lettori e ridefinito il genere del thriller storico.\nUn delitto inspiegabile. Un messaggio nascosto nei secoli. Un segreto capace di riscrivere la storia. Quando il curatore del Louvre, Jacques Saunière, viene assassinato, l’ultimo enigma che lascia dietro di sé conduce a un nome: Robert Langdon. Il celebre professore di simbologia di Harvard viene convocato sulla scena del crimine, ma ben presto si rende conto di essere il principale sospettato. Affiancato dalla crittologa Sophie Neveu, nipote della vittima, Langdon inizia una disperata corsa contro il tempo tra Parigi e Londra. Il loro viaggio si snoda attraverso codici nascosti nelle opere di Leonardo da Vinci, antiche società segrete e un mistero legato al Santo Graal, capace di sconvolgere la storia del Cristianesimo. Ogni scoperta li avvicina alla verità, ma li espone a pericoli mortali.", "images/covers/book_13.jpg", 6, 6),
    ("La strada", "Cormac McCarthy", 1, 2006, "Dal celebre romanzo di Cormac McCarthy, premio Pulitzer 2007, Manu Larcenet ha tratto un adattamento a fumetti di strabiliante potenza visiva e narrativa.\nUn padre e un figlio attraversano le rovine di un mondo post-apocalittico ridotto in cenere. Camminano da soli in direzione dell’oceano, sostenendosi a vicenda e lottando passo dopo passo contro la fame, il freddo, le bande di predoni e ogni sorta di insidie, mentre la civiltà non esiste più e la sopravvivenza sembra essere l’unica legge. In questa oscurità senza speranza resta solo il fuoco dell’amore a indicare loro la via.", "images/covers/book_14.jpg", 2, 2),
    ("Il piccolo principe", "Antoine de Saint-Exupéry", 1, 1943, "\"Il Piccolo Principe\" è la storia dell'incontro in mezzo al deserto tra un aviatore e un buffo ometto vestito da principe che è arrivato sulla Terra dallo spazio. Ma c'è molto di più di una semplice amicizia in questo libro surreale, filosofico e magico. C'è la saggezza di chi guarda le cose con occhi puri, la voce dei sentimenti che parla la lingua universale, e una sincera e naturale voglia di autenticità. Perché la bellezza, quando non è filtrata dai pregiudizi, riesce ad arrivare fino al cuore dei bambini, ma anche a quello degli adulti che hanno perso la capacità di ascoltare davvero.", "images/covers/book_15.jpg", 5, 5),
    ("Il ritratto di Dorian Gray", "Oscar Wilde", 1, 1890, "Dorian Gray, un giovane di straordinaria bellezza, si è fatto fare un ritratto da un pittore. Ossessionato dalla paura della vecchiaia, ottiene, con un sortilegio, che ogni segno che il tempo dovrebbe lasciare sul suo viso, compaia invece solo sul ritratto. Avido di piacere, si abbandona agli eccessi più sfrenati, mantenendo intatta la freschezza e la perfezione del suo viso. Poiché Hallward, il pittore, gli rimprovera tanta vergogna, lo uccide. A questo punto il ritratto diventa per Dorian un atto d'accusa e in un impeto di disperazione lo squarcia con una pugnalata. Ma è lui a cadere morto: il ritratto torna a raffigurare il giovane bello e puro di un tempo e a terra giace un vecchio segnato dal vizio.", "images/covers/book_16.jpg", 3, 3),
    ("La metamorfosi", "Franz Kafka", 1, 1915, "Nell'autunno del 1912, a Praga, tra 17 novembre e il 7 dicembre, Franz Kafka scrisse \"La metamorfosi\", l'incubo sotterraneo e letterale di Gregor Samsa, un commesso viaggiatore che si sveglia un mattino dopo sogni agitati e si ritrova mutato in un enorme insetto. La speranza di recuperare la condizione perduta, i tentativi di adattarsi al nuovo stato, i comportamenti familiari e sociali, l'oppressione della situazione, lo svanire del tempo sono gli ingredienti con i quali l'autore elabora la trama dell'uomo contemporaneo, un essere condannato al silenzio, alla solitudine e all'insignificanza.", "images/covers/book_17.jpg", 4, 4),
    ("Il gabbiano Jonathan Livingston", "Richard Bach", 1, 1970, "Il gabbiano Jonathan Livingston non è come tutti gli altri. Là dove i suoi simili, schiavi di becco e pancia, si limitano a composti viaggetti per procurarsi il cibo inseguendo le barche da pesca, lui intuisce nel volo una bellezza e un valore assoluti. Tanto basta per meritargli il marchio dell’infamia e l’allontanamento dallo stormo Buonappetito. Solo, audace, sempre più libero, Jonathan il Reietto scopre l’ebbrezza del volo acrobatico e varca i confini di altri mondi, altre dimensioni abitate da gabbiani solitari simili a lui nella spasmodica fame e sete di perfezione. Ne diventa la guida, il capo indiscusso, e tra i compagni incontrerà chi senza saperlo è pronto a raccogliere la sua eredità. Un grandissimo romanzo-culto che, dopo cinquant’anni dalla prima edizione, conferma la sua straordinaria vitalità grazie anche all’imperdibile finale, scritto da Bach dopo un’esperienza tra la vita e la morte. Un racconto che parla all’anima con la forza di una visione e ci insegna a spiccare il volo e conoscere noi stessi.", "images/covers/book_18.jpg", 2, 2),
    ("Il diario di Anna Frank", "Anna Frank", 2, 1947, "Quando Anne inizia il suo diario, nel giugno del 1942, ha appena compiuto tredici anni. Poche pagine, e all'immagine della scuola, dei compagni e di amori più o meno ideali, si sostituisce la storia della lunga clandestinità. Obbedendo a una sicura vocazione di scrittrice, Anne ha voluto e saputo lasciare testimonianza di sé e dell'esperienza degli altri clandestini. La prima edizione del \"Diario\" subì tuttavia non pochi tagli, ritocchi, variazioni. Il testo, restituito alla sua integrità originale, ci consegna un'immagine nuova: quella di una ragazza vera, ironica, passionale, irriverente, animata da un'allegra voglia di vivere, già adulta nelle sue riflessioni. Questa edizione, in appendice, offre anche una ricostruzione degli ultimi mesi della vita di Anne e della sorella Margot, sulla base di testimonianze e documenti raccolti negli anni. Prefazione di Eraldo Affinati.", "images/covers/book_19.jpg", 3, 3),
    ("V per Vendetta", "Alan Moore e David Lloyd", 12, 1988, "In un’Inghilterra futuristica e oppressa da un regime totalitario, una misteriosa figura coperta da una maschera di porcellana si ribella all’oppressore. Armato solo di coltelli e del suo ingegno, il vigilante che si fa chiamare V è intenzionato a portare la rivoluzione nel mondo. La sua unica alleata è la giovane Evey Hammond, che potrebbe aver fatto il passo più lungo della gamba... L’opera che ha cementato la fama di Alan Moore lanciandolo nell’olimpo degli autori più celebrati al mondo, illustrata con maestria dal grande David Lloyd.", "images/covers/book_20.jpg", 4, 4),
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
