package pe.edu.upn.smartroute.driver.data.mock

import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import pe.edu.upn.smartroute.driver.domain.model.DriverProfile
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.GoogleCredentialSource

/** Sesión de demostración. No valida credenciales ni emite tokens. */
class MockAuthRepository : AuthRepository {
    private val driver = MutableStateFlow<DriverProfile?>(null)

    override val isDemo: Boolean = true

    override val currentDriver: StateFlow<DriverProfile?> = driver.asStateFlow()

    override suspend fun signIn(source: GoogleCredentialSource): Result<DriverProfile> {
        val profile = DriverProfile(uid = MockRouteRepository.DEMO_DRIVER_ID, displayName = "Repartidor demo")
        driver.value = profile
        return Result.success(profile)
    }

    override suspend fun signOut() {
        driver.value = null
    }

    override suspend fun idToken(forceRefresh: Boolean): String? = null
}
