package pe.edu.upn.smartroute.driver.di

import android.content.Context
import com.google.firebase.FirebaseApp
import pe.edu.upn.smartroute.driver.BuildConfig
import pe.edu.upn.smartroute.driver.data.auth.FirebaseAuthRepository
import pe.edu.upn.smartroute.driver.data.mock.MockAuthRepository
import pe.edu.upn.smartroute.driver.data.mock.MockRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.ApiRouteRepository
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository
import pe.edu.upn.smartroute.driver.ui.auth.CredentialManagerSource

/** Configuración pública (no secreta). Las claves de mapas y del backend nunca van en la app. */
object AppConfig {
    const val GATEWAY_BASE_URL = "https://us014-gateway-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app"

    /** Pon true para forzar el modo demostración aunque Firebase esté configurado. */
    const val FORCE_DEMO = false

    /** Sólo las builds debug pueden probar mutaciones; en release siempre quedan bloqueadas. */
    const val ENABLE_DELIVERY_MUTATIONS = true

    // Armado independiente para pruebas manuales; desactivado en el repositorio.
    // Un build RELEASE jamás habilita mutaciones QA.
    const val ENABLE_QA_WRITE_TEST = true
    private const val QA_UID = "zMuwbYHLfST2QNdNkfosoCbUZ003"
    private const val QA_ROUTE_ID = "21e3de4b-4002-5870-bc4e-8eafb2826219"

    fun canMutateQaRoute(uid: String?, routeId: String): Boolean =
        pe.edu.upn.smartroute.driver.BuildConfig.DEBUG &&
            ENABLE_DELIVERY_MUTATIONS && ENABLE_QA_WRITE_TEST &&
            !FORCE_DEMO &&
            uid == QA_UID && routeId == QA_ROUTE_ID
}

/**
 * Inyección manual. Usa el backend real solo si Firebase quedó configurado
 * (app/google-services.json presente). Si no, la app arranca en modo demostración.
 */
class AppContainer(context: Context) {

    val backendEnabled: Boolean =
        !AppConfig.FORCE_DEMO &&
            FirebaseApp.getApps(context).isNotEmpty() &&
            CredentialManagerSource.webClientId(context) != null

    val authRepository: AuthRepository =
        if (backendEnabled) FirebaseAuthRepository() else MockAuthRepository()

    val routeRepository: RouteRepository =
        if (backendEnabled) ApiRouteRepository(AppConfig.GATEWAY_BASE_URL, authRepository) else MockRouteRepository()
}
