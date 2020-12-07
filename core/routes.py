from . import views


def register(router):
    router.register(r'professionals', views.Professionals, basename='Professional')
    router.register(r'profile', views.Users, basename='User')
    router.register(r'profile/availabilities', views.PrivateAvailabilities, basename='SelfAvailabilities')
