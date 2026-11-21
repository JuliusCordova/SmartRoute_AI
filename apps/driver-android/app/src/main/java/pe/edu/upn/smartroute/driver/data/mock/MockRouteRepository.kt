package pe.edu.upn.smartroute.driver.data.mock

import kotlinx.coroutines.delay
import pe.edu.upn.smartroute.driver.domain.model.DataOrigin
import pe.edu.upn.smartroute.driver.domain.model.DeliveryStop
import pe.edu.upn.smartroute.driver.domain.model.Depot
import pe.edu.upn.smartroute.driver.domain.model.GeoPoint
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.model.RouteMetrics
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository

/**
 * Ruta ficticia de cinco paradas en Lima. Todo es sintético (DataOrigin.SYNTHETIC):
 * no proviene del backend ni de una medición. Las direcciones son referenciales.
 */
class MockRouteRepository(private val latencyMs: Long = 400) : RouteRepository {

    override val isDemoData: Boolean = true

    /** Estado en memoria únicamente: se restablece al reiniciar la app. */
    private var currentRoute: Route = demoRoute.copy(version = 1)

    override suspend fun getAssignedRoutes(driverId: String): List<Route> {
        delay(latencyMs)
        return listOf(currentRoute).filter { it.driverId == driverId }
    }

    override suspend fun getRoute(routeId: String): Route? {
        delay(latencyMs)
        return currentRoute.takeIf { it.id == routeId }
    }

    override suspend fun recordStop(
        routeId: String, orderId: String, delivered: Boolean, reason: String?,
        expectedVersion: Int, idempotencyKey: String,
    ): Route {
        require(currentRoute.id == routeId && currentRoute.status == RouteStatus.ACTIVE &&
            currentRoute.version == expectedVersion) { "Ruta de demostración desactualizada" }
        val stop = currentRoute.stop(orderId)
            ?: throw IllegalArgumentException("Parada no encontrada")
        require(!stop.status.isClosed) { "Parada ya atendida" }
        require(delivered || !reason.isNullOrBlank()) { "Indica el motivo del fallo" }
        currentRoute = currentRoute.copy(
            version = expectedVersion + 1,
            stops = currentRoute.stops.map {
                if (it.orderId == orderId) it.copy(status = if (delivered) OrderStatus.DELIVERED else OrderStatus.FAILED)
                else it
            },
        )
        return currentRoute
    }

    override suspend fun completeRoute(routeId: String, expectedVersion: Int, idempotencyKey: String): Route {
        require(currentRoute.id == routeId && currentRoute.status == RouteStatus.ACTIVE &&
            currentRoute.version == expectedVersion &&
            currentRoute.stops.all { it.status.isClosed }) { "Hay entregas pendientes" }
        currentRoute = currentRoute.copy(status = RouteStatus.COMPLETED, version = expectedVersion + 1)
        return currentRoute
    }

    companion object {
        const val DEMO_DRIVER_ID = "driver-demo-01"
        const val DEMO_ROUTE_ID = "RUTA-DEMO-001"

        val demoRoute = Route(
            id = DEMO_ROUTE_ID,
            status = RouteStatus.ACTIVE,
            driverId = DEMO_DRIVER_ID,
            depot = Depot(
                name = "Depósito de prueba",
                address = "Av. Javier Prado Oeste (referencial), San Isidro",
                location = GeoPoint(-12.0950, -77.0350),
            ),
            stops = listOf(
                DeliveryStop("PED-1001", 1, "Av. Arequipa 2450", "Lince", GeoPoint(-12.0850, -77.0340), OrderStatus.DELIVERED, "09:00–11:00"),
                DeliveryStop("PED-1002", 2, "Jr. Huiracocha 1290", "Jesús María", GeoPoint(-12.0765, -77.0480), OrderStatus.DELIVERED, "09:00–11:00"),
                DeliveryStop("PED-1003", 3, "Av. Brasil 2780", "Pueblo Libre", GeoPoint(-12.0790, -77.0610), OrderStatus.IN_TRANSIT, "10:00–12:00", "Tocar el timbre del segundo piso"),
                DeliveryStop("PED-1004", 4, "Av. La Marina 1350", "San Miguel", GeoPoint(-12.0805, -77.0790), OrderStatus.ASSIGNED, "10:00–13:00"),
                DeliveryStop("PED-1005", 5, "Av. Del Ejército 980", "Magdalena del Mar", GeoPoint(-12.0950, -77.0630), OrderStatus.ASSIGNED, "11:00–13:00"),
            ),
            metrics = RouteMetrics(distanceKm = 14.8, durationMinutes = 41, dataOrigin = DataOrigin.SYNTHETIC),
        )

        val routes: List<Route> = listOf(demoRoute)
    }
}
