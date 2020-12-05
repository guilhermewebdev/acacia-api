from . import views

def register(router):
    router.register(r'proposals', views.ProposalsViewset, basename='Proposal')
    router.register(r'proposals/(?P<proposal_uuid>[^/.]+)/', views.CounterProposal, basename='CouterProposal')