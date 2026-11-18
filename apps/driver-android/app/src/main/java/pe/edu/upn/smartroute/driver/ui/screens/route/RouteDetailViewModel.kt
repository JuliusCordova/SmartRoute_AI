package pe.edu.upn.smartroute.driver.ui.screens.route

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
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
