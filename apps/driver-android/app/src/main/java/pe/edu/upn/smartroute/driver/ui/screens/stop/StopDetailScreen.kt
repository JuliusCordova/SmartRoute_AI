package pe.edu.upn.smartroute.driver.ui.screens.stop

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.TextButton
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import android.content.Intent
import android.net.Uri
import pe.edu.upn.smartroute.driver.di.AppConfig
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import pe.edu.upn.smartroute.driver.domain.model.DeliveryStop
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.ui.UiState
import pe.edu.upn.smartroute.driver.ui.components.DemoDataBanner
import pe.edu.upn.smartroute.driver.ui.components.LoadingView
import pe.edu.upn.smartroute.driver.ui.components.MessageView
import pe.edu.upn.smartroute.driver.ui.components.RouteMap
import pe.edu.upn.smartroute.driver.ui.components.StatusChip
import pe.edu.upn.smartroute.driver.ui.screens.route.RouteDetailViewModel
import java.util.Locale

/** Detalle de un pedido. Las acciones de entrega se habilitarán cuando el backend publique las transiciones. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun StopDetailScreen(
    orderId: String,
    viewModel: RouteDetailViewModel,
    onBack: () -> Unit,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    val mutating by viewModel.mutating.collectAsStateWithLifecycle()
    val mutationError by viewModel.mutationError.collectAsStateWithLifecycle()
    var confirmDelivery by remember { mutableStateOf(false) }
    var confirmFailure by remember { mutableStateOf(false) }
    var failureReason by remember { mutableStateOf("") }
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Pedido $orderId") },
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
                    val stop = s.data.stop(orderId)
                    if (stop == null) {
                        MessageView("Este pedido no pertenece a la ruta.", "Volver", onBack)
                    } else {
                        StopContent(s.data, stop, viewModel.isDemoData, mutating, mutationError,
                            onDelivery = { confirmDelivery = true },
                            onFailure = { confirmFailure = true })
                    }
                }
            }
        }
    }
    if (confirmDelivery) {
        AlertDialog(
            onDismissRequest = { confirmDelivery = false },
            title = { Text("¿Confirmar entrega?") },
            text = { Text("Se registrará la entrega en GCP. Esta acción no se puede deshacer desde Android.") },
            confirmButton = {
                TextButton(onClick = {
                    confirmDelivery = false
                    viewModel.recordStop(orderId, delivered = true, reason = null)
                }) { Text("Confirmar entregado") }
            },
            dismissButton = { TextButton(onClick = { confirmDelivery = false }) { Text("Cancelar") } },
        )
    }
    if (confirmFailure) {
        AlertDialog(
            onDismissRequest = { confirmFailure = false },
            title = { Text("Registrar entrega fallida") },
            text = {
                OutlinedTextField(
                    value = failureReason,
                    onValueChange = { if (it.length <= 250) failureReason = it },
                    label = { Text("Motivo obligatorio") },
                    supportingText = { Text("Máximo 250 caracteres") },
                    minLines = 2,
                    modifier = Modifier.fillMaxWidth(),
                )
            },
            confirmButton = {
                TextButton(
                    enabled = failureReason.isNotBlank(),
                    onClick = {
                        confirmFailure = false
                        viewModel.recordStop(orderId, delivered = false, reason = failureReason.trim())
                    },
                ) { Text("Confirmar fallo") }
            },
            dismissButton = { TextButton(onClick = { confirmFailure = false }) { Text("Cancelar") } },
        )
    }
}

@Composable
private fun StopContent(
    route: Route, stop: DeliveryStop, isDemoData: Boolean, mutating: Boolean, mutationError: String?,
    onDelivery: () -> Unit, onFailure: () -> Unit,
) {
    Column(
        Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState()),
    ) {
        RouteMap(
            route = route,
            highlightOrderId = stop.orderId,
            modifier = Modifier
                .fillMaxWidth()
                .height(220.dp),
        )
        Column(Modifier.padding(16.dp)) {
            Row {
                Text(
                    "Parada ${stop.sequence} de ${route.stops.size}",
                    style = MaterialTheme.typography.labelLarge,
                    modifier = Modifier.weight(1f),
                )
                StatusChip(stop.status, Modifier.testTag("stop-status"))
            }
            Spacer(Modifier.height(8.dp))
            Text(stop.address, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
            stop.district?.let { Text(it, style = MaterialTheme.typography.bodyLarge) }
            Spacer(Modifier.height(12.dp))
            stop.timeWindow?.let { Field("Ventana de entrega", it) }
            Field("Pedido", stop.orderId)
            Field("Coordenadas", String.format(Locale.US, "%.5f, %.5f", stop.location.latitude, stop.location.longitude))
            stop.notes?.let { Field("Indicaciones", it) }
            Spacer(Modifier.height(20.dp))
            val context = LocalContext.current
            OutlinedButton(
                onClick = {
                    val point = "${stop.location.latitude},${stop.location.longitude}"
                    val uri = Uri.parse("https://www.google.com/maps/dir/?api=1&destination=" + Uri.encode(point))
                    context.startActivity(Intent(Intent.ACTION_VIEW, uri))
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("Navegar a esta parada") }
            Spacer(Modifier.height(12.dp))
            val enabled = !mutating && AppConfig.ENABLE_DELIVERY_MUTATIONS &&
                route.status == RouteStatus.ACTIVE && !stop.status.isClosed && route.version != null
            Button(onClick = onDelivery, enabled = enabled, modifier = Modifier.fillMaxWidth()) {
                Text(if (mutating) "Registrando..." else "Marcar como entregado")
            }
            Spacer(Modifier.height(8.dp))
            OutlinedButton(onClick = onFailure, enabled = enabled, modifier = Modifier.fillMaxWidth()) {
                Text("No se pudo entregar")
            }
            Spacer(Modifier.height(6.dp))
            if (mutationError != null) {
                Text(mutationError, color = MaterialTheme.colorScheme.error)
            }
            if (!AppConfig.ENABLE_DELIVERY_MUTATIONS) {
                Text("Entregas bloqueadas hasta validar y activar los endpoints US-013/014 en GCP.",
                    style = MaterialTheme.typography.bodySmall)
            } else if (route.status != RouteStatus.ACTIVE) {
                Text("Inicia el recorrido para registrar entregas.", style = MaterialTheme.typography.bodySmall)
            } else if (stop.status.isClosed) {
                Text("Esta parada ya tiene resultado registrado.", style = MaterialTheme.typography.bodySmall)
            }
        }
    }
}

@Composable
private fun Field(label: String, value: String) {
    Column(Modifier.padding(vertical = 4.dp)) {
        Text(label, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyLarge)
    }
}
