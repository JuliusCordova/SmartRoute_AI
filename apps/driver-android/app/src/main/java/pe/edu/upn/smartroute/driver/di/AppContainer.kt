package pe.edu.upn.smartroute.driver.di

import android.content.Context
import com.google.firebase.FirebaseApp
import pe.edu.upn.smartroute.driver.data.auth.FirebaseAuthRepository
import pe.edu.upn.smartroute.driver.data.mock.MockAuthRepository
import pe.edu.upn.smartroute.driver.data.mock.MockRouteRepository
import pe.edu.upn.smartroute.driver.data.remote.ApiRouteRepository
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.RouteRepository
import pe.edu.upn.smartroute.driver.ui.auth.CredentialManagerSource

/** Configuración pública (no secreta). Las claves de mapas y del backend nunca van en la app. */
object AppConfig {
    const val GATEWAY_BASE_URL = "https://smartroute-gateway-staging-913797829604.us-central1.run.app"

    /** Pon true para forzar el modo demostración aunque Firebase esté configurado. */
    const val FORCE_DEMO = false

    /** Fail-closed hasta validar los endpoints de US-013/014 en GCP. */
    const val ENABLE_DELIVERY_MUTATIONS = false
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
