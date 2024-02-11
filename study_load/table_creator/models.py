from django.db import models
from django.urls import reverse


class Teacher(models.Model):
    name = models.CharField(unique=True, max_length=70, verbose_name='ФИО преподавателя')
    hours_load = models.ManyToManyField('HoursLoad', through='TeacherHours')

    objects = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(viewname='teacher', kwargs={'teacher_id': self.pk})


class Subject(models.Model):
    name = models.CharField(unique=True, max_length=200, verbose_name='Предмет')
    is_paid = models.BooleanField(verbose_name='Б/ВБ', default=False)

    objects = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(viewname='subject', kwargs={'subject_id': self.pk})


class TypeLoad(models.Model):

    name = models.CharField(max_length=50, verbose_name='Тип нагрузки')

    objects = models.Manager()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse(viewname='type_load', kwargs={'type_load_id': self.pk})


class Semester(models.Model):
    class Semesters(models.IntegerChoices):
        FIRST = 1, 'I'
        SECOND = 2, 'II'

    number = models.IntegerField(verbose_name='Семестр', choices=Semesters.choices)
    type_load = models.ManyToManyField(TypeLoad, through='HoursLoad')

    objects = models.Manager()

    def __str__(self):
        return str(self.number)


class Exam(models.Model):
    class TypeExam(models.TextChoices):
        exam = 'Э', 'Экзамен'
        test = 'ДЗ', 'Зачёт'

    exam = models.CharField(max_length=2, verbose_name='ДЗ/Э')

    objects = models.Manager()

    def __str__(self):
        return self.exam


class Speciality(models.Model):
    name = models.CharField(unique=True, max_length=50, verbose_name='Специальность')

    objects = models.Manager()

    def __str__(self):
        return self.name


class Course(models.Model):
    class Courses(models.IntegerChoices):
        FIRST = 1
        SECOND = 2
        THIRD = 3
        FOURTH = 4
        FIFTH = 5

    course = models.IntegerField(verbose_name='Курс', choices=Courses.choices)
    specialities = models.ManyToManyField(Speciality, through='SpecialityHasCourse')

    objects = models.Manager()

    def __str__(self):
        return f"{self.course}"


class SpecialityHasCourse(models.Model):
    course_has_speciality = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)
    name_group = models.CharField(unique=True, max_length=60)
    is_paid = models.BooleanField(verbose_name='Б/ВБ', default=False)
    group = models.ManyToManyField(Subject, through='GroupHasSubject')

    objects = models.Manager()

    def __str__(self):
        return self.name_group

    def get_absolute_url(self):
        return reverse(viewname='group', kwargs={'course_has_speciality': self.course_has_speciality})


class GroupHasSubject(models.Model):
    group = models.ForeignKey(SpecialityHasCourse, on_delete=models.CASCADE, verbose_name='Группа')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    objects = models.Manager()

    def __str__(self):
        return f'{self.group} {self.subject}'


class HoursLoad(models.Model):
    semester = models.ForeignKey(Semester, verbose_name='Семестр', on_delete=models.CASCADE)
    type_load = models.ForeignKey(TypeLoad, verbose_name='Тип нагрузки', on_delete=models.CASCADE)
    group_has_subject = models.ForeignKey(GroupHasSubject, verbose_name='Группа и Предмет',on_delete=models.CASCADE)
    hours = models.IntegerField(default=None, verbose_name='Часы', null=True)
    exam = models.ForeignKey(Exam, verbose_name='ДЗ/Э', on_delete=models.SET_NULL, null=True)
    unallocated_hours = models.IntegerField(default=0, verbose_name='Нераспределённые часы')

    objects = models.Manager()

    class Meta:
        unique_together = ['semester', 'type_load', 'group_has_subject']

    def __str__(self):
        if self.exam:
            return f"{self.semester} | {self.type_load} | {self.group_has_subject} | {self.exam} |" \
                   f"нр {self.unallocated_hours}"
        else:
            return f"{self.semester} | {self.type_load} | {self.group_has_subject} | {self.hours} |" \
                   f"нр {self.unallocated_hours}"


class TeacherHours(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    hours_load = models.ForeignKey(HoursLoad, on_delete=models.CASCADE)
    cur_hours = models.IntegerField(default=0, verbose_name='Часы', null=True)
    cur_exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True)

    objects = models.Manager()

    class Meta:
        unique_together = ['teacher', 'hours_load']

    def __str__(self):
        if self.cur_exam:
            return f"{self.teacher} {self.hours_load} | {self.cur_exam}"
        else:
            return f"{self.teacher} {self.hours_load} | {self.cur_hours}"