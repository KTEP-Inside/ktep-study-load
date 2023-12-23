document.addEventListener('DOMContentLoaded', function() {
    let teacherSelect = document.getElementById('teacher');

    teacherSelect.addEventListener('change', updateGroups);

    function updateGroups() {
        let selectedTeacherId = teacherSelect.value;
        let groupElements = document.querySelectorAll('.group');
        let subjectElements = document.querySelectorAll('.subject');

        subjectElements.forEach(function(subjectElement) {
             subjectElement.innerHTML = '<option value="" selected disabled></option>';
        });

        // Iterate through all elements with class 'group'
        groupElements.forEach(function(groupElement) {
            groupElement.innerHTML = '<option value="" selected disabled></option>';

            fetch(`/get-groups/${selectedTeacherId}/`)
                .then(response => response.json())
                .then(data => {
                    data.forEach(function(group) {
                        let option = document.createElement('option');
                        option.value = group.course_has_speciality;
                        option.text = group.name_group;
                        // Append the option to the current group element
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


//    groupSelect.addEventListener('change', function() {
//        let selectedGroupSelectId = groupSelect.value;
//        let selectedTeacherSelectId = teacherSelect.value;
//        subjectSelect.value = '';
//
//        // Очищаем текущие опции и добавляем по умолчанию пустой вариант
//        subjectSelect.innerHTML = '<option value="" selected disabled></option>';
//
//        if (selectedGroupSelectId){
//            fetch(`/get-subjects/${selectedTeacherSelectId}/${selectedGroupSelectId}/`)
//                .then(response => response.json())
//                .then(data => {
//
//                    data.forEach(function(subject) {
//                        let option = document.createElement('option');
//                        option.value = subject.pk;
//                        option.text = subject.name;
//                        subjectSelect.add(option);
//                    });
//
//                    // Разблокировать селект
//                    subjectSelect.disabled = false;
//                })
//                .catch(error => {
//                    console.error('Error fetching specialities:', error);
//                });
//        } else {
//            subjectSelect.disabled = true;
//        }
//    });
//
//    subjectSelect.addEventListener('change', function() {
//        let selectedGroupSelectId = groupSelect.value;
//        let selectedTeacherSelectId = teacherSelect.value;
//        let selectedSubjectSelectId = subjectSelect.value;
//    });

});

