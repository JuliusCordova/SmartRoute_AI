package pe.edu.upn.smartroute.driver

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import pe.edu.upn.smartroute.driver.ui.navigation.SmartRouteNavHost
import pe.edu.upn.smartroute.driver.ui.theme.SmartRouteTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val container = (application as SmartRouteApplication).container
        setContent {
            SmartRouteTheme {
                SmartRouteNavHost(container = container)
            }
        }
    }
}
