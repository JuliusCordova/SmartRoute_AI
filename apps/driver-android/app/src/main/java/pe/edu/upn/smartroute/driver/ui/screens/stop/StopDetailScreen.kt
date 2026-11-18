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
                        StopContent(s.data, stop)
                    }
                }
            }
        }
    }
}

@Composable
private fun StopContent(route: Route, stop: DeliveryStop) {
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
            // Acciones visibles pero deshabilitadas: el backend aún no expone las transiciones de estado.
            Button(onClick = {}, enabled = false, modifier = Modifier.fillMaxWidth()) {
                Text("Marcar como entregado")
            }
            Spacer(Modifier.height(8.dp))
            OutlinedButton(onClick = {}, enabled = false, modifier = Modifier.fillMaxWidth()) {
                Text("No se pudo entregar")
            }
            Spacer(Modifier.height(6.dp))
            Text(
                "Las acciones de entrega se activarán cuando el servidor publique las transiciones de estado.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
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
