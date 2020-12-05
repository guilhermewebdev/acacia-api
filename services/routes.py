from . import views

def register(router):
    router.register(r'proposals', views.ProposalsViewset, basename='Proposal')