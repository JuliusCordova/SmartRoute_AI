package pe.edu.upn.smartroute.driver

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import pe.edu.upn.smartroute.driver.data.remote.HttpResponse
import pe.edu.upn.smartroute.driver.data.remote.HttpTransport
import pe.edu.upn.smartroute.driver.domain.model.DriverProfile
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.GoogleCredentialSource

/** Sesión falsa con tokens sintéticos; registra si se pidió renovar el token. */
class FakeAuth(private val token: String? = "token-sintetico") : AuthRepository {
    override val isDemo = false
    private val mutableDriver = MutableStateFlow<DriverProfile?>(
        if (token != null) DriverProfile("driver-uid-sintetico", "Repartidor") else null
    )
    override val currentDriver: StateFlow<DriverProfile?> = mutableDriver
    fun changeDriver(uid: String?) {
        mutableDriver.value = uid?.let { DriverProfile(it, "Repartidor") }
    }
    val refreshes = mutableListOf<Boolean>()

    override suspend fun signIn(source: GoogleCredentialSource) = Result.failure<DriverProfile>(UnsupportedOperationException())
    override suspend fun signOut() = Unit
    override suspend fun idToken(forceRefresh: Boolean): String? {
        refreshes += forceRefresh
        return token?.let { if (forceRefresh) "$it-renovado" else it }
    }
}

/** Transporte falso: devuelve respuestas en orden y registra cada llamada. */
class FakeTransport(vararg responses: HttpResponse, private val failWith: Exception? = null) : HttpTransport {
    private val queue = ArrayDeque(responses.toList())
    val calls = mutableListOf<Pair<String, Map<String, String>>>()

    override suspend fun get(url: String, headers: Map<String, String>): HttpResponse {
        calls += url to headers
        failWith?.let { throw it }
        return queue.removeFirstOrNull() ?: error("Sin respuesta programada")
    }
}

/** Ejemplo del contrato DriverRoute tal como lo serializa la API (FastAPI/Pydantic). */
const val DRIVER_ROUTE_JSON = """
{
  "id": "3f6c2a1e-8b9d-4c1f-9a2e-6d7b8c9d0e1f",
  "status": "PLANNED",
  "depot": {"latitude": -12.095, "longitude": -77.035},
  "stops": [
    {"sequence": 2, "order_id": "ord-b", "address_label": "Av. Brasil 2780, Pueblo Libre", "geo": {"latitude": -12.079, "longitude": -77.061}},
    {"sequence": 1, "order_id": "ord-a", "address_label": "Av. Arequipa 2450, Lince", "geo": {"latitude": -12.085, "longitude": -77.034}}
  ],
  "optimized_seconds": 1500,
  "optimized_meters": 15260,
  "data_origin": "estimated",
  "assigned_at": "2026-11-15T21:30:00Z"
}
"""
