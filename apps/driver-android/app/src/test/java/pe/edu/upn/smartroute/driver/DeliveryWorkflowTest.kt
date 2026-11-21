package pe.edu.upn.smartroute.driver

import kotlinx.coroutines.test.runTest
import org.json.JSONObject
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Assert.fail
import org.junit.Test
import pe.edu.upn.smartroute.driver.data.remote.ApiRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.DriverRouteParser
import pe.edu.upn.smartroute.driver.data.remote.HttpResponse
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.domain.model.RouteError
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus

/** US-013/014: contrato Android (el backend debe cumplirlo antes de habilitar el flag). */
class DeliveryWorkflowTest {
    private val routeId = "3f6c2a1e-8b9d-4c1f-9a2e-6d7b8c9d0e1f"
    private val key = "d343e4d7-bfa6-4426-bbdc-596ef25e3400"

    private fun activeRouteJson(vararg states: Pair<String, String>): String {
        val json = JSONObject(DRIVER_ROUTE_JSON)
        json.put("status", "ACTIVE")
        json.put("version", 2)
        val arr = json.getJSONArray("stops")
        for (i in 0 until arr.length()) {
            val item = arr.getJSONObject(i)
            states.firstOrNull { it.first == item.getString("order_id") }?.let { item.put("status", it.second) }
        }
        return json.toString()
    }

    @Test
    fun start_route_posts_expected_version_and_validates_receipt() = runTest {
        val planned = JSONObject(DRIVER_ROUTE_JSON).put("version", 2).toString()
        val transport = FakeTransport(
            HttpResponse(200, planned),
            HttpResponse(200, """{"id":"$routeId","status":"ACTIVE","version":3}"""),
        )
        val repo = ApiRouteRepository("https://gateway.example", FakeAuth(), transport, qaWriteAllowed = { _, _ -> true })
        repo.getAssignedRoutes("ignored")
        val updated = repo.startRoute(routeId, 2, key)
        assertEquals(RouteStatus.ACTIVE, updated.status)
        assertEquals(3, updated.version)
        assertTrue(transport.posts.single().first.endsWith("/api/v1/driver/me/route/start"))
        val body = JSONObject(transport.posts.single().third)
        assertEquals(2, body.getInt("expected_version"))
        assertEquals(key, body.getString("idempotency_key"))
    }

    @Test
    fun parser_reads_authoritative_stop_statuses() {
        val route = DriverRouteParser.parse(
            activeRouteJson("ord-a" to "DELIVERED", "ord-b" to "FAILED"), "qa",
        )
        assertEquals(1, route.progress.delivered)
        assertEquals(1, route.progress.failed)
        assertEquals(0, route.progress.pending)
    }

    @Test
    fun deliver_sends_version_and_idempotency_and_updates_progress() = runTest {
        val transport = FakeTransport(
            HttpResponse(200, activeRouteJson()),
            HttpResponse(200, """{"id":"$routeId","status":"ACTIVE","version":3,"order_id":"ord-a","order_status":"DELIVERED"}"""),
        )
        val repo = ApiRouteRepository("https://gateway.example", FakeAuth(), transport, qaWriteAllowed = { _, _ -> true })
        repo.getAssignedRoutes("ignored")
        val updated = repo.recordStop(routeId, "ord-a", true, null, 2, key)
        assertEquals(3, updated.version)
        assertEquals(OrderStatus.DELIVERED, updated.stop("ord-a")?.status)
        assertEquals(1, updated.progress.delivered)
        assertEquals("https://gateway.example/api/v1/driver/me/route/stops/ord-a/deliver", transport.posts.single().first)
        val request = JSONObject(transport.posts.single().third)
        assertEquals(2, request.getInt("expected_version"))
        assertEquals(key, request.getString("idempotency_key"))
        assertTrue(!request.has("reason"))
        assertTrue(transport.posts.single().second["Authorization"]!!.startsWith("Bearer "))
    }

    @Test
    fun failure_requires_reason_and_post_includes_it() = runTest {
        val transport = FakeTransport(
            HttpResponse(200, activeRouteJson()),
            HttpResponse(200, """{"id":"$routeId","status":"ACTIVE","version":3,"order_id":"ord-b","order_status":"FAILED"}"""),
        )
        val repo = ApiRouteRepository("https://gateway.example", FakeAuth(), transport, qaWriteAllowed = { _, _ -> true })
        repo.getAssignedRoutes("ignored")
        try {
            repo.recordStop(routeId, "ord-b", false, " ", 2, key)
            fail("Debe exigir motivo")
        } catch (_: IllegalArgumentException) { }
        assertTrue(transport.posts.isEmpty())
        val updated = repo.recordStop(routeId, "ord-b", false, "Dirección cerrada", 2, key)
        assertEquals(OrderStatus.FAILED, updated.stop("ord-b")?.status)
        assertEquals("Dirección cerrada", JSONObject(transport.posts.single().third).getString("reason"))
    }

    @Test
    fun complete_requires_all_stops_closed_and_checks_server_receipt() = runTest {
        val transport = FakeTransport(
            HttpResponse(200, activeRouteJson("ord-a" to "DELIVERED", "ord-b" to "FAILED")),
            HttpResponse(200, """{"id":"$routeId","status":"COMPLETED","version":3}"""),
        )
        val repo = ApiRouteRepository("https://gateway.example", FakeAuth(), transport, qaWriteAllowed = { _, _ -> true })
        repo.getAssignedRoutes("ignored")
        val updated = repo.completeRoute(routeId, 2, key)
        assertEquals(RouteStatus.COMPLETED, updated.status)
        assertEquals(3, updated.version)
        assertTrue(transport.posts.single().first.endsWith("/api/v1/driver/me/route/complete"))
    }

    @Test
    fun complete_rejects_pending_stops_without_post() = runTest {
        val transport = FakeTransport(HttpResponse(200, activeRouteJson()))
        val repo = ApiRouteRepository("https://gateway.example", FakeAuth(), transport, qaWriteAllowed = { _, _ -> true })
        repo.getAssignedRoutes("ignored")
        try {
            repo.completeRoute(routeId, 2, key)
            fail("No debe cerrar pendientes")
        } catch (_: RouteError.Conflict) { }
        assertTrue(transport.posts.isEmpty())
    }

    @Test
    fun rejects_unconfirmed_success_and_missing_backend_endpoint() = runTest {
        val wrong = FakeTransport(
            HttpResponse(200, activeRouteJson()),
            HttpResponse(200, """{"id":"$routeId","status":"ACTIVE","version":2,"order_id":"ord-a","order_status":"DELIVERED"}"""),
        )
        val repo1 = ApiRouteRepository("https://gateway.example", FakeAuth(), wrong, qaWriteAllowed = { _, _ -> true })
        repo1.getAssignedRoutes("ignored")
        try {
            repo1.recordStop(routeId, "ord-a", true, null, 2, key)
            fail("No debe aceptar versión sin incrementar")
        } catch (_: RouteError.InvalidResponse) { }

        val missing = FakeTransport(HttpResponse(200, activeRouteJson()), HttpResponse(404, ""))
        val repo2 = ApiRouteRepository("https://gateway.example", FakeAuth(), missing, qaWriteAllowed = { _, _ -> true })
        repo2.getAssignedRoutes("ignored")
        try {
            repo2.recordStop(routeId, "ord-a", true, null, 2, key)
            fail("No debe confirmar entrega sin endpoint")
        } catch (_: RouteError.InvalidResponse) { }
    }
}
