import { getCookie } from './cookie-utils.js';
let unallocatedGroups = document.getElementById('unallocated-groups');
let unallocatedSubjects = document.getElementById('unallocated-subjects');

document.addEventListener('DOMContentLoaded', function() {

    unallocatedGroups.addEventListener('input', function() {
        getSubjects(unallocatedGroups.value);
        openModal();
    });

    unallocatedSubjects.addEventListener('input', function() {
        getUnallocatedData(unallocatedGroups.value, unallocatedSubjects.value)
    });

});

function getSubjects(selectedGroupId) {
    
    let subjectElement = document.getElementById('unallocated-subjects');
    let selectedValue = unallocatedGroups.options[unallocatedGroups.selectedIndex];
    let firstOption = unallocatedGroups.options[0];
    subjectElement.innerHTML = '<option value="" selected disabled></option>';

    firstOption.value = selectedValue.value;
    firstOption.innerText = selectedValue.innerText;

    fetch(`/get-subjects/${selectedGroupId}/`)
        .then(response => response.json())
        .then(data => {
            data.forEach(function (subject) {
                let option = document.createElement('option');
                option.value = subject.pk;
                option.text = subject.name;
                option.setAttribute('data-is-paid', subject.is_paid);

                subjectElement.add(option);
            });
            subjectElement.disabled = false;
        })
        .catch(error => {
            console.error('Error fetching subjects:', error);
        });

    getUnallocatedData(selectedGroupId);
};
// динамически отправляем содержимое
function getUnallocatedData(groupId=null, subjectId=null) {

    let url = `/unallocated-hours-content-update/${groupId}/`;
    if (subjectId) {
        url = `/unallocated-hours-content-update/${groupId}/${subjectId}/`
    }
    
    fetch(url)
    .then(response => {
        if (!response.ok) {
        throw new Error('Ошибка соединения');
        }
        return response.json();
    })
    .then(data => {
        console.log(data);
        let list = document.getElementById('unallocated-rows-list');
        while (list.firstChild) {
            list.removeChild(list.firstChild);
        }
        for (let obj of data.data) {
            let liElement = document.createElement('li');
            liElement.textContent = obj;
            list.appendChild(liElement);
        }

        if (list.childElementCount === 0) {
            let liElement = document.createElement('h2');
            liElement.textContent = 'Ничего не найдено';
            list.appendChild(liElement);
        }
    })
    .catch(error => console.error('Error:', error));            
}
