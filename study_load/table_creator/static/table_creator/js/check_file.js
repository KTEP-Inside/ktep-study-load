document.addEventListener('DOMContentLoaded', function() {
    let form = document.getElementById("uploadForm");

    form.addEventListener('input', checkFileSelection);

    function checkFileSelection() {
        console.log(1);
        let fileInput = document.getElementById('uploadForm_File');
        let submitButton = document.getElementById('uploadForm_Submit');
        if (fileInput.files.length > 0) {
            submitButton.disabled = false; // Включаем кнопку
            submitButton.style.cursor = 'pointer';
            submitButton.classList.add('active-button');
        } else {
            submitButton.disabled = true;  // Выключаем кнопку
            submitButton.style.cursor = 'default';
            submitButton.classList.remove('active-button');
        }
    }
});