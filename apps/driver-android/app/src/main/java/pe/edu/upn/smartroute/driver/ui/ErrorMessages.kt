package pe.edu.upn.smartroute.driver.ui

import pe.edu.upn.smartroute.driver.domain.model.RouteError

/** Mensajes en lenguaje del repartidor, con la acción a seguir (Nielsen H9). */
fun Throwable.toUserMessage(): String = when (this) {
    is RouteError.Unauthorized -> "Tu sesión venció. Cierra sesión y vuelve a ingresar."
    is RouteError.Forbidden -> "Tu cuenta no está habilitada como repartidor. Pide al operador que la active."
    is RouteError.Conflict -> "Tu ruta asignada tiene un problema en el servidor. Avisa al operador."
    is RouteError.Unavailable -> "El servicio no está disponible en este momento. Inténtalo en unos minutos."
    is RouteError.Network -> "Sin conexión. Revisa tus datos móviles o el wifi e inténtalo de nuevo."
    is RouteError.InvalidResponse -> "Recibimos datos de ruta no válidos. Avisa al operador."
    else -> "No se pudo cargar la información. Inténtalo de nuevo."
}
