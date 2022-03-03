from django.urls import path

#from core.reports.views.schoolfeeding_report.views import SchoolFeedingReportView
from core.reports.views.psychologicalorientation_report.views import PsychologicalOrientationReportView
from core.reports.views.conferences_report.views import ConferencesReportView
from core.reports.views.shifts_report.views import ShiftsReportView
from core.reports.views.assistance_report.teacher.views import AssistanceTeacherReportView
from core.reports.views.assistance_report.student.views import AssistanceStudentReportView
from core.reports.views.student.views import StudentReportView
from core.reports.views.teachers_report.views import TeachersReportView
from core.reports.views.grades_report.views import GradesReportView
from core.reports.views.inventory_report.views import InventoryReportView


urlpatterns = [
    #path('school/feeding/', SchoolFeedingReportView.as_view(), name='schoolfeeding_report'),
    path('psychological/orientation/', PsychologicalOrientationReportView.as_view(),
         name='psychologicalorientation_report'),
    path('conferences/', ConferencesReportView.as_view(), name='conferences_report'),
    path('shifts/', ShiftsReportView.as_view(), name='shifts_report'),
    path('assistance/teacher/', AssistanceTeacherReportView.as_view(), name='assistanceteacher_report'),
    path('assistance/student/', AssistanceStudentReportView.as_view(), name='assistancestudent_report'),
    path('student/', StudentReportView.as_view(), name='student_report'),
    path('teachers/', TeachersReportView.as_view(), name='teachers_report'),
    path('grades/', GradesReportView.as_view(), name='grades_report'),
    path('inventory/', InventoryReportView.as_view(), name='inventory_report'),

]
