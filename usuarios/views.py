from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import auth, firestore
from proyecto_clase.firebase_config import initialize_firebase
from functools import wraps
import requests
import os

# Create your views here.
db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            # Crear usuario en Firebase Auth
            usuario = auth.create_user(
                email=email,
                password=password
            )

            # Crear en firestore

            db.collection('perfiles').document(usuario.uid).set({
                'email': email,
                'uid': usuario.uid,
                'rol': 'aprendiz',
                'fecha_registro': firestore.SERVER_TIMESTAMP

            })

            mensaje = f"✅ Usuario registrado exitosamente con UID ✅: {usuario.uid}"

        except Exception as e:
            mensaje = f"❌ Error ❌{e}"
            
    return render(request, 'registros.html', {'mensaje': mensaje})

#logica para inisio sesion
#decorador de seguridad para proteger las vistas

def login_required_firebase(view_func):
    """
    este decorador protege las vistas si el usuario no ha inicioado sesion y lo redirecciona a inisiar sesion 
    """

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "❌ Acceso Denegado, Debes iniciar sesión para acceder a esta página ❌")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped_view

#logica para solicitud dde autenticacion a firebase

def login_usuario(request):
    #si ya esta logeaddo lo redirigimos al dashboard
    if  'uid' in request.session:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        #endpoint oficial de google para el login

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        #mi carga util
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        try:   
            #peticion HTTP al servicio de autenticacion 

            response = requests.post(url, json=payload)
            data = response.json()  

            if response.status_code == 200:
                # ✅Exito: vamos a almacenar los datos en la sesion✅
                request.session['uid'] = data['localId']
                request.session['email'] = data['email']
                request.session['id_token'] = data['idToken'] #token temporal acceso
                messages.success(request, "✅ Inicio de sesión exitoso ✅")
                return redirect('dashboard')
            else:
                #analizamos el error
                error_msg = data.get('error', {}).get('message', 'UNKNOWN_ERROR')

                errores_comunes = {
                    'INVALID_LOGIN_CREDENTIALS': 'La contraseña es incorrecta o el correo no es válido.',
                    'EMAIL_NOT_FOUND': 'Este correo no está registrado en el sistema.',
                    'USER_DISABLED': 'Esta cuenta ha sido inhabilitada por el administrador.',
                    'TOO_MANY_ATTEMPTS_TRY_LATER': 'Demasiados intentos fallidos. Espere unos minutos.'
                }

                mensaje_usuario = errores_comunes.get(error_msg, '❌ Error de autenticacion ❌. Por favor, inténtalo de nuevo o revise sus datos .')

                messages.error(request, mensaje_usuario)
                               
        except requests.exceptions.RequestException as e:
            messages.error(request, "Error de conexión de autenticación.")
        except Exception as e:
            messages.error(request, f"Error inesperado: {str(e)}")
    return render(request, 'login.html')

def cerrar_sesion(request):
    #limpiar la sesion del usuario
    request.session.flush() 
    messages.success(request, "✅ Sesión cerrada exitosamente ✅")
    return redirect('login')
def login_required_firebase(view_func):
    """
    este decorador protege las vistas si el usuario no ha inicioado sesion
    """
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if 'uid' not in request.session:
            messages.warning(request, "❌ Acceso Denegado, Debes iniciar sesión ❌")
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapped_view


# 🔥 AQUI PEGAS EL NUEVO, SIN BORRAR EL DE ARRIBA
def rol_requerido(roles_permitidos):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):

            uid = request.session.get('uid')

            try:
                doc = db.collection('perfiles').document(uid).get()
                if doc.exists:
                    perfil = doc.to_dict()
                    rol_usuario = perfil.get('rol')

                    if rol_usuario not in roles_permitidos:
                        messages.error(request, "❌ No tienes permiso para realizar esta acción ❌")
                        return redirect('dashboard')
                else:
                    messages.error(request, "Perfil no encontrado.")
                    return redirect('dashboard')

            except Exception as e:
                messages.error(request, f"Error verificando rol: {e}")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)

        return wrapped_view
    return decorator

@login_required_firebase
def dashboard(request):
    if not request.session.get('uid'):
        return redirect('login')

    uid = request.session.get('uid')
    perfil = db.collection('perfiles').document(uid).get().to_dict()

    # Total de jugadores del entrenador
    jugadores = list(db.collection('jugadores')
                     .where('uid_entrenador', '==', uid)
                     .stream())

    # Total de entrenamientos
    entrenamientos = list(db.collection_group('entrenamientos').stream())

    # Total de tareas (ya no filtramos por UID)
    tareas = list(db.collection('tareas').stream())

    context = {
        'datos_usuario': perfil,
        'total_jugadores': len(jugadores),
        'total_entrenamientos': len(entrenamientos),
        'total_tareas': len(tareas),
    }
    print("UID sesión:", uid)

    return render(request, 'dashboard.html', context)
@login_required_firebase 
def listar_tarea(request):
    """
    READ: recuperar todas las tareas del usuario q esten en firebase 
    """
    uid = request.session.get('uid')
    tareas=[]
    try:
        #filtrar por el uid del usuario
        docs =db.collection('tareas').where('usuario_id','==',uid).stream()
        for doc in docs:
            tarea = doc.to_dict()
            tarea['id'] = doc.id
            tareas.append(tarea)
    except Exception as e:
        messages.error(request, f"Hubo un error al obtener las tareas {e}")

    return render(request, 'tareas/listar.html', {'tareas': tareas})

@login_required_firebase
def form_tarea(request):
    """
    CREATE: Recibimos los datos del formulario y los almacenamos 
    """
    if request.method == 'POST':
        titulo = request.POST.get('titulo')
        descripcion = request.POST.get('descripcion')
        uid = request.session.get('uid')

        try:
            db.collection('tareas').add({
                'titulo': titulo,
                'descripcion': descripcion,
                'estado': 'pendiente',  
                'usuario_id': uid,
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })
            messages.success(request, "✅ Tarea creada con exito ✅")
            return redirect('listar_tarea')
        except Exception as e:
            messages.error(request, f"Error al crear la tarea: {e}")

    return render(request, 'tareas/form.html')

@login_required_firebase
def eliminar_tarea(request, tarea_id):
    """
    DELETE: Elimina un documento especificopor su id
    """
    
    try:
        db.collection('tareas').document(tarea_id).delete()
        messages.success(request, "✅ Tarea eliminada con exito ✅")
    except Exception as e:
        messages.error(request, f"Error al eliminar la tarea: {e}")
    return redirect('listar_tarea')

@login_required_firebase
def editar_tarea(request, tarea_id):
    """
    UPDATE: Editar una tarea existente
    """
    uid=request.session.get('uid')
    tarea_ref = db.collection('tareas').document(tarea_id)

    try:
        doc = tarea_ref.get()
        if not doc.exists:
            messages.error(request, "La tarea no existe.")
            return redirect('listar_tarea')
        tarea_data = doc.to_dict()
        if tarea_data['usuario_id'] != uid:
            messages.error(request, "No tienes permiso para editar esta tarea.")
            return redirect('listar_tarea')
        
        if request.method == 'POST':
            nuevo_titulo = request.POST.get('titulo')
            nueva_descripcion = request.POST.get('descripcion')
            nuevo_estado = request.POST.get('estado')

            tarea_ref.update({
                'titulo': nuevo_titulo,
                'descripcion': nueva_descripcion,
                'estado': nuevo_estado,
                'fecha_actualizacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Tarea actualizada con exito ✅")
            return redirect('listar_tarea')
    except Exception as e:
        messages.error(request, f"Error al editar la tarea: {e}")
        return redirect('listar_tarea')

    return render(request, 'tareas/editar_tarea.html', {'tarea': tarea_data, 'tarea_id': tarea_id})
@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def registrar_entrenamiento(request):
    """
    CREATE: Registrar entrenamiento del jugador
    """
    if request.method == 'POST':
        jugador_id = request.POST.get('jugador_id')
        tipo = request.POST.get('tipo')
        duracion = request.POST.get('duracion')
        intensidad = request.POST.get('intensidad')
        observaciones = request.POST.get('observaciones')
        uid = request.session.get('uid')

        try:
            db.collection('jugadores') \
        .document(jugador_id) \
        .collection('entrenamientos') \
        .add({
        'tipo': tipo,
        'duracion': duracion,
        'intensidad': intensidad,
        'observaciones': observaciones,
        'registrado_por': uid,
        'fecha_creacion': firestore.SERVER_TIMESTAMP
        })
            messages.success(request, "✅ Entrenamiento registrado con éxito ✅")
            return redirect('listar_entrenamientos')
            print("UID guardado:", request.session.get("uid"))

        except Exception as e:
            messages.error(request, f"Error al registrar el entrenamiento: {e}")

    # 🔥 ESTA PARTE ES LA NUEVA (para cargar jugadores en el select)
    jugadores = db.collection('jugadores').stream()
    lista_jugadores = []

    for doc in jugadores:
        data = doc.to_dict()
        data['id'] = doc.id
        lista_jugadores.append(data)

    return render(request, 'entrenamientos/form_entrenamiento.html', {
        'jugadores': lista_jugadores
    })

@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def listar_entrenamientos(request):

    entrenamientos = []

    jugadores = db.collection('jugadores').stream()

    for jugador in jugadores:
        jugador_id = jugador.id

        subcoleccion = db.collection('jugadores') \
            .document(jugador_id) \
            .collection('entrenamientos') \
            .stream()

        for e in subcoleccion:
            data = e.to_dict()
            data['id'] = e.id
            data['jugador_id'] = jugador_id
            entrenamientos.append(data)

    return render(request, 'entrenamientos/listar_entrenamientos.html', {
        'entrenamientos': entrenamientos
    })
@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def eliminar_entrenamiento(request, jugador_id, entrenamiento_id):

    try:
        db.collection('jugadores') \
            .document(jugador_id) \
            .collection('entrenamientos') \
            .document(entrenamiento_id) \
            .delete()

        messages.success(request, "Entrenamiento eliminado con éxito")

    except Exception as e:
        messages.error(request, f"Error al eliminar: {e}")

    return redirect('historial_entrenamientos_jugador', jugador_id=jugador_id)
@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def crear_jugador(request):
    """
    CREATE: Crear jugador en Firestore y su cuenta de autenticación
    """
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        posicion = request.POST.get('posicion')
        numero = request.POST.get('numero')
        edad = request.POST.get('edad')
        uid_entrenador = request.session.get('uid')

        try:
            # 1️⃣ Crear usuario en Firebase Authentication
            user_record = auth.create_user(
                display_name=nombre
            )
            uid_jugador = user_record.uid

            # 2️⃣ Crear documento del jugador en Firestore
            db.collection('jugadores').document(uid_jugador).set({
                'nombre': nombre,
                
                'posicion': posicion,
                'numero': numero,
                'edad': edad,
                'creado_por': uid_entrenador,
                "uid_entrenador": uid_entrenador,
                "uid": uid_jugador
            })

            messages.success(request, "✅ Jugador y cuenta creados con éxito ✅")
            return redirect('listar_jugadores')

        except Exception as e:
            messages.error(request, f"Error al crear jugador: {e}")

    return render(request, 'jugadores/form_jugador.html')
@login_required_firebase
def listar_jugadores(request):
    """
    READ: Listar jugadores
    """
    jugadores = []

    try:
        docs = db.collection('jugadores').stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            jugadores.append(data)
    except Exception as e:
        messages.error(request, f"Error al cargar jugadores: {e}")

    return render(request, 'jugadores/listar_jugadores.html', {'jugadores': jugadores})


@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def eliminar_jugador(request, jugador_id):
    if request.method == "POST":
        db.collection("jugadores").document(jugador_id).delete()

        messages.success(request, "Jugador eliminado correctamente")
        return redirect("listar_jugadores")

    return redirect("listar_jugadores")

@login_required_firebase
def historial_entrenamientos_jugador(request, jugador_id):

    jugador_ref = db.collection('jugadores').document(jugador_id)
    jugador = jugador_ref.get().to_dict()

    entrenamientos_ref = jugador_ref.collection('entrenamientos') \
        .order_by('fecha_creacion', direction=firestore.Query.DESCENDING) \
        .stream()

    lista = []

    for doc in entrenamientos_ref:
        data = doc.to_dict()
        data['id'] = doc.id
        lista.append(data)

    return render(request, 'entrenamientos/historial_entrenamientos.html', {
    'jugador': jugador,
    'jugador_id': jugador_id,
    'entrenamientos': lista
})
@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def crear_entrenamiento(request, jugador_id):

    jugador_ref = db.collection('jugadores').document(jugador_id)
    jugador = jugador_ref.get().to_dict()

    if request.method == 'POST':
        tipo = request.POST.get('tipo')
        duracion = request.POST.get('duracion')
        intensidad = request.POST.get('intensidad')
        observaciones = request.POST.get('observaciones')
        uid = request.session.get('uid')

        try:
            jugador_ref.collection('entrenamientos').add({
                'tipo': tipo,
                'duracion': duracion,
                'intensidad': intensidad,
                'observaciones': observaciones,
                'registrado_por': uid,
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, "✅ Entrenamiento agregado correctamente")
            return redirect('listar_entrenamientos')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'entrenamientos/form_entrenamiento.html', {
        'jugador': jugador,
        'jugador_id': jugador_id
    })
@login_required_firebase
@rol_requerido(['entrenador', 'admin'])
def editar_entrenamiento(request, jugador_id, entrenamiento_id):

    entrenamiento_ref = db.collection('jugadores') \
        .document(jugador_id) \
        .collection('entrenamientos') \
        .document(entrenamiento_id)

    doc = entrenamiento_ref.get()

    if not doc.exists:
        messages.error(request, "El entrenamiento no existe.")
        return redirect('listar_entrenamientos')

    if request.method == "POST":
        entrenamiento_ref.update({
            'tipo': request.POST.get('tipo'),
            'duracion': request.POST.get('duracion'),
            'intensidad': request.POST.get('intensidad'),
            'observaciones': request.POST.get('observaciones')
        })

        messages.success(request, "Entrenamiento actualizado correctamente")
        return redirect("historial_entrenamientos_jugador", jugador_id=jugador_id)

    return render(request, "entrenamientos/editar_entrenamiento.html", {
        "entrenamiento": doc.to_dict(),
        "jugador_id": jugador_id,
        "entrenamiento_id": entrenamiento_id
    })
