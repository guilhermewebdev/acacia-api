from . import views


def register(router):
    router.register(r'professionals', views.Professionals, basename='Professional')
    router.register(r'users', views.Users, basename='User')

    router.register(r'professionals/(?P<professional_uuid>[^/.]+)/availabilities', views.Availabilities, basename='ProfessionalAvailabilities')

    router.register(r'users/profile/availabilities', views.PrivateAvailabilities, basename='SelfAvailabilities')
