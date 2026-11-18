package pe.edu.upn.smartroute.driver.data.auth

import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseUser
import com.google.firebase.auth.GoogleAuthProvider
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.tasks.await
import pe.edu.upn.smartroute.driver.domain.model.DriverProfile
import pe.edu.upn.smartroute.driver.domain.repository.AuthRepository
import pe.edu.upn.smartroute.driver.domain.repository.GoogleCredentialSource

/**
 * Firebase Authentication con Google Sign-In, el mismo proveedor que el panel web.
 * El rol DRIVER NO se decide aquí: lo verifica el backend en users/{uid}.
 * El SDK de Firebase guarda la sesión; la app no persiste tokens por su cuenta.
 */
class FirebaseAuthRepository(
    private val firebaseAuth: FirebaseAuth = FirebaseAuth.getInstance(),
) : AuthRepository {

    override val isDemo: Boolean = false

    private val driver = MutableStateFlow(firebaseAuth.currentUser?.toProfile())
    override val currentDriver: StateFlow<DriverProfile?> = driver.asStateFlow()

    override suspend fun signIn(source: GoogleCredentialSource): Result<DriverProfile> = runCatching {
        val googleIdToken = source.googleIdToken()
        val credential = GoogleAuthProvider.getCredential(googleIdToken, null)
        val user = firebaseAuth.signInWithCredential(credential).await().user
            ?: error("Firebase no devolvió usuario")
        user.toProfile().also { driver.value = it }
    }

    override suspend fun signOut() {
        firebaseAuth.signOut()
        driver.value = null
    }

    override suspend fun idToken(forceRefresh: Boolean): String? =
        firebaseAuth.currentUser?.getIdToken(forceRefresh)?.await()?.token

    private fun FirebaseUser.toProfile() = DriverProfile(
        uid = uid,
        displayName = displayName?.takeIf { it.isNotBlank() } ?: "Repartidor",
    )
}
