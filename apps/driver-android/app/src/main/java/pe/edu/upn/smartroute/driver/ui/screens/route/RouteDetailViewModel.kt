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

    private val _starting = MutableStateFlow(false)
    val starting: StateFlow<Boolean> = _starting.asStateFlow()
    private val _startError = MutableStateFlow<String?>(null)
    val startError: StateFlow<String?> = _startError.asStateFlow()

    /** Solo se ejecuta después de confirmación explícita en la UI. */
    fun startRoute() {
        if (_starting.value || isDemoData) return
        val route = (_state.value as? UiState.Success)?.data ?: return
        val version = route.version ?: return
        if (route.status != RouteStatus.PLANNED) return
        _starting.value = true
        _startError.value = null
        val key = UUID.randomUUID().toString()
        viewModelScope.launch {
            try {
                val active = routes.startRoute(route.id, version, key)
                _state.value = UiState.Success(active)
            } catch (e: Exception) {
                _startError.value = e.toUserMessage()
            } finally {
                _starting.value = false
            }
        }
    }


    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            _state.value = try {
                routes.getRoute(routeId)?.let { UiState.Success(it) }
                    ?: UiState.NotFound("Esta ruta ya no está asignada a tu cuenta.")
            } catch (e: Exception) {
                UiState.Error(e.toUserMessage())
            }
        }
    }
}
