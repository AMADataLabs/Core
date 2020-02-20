from django.urls import path, re_path
from django_ppd_test.graphqltest.views import PhysiciansDetailView, PhysicianList
urlpatterns = [
    #path('physicians/', ListPhysiciansView.as_view(), name="Physicians-ALL"),
    path('physicians/<int:pk>', PhysiciansDetailView.as_view(), name="Physician-detail"),
    path('physicians/<int:pk>?.*', PhysiciansDetailView.as_view(), name="Physician-detail"),
    re_path(r'^physicians?.*', PhysicianList.as_view(), name='filter'),
]
