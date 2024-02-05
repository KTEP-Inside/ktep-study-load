
let year = document.getElementById('education_year');


function setCurrentYear() {

    let currentYear = new Date().getFullYear();
    let nextYear = currentYear + 1;
    let yearsString = currentYear + ' - ' + nextYear;
    document.getElementById('year').innerText = yearsString;
};

setCurrentYear();
