from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Speciality)
class SpecialityAdmin(admin.ModelAdmin):
    pass


@admin.register(TypeLoad)
class TeacherAdmin(admin.ModelAdmin):
    pass


@admin.register(TeacherHasSubject)
class TeacherHasSubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(SpecialityHasCourse)
class SpecialityHasCourseAdmin(admin.ModelAdmin):
    pass


@admin.register(HoursLoad)
class HoursLoadAdmin(admin.ModelAdmin):
    pass