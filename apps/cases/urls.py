from django.urls import path
from apps.cases.views import TestCaseView

urlpatterns = [
    path('testCase/', TestCaseView.as_view(), name='testCase')
]
