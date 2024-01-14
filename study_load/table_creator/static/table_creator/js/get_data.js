document.addEventListener('DOMContentLoaded', function() {
    
    let teacherSelect = document.getElementById('teacher');
    let mainTable = document.getElementById('table_body');
    let typeLoadElements = document.querySelectorAll(".type_load");
    let tableResults = document.getElementById('table_results');

    teacherSelect.addEventListener('input', updateGroups);

    mainTable.addEventListener('input', function (event) {
        const target = event.target;

        // Проверяем, является ли элемент с классом 'group'
        if (target.classList.contains('group')) {
            onGroupElementChange.call(target, event);
        } 
        // Проверяем, является ли элемент с классом 'subject'
        else if (target.classList.contains('subject')) {
            onSubjectElementChange.call(target, event);
        } 
    });

    mainTable.addEventListener('focusout', function (event) {
        const target = event.target;
        // Проверяем, является ли элемент с классом 'data-element'
        if (target.classList.contains('data-element')) {   
            
            // Извлекаем номер строки из ID
            let row = target.id;
            
            let regex = /(\d+)/g;
            let matches = row.match(regex);
            let rowid = matches[0];
            let prevVal = document.getElementById(row).value

            
            // вызов отправки данных django
            let teacherSelect = document.getElementById('teacher').value;
            let groupSelect = document.getElementById(`group_${rowid}`).value;
            let subjectSelect = document.getElementById(`subject_${rowid}`).value;
            let semesterSelect = row[row.length - 1];
            let typeLoadSelect = row[row.length - 3];

            let url = `update-hours/${teacherSelect}/${groupSelect}/${subjectSelect}/${typeLoadSelect}/${semesterSelect}/`

            let data = {
                val: prevVal
            }
            console.log(data);
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
                console.log(data);
                if (data.status == 'success') {
                    onChangeHours.call(target, rowid, event);
                    
                } else if (data.status == 'validation-error') {
                    alert(data.message);
                    document.getElementById(row).value = data.data;
                } else {
                    document.getElementById(row).value = data.data;
                }

            })
            .catch(error => console.error('Error:', error));

            
        }
    });

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = cookies[i].trim();
                // Ищем куки с нужным именем
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function updateGroups() {
        let selectedTeacherId = teacherSelect.value;
        let groupElements = document.querySelectorAll('.group');
        let subjectElements = document.querySelectorAll('.subject');

        if (mainTable.rows.length >= 1) {
            for (let rowIdx = 0; rowIdx < mainTable.rows.length; rowIdx++) {

                let row = mainTable.rows[rowIdx];
                let cells = row.cells;
                let last = typeLoadElements.length * 2 + 3 + 3;

                for (let j = 3; j < last; j++) {
                    cells[j].getElementsByTagName('input')[0].value = 0;
                    cells[j].getElementsByTagName('input')[0].disabled = true;
                }
            }
            for (let rowIdx = 0; rowIdx < tableResults.rows.length; rowIdx++) {
                let row = tableResults.rows[rowIdx];
                let cells = row.cells;
    
                for (let j = 2; j < 5; j++) {
                    cells[j].getElementsByTagName('input')[0].value = 0;
                    cells[j].getElementsByTagName('input')[0].disabled = true;
                }
            }
        };


        subjectElements.forEach(function(subjectElement) {
             subjectElement.innerHTML = '<option value="" selected disabled></option>';
             subjectElement.disabled = true;
        });

        groupElements.forEach(function(groupElement) {
            groupElement.innerHTML = '<option value="" selected disabled></option>';

            fetch(`/get-groups/${selectedTeacherId}/`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(function(group) {
                        let option = document.createElement('option');
                        option.value = group.course_has_speciality;
                        option.text = group.name_group;

                        groupElement.add(option);
                    });
                    // Разблокировать селект
                    groupElement.disabled = false;
                })
                .catch(error => {
                    console.error('Error fetching groups:', error);
                });
        });
    }

    function onGroupElementChange() {
        let selectedTeacherId = teacherSelect.value;
        let selectedGroupId = this.value;
        let subjectId = 'subject_' + this.id.split('_')[1];
        let subjectElement = document.getElementById(subjectId);

        subjectElement.innerHTML = '<option value="" selected disabled></option>';
        fetch(`/get-subjects/${selectedTeacherId}/${selectedGroupId}/`)
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

    }

    function onSubjectElementChange() {
        
        let rowId = this.id.split('_')[1];
        let selectedTeacherId = teacherSelect.value;
        let selectedSubjectId = this.value;
        let groupId = `group_${rowId}`;
        let selectedGroupId = document.getElementById(groupId).value;

        let fetchPromises = Array.from(typeLoadElements).map(typeLoad => {
            return fetch(`/get-hours/${selectedTeacherId}/${selectedGroupId}/${selectedSubjectId}/${typeLoad.id}/`)
                .then(response => response.json())
                .then(data => {
                    let semester = 1;
                    data.forEach(function(hour_load) {
                        let semesterVal = 0;
                        if (hour_load.hours !== null) {
                            semesterVal = hour_load.hours;
                        } else {
                            semesterVal = hour_load.exam;
                        }
                        let semesterId = `type-load_${rowId}_${typeLoad.id}_${semester}`;
                        document.getElementById(semesterId).value = semesterVal;
                        document.getElementById(semesterId).disabled = false;
                        semester++;
                    });
                // for (let i = 1; i < 3; i++) {
                //     let semesterId = `type-load_${rowId}_${typeLoad.id}_${i}`;
                //     document.getElementById(semesterId).disabled = false;
                // }
                })
                .catch(error => {
                    console.error('Error fetching subjects:', error);
                });
        });
        
        Promise.all(fetchPromises)
            .then(() => {
                let budget_sum = createCurrentBudget(rowId - 1);
                setCurrentBudget(rowId - 1, budget_sum);
        });
    };

    function onChangeHours(curRowId) {
        let budget_sum = createCurrentBudget(curRowId-1);
        setCurrentBudget(curRowId-1, budget_sum);
        
    }

    function createCurrentBudget(rowId) { 
        let budget_sum = 0;
        let cells = mainTable.rows[rowId].cells;
        for (i = 3; i < typeLoadElements.length * 2 + 3; i++) {
            
            let num = parseInt(cells[i].getElementsByTagName('input')[0].value);
            if (!isNaN(num)) {
                budget_sum += num;
            }
        }
        return budget_sum;
    }
        
    function setCurrentBudget(rowId, budget_sum) {
        
        let cells = mainTable.rows[rowId].cells;
        let selectedOption = cells[1].getElementsByTagName('select')[0].querySelector('option:checked');
        let dataIsPaidValue = selectedOption.getAttribute('data-is-paid');
        
        if (dataIsPaidValue === 'true') {
            document.getElementById(`budget_0_${rowId+1}`).value = 0;
            document.getElementById(`budget_1_${rowId+1}`).value = budget_sum;
        } else {
            document.getElementById(`budget_0_${rowId+1}`).value = budget_sum;
            document.getElementById(`budget_1_${rowId+1}`).value = 0;
        }

        document.getElementById(`budget_2_${rowId+1}`).value = budget_sum;
        changeResults(dataIsPaidValue);
    }
    

    function changeResults(is_paid) {
        let newBudget = 0;
        let newExtraBudget = 0;
        let newTotalBudget = 0;

        if (is_paid === 'true') {
            let extraBudgetElements = document.querySelectorAll('[id^="budget_1_"]');
            extraBudgetElements.forEach(function(element) {
                newExtraBudget += parseInt(element.value);
            });
            document.getElementById('extra_budget_sum_1').value = newExtraBudget;
            document.getElementById('extra_budget_sum_3').value = newExtraBudget;
        } else {

            let budgetElements = document.querySelectorAll('[id^="budget_0_"]');
            budgetElements.forEach(function(element) {
                newBudget += parseInt(element.value);
            });
            document.getElementById('budget_sum_1').value = newBudget;
            document.getElementById('budget_sum_3').value = newBudget;
        }
        let totalBudgetElements = document.querySelectorAll('[id^="budget_2_"]');
        totalBudgetElements.forEach(function(element) {
            newTotalBudget += parseInt(element.value);
        });
        document.getElementById('budget_result_1').value = newTotalBudget;
        document.getElementById('budget_result_3').value = newTotalBudget;
    }

    
});

 
