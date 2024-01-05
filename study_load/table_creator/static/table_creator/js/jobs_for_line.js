let typeLoadElements = document.querySelectorAll(".type_load");

function addRow() {
     // Функция, которая создает новую строку в таблице
        let table = document.getElementById('table_body');
        let rowCount = table.rows.length;
        let row = table.insertRow(rowCount);

        // Добавляем ячейки в строку
        let cell1 = row.insertCell(0);
        rowCount = rowCount + 1;
        cell1.innerHTML = `<span class="row-number">${rowCount}</span>`;

        let cell3 = row.insertCell(1);
        cell3.innerHTML = '<select id="subject_' + rowCount + '" class="subject" name="subject_' + rowCount + '" ></select>';

        let cell4 = row.insertCell(2);
        cell4.innerHTML = '<select id="group_' + rowCount + '" class="group" name="group_' + rowCount + '"></select>';
        let groupSelect = cell4.querySelector('select');

        typeLoadElements.forEach(function(typeLoad){
            for (let semester = 1; semester < 3; semester++) {
                let cell = row.insertCell(-1);
                cell.innerHTML = `<input type="text" id="type-load_${rowCount}_${typeLoad.id}_${semester}" value="0"
                    name="type-load_${rowCount}_${typeLoad.id}_${semester}" class="data-element" disabled>`;
            }
        });

        for (let i = 0; i < 3; i++) { 
            let cell = row.insertCell(-1);
            cell.innerHTML = '<input type="text" id="budget_' + i + '_' + rowCount + '" name="budget_' + i + '_' + rowCount + '" value="0" disabled />';

        }

        updateGroup(groupSelect)
        
}

function deleteRow() {
    let table = document.getElementById('table_body');
    let rowNumberInput = document.getElementById('row_number_input');
    let rowDelete = parseInt(rowNumberInput.value, 10);

    if (!isNaN(rowDelete) && rowDelete >= 0 && rowDelete <= table.rows.length) {
        let curDelRow = table.rows[rowDelete - 1].cells

        let budget = curDelRow[curDelRow.length - 1].getElementsByTagName('input')[0].value;
        let extraBudget = curDelRow[curDelRow.length - 2].getElementsByTagName('input')[0].value;
        let totalBudget = curDelRow[curDelRow.length - 3].getElementsByTagName('input')[0].value;
        
        deductFromBudget(budget, extraBudget, totalBudget);

        table.deleteRow(rowDelete - 1);


        // Пересчитываем оставшиеся строки
        for (let i = rowDelete - 1; i < table.rows.length; i++) {

            
            let cells = table.rows[i].cells;
            let rowNum = i + 1;
            // Пересчитываем номер в первой ячейке (например, номер строки)
            cells[0].innerHTML = `<span class="row-number">${rowNum}</span>`;

            // Обновляем id у элементов в ячейках
            cells[1].getElementsByTagName('select')[0].id = 'subject_' + rowNum;
            cells[1].getElementsByTagName('select')[0].name = 'subject_' + rowNum;

            cells[2].getElementsByTagName('select')[0].id = 'group_' + rowNum;
            cells[2].getElementsByTagName('select')[0].name = 'group_' + rowNum;
            
            let indx = 3
            typeLoadElements.forEach(function(typeLoad){
                for (let semester = 1; semester < 3; semester++) {
                        let inputElement = cells[indx].getElementsByTagName('input')[0];
                        let inputId = `type-load_${rowNum}_${typeLoad.id}_${semester}`;
                        inputElement.id = inputId;
                        inputElement.name = inputId;

                        indx++;
                    }
            });
            
            let last = indx + 3;
            let k = 0;
            for (indx; indx < last; indx++) {
                cells[indx].getElementsByTagName('input')[0].id = `budget_${k}_${rowNum}`;
                cells[indx].getElementsByTagName('input')[0].name = `budget_${k}_${rowNum}`;
                k++;
            }
            
        }
    } else {
        alert('Недопустимый номер строки или такой строки не существует.');
    }
}

    function updateGroup(cur_row) {
       let teacherSelect = document.getElementById('teacher');
       let selectedTeacherId = teacherSelect.value;
       // Очищаем текущие опции и добавляем по умолчанию пустой вариант

        cur_row.innerHTML = '<option value="" selected disabled></option>';

        if (selectedTeacherId) {
            fetch(`/get-groups/${selectedTeacherId}/`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(function(group) {
                        let option = document.createElement('option');
                        option.value = group.course_has_speciality;
                        option.text = group.name_group;
                        cur_row.add(option);
                    });

                    cur_row.disabled = false;
                })
                .catch(error => {
                    console.error('Error fetching groups:', error);
                });
        } else {
            cur_row.disabled = true;
        }
}

function deductFromBudget(budget, extraBudget, totalBudget) {
    document.getElementById('extra_budget_sum_1').value -= extraBudget;
    document.getElementById('extra_budget_sum_3').value -= extraBudget;
    document.getElementById('budget_sum_1').value -= budget;
    document.getElementById('budget_sum_3').value -= budget;
    document.getElementById('budget_result_1').value -= totalBudget;
    document.getElementById('budget_result_3').value -= totalBudget;
}

document.addEventListener('DOMContentLoaded', function() {
    let buttonAddRow = document.getElementById('add_row');
    let buttonDeleteRow = document.getElementById('delete_row');

    buttonAddRow.addEventListener('click', function() {
        addRow();
    })

    buttonDeleteRow.addEventListener('click', function() {
        deleteRow();
    })

});
