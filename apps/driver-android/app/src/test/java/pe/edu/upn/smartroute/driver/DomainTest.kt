package pe.edu.upn.smartroute.driver

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertThrows
import org.junit.Assert.assertTrue
import org.junit.Test
import pe.edu.upn.smartroute.driver.domain.model.DeliveryProgress
import pe.edu.upn.smartroute.driver.domain.model.DeliveryStop
import pe.edu.upn.smartroute.driver.domain.model.GeoPoint
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus

class DomainTest {

    private fun stop(seq: Int, status: OrderStatus) =
        DeliveryStop("P$seq", seq, "Dirección $seq", "Lima", GeoPoint(-12.05, -77.04), status, "09:00–12:00")

    @Test
    fun progress_counts_delivered_and_failed_as_closed() {
        val p = DeliveryProgress.of(
            listOf(
                stop(1, OrderStatus.DELIVERED),
                stop(2, OrderStatus.FAILED),
                stop(3, OrderStatus.IN_TRANSIT),
                stop(4, OrderStatus.ASSIGNED),
            )
        )
        assertEquals(1, p.delivered)
        assertEquals(1, p.failed)
        assertEquals(2, p.closed)
        assertEquals(2, p.pending)
        assertEquals(0.5f, p.fraction, 0.0001f)
        assertEquals(50, p.percent)
    }

    @Test
    fun progress_of_empty_route_is_zero_not_nan() {
        val p = DeliveryProgress.of(emptyList())
        assertEquals(0f, p.fraction, 0f)
        assertEquals(0, p.percent)
    }

    @Test
    fun only_delivered_and_failed_are_closed_states() {
        assertTrue(OrderStatus.DELIVERED.isClosed)
        assertTrue(OrderStatus.FAILED.isClosed)
        assertFalse(OrderStatus.PENDING.isClosed)
        assertFalse(OrderStatus.ASSIGNED.isClosed)
        assertFalse(OrderStatus.IN_TRANSIT.isClosed)
    }

    @Test
    fun geopoint_rejects_out_of_range_coordinates() {
        assertThrows(IllegalArgumentException::class.java) { GeoPoint(-95.0, -77.0) }
        assertThrows(IllegalArgumentException::class.java) { GeoPoint(-12.0, 190.0) }
    }

    @Test
    fun stop_sequence_starts_at_one() {
        assertThrows(IllegalArgumentException::class.java) { stop(0, OrderStatus.ASSIGNED) }
    }
}
