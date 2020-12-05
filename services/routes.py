from . import views

def register(router):
    router.register(r'jobs', views.JobViewSet, basename='Jobs')
    router.register(r'proposals', views.ProposalsViewSet, basename='Proposal')