import { getCookie } from './cookie-utils.js';
import { addRow, deleteRow, clearTable } from './jobs_for_line.js';
import { createCurrentBudget, setCurrentBudget, clearBudget, deductFromBudget} from './budget-utils.js';
import { openModal, closeModal } from './modal-utils.js';

document.addEventListener('DOMContentLoaded', function() {

    let teacherSelect = document.getElementById('teacher');
    let typeLoadElements = document.querySelectorAll(".type_load");
    let mainTable = document.getElementById('table_body');
    const downloadButton = document.getElementById('download-data');

    teacherSelect.addEventListener('input', getDataForTeacher);

    mainTable.addEventListener('input', function (event) {
        const target = event.target;

        // Проверяем, является ли элемент с классом 'group'
        if (target.classList.contains('group')) {
            onGroupElementChange.call(target);
        } 
        // Проверяем, является ли элемент с классом 'subject'
        else if (target.classList.contains('subject')) {
            onSubjectElementChange.call(target);
        } 
    });

    mainTable.addEventListener('focusout', function (event) {
        const target = event.target;
        // Проверяем, является ли элемент с классом 'data-element'
        if (target.classList.contains('data-element')) {   
            
            let row = target.id;
            let regex = /(\d+)/g;
            let matches = row.match(regex);
            let rowid = matches[0];
            let newVal = document.getElementById(row).value;

            // вызов отправки данных django
            let teacherSelect = document.getElementById('teacher').value;
            let groupSelect = document.getElementById(`group_${rowid}`).value;
            let subjectSelect = document.getElementById(`subject_${rowid}`).value;
            let semesterSelect = row[row.length - 1];
            let typeLoadSelect = row[row.length - 3];

            let url = `update-hours/${teacherSelect}/${groupSelect}/${subjectSelect}/${typeLoadSelect}/${semesterSelect}/`

            let data = {
                val: newVal
            }
            let requestOptions = {
                method: 'PUT',
                headers: {
                    'Content-type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken'),
                },
                body: JSON.stringify(data)
            }
            
            fetch(url, requestOptions)
            .then(response => {
                if (!response.ok) {
                throw new Error('Ошибка соединения');
                }
                return response.json();
            })
            .then(data => {
                if (data.status == 'success') {
                    onChangeHours.call(target, rowid, event);
                    document.getElementById(row).setAttribute('value', newVal);
                    document.getElementById(row).value = newVal;
                    if (data.is_null) {
                        deleteRow(rowid);
                    }

                } else if (data.status == 'validation-error') {
                    openModal(data.message, 'warning');
                    document.getElementById(row).value = data.data;
                    document.getElementById(row).setAttribute('value', data.data);
                } else {
                    document.getElementById(row).value = data.data;
                    document.getElementById(row).setAttribute('value', data.data);
                }

            })
            .catch(error => console.error('Error:', error));            
        }
    });

    downloadButton.addEventListener('click', function(event) {
        const year = document.getElementById('year').innerText;
        const teacher = teacherSelect.options[teacherSelect.selectedIndex].innerText;
        let data = {
            val: document.documentElement.innerHTML,
        }

        const requestOptions = {
            method: 'POST',
            headers: {
                'Content-type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify(data)
        };
        
        if (teacher) {
            fetch('download-data/', requestOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Ошибка соединения');
                }
                return response.blob();
            })
            .then(blob => {
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `${teacher}-${year}.xlsx`;  // Имя файла для скачивания
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);  // Освобождение ресурсов
            })
            .catch(error => console.error('Error:', error));
        } else {
            openModal('Выберите преподавателя!', 'warning');
        }
    });

    function getDataForTeacher() {
        let teacherId = teacherSelect.options[teacherSelect.selectedIndex].value;
        clearTable();
        clearBudget();
        fetch(`get-all-data-for-teacher/${teacherId}/`)
        .then(response => response.json())
        .then(data => {
            teacherSelect.disabled = true;
            setTeacherElementAndDocTitle();
            data.data.forEach(function (teacherData) {
                let curGroup = addRow(true);
                curGroup.options[curGroup.selectedIndex].value = teacherData.group;
                curGroup.options[curGroup.selectedIndex].innerText = teacherData.name_group;
                curGroup.options[curGroup.selectedIndex].setAttribute('data-is-paid', teacherData.group_is_paid);

                let curSubject = onGroupElementChange.call(curGroup, true);
                curSubject.options[curSubject.selectedIndex].value = teacherData.subject_id;
                curSubject.options[curSubject.selectedIndex].innerText = teacherData.subject_name;
                curSubject.options[curSubject.selectedIndex].setAttribute('data-is-paid', teacherData.subject_is_paid);
                
                onSubjectElementChange.call(curSubject, true);
            });
            teacherSelect.disabled = false;

        });
    };

    function setTeacherElementAndDocTitle() {
        let selectedValue = teacherSelect.options[teacherSelect.selectedIndex];
        let firstOption = teacherSelect.options[0];
        firstOption.value = selectedValue.value;
        firstOption.innerText = selectedValue.innerText;
        document.title = teacherSelect.options[teacherSelect.selectedIndex].text;
    }

    function onGroupElementChange(flag=false) {

        
        let selectedTeacherId = teacherSelect.value;
        let selectedGroupId = this.value;

        let subjectId = 'subject_' + this.id.split('_')[1];
        let subjectElement = document.getElementById(subjectId);
        
        let groupSelected = document.getElementById('group_' + this.id.split('_')[1])
        let selectedValue = groupSelected.options[groupSelected.selectedIndex];
        let firstOption = groupSelected.options[0];

    
        if (!flag) {
            let subjectValue = subjectElement.options[subjectElement.selectedIndex];
            
            if (subjectValue.value){
                
                let group = firstOption.value;
                let subjectSelectId = subjectValue.value;
                
                deleteTeacherRow(selectedTeacherId, group, subjectSelectId);
            };
            
            
            let row = mainTable.rows[this.id.split('_')[1] - 1];
            let cells = row.cells;
            let last = typeLoadElements.length * 2 + 3 + 3;

            let budget = cells[last - 3].getElementsByTagName('input')[0].value;
            let extraBudget = cells[last - 2].getElementsByTagName('input')[0].value;
            let totalBudget = cells[last - 1].getElementsByTagName('input')[0].value;
            if (budget || extraBudget || totalBudget) {
                deductFromBudget(budget, extraBudget, totalBudget);
            }
            for (let j = 3; j < last; j++) {
                cells[j].getElementsByTagName('input')[0].value = 0;
                cells[j].getElementsByTagName('input')[0].setAttribute('value', 0);
                cells[j].getElementsByTagName('input')[0].disabled = true;
            }

        }
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
        
        if (flag) {
            return subjectElement;
        }
    }

    function onSubjectElementChange(flag=false) {
        let curSubject = this;
        let rowId = this.id.split('_')[1];
        let selectedTeacherId = teacherSelect.value;
        let selectedSubjectId = this.value;
        let groupId = `group_${rowId}`;
        let selectedGroupId = document.getElementById(groupId).value;

        let subjectSelected = document.getElementById('subject_' + this.id.split('_')[1])
        let selectedValue = subjectSelected.options[subjectSelected.selectedIndex];
        let firstOption = subjectSelected.options[0];
        
        if (!flag) {
            
        };
        if (flag) {
            fetchData(selectedTeacherId, selectedGroupId, selectedSubjectId, typeLoadElements,
                 rowId, flag, firstOption, selectedValue) 
        } else {
        let valInBase = checkDoubleValue(rowId, selectedGroupId, selectedValue);
            if (valInBase) {
                curSubject.value = firstOption.value;
                return
            };
        validateHoursLoad(selectedGroupId, selectedSubjectId)
        .then(function(isValid) {
            if (!isValid) {
                curSubject.value = firstOption.value;
                return
            } else {

                if (firstOption.value) {
                    
                    let subj = firstOption.value;
                    deleteTeacherRow(selectedTeacherId, selectedGroupId, subj);
                };
                fetchData(selectedTeacherId, selectedGroupId, selectedSubjectId, typeLoadElements,
                     rowId, flag, firstOption, selectedValue) 
            }
        })
        .catch(function(error) {
            console.error("Произошла ошибка при проверке:", error);
        }); 
        }
    };

});

function onChangeHours(curRowId) {
    let budget_sum = createCurrentBudget(curRowId-1);
    setCurrentBudget(curRowId-1, budget_sum);   
}

function checkDoubleValue(rowId, selectedGroupId, selectedValue) {
    let table = document.getElementById('table_body');
    let rowCount = table.rows.length;

    for (let i = 0; i < rowCount; i++) {
        let rowGroup = table.rows[i].cells[2].getElementsByTagName('select')[0].value;
        let rowSubject =  table.rows[i].cells[1].getElementsByTagName('select')[0].value;
        if (i == rowId - 1) continue
        if (selectedValue.value == rowSubject && selectedGroupId == rowGroup) {
            openModal('У этого преподавателя уже есть такой предмет', 'warning');
            return true
        }
        
    };
    return false
}

function createRowForTeacher (selectedTeacherId, selectedGroupId, selectedSubjectId, 
    firstOption, selectedValue) {
    fetch(`/create-row-for-teacher/${selectedTeacherId}/${selectedGroupId}/${selectedSubjectId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            console.error('Ошибка создания записи');
        }
    })
    .catch(error => {
        console.error('Ошибка запроса:', error);
    });
    firstOption.value = selectedValue.value;
    firstOption.innerText = selectedValue.innerText;
}


function validateHoursLoad (selectedGroupId, selectedSubjectId) {
    let url = `validate-group-has-subject-unallocated-hours/${selectedGroupId}/${selectedSubjectId}`;
    return fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data.status === 'validation-error') {
                openModal(data.message, 'warning');
                return false;
            } else if (data.status === 'error') {
                console.log('Ошибка при валидации данных');
                return false;
            } else {
                return true;
            }
        })
        .catch(error => {
            console.error('Ошибка запроса:', error);
            return false;
        });
}

function fetchData(selectedTeacherId, selectedGroupId, selectedSubjectId, typeLoadElements, rowId, flag,
    firstOption, selectedValue) {
    let fetchPromises = Array.from(typeLoadElements).map(typeLoad => {
        return fetch(`/get-hours/${selectedTeacherId}/${selectedGroupId}/${selectedSubjectId}/${typeLoad.id}/`)
            .then(response => response.json())
            .then(data => {
                let semester = 1;
                data.forEach(function(hour_load) {
                    let semesterVal = 0;
                    if (hour_load.cur_exam !== null) {
                        semesterVal = hour_load.cur_exam;
                    } else {
                        semesterVal = hour_load.cur_hours;
                    }
                    let semesterId = `type-load_${rowId}_${typeLoad.id}_${semester}`;
                    document.getElementById(semesterId).value = semesterVal;
                    document.getElementById(semesterId).setAttribute('value', semesterVal);
                    document.getElementById(semesterId).disabled = false;
                    semester++;
                });
            })
            .catch(error => {
                console.error('Error fetching subjects:', error);
            });
    });

    Promise.all(fetchPromises)
        .then(() => {
            let budget_sum = createCurrentBudget(rowId - 1);
            setCurrentBudget(rowId - 1, budget_sum);
            if (!flag) {
                createRowForTeacher(selectedTeacherId, selectedGroupId, selectedSubjectId,
                    firstOption, selectedValue);
            };
        });
}

function deleteTeacherRow(selectedTeacherId, selectedGroupId, subjectSelectId) {
    fetch(`/delete-row-for-teacher/${selectedTeacherId}/${selectedGroupId}/${subjectSelectId}/`, {
        method: 'DELETE',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken'),
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            console.error('Ошибка при удалении записи состояния');
        }
    })
    .catch(error => {
        console.error('Ошибка запроса:', error);
    });
}

let modal = document.getElementById("myModal");
let span = document.getElementsByClassName("close")[0];
  
  // Закрываем модальное окно при нажатии на крестик
  span.onclick = function() {
    closeModal();
  }
  
  // Закрываем модальное окно при клике вне его области
  window.onclick = function(event) {
    if (event.target == modal) {
      closeModal();
    }
  }
  
