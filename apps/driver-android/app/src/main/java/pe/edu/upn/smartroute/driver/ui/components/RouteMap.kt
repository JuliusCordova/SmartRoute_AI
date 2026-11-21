package pe.edu.upn.smartroute.driver.ui.components

import android.content.Context
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.BoundingBox
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker
import org.osmdroid.views.overlay.Polyline
import pe.edu.upn.smartroute.driver.domain.model.GeoPoint
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.ui.theme.Ink
import org.osmdroid.util.GeoPoint as OsmPoint

/**
 * Mapa OpenStreetMap con el depósito (D), las paradas numeradas y una línea recta que une
 * el orden de visita. La línea NO es el trazado vial: solo muestra la secuencia.
 * Las teselas exigen atribución visible (licencia ODbL).
 */
@Composable
fun RouteMap(
    route: Route,
    modifier: Modifier = Modifier,
    highlightOrderId: String? = null,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val mapView = remember { createMapView(context) }

    DisposableEffect(lifecycleOwner) {
        val observer = LifecycleEventObserver { _, event ->
            when (event) {
                Lifecycle.Event.ON_RESUME -> mapView.onResume()
                Lifecycle.Event.ON_PAUSE -> mapView.onPause()
                else -> Unit
            }
        }
        lifecycleOwner.lifecycle.addObserver(observer)
        onDispose {
            lifecycleOwner.lifecycle.removeObserver(observer)
            mapView.onDetach()
        }
    }

    Box(modifier) {
        AndroidView(
            factory = { mapView },
            update = { view -> renderRoute(view, route, highlightOrderId) },
        )
        Text(
            "© OpenStreetMap contributors",
            style = MaterialTheme.typography.labelSmall,
            color = Ink,
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .background(Color.White.copy(alpha = 0.8f))
                .padding(horizontal = 6.dp, vertical = 2.dp),
        )
    }
}

private fun createMapView(context: Context): MapView {
    val config = Configuration.getInstance()
    config.load(context, context.getSharedPreferences("osmdroid", Context.MODE_PRIVATE))
    // La política de teselas de OSM exige identificar la aplicación.
    config.userAgentValue = context.packageName
    return MapView(context).apply {
        setTileSource(TileSourceFactory.MAPNIK)
        setMultiTouchControls(true)
        minZoomLevel = 10.0
        maxZoomLevel = 19.0
    }
}

private fun GeoPoint.toOsm() = OsmPoint(latitude, longitude)

private fun renderRoute(map: MapView, route: Route, highlightOrderId: String?) {
    map.overlays.clear()

    val path = listOf(route.depot.location.toOsm()) + route.orderedStops.map { it.location.toOsm() }
    map.overlays.add(
        Polyline(map).apply {
            setPoints(path)
            outlinePaint.color = Ink.copy(alpha = 0.55f).toArgb()
            outlinePaint.strokeWidth = 6f
        }
    )

    map.overlays.add(
        Marker(map).apply {
            position = route.depot.location.toOsm()
            title = "Depósito: ${route.depot.name}"
            setTextIcon("D")
            setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
        }
    )
    route.orderedStops.forEach { stop ->
        map.overlays.add(
            Marker(map).apply {
                position = stop.location.toOsm()
                title = "${stop.sequence}. ${stop.address}"
                snippet = stop.status.label()
                setTextIcon(if (stop.orderId == highlightOrderId) "▶${stop.sequence}" else "${stop.sequence}")
                setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
            }
        )
    }

    val box = BoundingBox.fromGeoPointsSafe(path)
    map.post {
        if (highlightOrderId != null) {
            route.stop(highlightOrderId)?.let {
                map.controller.setZoom(16.0)
                map.controller.setCenter(it.location.toOsm())
            }
        } else {
            map.zoomToBoundingBox(box.increaseByScale(1.3f), false)
        }
    }
    map.invalidate()
}
