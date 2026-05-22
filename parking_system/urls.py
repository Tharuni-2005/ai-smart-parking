from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path('', views.home, name='home'),

    path('dashboard/<int:slot_id>/',
     views.dashboard,
     name='dashboard'),

    path('book/<int:slot_id>/',
         views.book_slot,
         name='book_slot'),

    path( 'cancel/<int:booking_id>/',
     views.cancel_booking,
     name='cancel_booking'),

     path('my-bookings/',
      views.my_bookings,
      name='my_bookings'),

      path('admin-login/',
       views.admin_login,
       name='admin_login'),

      path('admin-dashboard/',
        views.admin_dashboard,
        name='admin_dashboard'),

        path('history/',
          views.booking_history,
          name='booking_history'),
]

if settings.DEBUG:

    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )