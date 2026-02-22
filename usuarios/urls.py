from django.urls import path
from . import views

urlpatterns = [

    # =========================
    # 🔐 AUTENTICACIÓN
    # =========================
    path('registros/', views.registro_usuario, name='registro'),
    path('login/', views.login_usuario, name='login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views.cerrar_sesion, name='logout'),

    # =========================
    # 📝 GESTIÓN DE TAREAS (CRUD)
    # =========================
    path('tareas/', views.listar_tarea, name='listar_tarea'),
    path('tareas/form/', views.form_tarea, name='form_tarea'),
    path('tareas/editar/<str:tarea_id>/', views.editar_tarea, name='editar_tarea'),
    path('tareas/eliminar/<str:tarea_id>/', views.eliminar_tarea, name='eliminar_tarea'),

    # =========================
    # 👥 GESTIÓN DE JUGADORES
    # =========================
    path('jugadores/', views.listar_jugadores, name='listar_jugadores'),
    path('jugadores/nuevo/', views.crear_jugador, name='crear_jugador'),
    path('jugadores/eliminar/<str:jugador_id>/', views.eliminar_jugador, name='eliminar_jugador'),

    # =========================
    # 🏋️ ENTRENAMIENTOS POR JUGADOR
    # =========================

    # Historial de entrenamientos de un jugador
    path(
        'jugadores/<str:jugador_id>/historial/',
        views.historial_entrenamientos_jugador,
        name='historial_entrenamientos'
    ),

    # Crear entrenamiento para un jugador
    path(
        'jugadores/<str:jugador_id>/crear-entrenamiento/',
        views.crear_entrenamiento,
        name='crear_entrenamiento'
    ),

    # Editar entrenamiento (requiere jugador_id + entrenamiento_id)
    path(
        'entrenamientos/<str:jugador_id>/<str:entrenamiento_id>/editar/',
        views.editar_entrenamiento,
        name='editar_entrenamiento'
    ),

    # Eliminar entrenamiento (requiere jugador_id + entrenamiento_id)
    path(
        'entrenamientos/<str:jugador_id>/<str:entrenamiento_id>/eliminar/',
        views.eliminar_entrenamiento,
        name='eliminar_entrenamiento'
    ),
    
    path(
    'entrenamientos/',
    views.listar_entrenamientos,
    name='listar_entrenamientos'
    ),

]