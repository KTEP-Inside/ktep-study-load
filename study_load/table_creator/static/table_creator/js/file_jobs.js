document.addEventListener('DOMContentLoaded', function() {
    let form = document.getElementById("uploadForm");
    const loaderContainer = document.getElementById('loader-container');
    const uploadForm = document.getElementById('uploadForm');

    form.addEventListener('input', checkFileSelection);
    uploadForm.addEventListener('submit', showLoader)

    function checkFileSelection() {
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

    function showLoader() {
        loaderContainer.style.display = 'block';
    }

});