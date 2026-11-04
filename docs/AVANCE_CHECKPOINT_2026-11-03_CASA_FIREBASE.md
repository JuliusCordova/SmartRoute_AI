# SmartRoute AI — checkpoint para continuar desde casa (2026-11-03, Lima)

## Dónde nos quedamos exactamente

Se creó en la consola de Firebase una **app web exclusiva del piloto** llamada `smartroute-auth-test`, dentro del proyecto correcto `proyectopersonal-480420` (número `913797829604`). El usuario ya obtuvo la configuración web `firebaseConfig` de esa app. El **inicio de sesión Google desde la página local no se ha ejecutado ni validado todavía**, y tampoco se ha confirmado la creación de la nueva cuenta Google de pruebas. **No se ha creado el perfil Firestore OPERATOR**.

La herramienta de prueba del navegador ya está en `main` (PR #50, commit `e06415e`):
- `tools/auth-smoke/index.html`
- `tools/auth-smoke/app.js`
- `tools/auth-smoke/firebase-config.example.js`
- `tools/auth-smoke/README.md`
- `.gitignore` excluye `tools/auth-smoke/firebase-config.local.js`.

## Por qué ejecutar la prueba en una computadora local

La web `auth-smoke` es **solo un arnés temporal de prueba** para verificar Google Sign-In con el SDK Firebase y obtener el UID. Firebase ya tenía `localhost` como dominio autorizado. No se requiere subir una web, abrir el gateway público ni dar permisos IAM adicionales para este paso. Se recomienda Windows/Chrome con `http://localhost:8080`, donde el flujo popup puede funcionar sin cambiar dominios autorizados que usan otras apps. **No es el despliegue del producto final**: el producto objetivo es Android, con Google Maps, OR-Tools y Gemini. El login definitivo se implementará en el cliente Android.

## Cómo retomar en la PC Windows

1. Crear una **cuenta Google NUEVA exclusiva para las pruebas de SmartRoute**, con recuperación y MFA; no reutilizar la cuenta administradora ya existente en Firebase Auth.
2. En PowerShell, dentro de una copia local del repo:
   ```powershell
   git pull --ff-only
   cd tools/auth-smoke
   Copy-Item firebase-config.example.js firebase-config.local.js
   notepad firebase-config.local.js
   ```
   Si el archivo `firebase-config.local.js` ya existe, inspeccionar antes de sobrescribir.
3. Pegar los campos de configuración obtenidos en Firebase Console → [Proyecto correcto → General → Tus aplicaciones → smartroute-auth-test → Config](https://console.firebase.google.com/project/proyectopersonal-480420/settings/general), manteniendo:
   ```javascript
   export const firebaseConfig = {
     apiKey: "COPIAR_DESDE_FIREBASE_CONSOLE",
     authDomain: "proyectopersonal-480420.firebaseapp.com",
     projectId: "proyectopersonal-480420",
     storageBucket: "proyectopersonal-480420.firebasestorage.app",
     messagingSenderId: "913797829604",
     appId: "1:913797829604:web:e37f620caa9e8f65ddedf1",
     measurementId: "G-ZM1694JW1X"
   };
   ```
   `firebase-config.local.js` queda local; no agregarlo a Git. No copiar claves privadas JSON de cuentas de servicio, contraseñas o tokens.
4. Desde `tools/auth-smoke`:
   ```powershell
   py -m http.server 8080 --bind 127.0.0.1
   ```
   Abrir **http://localhost:8080** desde ese mismo PC, marcar confirmación y pulsar **Continuar con Google**, eligiendo la nueva cuenta exclusiva. Se mostrará únicamente correo, proveedor `google.com` y UID; no se imprimen tokens.
5. Comprobar el usuario nuevo y su UID en [Firebase Authentication → Usuarios](https://console.firebase.google.com/project/proyectopersonal-480420/authentication/users). No usar botón `Agregar usuario` para Google Sign-In: ese botón crea Email/Password. Cerrar sesión tras comprobarlo.

## Qué sigue después del UID

Crear de manera controlada y reversible el perfil **solo** en la base nombrada `smartroute`: `users/{uid}` con `active=true` y `role=OPERATOR`. Antes de cualquier escritura, verificar UID y que ese documento no exista; no sobrescribir perfiles ajenos. No tocar las otras bases `(default)` ni `gestioncitas`. Firebase Auth es compartido con otras aplicaciones del proyecto, así que el aislamiento es por usuario dedicado y por documento de autorización, **no un tenant Firebase separado**.

Luego: token Firebase legítimo → gateway protegido IAM → backend privado → Firestore `smartroute`; ejecutar pruebas positivas/negativas y limpieza sintética. No enviar tokens en chat ni logs.

## Infraestructura y pruebas ya validadas

- Backend privado Cloud Run `smartroute-api-staging`.
- Firestore `smartroute`: E2E real con asignación transaccional y limpieza PASS.
- Gateway Cloud Run `smartroute-gateway-staging`, revisión `00001-bq9`, SA `smartroute-gateway@proyectopersonal-480420.iam.gserviceaccount.com`.
- Gateway invoca el backend privado con grant `roles/run.invoker` acotado exclusivamente al backend.
- Imagen gateway publicada con GitHub Actions por digest `sha256:d5c6abe6d73fd8b1ee4b0a8364ad89fb10799c67cc063c1b8f72826397c8ab47`.
- Acceso anónimo al gateway `/health`: **403**; proxy autenticado `/health`: **200**.
- `GET /api/v1/orders` sin Firebase ID Token: **401**; con token inventado: **401**.
- CI `api-tests` y `firestore-emulator` PASS; variable `GCP_STAGING_ENABLED=false`, despliegue continuo apagado.
- **Aún NO probados**: UID dedicado real, perfil OPERATOR real, E2E HTTP Firebase→gateway→backend→Firestore y recorrido Android.

**Recordatorio de seguridad:** `proyectopersonal-480420` alberga otras apps, incluidas `prima-demo-ui-firebase`. No cambiar proveedores/dominios Firebase compartidos, no abrir backend o gateway al público, no asignar roles IAM globales ni modificar recursos ajenos. El panel Firebase puede mostrar advertencias sobre reglas de otras bases; no cambiar reglas sin diagnosticar la base específica.
