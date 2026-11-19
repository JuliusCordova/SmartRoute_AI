package pe.edu.upn.smartroute.driver.data.remote

import org.json.JSONException
import org.json.JSONObject
import pe.edu.upn.smartroute.driver.domain.model.DataOrigin
import pe.edu.upn.smartroute.driver.domain.model.DeliveryStop
import pe.edu.upn.smartroute.driver.domain.model.Depot
import pe.edu.upn.smartroute.driver.domain.model.GeoPoint
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.model.RouteError
import pe.edu.upn.smartroute.driver.domain.model.RouteMetrics
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import kotlin.math.roundToInt

/**
 * Traduce el contrato DriverRoute de la API (services/api/app/driver_assignment.py):
 * { id, status: PLANNED|ACTIVE, depot: {latitude, longitude},
 *   stops: [{sequence, order_id, address_label, geo: {latitude, longitude}}] (1..10),
 *   optimized_seconds, optimized_meters, data_origin: "estimated", assigned_at? }
 *
 * El contrato no incluye el estado de cada parada: con la ruta PLANNED o ACTIVE todas las
 * paradas están reservadas para el repartidor, por eso se muestran como ASSIGNED.
 */
object DriverRouteParser {

    fun parse(json: String, driverId: String?): Route = try {
        val o = JSONObject(json)
        val status = when (val s = o.getString("status")) {
            "PLANNED" -> RouteStatus.PLANNED
            "ACTIVE" -> RouteStatus.ACTIVE
            "COMPLETED" -> RouteStatus.COMPLETED
            else -> throw RouteError.InvalidResponse("estado de ruta '$s'")
        }
        val origin = o.optString("data_origin", "estimated")
        if (origin != "estimated") throw RouteError.InvalidResponse("data_origin '$origin'")

        val arr = o.getJSONArray("stops")
        if (arr.length() !in 1..10) throw RouteError.InvalidResponse("${arr.length()} paradas")
        val stops = (0 until arr.length()).map { i ->
            val s = arr.getJSONObject(i)
            DeliveryStop(
                orderId = s.getString("order_id"),
                sequence = s.getInt("sequence"),
                address = s.getString("address_label"),
                district = null,
                location = geo(s.getJSONObject("geo")),
                status = when (s.optString("status", "ASSIGNED")) {
                    "ASSIGNED" -> OrderStatus.ASSIGNED
                    "IN_TRANSIT" -> OrderStatus.IN_TRANSIT
                    "DELIVERED" -> OrderStatus.DELIVERED
                    "FAILED" -> OrderStatus.FAILED
                    else -> throw RouteError.InvalidResponse("estado de parada no reconocido")
                },
                timeWindow = null,
            )
        }
        if (stops.map { it.sequence }.sorted() != (1..stops.size).toList()) throw RouteError.InvalidResponse("secuencia incompleta o repetida")
        if (stops.map { it.orderId }.toSet().size != stops.size) throw RouteError.InvalidResponse("pedido repetido")

        val seconds = o.getInt("optimized_seconds")
        val meters = o.getInt("optimized_meters")
        if (seconds < 0 || meters < 0) throw RouteError.InvalidResponse("métricas negativas")

        Route(
            id = o.getString("id"),
            status = status,
            driverId = driverId,
            depot = Depot(name = "Depósito", address = null, location = geo(o.getJSONObject("depot"))),
            stops = stops,
            version = if (o.has("version")) o.getInt("version").also { require(it >= 1) } else null,
            metrics = RouteMetrics(
                distanceKm = (meters / 100.0).roundToInt() / 10.0,
                durationMinutes = (seconds / 60.0).roundToInt(),
                dataOrigin = DataOrigin.ESTIMATED,
            ),
        )
    } catch (e: RouteError) {
        throw e
    } catch (e: JSONException) {
        throw RouteError.InvalidResponse("JSON: ${e.message}")
    } catch (e: IllegalArgumentException) {
        throw RouteError.InvalidResponse(e.message ?: "valor fuera de rango")
    }

    private fun geo(o: JSONObject) = GeoPoint(o.getDouble("latitude"), o.getDouble("longitude"))
}
