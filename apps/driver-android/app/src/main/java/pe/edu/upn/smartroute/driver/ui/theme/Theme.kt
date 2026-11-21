package pe.edu.upn.smartroute.driver.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Amber = Color(0xFFFFC000)
val Ink = Color(0xFF1A1A1A)
val Ok = Color(0xFF1E7B45)
val Risk = Color(0xFFB45F06)
val Bad = Color(0xFFB3261E)
val Neutral = Color(0xFF5A5852)

private val LightColors = lightColorScheme(
    primary = Ink,
    onPrimary = Color.White,
    secondary = Amber,
    onSecondary = Ink,
    tertiary = Ok,
    background = Color(0xFFF7F5EF),
    surface = Color.White,
    surfaceVariant = Color(0xFFF1EDE2),
)

private val DarkColors = darkColorScheme(
    primary = Amber,
    onPrimary = Ink,
    secondary = Amber,
    onSecondary = Ink,
    tertiary = Color(0xFF7BD49B),
)

/** Colores fijos de marca (sin color dinámico) para que el estado se lea igual en todos los equipos. */
@Composable
fun SmartRouteTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    MaterialTheme(colorScheme = if (darkTheme) DarkColors else LightColors, content = content)
}
