package pe.edu.upn.smartroute.driver.domain.repository

import kotlinx.coroutines.flow.StateFlow
import pe.edu.upn.smartroute.driver.domain.model.DriverProfile
import pe.edu.upn.smartroute.driver.domain.model.Route

/** Puerto de lectura de rutas del repartidor. La UI depende solo de esta interfaz. */
interface RouteRepository {
    /** Indica si los datos son de demostración, para mostrarlo en pantalla (BR-12). */
    val isDemoData: Boolean

    /** Capacidad de escribir limitada a la sesión y ruta QA; false por defecto. */
    fun canMutateRoute(routeId: String): Boolean = false

    /**
     * Rutas del repartidor autenticado. Con el backend real, la identidad la decide el servidor
     * a partir del token: [driverId] solo se usa en modo demostración.
     */
    suspend fun getAssignedRoutes(driverId: String): List<Route>

    suspend fun getRoute(routeId: String): Route?

    /** Solicita el estado fresco al servidor al volver de otra pantalla. */
    suspend fun refreshRoute(routeId: String): Route? = getRoute(routeId)

    /** US-012: mutación explícita, solo disponible para DRIVER autenticado y versión conocida. */
    suspend fun startRoute(routeId: String, expectedVersion: Int, idempotencyKey: String): Route {
        throw UnsupportedOperationException("Inicio no disponible en modo demostración")
    }

    /** US-013: confirma una entrega o falla por medio del gateway autenticado. */
    suspend fun recordStop(
        routeId: String, orderId: String, delivered: Boolean, reason: String?,
        expectedVersion: Int, idempotencyKey: String,
    ): Route {
        throw UnsupportedOperationException("Registro de entregas no disponible")
    }

    /** US-014: cierra el recorrido tras resolver la totalidad de paradas. */
    suspend fun completeRoute(routeId: String, expectedVersion: Int, idempotencyKey: String): Route {
        throw UnsupportedOperationException("Cierre no disponible")
    }
}

/** Fuente de la credencial de Google. La implementa la capa de UI porque necesita una Activity. */
fun interface GoogleCredentialSource {
    /** Devuelve el ID token de Google del usuario que eligió su cuenta. */
    suspend fun googleIdToken(): String
}

/**
 * Puerto de autenticación: Firebase Authentication con Google Sign-In (como el panel web),
 * o una sesión de demostración. La app no guarda contraseñas ni tokens en disco.
 */
interface AuthRepository {
    val isDemo: Boolean

    val currentDriver: StateFlow<DriverProfile?>

    suspend fun signIn(source: GoogleCredentialSource): Result<DriverProfile>

    suspend fun signOut()

    /** ID token de Firebase para el encabezado Authorization; null si no hay sesión. */
    suspend fun idToken(forceRefresh: Boolean = false): String?
}
