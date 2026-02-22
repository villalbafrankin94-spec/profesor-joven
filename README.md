# 🏆 Sistema de Gestión Deportiva  
### 🔥 Django + Firebase (Authentication & Firestore)

Sistema web desarrollado con **Django** y **Firebase** para la gestión de:

- 👤 Usuarios con autenticación segura  
- 📝 Tareas personales  
- 🧍 Jugadores  
- 💪 Entrenamientos  

---

# 🚀 Tecnologías Utilizadas

- Python 
- Django
- Firebase Authentication
- HTML + Bootstrap

---

# 📌 ¿Cómo Funciona el Sistema?

El sistema integra:

1. Autenticación con Firebase
2. Gestión de sesiones con Django
3. Base de datos NoSQL (Firestore)
4. Subcolecciones en Firestore

---

# 🔐 Módulo de Autenticación

## ✅ Registro de Usuario

Al registrarse:

- Se crea usuario en Firebase Authentication
- Se crea documento en colección `perfiles` en Firestore
- Se asigna rol por defecto: `aprendiz`

Datos almacenados:

```json
{
  "email": "usuario@email.com",
  "uid": "uid_generado",
  "rol": "aprendiz",
  "fecha_registro": "SERVER_TIMESTAMP"
}
```

---

## 🔑 Inicio de Sesión

- Se validan credenciales
- Se guarda en sesión:
  - uid
  - email
  - id_token

Se manejan errores como:
- Correo no registrado
- Contraseña incorrecta
- Cuenta deshabilitada
- Demasiados intentos

---

## 🚪 Cerrar Sesión

```python
request.session.flush()
```

Elimina completamente la sesión del usuario.

---

# 📊 Dashboard

Muestra:

- Total jugadores del entrenador
- Total entrenamientos
- Total tareas
- Datos del usuario logueado

---

# 📝 Módulo de Tareas (CRUD)

Colección en Firestore:

```
tareas/
```

## ➕ Crear
- titulo
- descripcion
- estado
- usuario_id
- fecha_creacion

## 📖 Listar
Filtrado por usuario.

## ✏ Editar
Solo el propietario puede modificarla.

## ❌ Eliminar
Se elimina por ID.

---

# 🧍 Módulo de Jugadores

Colección:

```
jugadores/
```

## ➕ Crear jugador

1. Se crea usuario en Firebase Authentication
2. Se crea documento en Firestore

Datos guardados:

```json
{
  "nombre": "Jugador",
  "posicion": "Delantero",
  "numero": "10",
  "edad": "18",
  "uid_entrenador": "uid_entrenador",
  "uid": "uid_jugador"
}
```

## 📖 Listar jugadores

## ❌ Eliminar jugador
Solo entrenador o admin.

---

# 💪 Módulo de Entrenamientos

Subcolección dentro de cada jugador:

```
jugadores/
   jugador_id/
      entrenamientos/
         entrenamiento_id
```

## ➕ Crear entrenamiento
- tipo
- duracion
- intensidad
- observaciones
- registrado_por
- fecha_creacion

## 📖 Listar entrenamientos

## 📜 Historial por jugador
Ordenado por fecha descendente.

## ✏ Editar entrenamiento

## ❌ Eliminar entrenamiento

---

# 🗂 Estructura General de Firestore

```
Firestore
│
├── perfiles
├── tareas
└── jugadores
       └── entrenamientos (subcolección)
```

---

# ⚙ Variables de Entorno

Debes configurar:

```
FIREBASE_WEB_API_KEY=tu_api_key
```

Y tener correctamente configurado:

```
firebase_config.py
```

---

# 🏁 Flujo del Sistema

1. Usuario se registra
2. Se crea perfil en Firestore
3. Inicia sesión
4. Accede al dashboard

---

# 🎯 Objetivo del Proyecto

Demostrar integración completa entre:

- Django
- Firebase Authentication
- Firestore
- Control de roles
- CRUD completo
- Subcolecciones
