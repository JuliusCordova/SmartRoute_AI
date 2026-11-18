package pe.edu.upn.smartroute.driver.ui.screens.dashboard

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ExitToApp
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
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
import pe.edu.upn.smartroute.driver.domain.model.Route
import pe.edu.upn.smartroute.driver.domain.model.RouteStatus
import pe.edu.upn.smartroute.driver.ui.UiState
import pe.edu.upn.smartroute.driver.ui.components.DemoDataBanner
import pe.edu.upn.smartroute.driver.ui.components.LoadingView
import pe.edu.upn.smartroute.driver.ui.components.MessageView
import pe.edu.upn.smartroute.driver.ui.components.ProgressSummary
import pe.edu.upn.smartroute.driver.ui.components.displayRouteId
import pe.edu.upn.smartroute.driver.ui.components.label

fun RouteStatus.label(): String = when (this) {
    RouteStatus.DRAFT -> "Borrador"
    RouteStatus.PLANNED -> "Planificada"
    RouteStatus.ACTIVE -> "En curso"
    RouteStatus.COMPLETED -> "Completada"
    RouteStatus.CANCELLED -> "Cancelada"
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DashboardScreen(
    driverName: String,
    viewModel: DashboardViewModel,
    onOpenRoute: (String) -> Unit,
    onSignOut: () -> Unit,
) {
    val state by viewModel.state.collectAsStateWithLifecycle()
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Mis rutas") },
                actions = {
                    IconButton(onClick = viewModel::load) {
                        Icon(Icons.Filled.Refresh, contentDescription = "Actualizar rutas")
                    }
                    IconButton(onClick = onSignOut) {
                        Icon(Icons.AutoMirrored.Filled.ExitToApp, contentDescription = "Cerrar sesión")
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
            Text(
                "Hola, $driverName",
                style = MaterialTheme.typography.titleLarge,
                modifier = Modifier.padding(start = 16.dp, top = 16.dp, end = 16.dp),
            )
            when (val s = state) {
                UiState.Loading -> LoadingView()
                is UiState.Error -> MessageView(s.message, "Reintentar", viewModel::load)
                is UiState.NotFound -> MessageView(s.message)
                is UiState.Success ->
                    if (s.data.isEmpty()) {
                        MessageView("No tienes rutas asignadas por ahora.")
                    } else {
                        LazyColumn(
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(12.dp),
                        ) {
                            items(s.data, key = { it.id }) { route ->
                                RouteCard(route = route, onClick = { onOpenRoute(route.id) })
                            }
                        }
                    }
            }
        }
    }
}

@Composable
fun RouteCard(route: Route, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .testTag("route-card-${route.id}"),
    ) {
        Column(Modifier.padding(16.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("Ruta " + displayRouteId(route.id), style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Text(route.status.label(), style = MaterialTheme.typography.labelLarge)
            }
            Text("Sale de: ${route.depot.name}", style = MaterialTheme.typography.bodyMedium)
            Text(
                "${route.stops.size} paradas · ${route.metrics.distanceKm} km · ${route.metrics.durationMinutes} min " +
                    "(${route.metrics.dataOrigin.label().lowercase()})",
                style = MaterialTheme.typography.bodySmall,
            )
            Spacer(Modifier.height(12.dp))
            ProgressSummary(route.progress)
        }
    }
}
