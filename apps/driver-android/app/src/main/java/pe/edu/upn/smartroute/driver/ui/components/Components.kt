package pe.edu.upn.smartroute.driver.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Info
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import pe.edu.upn.smartroute.driver.domain.model.DataOrigin
import pe.edu.upn.smartroute.driver.domain.model.DeliveryProgress
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.ui.theme.Amber
import pe.edu.upn.smartroute.driver.ui.theme.Bad
import pe.edu.upn.smartroute.driver.ui.theme.Ink
import pe.edu.upn.smartroute.driver.ui.theme.Neutral
import pe.edu.upn.smartroute.driver.ui.theme.Ok
import pe.edu.upn.smartroute.driver.ui.theme.Risk

/** Los IDs de ruta del backend son UUID: se muestra un prefijo legible. */
fun displayRouteId(id: String): String = if (id.length > 16) id.take(8) + "…" else id

/** Texto y color de cada estado del pedido. El color nunca es la única señal: siempre va con texto. */
fun OrderStatus.label(): String = when (this) {
    OrderStatus.PENDING -> "Pendiente"
    OrderStatus.ASSIGNED -> "Por entregar"
    OrderStatus.IN_TRANSIT -> "En camino"
    OrderStatus.DELIVERED -> "Entregado"
    OrderStatus.FAILED -> "No entregado"
}

fun OrderStatus.color(): Color = when (this) {
    OrderStatus.PENDING, OrderStatus.ASSIGNED -> Neutral
    OrderStatus.IN_TRANSIT -> Risk
    OrderStatus.DELIVERED -> Ok
    OrderStatus.FAILED -> Bad
}

fun DataOrigin.label(): String = when (this) {
    DataOrigin.SYNTHETIC -> "Sintético"
    DataOrigin.ESTIMATED -> "Estimado"
    DataOrigin.OBSERVED -> "Observado"
}

@Composable
fun StatusChip(status: OrderStatus, modifier: Modifier = Modifier) {
    val c = status.color()
    Text(
        text = status.label(),
        color = c,
        style = MaterialTheme.typography.labelMedium,
        fontWeight = FontWeight.Bold,
        modifier = modifier
            .border(1.dp, c, RoundedCornerShape(50))
            .background(c.copy(alpha = 0.10f), RoundedCornerShape(50))
            .padding(horizontal = 10.dp, vertical = 4.dp),
    )
}

/** Aviso permanente de que los datos no vienen del backend (honestidad del dato, BR-12). */
@Composable
fun DemoDataBanner(modifier: Modifier = Modifier) {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        modifier = modifier
            .fillMaxWidth()
            .background(Amber.copy(alpha = 0.25f))
            .padding(horizontal = 16.dp, vertical = 8.dp)
            .testTag("demo-banner"),
    ) {
        Icon(Icons.Filled.Info, contentDescription = null, tint = Ink, modifier = Modifier.size(18.dp))
        Spacer(Modifier.size(8.dp))
        Text(
            "Datos de demostración (sintéticos). La app aún no está conectada al backend.",
            style = MaterialTheme.typography.bodySmall,
            color = Ink,
        )
    }
}

@Composable
fun ProgressSummary(progress: DeliveryProgress, modifier: Modifier = Modifier) {
    Column(modifier = modifier.fillMaxWidth()) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text("Progreso de entregas", style = MaterialTheme.typography.titleSmall)
            Text(
                "${progress.closed} de ${progress.total} · ${progress.percent} %",
                style = MaterialTheme.typography.titleSmall,
                fontWeight = FontWeight.Bold,
            )
        }
        Spacer(Modifier.height(6.dp))
        LinearProgressIndicator(
            progress = { progress.fraction },
            modifier = Modifier
                .fillMaxWidth()
                .height(8.dp)
                .semantics { contentDescription = "Progreso ${progress.percent} por ciento" },
        )
        Spacer(Modifier.height(4.dp))
        Text(
            "Entregadas ${progress.delivered} · No entregadas ${progress.failed} · Pendientes ${progress.pending}",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
fun SequenceBadge(number: String, modifier: Modifier = Modifier) {
    Box(
        contentAlignment = Alignment.Center,
        modifier = modifier
            .size(32.dp)
            .background(Amber, CircleShape),
    ) {
        Text(number, color = Ink, fontWeight = FontWeight.Bold)
    }
}

@Composable
fun LoadingView() {
    Box(Modifier.fillMaxSize(), contentAlignment = Alignment.Center) { CircularProgressIndicator() }
}

@Composable
fun MessageView(message: String, actionLabel: String? = null, onAction: () -> Unit = {}) {
    Column(
        Modifier
            .fillMaxSize()
            .padding(24.dp),
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(message, style = MaterialTheme.typography.bodyLarge)
        if (actionLabel != null) {
            Spacer(Modifier.height(16.dp))
            Button(onClick = onAction) { Text(actionLabel) }
        }
    }
}
