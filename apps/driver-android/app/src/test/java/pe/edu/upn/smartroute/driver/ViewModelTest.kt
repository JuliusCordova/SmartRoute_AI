package pe.edu.upn.smartroute.driver

import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.advanceUntilIdle
import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import pe.edu.upn.smartroute.driver.data.mock.MockRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.ApiRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.HttpResponse
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository
import pe.edu.upn.smartroute.driver.ui.UiState
import pe.edu.upn.smartroute.driver.ui.screens.dashboard.DashboardViewModel
import pe.edu.upn.smartroute.driver.ui.screens.route.RouteDetailViewModel

@OptIn(ExperimentalCoroutinesApi::class)
class ViewModelTest {

    @get:Rule
    val mainRule = MainDispatcherRule()

    private val mock = MockRouteRepository(latencyMs = 0)

    @Test
    fun dashboard_loads_assigned_routes() = runTest(mainRule.dispatcher) {
        val vm = DashboardViewModel(MockRouteRepository.DEMO_DRIVER_ID, mock)
        advanceUntilIdle()
        val state = vm.state.value
        assertTrue(state is UiState.Success)
        assertEquals(1, (state as UiState.Success).data.size)
        assertTrue(vm.isDemoData)
    }

    @Test
    fun dashboard_explains_account_without_driver_role() = runTest(mainRule.dispatcher) {
        val api = ApiRouteRepository("https://gateway.example", FakeAuth(), FakeTransport(HttpResponse(403, "")))
        val vm = DashboardViewModel("x", api)
        advanceUntilIdle()
        val state = vm.state.value
        assertTrue(state is UiState.Error)
        assertTrue((state as UiState.Error).message.contains("repartidor"))
    }

    @Test
    fun dashboard_shows_error_on_network_failure() = runTest(mainRule.dispatcher) {
        val failing = object : RouteRepository {
            override val isDemoData = false
            override suspend fun getAssignedRoutes(driverId: String): List<Route> = throw java.io.IOException("sin red")
            override suspend fun getRoute(routeId: String): Route? = throw java.io.IOException("sin red")
        }
        val vm = DashboardViewModel("x", failing)
        advanceUntilIdle()
        assertTrue(vm.state.value is UiState.Error)
    }

    @Test
    fun dashboard_shows_empty_success_when_no_route_assigned() = runTest(mainRule.dispatcher) {
        val api = ApiRouteRepository("https://gateway.example", FakeAuth(), FakeTransport(HttpResponse(204, "")))
        val vm = DashboardViewModel("x", api)
        advanceUntilIdle()
        val state = vm.state.value
        assertTrue(state is UiState.Success && state.data.isEmpty())
    }

    @Test
    fun route_detail_loads_route_and_reports_not_found() = runTest(mainRule.dispatcher) {
        val ok = RouteDetailViewModel(MockRouteRepository.DEMO_ROUTE_ID, mock)
        val missing = RouteDetailViewModel("NO-EXISTE", mock)
        advanceUntilIdle()
        assertTrue(ok.state.value is UiState.Success)
        assertTrue(missing.state.value is UiState.NotFound)
    }
}
