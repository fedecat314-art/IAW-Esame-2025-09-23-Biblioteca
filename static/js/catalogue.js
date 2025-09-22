document.addEventListener('DOMContentLoaded', function () {
    const params = new URLSearchParams(window.location.search);

    // Imposta il filtro genere
    const genre = params.get('genre');
    if (genre) {
        const genreSelect = document.getElementById('genreFilter');
        if (genreSelect) genreSelect.value = genre;
    }

    // Imposta il campo di ricerca
    const search = params.get('search');
    if (search) {
        const searchInput = document.querySelector('input[name="search"]');
        if (searchInput) searchInput.value = search;
    }
});