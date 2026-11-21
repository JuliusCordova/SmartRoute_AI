package pe.edu.upn.smartroute.driver.ui.screens.welcome

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.safeDrawingPadding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Place
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import pe.edu.upn.smartroute.driver.ui.theme.Amber
import pe.edu.upn.smartroute.driver.ui.theme.Ink

/**
 * Bienvenida y acceso. Con Firebase configurado, el ingreso es con Google (igual que el panel web)
 * y el backend verifica que la cuenta tenga rol DRIVER. Sin configuración, modo demostración.
 */
@Composable
fun WelcomeScreen(
    backendEnabled: Boolean,
    onSignIn: () -> Unit,
    busy: Boolean = false,
    errorMessage: String? = null,
) {
    Column(
        modifier = Modifier
            .fillMaxSize()
            .safeDrawingPadding()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            contentAlignment = Alignment.Center,
            modifier = Modifier
                .size(88.dp)
                .background(Amber, RoundedCornerShape(24.dp)),
        ) {
            Icon(Icons.Filled.Place, contentDescription = null, tint = Ink, modifier = Modifier.size(48.dp))
        }
        Spacer(Modifier.height(24.dp))
        Text("SmartRoute AI", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Text(
            "App del repartidor · última milla en Lima",
            style = MaterialTheme.typography.bodyMedium,
            textAlign = TextAlign.Center,
        )
        Spacer(Modifier.height(40.dp))
        Button(
            onClick = onSignIn,
            enabled = !busy,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp)
                .testTag("sign-in"),
        ) {
            if (busy) {
                CircularProgressIndicator(strokeWidth = 2.dp, modifier = Modifier.size(22.dp))
            } else {
                Text(if (backendEnabled) "Ingresar con Google" else "Ingresar en modo demostración")
            }
        }
        if (errorMessage != null) {
            Spacer(Modifier.height(12.dp))
            Text(
                errorMessage,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodyMedium,
                textAlign = TextAlign.Center,
                modifier = Modifier.testTag("sign-in-error"),
            )
        }
        Spacer(Modifier.height(12.dp))
        Text(
            if (backendEnabled) {
                "Usa la cuenta de Google que el operador registró como repartidor."
            } else {
                "Firebase no está configurado en esta compilación: la app muestra datos sintéticos."
            },
            style = MaterialTheme.typography.bodySmall,
            textAlign = TextAlign.Center,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
