document.addEventListener('DOMContentLoaded', function() {
    let printButton = document.getElementById('print-button');

    printButton.addEventListener('click', function() {
        window.print();
    });
});