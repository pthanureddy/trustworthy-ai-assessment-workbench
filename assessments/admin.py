from django.contrib import admin

from .models import Assessment, AssessmentEvent, Framework, Question, RegulatoryReference, Requirement, Response

admin.site.register([Framework, RegulatoryReference, Requirement, Question, Assessment, Response, AssessmentEvent])
