package pe.edu.upn.smartroute.driver.domain.model

/** Errores de carga de ruta, independientes del transporte. La UI los traduce a mensajes. */
sealed class RouteError(message: String) : Exception(message) {
    /** 401: token ausente, vencido o inválido. */
    class Unauthorized : RouteError("Sesión no válida")

    /** 403: la cuenta no existe en users/{uid}, está inactiva o no tiene rol DRIVER. */
    class Forbidden : RouteError("Cuenta no habilitada como repartidor")

    /** 409: la reserva o la ruta asignada están inconsistentes en el servidor. */
    class Conflict : RouteError("Ruta asignada no disponible")

    /** 5xx: gateway, API o Firestore no disponibles. */
    class Unavailable(val code: Int) : RouteError("Servicio no disponible ($code)")

    /** Sin conexión o tiempo de espera agotado. */
    class Network : RouteError("Sin conexión")

    /** La respuesta no cumple el contrato DriverRoute. */
    class InvalidResponse(detail: String) : RouteError("Respuesta inválida: $detail")
}
