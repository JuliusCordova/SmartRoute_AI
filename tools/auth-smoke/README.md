# SmartRoute — Google Sign-In local (UID solamente)

Esta página local permite registrar mediante Google Sign-In una **cuenta de pruebas NUEVA** en Firebase Authentication del proyecto compartido `proyectopersonal-480420`. **No accede a Firestore ni al gateway**, no crea perfiles OPERATOR, no imprime tokens.

## Requisitos previos

1. Crear una cuenta Google nueva dedicada a SmartRoute AI (no usar la cuenta administradora).
2. Entrar a [Firebase Console, configuración del proyecto correcto](https://console.firebase.google.com/project/proyectopersonal-480420/settings/general). En **Tus aplicaciones**, agregar una aplicación **Web** con apodo `smartroute-auth-test` (si ya existe una app Web de SmartRoute registrada, utilizar su configuración). **No habilitar Hosting** ni cambiar apps existentes.
3. Copiar el bloque `firebaseConfig` de la app Web (API key, authDomain, projectId, appId, messagingSenderId). No son claves privadas; nunca copiar la clave JSON de una service account.
4. Confirmar que **Google** está habilitado en Authentication → Método de acceso (previamente verificado) y que `localhost` es un dominio autorizado (previamente confirmado para este proyecto). No agregar otros dominios al proyecto compartido.

## Configurar únicamente tu entorno local

En una computadora con Git y Python, ejecutar desde la raíz del repositorio:

```bash
cd SmartRoute_AI/tools/auth-smoke
cp firebase-config.example.js firebase-config.local.js
```

Editar `firebase-config.local.js` y pegar los campos de `firebaseConfig` de Firebase Console. Debe mantener `projectId: "proyectopersonal-480420"` y `authDomain: "proyectopersonal-480420.firebaseapp.com"`. No usar configuraciones de proyectos `calculadora`, `primademo` ni `proyectopersonal-480420-c8e3e`.

**No hacer commit de `firebase-config.local.js`.** Esta configuración es pública por diseño, pero mantenerla local reduce errores y acoplamiento accidental. Nunca colocar secretos reales en el directorio.

Ejecutar en la misma carpeta:

```bash
python3 -m http.server 8080 --bind 127.0.0.1
```

Abrir **desde el navegador de esa misma computadora**: http://localhost:8080 . No abrir como archivo `file://`. Si se usa Cloud Shell, su vista previa usa un dominio distinto de localhost y el flujo puede fallar por dominio no autorizado; preferir PC local y no cambiar allowlist del proyecto compartido para resolverlo.

Marcar la casilla de confirmación y hacer clic en **Continuar con Google**. Elegir explícitamente la **cuenta Google nueva** en el selector. La página muestra email, UID y proveedor `google.com`; NO muestra tokens. Copiar únicamente el UID si es necesario.

Visitar [Firebase Authentication → Usuarios](https://console.firebase.google.com/project/proyectopersonal-480420/authentication/users), comprobar que el usuario nuevo y proveedor Google aparecen con el UID generado. **No usar el botón Agregar usuario** (crea Email/Password, distinto del Google Sign-In).

Al terminar, pulsar **Cerrar sesión**; detener servidor local con Ctrl+C.

## Fase posterior: autorizar exclusivamente en Firestore `smartroute`

No editar Firestore hasta verificar UID. Se preparará un alta controlada de `users/{uid}` con campos `active: true`, `role: "OPERATOR"`, usando explícitamente la **base nombrada** `smartroute`, no `(default)` ni `gestioncitas`. Más tarde: prueba E2E autenticada por IAM/Firebase, limpieza y desactivación.

Aviso de seguridad: cualquier Firebase Auth user del proyecto compartido existe a nivel del proyecto, aunque use una cuenta Google exclusiva. La autorización OPERATOR se delimita en Firestore. El gateway sigue IAM privado y `GCP_STAGING_ENABLED=false`; no cambiar permisos para ejecutar esta página.
