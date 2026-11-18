package pe.edu.upn.smartroute.driver

import kotlinx.coroutines.test.runTest
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import pe.edu.upn.smartroute.driver.data.remote.ApiRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.DriverRouteParser
import pe.edu.upn.smartroute.driver.data.remote.HttpResponse
import pe.edu.upn.smartroute.driver.domain.model.DataOrigin
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.domain.model.RouteError
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import java.io.IOException

class DriverRouteContractTest {

    private val base = "https://gateway.example"
    private val routeId = "3f6c2a1e-8b9d-4c1f-9a2e-6d7b8c9d0e1f"

    // ---------- Parser del contrato DriverRoute ----------

    @Test
    fun parser_maps_driver_route_contract() {
        val route = DriverRouteParser.parse(DRIVER_ROUTE_JSON, "driver-uid")
        assertEquals(routeId, route.id)
        assertEquals(RouteStatus.PLANNED, route.status)
        assertEquals(listOf("ord-a", "ord-b"), route.orderedStops.map { it.orderId })
        assertEquals("Av. Arequipa 2450, Lince", route.orderedStops.first().address)
        assertEquals(-12.095, route.depot.location.latitude, 1e-9)
        assertEquals(15.3, route.metrics.distanceKm, 1e-9)
        assertEquals(25, route.metrics.durationMinutes)
        assertEquals(DataOrigin.ESTIMATED, route.metrics.dataOrigin)
        assertTrue(route.stops.all { it.status == OrderStatus.ASSIGNED })
        assertNull(route.stops.first().timeWindow)
    }

    @Test
    fun parser_reads_version_for_us012_and_preserves_legacy_compatibility() {
        val legacy = DriverRouteParser.parse(DRIVER_ROUTE_JSON, "driver-uid")
        assertNull(legacy.version)
        val versioned = org.json.JSONObject(DRIVER_ROUTE_JSON).put("version", 2).toString()
        assertEquals(2, DriverRouteParser.parse(versioned, "driver-uid").version)
    }

    @Test
    fun parser_rejects_unknown_route_status() {
        expectInvalid(DRIVER_ROUTE_JSON.replace("\"PLANNED\"", "\"COMPLETED\""))
    }

    @Test
    fun parser_rejects_non_estimated_origin() {
        expectInvalid(DRIVER_ROUTE_JSON.replace("\"estimated\"", "\"observed\""))
    }

    @Test
    fun parser_rejects_non_consecutive_sequence() {
        expectInvalid(DRIVER_ROUTE_JSON.replace("\"sequence\": 2", "\"sequence\": 3"))
    }

    @Test
    fun parser_rejects_duplicated_sequence() {
        expectInvalid(DRIVER_ROUTE_JSON.replace("\"sequence\": 2", "\"sequence\": 1"))
    }

    @Test
    fun parser_rejects_malformed_json_and_out_of_range_coordinates() {
        expectInvalid("{ no es json")
        expectInvalid(DRIVER_ROUTE_JSON.replace("-12.095", "-120.0"))
    }

    private fun expectInvalid(json: String) {
        try {
            DriverRouteParser.parse(json, null)
            fail("Debió rechazar la respuesta")
        } catch (e: RouteError.InvalidResponse) {
            // esperado
        }
    }

    // ---------- Repositorio contra el gateway ----------

    @Test
    fun repository_calls_own_route_with_bearer_token() = runTest {
        val transport = FakeTransport(HttpResponse(200, DRIVER_ROUTE_JSON))
        val repo = ApiRouteRepository(base, FakeAuth(), transport)
        val routes = repo.getAssignedRoutes("ignorado-por-el-servidor")
        assertEquals(1, routes.size)
        assertFalse(repo.isDemoData)
        val (url, headers) = transport.calls.single()
        assertEquals("$base/api/v1/driver/me/route", url)
        assertEquals("Bearer token-sintetico", headers["Authorization"])
        assertFalse("La app no envía el UID para pedir rutas", url.contains("ignorado"))
    }

    @Test
    fun repository_returns_empty_list_on_204() = runTest {
        val repo = ApiRouteRepository(base, FakeAuth(), FakeTransport(HttpResponse(204, "")))
        assertTrue(repo.getAssignedRoutes("x").isEmpty())
    }

    @Test
    fun repository_refreshes_token_once_on_401() = runTest {
        val auth = FakeAuth()
        val transport = FakeTransport(HttpResponse(401, ""), HttpResponse(200, DRIVER_ROUTE_JSON))
        val repo = ApiRouteRepository(base, auth, transport)
        assertEquals(1, repo.getAssignedRoutes("x").size)
        assertEquals(listOf(false, true), auth.refreshes)
        assertEquals("Bearer token-sintetico-renovado", transport.calls[1].second["Authorization"])
    }

    @Test
    fun repository_maps_http_errors() = runTest {
        expectError<RouteError.Unauthorized>(HttpResponse(401, ""), HttpResponse(401, ""))
        expectError<RouteError.Forbidden>(HttpResponse(403, "{\"detail\":\"Driver role required\"}"))
        expectError<RouteError.Conflict>(HttpResponse(409, ""))
        expectError<RouteError.Unavailable>(HttpResponse(503, ""))
        expectError<RouteError.Unavailable>(HttpResponse(502, ""))
    }

    @Test
    fun repository_without_session_does_not_call_network() = runTest {
        val transport = FakeTransport(HttpResponse(200, DRIVER_ROUTE_JSON))
        val repo = ApiRouteRepository(base, FakeAuth(token = null), transport)
        try {
            repo.getAssignedRoutes("x")
            fail("Debió exigir sesión")
        } catch (e: RouteError.Unauthorized) {
            assertTrue(transport.calls.isEmpty())
        }
    }

    @Test
    fun repository_maps_io_failure_to_network_error() = runTest {
        val repo = ApiRouteRepository(base, FakeAuth(), FakeTransport(failWith = IOException("timeout")))
        try {
            repo.getAssignedRoutes("x")
            fail("Debió fallar por red")
        } catch (e: RouteError.Network) {
            // esperado
        }
    }

    @Test
    fun get_route_uses_cache_and_rejects_other_ids() = runTest {
        val transport = FakeTransport(HttpResponse(200, DRIVER_ROUTE_JSON), HttpResponse(200, DRIVER_ROUTE_JSON))
        val repo = ApiRouteRepository(base, FakeAuth(), transport)
        repo.getAssignedRoutes("x")
        assertEquals(routeId, repo.getRoute(routeId)?.id)
        assertEquals(1, transport.calls.size)
        assertNull(repo.getRoute("otra-ruta"))
    }

    @Test
    fun cached_route_is_not_visible_after_sign_out() = runTest {
        val auth = FakeAuth()
        val transport = FakeTransport(HttpResponse(200, DRIVER_ROUTE_JSON))
        val repo = ApiRouteRepository(base, auth, transport)
        repo.getAssignedRoutes("driver-uid-sintetico")
        auth.changeDriver(null)
        try {
            repo.getRoute(routeId)
            fail("La ruta en caché no debe exponerse sin sesión")
        } catch (e: RouteError.Unauthorized) {
            assertEquals(1, transport.calls.size)
        }
    }

    @Test
    fun cached_route_is_not_shared_between_drivers() = runTest {
        val auth = FakeAuth()
        val transport = FakeTransport(HttpResponse(200, DRIVER_ROUTE_JSON), HttpResponse(204, ""))
        val repo = ApiRouteRepository(base, auth, transport)
        repo.getAssignedRoutes("driver-uid-sintetico")
        auth.changeDriver("otro-conductor")
        assertNull(repo.getRoute(routeId))
        assertEquals(2, transport.calls.size)
    }

    private suspend inline fun <reified E : RouteError> expectError(vararg responses: HttpResponse) {
        val repo = ApiRouteRepository(base, FakeAuth(), FakeTransport(*responses))
        try {
            repo.getAssignedRoutes("x")
            fail("Debió lanzar ${E::class.simpleName}")
        } catch (e: RouteError) {
            assertTrue("Se esperaba ${E::class.simpleName} y llegó ${e::class.simpleName}", e is E)
        }
    }
}
