package pe.edu.upn.smartroute.driver.ui.screens.route

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import java.util.UUID
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository
import pe.edu.upn.smartroute.driver.ui.UiState
import pe.edu.upn.smartroute.driver.ui.toUserMessage

/** Carga una ruta; lo usan el detalle de ruta y el detalle de pedido. */
class RouteDetailViewModel(
    private val routeId: String,
    private val routes: RouteRepository,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<Route>>(UiState.Loading)
    val state: StateFlow<UiState<Route>> = _state.asStateFlow()

    val isDemoData: Boolean get() = routes.isDemoData

    fun canMutateRoute(routeId: String): Boolean = routes.canMutateRoute(routeId)

    private val _gpsError = MutableStateFlow<String?>(null)
    val gpsError: StateFlow<String?> = _gpsError.asStateFlow()
    private val _gpsLastSent = MutableStateFlow<String?>(null)
    val gpsLastSent: StateFlow<String?> = _gpsLastSent.asStateFlow()

    /** GPS only with consent in the visible ACTIVE route screen. */
    suspend fun sendGps(latitude: Double, longitude: Double, accuracyMeters: Float,
                        timestampIso: String) {
        val route = (_state.value as? UiState.Success)?.data ?: return
        if (route.status != RouteStatus.ACTIVE || isDemoData || !canMutateRoute(route.id)) return
        try {
            routes.submitLocation(route.id, latitude, longitude, accuracyMeters, timestampIso)
            _gpsLastSent.value = timestampIso
            _gpsError.value = null
        } catch (e: Exception) {
            _gpsError.value = e.toUserMessage()
        }
    }

    private val _starting = MutableStateFlow(false)
    val starting: StateFlow<Boolean> = _starting.asStateFlow()
    private val _startError = MutableStateFlow<String?>(null)
    val startError: StateFlow<String?> = _startError.asStateFlow()

    /** Solo se ejecuta después de confirmación explícita en la UI. */
    fun startRoute() {
        if (_starting.value || isDemoData) return
        val route = (_state.value as? UiState.Success)?.data ?: return
        if (!canMutateRoute(route.id)) return
        val version = route.version ?: return
        if (route.status != RouteStatus.PLANNED) return
        _starting.value = true
        _startError.value = null
        val key = idempotencyFor("start:${route.id}:$version")
        viewModelScope.launch {
            try {
                val active = routes.startRoute(route.id, version, key)
                _state.value = UiState.Success(active)
                clearPending()
            } catch (e: Exception) {
                _startError.value = e.toUserMessage()
            } finally {
                _starting.value = false
            }
        }
    }


    /** Reutiliza una misma clave de idempotencia al reintentar una mutación fallida. */
    private var pendingSignature: String? = null
    private var pendingKey: String? = null
    private fun idempotencyFor(signature: String): String {
        if (pendingSignature != signature) {
            pendingSignature = signature
            pendingKey = UUID.randomUUID().toString()
        }
        return pendingKey!!
    }
    private fun clearPending() { pendingSignature = null; pendingKey = null }

    private val _mutating = MutableStateFlow(false)
    val mutating: StateFlow<Boolean> = _mutating.asStateFlow()
    private val _mutationError = MutableStateFlow<String?>(null)
    val mutationError: StateFlow<String?> = _mutationError.asStateFlow()

    /** US-013: confirmación explícita, solo ACTIVE y solo con backend habilitado. */
    fun recordStop(orderId: String, delivered: Boolean, reason: String?) {
        if (_mutating.value || _starting.value) return
        val route = (_state.value as? UiState.Success)?.data ?: return
        if (!isDemoData && !canMutateRoute(route.id)) return
        val stop = route.stop(orderId) ?: return
        val version = route.version ?: return
        if (route.status != RouteStatus.ACTIVE || stop.status.isClosed) return
        if (!delivered && (reason.isNullOrBlank() || reason.trim().length > 250)) {
            _mutationError.value = "Indica un motivo de 1 a 250 caracteres."
            return
        }
        val signature = "stop:${route.id}:$orderId:$delivered:${reason?.trim()}:$version"
        val key = idempotencyFor(signature)
        _mutating.value = true
        _mutationError.value = null
        viewModelScope.launch {
            try {
                _state.value = UiState.Success(
                    routes.recordStop(route.id, orderId, delivered, reason, version, key)
                )
                clearPending()
            } catch (e: Exception) {
                _mutationError.value = e.toUserMessage()
            } finally {
                _mutating.value = false
            }
        }
    }

    /** US-014: cierre solo tras resolver todas las entregas. */
    fun completeRoute() {
        if (isDemoData || _mutating.value || _starting.value) return
        val route = (_state.value as? UiState.Success)?.data ?: return
        val version = route.version ?: return
        if (!canMutateRoute(route.id)) return
        if (route.status != RouteStatus.ACTIVE || route.progress.pending != 0 || route.stops.isEmpty()) return
        val key = idempotencyFor("complete:${route.id}:$version")
        _mutating.value = true
        _mutationError.value = null
        viewModelScope.launch {
            try {
                _state.value = UiState.Success(routes.completeRoute(route.id, version, key))
                clearPending()
            } catch (e: Exception) {
                _mutationError.value = e.toUserMessage()
            } finally {
                _mutating.value = false
            }
        }
    }

    init {
        load()
    }

    fun load() {
        if (_starting.value || _mutating.value) return
        _mutationError.value = null
        _startError.value = null
        _state.value = UiState.Loading
        viewModelScope.launch {
            _state.value = try {
                routes.refreshRoute(routeId)?.let { UiState.Success(it) }
                    ?: UiState.NotFound("Esta ruta ya no está asignada a tu cuenta.")
            } catch (e: Exception) {
                UiState.Error(e.toUserMessage())
            }
        }
    }
}
