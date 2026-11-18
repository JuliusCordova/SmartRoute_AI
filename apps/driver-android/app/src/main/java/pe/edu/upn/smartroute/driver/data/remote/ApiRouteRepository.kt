package pe.edu.upn.smartroute.driver.data.remote

import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.model.RouteError
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository
import java.io.IOException

/**
 * Adaptador hacia el gateway autenticado: GET /api/v1/driver/me/route.
 * El servidor identifica al repartidor por su token de Firebase; la app nunca envía un UID
 * para pedir rutas, ni llama a la API privada o a Firestore directamente.
 */
class ApiRouteRepository(
    private val gatewayBaseUrl: String,
    private val auth: AuthRepository,
    private val transport: HttpTransport = UrlConnectionTransport(),
) : RouteRepository {

    override val isDemoData: Boolean = false

    private val mutex = Mutex()
    private var cached: Route? = null
    private var cachedUid: String? = null

    private fun currentUid(): String = auth.currentDriver.value?.uid
        ?: throw RouteError.Unauthorized()

    private fun resetCacheFor(uid: String) {
        if (cachedUid != uid) {
            cached = null
            cachedUid = uid
        }
    }

    override suspend fun getAssignedRoutes(driverId: String): List<Route> = mutex.withLock {
        resetCacheFor(currentUid())
        val route = fetchOwnRoute()
        cached = route
        listOfNotNull(route)
    }

    override suspend fun getRoute(routeId: String): Route? = mutex.withLock {
        resetCacheFor(currentUid())
        cached?.takeIf { it.id == routeId }?.let { return@withLock it }
        val route = fetchOwnRoute()
        cached = route
        route?.takeIf { it.id == routeId }
    }

    /** Devuelve null cuando el servidor responde 204 (sin ruta asignada). */
    private suspend fun fetchOwnRoute(): Route? {
        var response = call(forceRefresh = false)
        if (response.code == 401) {
            // El token de Firebase vence cada hora: se renueva una vez y se reintenta.
            response = call(forceRefresh = true)
        }
        return when (response.code) {
            200 -> DriverRouteParser.parse(response.body, auth.currentDriver.value?.uid)
            204 -> null
            401 -> throw RouteError.Unauthorized()
            403 -> throw RouteError.Forbidden()
            409 -> throw RouteError.Conflict()
            in 500..599 -> throw RouteError.Unavailable(response.code)
            else -> throw RouteError.InvalidResponse("HTTP ${response.code}")
        }
    }

    private suspend fun call(forceRefresh: Boolean): HttpResponse {
        val token = auth.idToken(forceRefresh) ?: throw RouteError.Unauthorized()
        return try {
            transport.get(
                url = gatewayBaseUrl.trimEnd('/') + OWN_ROUTE_PATH,
                headers = mapOf("Authorization" to "Bearer $token", "Accept" to "application/json"),
            )
        } catch (e: IOException) {
            throw RouteError.Network()
        }
    }

    companion object {
        const val OWN_ROUTE_PATH = "/api/v1/driver/me/route"
    }
}
