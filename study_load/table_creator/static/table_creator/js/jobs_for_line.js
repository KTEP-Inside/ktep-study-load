function addLine() {
     // Функция, которая создает новую строку в таблице
        let table = document.getElementById('table_body');
        let rowCount = table.rows.length;
        let row = table.insertRow(rowCount);

        // Добавляем ячейки в строку
        let cell1 = row.insertCell(0);
        cell1.innerHTML = rowCount;

        let cell3 = row.insertCell(1);
        cell3.innerHTML = '<select id="subject_' + rowCount + '" class="subject" name="subject_' + rowCount + '"></select>';

        let cell4 = row.insertCell(2);
        cell4.innerHTML = '<select id="group_' + rowCount + '" class="group" name="group_' + rowCount + '"></select>';
        let groupSelect = cell4.querySelector('select');

        // Добавляем ячейки для семестров
        let semesterRange = 20;
        for (let i = 0; i < semesterRange; i++) {
            let cell = row.insertCell(i+3);
            cell.innerHTML = '<input type="text" id="hour_' + rowCount + '_' + i + '" name="hour_' + rowCount + '_' + i + '">';
        }

        updateGroup(groupSelect)
        
}

function deleteRow() {
    let table = document.getElementById('table_body');
    let rowNumberInput = document.getElementById('row_number_input');
    let rowDelete = parseInt(rowNumberInput.value, 10);

    if (!isNaN(rowDelete) && rowDelete >= 0 && rowDelete < table.rows.length) {
        table.deleteRow(rowDelete);

        // Пересчитываем оставшиеся строки
        for (let i = rowDelete; i < table.rows.length; i++) {
            let cells = table.rows[i].cells;

            // Пересчитываем номер в первой ячейке (например, номер строки)
            cells[0].innerHTML = i;

            // Обновляем id у элементов в ячейках
            cells[1].getElementsByTagName('select')[0].id = 'subject_' + i;
            cells[1].getElementsByTagName('select')[0].name = 'subject_' + i;

            cells[2].getElementsByTagName('select')[0].id = 'group_' + i;
            cells[2].getElementsByTagName('select')[0].name = 'group_' + i;

            // Дополнительные ячейки с идентификаторами вида "hour_1_2" и т.д.
            for (let j = 3; j < cells.length; j++) {
                cells[j].getElementsByTagName('input')[0].id = 'hour_' + i + '_' + (j - 3);
                cells[j].getElementsByTagName('input')[0].name = 'hour_' + i + '_' + (j - 3);
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