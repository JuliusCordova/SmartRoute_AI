package pe.edu.upn.smartroute.driver

import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onNodeWithTag
import androidx.compose.ui.test.onNodeWithText
import androidx.compose.ui.test.performClick
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Assert.assertTrue
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import pe.edu.upn.smartroute.driver.data.mock.MockRouteRepository
import pe.edu.upn.smartroute.driver.domain.model.OrderStatus
import pe.edu.upn.smartroute.driver.ui.components.DemoDataBanner
import pe.edu.upn.smartroute.driver.ui.components.StatusChip
import pe.edu.upn.smartroute.driver.ui.screens.dashboard.RouteCard
import pe.edu.upn.smartroute.driver.ui.screens.welcome.WelcomeScreen
import pe.edu.upn.smartroute.driver.ui.theme.SmartRouteTheme

/** Pruebas de UI con Compose. Requieren un emulador o un dispositivo. */
@RunWith(AndroidJUnit4::class)
class ScreensTest {

    @get:Rule
    val compose = createComposeRule()

    @Test
    fun welcome_button_triggers_demo_sign_in() {
        var clicked = false
        compose.setContent { SmartRouteTheme { WelcomeScreen(backendEnabled = false, onSignIn = { clicked = true }) } }
        compose.onNodeWithText("SmartRoute AI").assertExists()
        compose.onNodeWithText("Ingresar en modo demostración").assertExists()
        compose.onNodeWithTag("sign-in").performClick()
        assertTrue(clicked)
    }

    @Test
    fun welcome_shows_google_sign_in_and_error_when_backend_enabled() {
        compose.setContent {
            SmartRouteTheme {
                WelcomeScreen(backendEnabled = true, onSignIn = {}, errorMessage = "Cancelaste el inicio de sesión.")
            }
        }
        compose.onNodeWithText("Ingresar con Google").assertExists()
        compose.onNodeWithTag("sign-in-error").assertExists()
    }

    @Test
    fun demo_banner_states_data_is_synthetic() {
        compose.setContent { SmartRouteTheme { DemoDataBanner() } }
        compose.onNodeWithText("sintéticos", substring = true).assertExists()
    }

    @Test
    fun route_card_shows_progress_and_opens_route() {
        var opened = false
        compose.setContent {
            SmartRouteTheme { RouteCard(route = MockRouteRepository.demoRoute, onClick = { opened = true }) }
        }
        compose.onNodeWithText("2 de 5 · 40 %").assertExists()
        compose.onNodeWithTag("route-card-${MockRouteRepository.DEMO_ROUTE_ID}").performClick()
        assertTrue(opened)
    }

    @Test
    fun status_chip_uses_text_not_only_color() {
        compose.setContent { SmartRouteTheme { StatusChip(OrderStatus.FAILED) } }
        compose.onNodeWithText("No entregado").assertExists()
    }
}
