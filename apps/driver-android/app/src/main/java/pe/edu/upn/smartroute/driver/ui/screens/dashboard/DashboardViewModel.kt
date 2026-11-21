package pe.edu.upn.smartroute.driver.ui.screens.dashboard

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

class DashboardViewModel(
    private val driverId: String,
    private val routes: RouteRepository,
) : ViewModel() {

    private val _state = MutableStateFlow<UiState<List<Route>>>(UiState.Loading)
    val state: StateFlow<UiState<List<Route>>> = _state.asStateFlow()

    val isDemoData: Boolean get() = routes.isDemoData

    init {
        load()
    }

    fun load() {
        _state.value = UiState.Loading
        viewModelScope.launch {
            _state.value = try {
                UiState.Success(routes.getAssignedRoutes(driverId))
            } catch (e: Exception) {
                UiState.Error(e.toUserMessage())
            }
        }
    }
}
