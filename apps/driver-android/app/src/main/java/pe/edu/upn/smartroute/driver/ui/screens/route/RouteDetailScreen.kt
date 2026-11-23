package pe.edu.upn.smartroute.driver.ui.screens.route

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.TextButton
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pe.edu.upn.smartroute.driver.domain.model.DeliveryStop
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import pe.edu.upn.smartroute.driver.ui.UiState
import pe.edu.upn.smartroute.driver.ui.components.DemoDataBanner
import pe.edu.upn.smartroute.driver.ui.components.LoadingView
import pe.edu.upn.smartroute.driver.ui.components.MessageView
import pe.edu.upn.smartroute.driver.ui.components.ProgressSummary
import pe.edu.upn.smartroute.driver.ui.components.RouteMap
import pe.edu.upn.smartroute.driver.ui.components.SequenceBadge
import pe.edu.upn.smartroute.driver.ui.components.StatusChip
import pe.edu.upn.smartroute.driver.ui.components.displayRouteId
import pe.edu.upn.smartroute.driver.ui.components.label
import java.util.Locale
import android.Manifest
import androidx.activity.compose.rememberLauncherForActivityResult
import com.google.firebase.auth.FirebaseAuth
import pe.edu.upn.smartroute.driver.di.AppConfig
import pe.edu.upn.smartroute.driver.di.AppConfig
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.platform.LocalContext
import kotlinx.coroutines.delay
import java.time.Instant
import androidx.compose.material3.OutlinedButton
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RouteDetailScreen(
    routeId: String,
    viewModel: RouteDetailViewModel,
    onBack: () -> Unit,
    onOpenStop: (String) -> Unit,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val starting by viewModel.starting.collectAsStateWithLifecycle()
    val startError by viewModel.startError.collectAsStateWithLifecycle()
    val mutating by viewModel.mutating.collectAsStateWithLifecycle()
    val mutationError by viewModel.mutationError.collectAsStateWithLifecycle()
    val gpsError by viewModel.gpsError.collectAsStateWithLifecycle()
    val gpsLastSent by viewModel.gpsLastSent.collectAsStateWithLifecycle()
    val context = LocalContext.current
    var consentGps by remember(routeId) { mutableStateOf(false) }
    var gpsMessage by remember(routeId) { mutableStateOf<String?>(null) }
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        consentGps = permissions.values.any { it }
        gpsMessage = if (consentGps) "GPS autorizado para esta ruta." else "GPS denegado; no se transmitirá ubicación."
    }
    val activeRoute = (state as? UiState.Success)?.data
    val gpsActive = activeRoute?.status == RouteStatus.ACTIVE && viewModel.canMutateRoute(routeId)
    // Foreground-only: leaving the route screen or completing cancels this coroutine.
    LaunchedEffect(gpsActive, consentGps, routeId) {
        while (gpsActive && consentGps) {
            val fix = RouteGps.freshFix(context)
            if (fix == null) {
                gpsMessage = "No hay posición GPS reciente; verifica permisos y ubicación."
            } else {
                viewModel.sendGps(fix.latitude, fix.longitude, fix.accuracy,
                    Instant.ofEpochMilli(fix.time).toString())
                gpsMessage = "GPS capturado; precisión: " + fix.accuracy.toInt() + " m."
            }
            delay(30_000L)
        }
    }
    var confirmStart by remember { mutableStateOf(false) }
    var confirmComplete by remember { mutableStateOf(false) }
    // Al regresar desde una parada, consultar el estado definitivo del servidor.
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { viewModel.load() }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ruta " + displayRouteId(routeId)) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = "Volver")
                    }
                },
            )
        },
    ) { padding ->
        Column(
            Modifier
                .fillMaxSize()
                .padding(padding),
        ) {
            if (viewModel.isDemoData) DemoDataBanner()
            when (val s = state) {
                UiState.Loading -> LoadingView()
                is UiState.Error -> MessageView(s.message, "Reintentar", viewModel::load)
                is UiState.NotFound -> MessageView(s.message, "Volver", onBack)
                is UiState.Success -> {
                    // Mostrar el estado de preparación, sin relajar ni una validación de escritura.
                    // El botón permanece protegido también en RouteDetailViewModel y ApiRouteRepository.
                    if (s.data.status == RouteStatus.PLANNED) {
                        val writeAllowed = viewModel.canMutateRoute(s.data.id)
                        val reason = when {
                            viewModel.isDemoData ->
                                "Modo demostración: no se pueden iniciar rutas reales."
                            !writeAllowed ->
                                AppConfig.qaWriteBlockReason(
                                    FirebaseAuth.getInstance().currentUser?.uid, s.data.id
                                ) ?: "La sesión Android no coincide con la autorización del repositorio."
                            s.data.version == null ->
                                "El Gateway no entregó la versión de la ruta; inicio bloqueado."
                            else -> null
                        }
                        if (reason == null) {
                            Button(
                                onClick = { confirmStart = true },
                                enabled = !starting,
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                            ) { Text(if (starting) "Iniciando recorrido..." else "Iniciar recorrido") }
                        } else {
                            Text(
                                "Inicio bloqueado: $reason",
                                modifier = Modifier.padding(horizontal = 16.dp, vertical = 8.dp),
                                color = MaterialTheme.colorScheme.error,
                            )
                        }
                    }
                    if (s.data.status == RouteStatus.ACTIVE && !viewModel.isDemoData && viewModel.canMutateRoute(s.data.id)) {
                        if (!consentGps) {
                            OutlinedButton(
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                                onClick = {
                                    if (RouteGps.permitted(context)) {
                                        consentGps = true
                                        gpsMessage = "GPS consentido solo durante esta ruta activa."
                                    } else {
                                        permissionLauncher.launch(arrayOf(
                                            Manifest.permission.ACCESS_FINE_LOCATION,
                                            Manifest.permission.ACCESS_COARSE_LOCATION,
                                        ))
                                    }
                                }
                            ) { Text("Autorizar GPS durante ruta activa") }
                        } else {
                            OutlinedButton(
                                modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                                onClick = { consentGps = false; gpsMessage = "GPS detenido." }
                            ) { Text("Detener GPS") }
                        }
                        gpsMessage?.let { Text(it, modifier = Modifier.padding(horizontal = 16.dp)) }
                        gpsLastSent?.let { Text("Último envío: $it", modifier = Modifier.padding(horizontal = 16.dp)) }
                        gpsError?.let { Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(horizontal = 16.dp)) }
                    }
                    if (viewModel.canMutateRoute(s.data.id) &&
                        s.data.status == RouteStatus.ACTIVE &&
                        s.data.progress.pending == 0 && s.data.stops.isNotEmpty() &&
                        s.data.version != null) {
                        Button(
                            onClick = { confirmComplete = true }, enabled = !mutating,
                            modifier = Modifier.fillMaxWidth().padding(horizontal = 16.dp),
                        ) { Text(if (mutating) "Finalizando..." else "Finalizar recorrido") }
                    }
                    if (s.data.status == RouteStatus.COMPLETED) {
                        Text("Recorrido completado: ${s.data.progress.delivered} entregadas y ${s.data.progress.failed} fallidas.",
                            modifier = Modifier.padding(16.dp))
                    }
                    if (mutationError != null) {
                        Text(mutationError.orEmpty(), color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(horizontal = 16.dp))
                        OutlinedButton(onClick = viewModel::load, enabled = !mutating,
                            modifier = Modifier.padding(horizontal = 16.dp)) { Text("Actualizar estado") }
                    }
                    if (startError != null) {
                        Text(startError.orEmpty(), color = MaterialTheme.colorScheme.error,
                            modifier = Modifier.padding(horizontal = 16.dp))
                    }
                    RouteContent(s.data, onOpenStop)
                }
            }
        }
    }
    if (confirmComplete) {
        AlertDialog(
            onDismissRequest = { confirmComplete = false },
            title = { Text("¿Finalizar recorrido?") },
            text = { Text("Las entregas deben estar resueltas. GCP confirmará el cierre y liberará la reserva del conductor.") },
            confirmButton = {
                TextButton(onClick = {
                    confirmComplete = false
                    viewModel.completeRoute()
                }) { Text("Confirmar finalización") }
            },
            dismissButton = {
                TextButton(onClick = { confirmComplete = false }) { Text("Cancelar") }
            },
        )
    }
    if (confirmStart) {
        AlertDialog(
            onDismissRequest = { confirmStart = false },
            title = { Text("¿Iniciar este recorrido?") },
            text = { Text("La ruta pasará de PLANNED a ACTIVE y quedará registrada en GCP. Esta acción no confirma entregas.") },
            confirmButton = {
                TextButton(onClick = {
                    confirmStart = false
                    viewModel.startRoute()
                }) { Text("Confirmar inicio") }
            },
            dismissButton = {
                TextButton(onClick = { confirmStart = false }) { Text("Cancelar") }
            },
        )
    }
}

@Composable
private fun RouteContent(route: Route, onOpenStop: (String) -> Unit) {
    LazyColumn(Modifier.fillMaxSize()) {
        item {
            RouteMap(
                route = route,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(280.dp)
                    .testTag("route-map"),
            )
            Text(
                "La línea une las paradas en el orden de visita; no es el trazado por las calles.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp),
            )
            Column(Modifier.padding(16.dp)) {
                ProgressSummary(route.progress)
                Spacer(Modifier.height(12.dp))
                Text(
                    "${route.metrics.distanceKm} km · ${route.metrics.durationMinutes} min · dato ${route.metrics.dataOrigin.label().lowercase()}",
                    style = MaterialTheme.typography.bodyMedium,
                )
            }
            HorizontalDivider()
            DepotRow(route)
            HorizontalDivider()
        }
        items(route.orderedStops, key = { it.orderId }) { stop ->
            StopRow(stop, onClick = { onOpenStop(stop.orderId) })
            HorizontalDivider()
        }
    }
}

@Composable
private fun DepotRow(route: Route) {
    Row(
        Modifier
            .fillMaxWidth()
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        SequenceBadge("D")
        Spacer(Modifier.width(12.dp))
        Column {
            Text("Salida: ${route.depot.name}", style = MaterialTheme.typography.titleSmall)
            Text(
                route.depot.address ?: String.format(
                    Locale.US, "%.5f, %.5f", route.depot.location.latitude, route.depot.location.longitude,
                ),
                style = MaterialTheme.typography.bodySmall,
            )
        }
    }
}

@Composable
private fun StopRow(stop: DeliveryStop, onClick: () -> Unit) {
    Row(
        Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(16.dp)
            .testTag("stop-row-${stop.orderId}"),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        SequenceBadge("${stop.sequence}")
        Spacer(Modifier.width(12.dp))
        Column(Modifier.weight(1f)) {
            Text(stop.address, style = MaterialTheme.typography.titleSmall, fontWeight = FontWeight.SemiBold)
            val details = listOfNotNull(stop.district, stop.timeWindow?.let { "ventana $it" })
            if (details.isNotEmpty()) {
                Text(details.joinToString(" · "), style = MaterialTheme.typography.bodySmall)
            }
            Text("Pedido ${stop.orderId}", style = MaterialTheme.typography.bodySmall)
        }
        Spacer(Modifier.width(8.dp))
        StatusChip(stop.status)
    }
}
