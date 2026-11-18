package pe.edu.upn.smartroute.driver

import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test
import pe.edu.upn.smartroute.driver.data.mock.MockAuthRepository
import pe.edu.upn.smartroute.driver.data.mock.MockRouteRepository
import pe.edu.upn.smartroute.driver.domain.model.DataOrigin

class RepositoryTest {

    private val repo = MockRouteRepository(latencyMs = 0)

    @Test
    fun mock_route_has_five_ordered_stops_inside_lima() = runTest {
        val route = repo.getRoute(MockRouteRepository.DEMO_ROUTE_ID)
        assertNotNull(route)
        route!!
        assertEquals(5, route.stops.size)
        assertEquals(listOf(1, 2, 3, 4, 5), route.orderedStops.map { it.sequence })
        assertEquals(5, route.stops.map { it.orderId }.toSet().size)
        // Caja aproximada de Lima Metropolitana.
        (route.stops.map { it.location } + route.depot.location).forEach {
            assertTrue("Latitud fuera de Lima: ${it.latitude}", it.latitude in -12.30..-11.70)
            assertTrue("Longitud fuera de Lima: ${it.longitude}", it.longitude in -77.20..-76.80)
        }
    }

    @Test
    fun mock_data_is_flagged_as_synthetic() = runTest {
        val route = repo.getRoute(MockRouteRepository.DEMO_ROUTE_ID)!!
        assertEquals(DataOrigin.SYNTHETIC, route.metrics.dataOrigin)
        assertTrue(repo.isDemoData)
    }

    @Test
    fun driver_only_sees_own_routes() = runTest {
        assertEquals(1, repo.getAssignedRoutes(MockRouteRepository.DEMO_DRIVER_ID).size)
        assertTrue(repo.getAssignedRoutes("otro-repartidor").isEmpty())
    }

    @Test
    fun unknown_route_returns_null() = runTest {
        assertNull(repo.getRoute("NO-EXISTE"))
    }

    @Test
    fun mock_auth_signs_in_and_out() = runTest {
        val auth = MockAuthRepository()
        assertNull(auth.currentDriver.value)
        val result = auth.signIn { "no-se-usa" }
        assertTrue(result.isSuccess)
        assertEquals(MockRouteRepository.DEMO_DRIVER_ID, auth.currentDriver.value?.uid)
        auth.signOut()
        assertNull(auth.currentDriver.value)
    }
}
