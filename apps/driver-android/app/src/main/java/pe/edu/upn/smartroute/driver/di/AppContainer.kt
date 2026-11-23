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
    // Debug connects to isolated QA Gateway; release retains original endpoint.
    val GATEWAY_BASE_URL: String =
        if (BuildConfig.DEBUG) "https://qa-90681ae---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app"
        else "https://us014-gateway-test---smartroute-gateway-staging-mkqutd4koq-uc.a.run.app"

    /** Pon true para forzar el modo demostración aunque Firebase esté configurado. */
    const val FORCE_DEMO = false

    /** Sólo las builds debug pueden probar mutaciones; en release siempre quedan bloqueadas. */
    const val ENABLE_DELIVERY_MUTATIONS = true

    // En DEBUG se restringe por el UID Firebase real; el backend mantiene propiedad de ruta.
    // RELEASE siempre deshabilita mutaciones QA.
    val ENABLE_QA_WRITE_TEST: Boolean = BuildConfig.DEBUG && BuildConfig.QA_WRITE_TEST_ENABLED
    private const val QA_UID = "zMuwbYHLfST2QNdNkfosoCbUZ003"

    /** QA-only, non-sensitive reason. Does not expose tokens or the user's UID. */
    fun qaWriteBlockReason(uid: String?, routeId: String): String? = when {
        !BuildConfig.DEBUG -> "La APK no es debug."
        !ENABLE_DELIVERY_MUTATIONS || !ENABLE_QA_WRITE_TEST ->
            "Esta compilación no está autorizada para operaciones QA."
        FORCE_DEMO -> "La aplicación está en modo demostración."
        uid == null -> "No hay una sesión Firebase activa en Android."
        uid != QA_UID -> "El UID de la sesión Android es diferente al conductor QA autorizado."
        else -> null
    }

    fun canMutateQaRoute(uid: String?, routeId: String): Boolean =
        pe.edu.upn.smartroute.driver.BuildConfig.DEBUG &&
            ENABLE_DELIVERY_MUTATIONS && ENABLE_QA_WRITE_TEST &&
            !FORCE_DEMO &&
            uid == QA_UID && routeId.isNotBlank()
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
