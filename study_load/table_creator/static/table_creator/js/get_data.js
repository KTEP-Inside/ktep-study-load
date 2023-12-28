document.addEventListener('DOMContentLoaded', function() {
    let teacherSelect = document.getElementById('teacher');
    let mainTable = document.getElementById('table_body');


    teacherSelect.addEventListener('input', updateGroups);

    mainTable.addEventListener('input', function () {
        let groupElements = document.querySelectorAll('.group');
        let subjectElements = document.querySelectorAll('.subject');

        groupElements.forEach(function (groupElement) {
            // Перед добавлением слушателя сначала удаляем существующие слушатели,
            // чтобы избежать множественного добавления
            groupElement.removeEventListener('change', onGroupElementChange);
            groupElement.addEventListener('change', onGroupElementChange);
        });

        subjectElements.forEach(function (subjectElement) {
            subjectElement.removeEventListener('change', onSubjectElementChange);
            subjectElement.addEventListener('change', onSubjectElementChange);
        });
    });

    function updateGroups() {
        let selectedTeacherId = teacherSelect.value;
        let groupElements = document.querySelectorAll('.group');
        let subjectElements = document.querySelectorAll('.subject');

        subjectElements.forEach(function(subjectElement) {
             subjectElement.innerHTML = '<option value="" selected disabled></option>';
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

                subjectElement.add(option);
            });
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

        typeLoadElements.forEach(function(typeLoad){

            fetch(`/get-hours/${selectedTeacherId}/${selectedGroupId}/${selectedSubjectId}/${typeLoad.id}/`)
            .then(response => response.json())
            .then(data => {
                let semester = 1;
                
                data.forEach(function(hour_load) {

                    let semesterVal = 0
                    if (hour_load.hours !== null) {
                        semesterVal = hour_load.hours;
                    } else {
                        semesterVal = hour_load.exam;
                    }
                    
                    let semesterId = `type-load_${rowId}_${typeLoad.id}_${semester}`;
                    document.getElementById(semesterId).value = semesterVal;
                    console.log()
                    
                    semester++;
                    
                });
            })
            .catch(error => {
                console.error('Error fetching subjects:', error);
            });
        });


    };
});

