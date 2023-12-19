from django.db import models


class Teacher(models.Model):
    name = models.CharField(unique=True, max_length=60, verbose_name='ФИО преподавателя')

    objects = models.Manager()

    def __str__(self):
        return self.name


class Subject(models.Model):
    name = models.CharField(unique=True, max_length=100, verbose_name='Предмет')
    teachers = models.ManyToManyField(Teacher, through='TeacherHasSubject')

    objects = models.Manager()

    def __str__(self):
        return self.name


class TeacherHasSubject(models.Model):
    teacher_has_subject = models.AutoField(primary_key=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    objects = models.Manager()

    def __str__(self):
        return f"{self.teacher}: {self.subject}"


class TypeLoad(models.Model):

    name = models.CharField(max_length=50, verbose_name='Тип нагрузки')

    objects = models.Manager()

    def __str__(self):
        return self.name


class Semester(models.Model):
    class Semesters(models.IntegerChoices):
        FIRST = 1, 'I'
        SECOND = 2, 'II'

    number = models.IntegerField(verbose_name='Семестр', choices=Semesters.choices)
    type_load = models.ManyToManyField(TypeLoad, through='HoursLoad')

    objects = models.Manager()

    def __str__(self):
        return self.number


class Exam(models.Model):
    class TypeExam(models.TextChoices):
        exam = 'Э', 'Экзамен'
        test = 'ДЗ', 'Зачёт'

    exam = models.CharField(max_length=2)

    objects = models.Manager()

    def __str__(self):
        return self.exam


class HoursLoad(models.Model):
    semester = models.ForeignKey(Semester, on_delete=models.CASCADE)
    type_load = models.ForeignKey(TypeLoad, on_delete=models.CASCADE)
    group = models.ForeignKey('SpecialityHasCourse', on_delete=models.CASCADE)
    teacher_subject = models.ForeignKey(TeacherHasSubject, on_delete=models.CASCADE)
    hours = models.IntegerField(default=None, verbose_name='Часы', null=True)  # как взять ДЗ и Э
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True)

    objects = models.Manager()

    def __str__(self):
        if self.exam:
            return f"{self.type_load} {self.group} {self.teacher_subject} {self.exam}"
        else:
            return f"{self.type_load} {self.group} {self.teacher_subject} {self.hours}"


class Speciality(models.Model):
    name = models.CharField(unique=True, max_length=15, verbose_name='Специальность')

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
        return self.course


class SpecialityHasCourse(models.Model):
    course_has_speciality = models.AutoField(primary_key=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    speciality = models.ForeignKey(Speciality, on_delete=models.CASCADE)
    name_group = models.CharField(unique=True, max_length=50)

    objects = models.Manager()

    def __str__(self):
        return self.name_group
