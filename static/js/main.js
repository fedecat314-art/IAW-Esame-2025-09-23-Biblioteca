document.addEventListener('DOMContentLoaded', function () {
    let toastElList = [].slice.call(document.querySelectorAll('.alert'));
    let toastList = toastElList.map(function (toastEl) {
        return new bootstrap.Toast(toastEl, {
            autohide: true,
            delay: 5000
        });
    });

    toastList.forEach(toast => toast.show());

    toastElList.forEach(function (toast) {
        toast.addEventListener('hidden.bs.alert', function () {
            toast.remove();
        });
    });
});
