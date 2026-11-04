# SmartRoute AI — Identidad exclusiva de prueba OPERATOR (Google Sign-In)

## Decisión

Se utilizará una **cuenta Google nueva, controlada por el equipo y usada solo para SmartRoute AI**, como identidad de prueba. No usar credenciales personales o de otras aplicaciones; no almacenar contraseñas, sesiones ni Firebase ID Tokens en GitHub, Cloud Shell logs o esta conversación.

**Límite de aislamiento:** Firebase Authentication está compartido por todas las apps del proyecto `proyectopersonal-480420`. Una cuenta Google dedicada crea un **usuario diferenciado** con UID propio, pero **NO** crea un tenant Firebase aislado. El aislamiento de permisos de SmartRoute se implementa con `users/{uid}` en la base de Firestore **nombrada** `smartroute`. Si se requiere aislamiento fuerte de credenciales, crear un proyecto Firebase o tenant Identity Platform separado como decisión arquitectónica posterior, con revisión de costos y configuración.

## Estado verificado

- Firebase Google Sign-In habilitado (`enabled=true`) y Email/password también habilitado. No modificar proveedores, dominios o usuarios existentes.
- Gateway `smartroute-gateway-staging` en Cloud Run con IAM privado. Checks HTTP reales: anónimo directo `403`, `/health` por proxy IAM `200`; sin Firebase token `401` y con token inválido `401`.
- Backend privado `smartroute-api-staging`, valida ID Token Firebase, lee el perfil en Firestore `smartroute/users/{uid}` y exige `active: true`, `role: OPERATOR` para órdenes/rutas.
- `GCP_STAGING_ENABLED=false`.

## Fase A — cuenta dedicada, sin modificar GCP

1. Propietario crea una cuenta Google de prueba nueva desde el procedimiento oficial de Google, sin compartir contraseña y con recuperación/MFA.
2. Se usa Google Sign-In mediante **Firebase Auth SDK** en una app registrada al proyecto `proyectopersonal-480420` (preferentemente el futuro cliente Android), con config Firebase app legítima. Iniciar sesión por primera vez con la cuenta dedicada genera automáticamente su usuario Firebase bajo el proyecto compartido. **No** crear por error un usuario email/password con una dirección Google y asumir que está enlazado al proveedor `google.com`.
3. En la consola [Firebase Authentication Users](https://console.firebase.google.com/project/proyectopersonal-480420/authentication/users), localizar **solo el usuario nuevo**, comprobar proveedor Google y copiar **solo UID**; no publicar tokens de sesión.
4. Confirmar que el UID es nuevo, que no está asociado a usuarios de otras aplicaciones y que su identidad se usa únicamente para el piloto. No eliminar usuarios ajenos.

Documentación de Firebase para Google Sign-In: https://firebase.google.com/docs/auth/web/google-signin. Los usuarios Firebase Auth son compartidos dentro del mismo proyecto: https://firebase.google.com/docs/auth/users/.

## Fase B — perfil de autorización exclusivamente SmartRoute

**Todavía no crear ningún documento** hasta confirmar UID de la cuenta nueva y acceso apropiado a la base correcta. Preparar documento en:
`projects/proyectopersonal-480420/databases/smartroute/documents/users/{UID_DE_LA_CUENTA_NUEVA}`

Campos mínimos:

```json
{
  "active": true,
  "role": "OPERATOR"
}
```

Usar solo la **base nombrada `smartroute`**, jamás `(default)` ni `gestioncitas`. El gateway **no** requiere permisos Firestore. Si se utiliza un script de alta, debe fallar si el documento ya existe, no conceder permisos amplios y ofrecer simulación por defecto; mantener principio de mínimo privilegio. No añadir roles por proyecto a Cloud Shell.

## Fase C — pruebas protegidas

1. Desde el cliente Firebase, obtener el ID Token de la sesión Google de prueba, pero **no imprimirlo en chat o logs**.
2. Acceder al gateway por un canal IAM autorizado (durante staging privado) y pasar `Authorization: Bearer <Firebase ID Token>` al endpoint permitido.
3. Esperado con perfil inexistente: backend `403 User not registered`; después del alta exacta, `GET /api/v1/orders` debe responder `200`.
4. Probar creación/lectura y asignación sintéticas de órdenes y rutas, con IDs identificables y limpieza comprobada.
5. Desactivar perfil `active=false` al finalizar piloto y, cuando corresponda, retirar **solo** la identidad Firebase dedicada. No borrar usuarios compartidos ni datos de terceros.
6. No exponer el gateway públicamente sin plan antiabuso, control de orígenes, costos y autorización del propietario.

**Criterio de salida:** UID de Google independiente y perfil OPERATOR exclusivamente en `smartroute`, prueba Firebase→Gateway→Backend→Firestore PASS, sin claves de SA, sin acceso público y sin alterar recursos ajenos.
