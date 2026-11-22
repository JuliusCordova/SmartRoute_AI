package pe.edu.upn.smartroute.driver.ui.screens.route

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.location.Location
import android.location.LocationListener
import android.location.LocationManager
import androidx.core.content.ContextCompat
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withTimeoutOrNull
import kotlin.coroutines.resume

/**
 * US-V1-008 foreground-only, one-shot GPS. No background service, no cached location,
 * no tracking after the screen leaves ACTIVE. Client never guesses coordinates.
 */
object RouteGps {
    fun permitted(context: Context): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_FINE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED ||
        ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_COARSE_LOCATION) ==
            PackageManager.PERMISSION_GRANTED

    @Suppress("DEPRECATION")
    suspend fun freshFix(context: Context): Location? {
        if (!permitted(context)) return null
        val manager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
        val provider = when {
            manager.isProviderEnabled(LocationManager.GPS_PROVIDER) -> LocationManager.GPS_PROVIDER
            manager.isProviderEnabled(LocationManager.NETWORK_PROVIDER) -> LocationManager.NETWORK_PROVIDER
            else -> return null
        }
        return withTimeoutOrNull(12_000L) {
            suspendCancellableCoroutine<Location?> { continuation ->
                val listener = object : LocationListener {
                    override fun onLocationChanged(location: Location) {
                        manager.removeUpdates(this)
                        if (continuation.isActive) continuation.resume(location)
                    }
                    override fun onProviderDisabled(provider: String) {
                        manager.removeUpdates(this)
                        if (continuation.isActive) continuation.resume(null)
                    }
                }
                try {
                    manager.requestSingleUpdate(provider, listener, null)
                    continuation.invokeOnCancellation { manager.removeUpdates(listener) }
                } catch (_: SecurityException) {
                    manager.removeUpdates(listener)
                    if (continuation.isActive) continuation.resume(null)
                } catch (_: IllegalArgumentException) {
                    manager.removeUpdates(listener)
                    if (continuation.isActive) continuation.resume(null)
                }
            }
        }?.takeIf {
            val ageMillis = System.currentTimeMillis() - it.time
            ageMillis in 0..60_000 && it.hasAccuracy() && it.accuracy in 0f..500f
        }
    }
}
