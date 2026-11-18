package pe.edu.upn.smartroute.driver.domain.model

/** Punto geográfico en grados decimales (WGS84). */
data class GeoPoint(val latitude: Double, val longitude: Double) {
    init {
        require(latitude in -90.0..90.0) { "Latitud fuera de rango: $latitude" }
        require(longitude in -180.0..180.0) { "Longitud fuera de rango: $longitude" }
    }
}

/** Estados del pedido según SPEC BR-02: PENDING → ASSIGNED → IN_TRANSIT → DELIVERED/FAILED. */
enum class OrderStatus { PENDING, ASSIGNED, IN_TRANSIT, DELIVERED, FAILED;

    /** Una parada está atendida cuando terminó, con éxito o sin él. */
    val isClosed: Boolean get() = this == DELIVERED || this == FAILED
}

/** Estados de la ruta según SPEC BR-03: DRAFT → PLANNED → ACTIVE → COMPLETED/CANCELLED. */
enum class RouteStatus { DRAFT, PLANNED, ACTIVE, COMPLETED, CANCELLED }

/**
 * Origen del dato según SPEC BR-12. Nunca se suman datos de orígenes distintos.
 * SYNTHETIC: generado para pruebas. ESTIMATED: calculado con la matriz vial. OBSERVED: medido en campo.
 */
enum class DataOrigin { SYNTHETIC, ESTIMATED, OBSERVED }

data class Depot(val name: String, val address: String?, val location: GeoPoint)

data class DeliveryStop(
    val orderId: String,
    val sequence: Int,
    val address: String,
    /** El backend aún no envía distrito ni ventana horaria: son opcionales. */
    val district: String?,
    val location: GeoPoint,
    val status: OrderStatus,
    val timeWindow: String?,
    val notes: String? = null,
) {
    init {
        require(sequence >= 1) { "La secuencia empieza en 1" }
    }
}

data class RouteMetrics(
    val distanceKm: Double,
    val durationMinutes: Int,
    val dataOrigin: DataOrigin,
)

data class Route(
    val id: String,
    val status: RouteStatus,
    val driverId: String?,
    val depot: Depot,
    val stops: List<DeliveryStop>,
    val metrics: RouteMetrics,
) {
    /** Paradas en el orden de visita. */
    val orderedStops: List<DeliveryStop> get() = stops.sortedBy { it.sequence }

    val progress: DeliveryProgress get() = DeliveryProgress.of(stops)

    fun stop(orderId: String): DeliveryStop? = stops.firstOrNull { it.orderId == orderId }
}

data class DriverProfile(val uid: String, val displayName: String)

/** Avance de la ruta: entregadas, fallidas y pendientes. */
data class DeliveryProgress(val delivered: Int, val failed: Int, val total: Int) {
    val closed: Int get() = delivered + failed
    val pending: Int get() = total - closed

    /** Fracción atendida entre 0 y 1; una ruta sin paradas vale 0. */
    val fraction: Float get() = if (total == 0) 0f else closed.toFloat() / total

    val percent: Int get() = (fraction * 100).toInt()

    companion object {
        fun of(stops: List<DeliveryStop>) = DeliveryProgress(
            delivered = stops.count { it.status == OrderStatus.DELIVERED },
            failed = stops.count { it.status == OrderStatus.FAILED },
            total = stops.size,
        )
    }
}
