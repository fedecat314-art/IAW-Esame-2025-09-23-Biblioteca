document.addEventListener('DOMContentLoaded', function () {
    const dataInizio = document.getElementById('dataInizio');
    const dataFine = document.getElementById('dataFine');

    if (dataInizio && dataFine) {
        dataInizio.addEventListener('change', function () {
            const startDate = new Date(this.value);
            if (!isNaN(startDate)) {
                startDate.setDate(startDate.getDate() + 14);
                const yyyy = startDate.getFullYear();
                const mm = String(startDate.getMonth() + 1).padStart(2, '0');
                const dd = String(startDate.getDate()).padStart(2, '0');
                dataFine.value = `${yyyy}-${mm}-${dd}`;
            } else {
                dataFine.value = '';
            }
        });
    }
});