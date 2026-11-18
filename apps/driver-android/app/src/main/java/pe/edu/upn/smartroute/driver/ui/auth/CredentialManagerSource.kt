package pe.edu.upn.smartroute.driver.ui.auth

import android.content.Context
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import pe.edu.upn.smartroute.driver.domain.repository.GoogleCredentialSource

/**
 * Selector de cuenta de Google con Credential Manager. Necesita el contexto de una Activity.
 * El client ID web lo genera el plugin google-services a partir de google-services.json
 * (recurso default_web_client_id); no se escribe en el código.
 */
class CredentialManagerSource(private val activityContext: Context) : GoogleCredentialSource {

    override suspend fun googleIdToken(): String {
        val clientId = webClientId(activityContext)
            ?: error("Falta google-services.json: no se encontró default_web_client_id")
        val option = GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(false)
            .setServerClientId(clientId)
            .build()
        val request = GetCredentialRequest.Builder().addCredentialOption(option).build()
        val credential = CredentialManager.create(activityContext).getCredential(activityContext, request).credential
        if (credential is CustomCredential && credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL) {
            return GoogleIdTokenCredential.createFrom(credential.data).idToken
        }
        error("Tipo de credencial no soportado")
    }

    companion object {
        /** Lee el recurso generado sin depender de él en tiempo de compilación. */
        fun webClientId(context: Context): String? {
            val id = context.resources.getIdentifier("default_web_client_id", "string", context.packageName)
            return if (id == 0) null else context.getString(id)
        }
    }
}
