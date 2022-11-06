from django.urls import path
from . import views
##aqui va la url que quieramos de los dos lados y en el medio en views. poenmos el nombre de la funcion creada en views
##podes entrar al link para ver si es que está retoranado el valor que queremos poniendo /y el primer valor ej /fprocess_order

urlpatterns=[
    path('', views.store, name ="store"),
    path('cart/', views.cart, name ="cart"),
    path('checkout/', views.checkout, name ="checkout"),
    path('update_item/', views.updateItem, name ="update_item"),
    path('process_order/', views.processOrder, name ="process_order"),


    
]