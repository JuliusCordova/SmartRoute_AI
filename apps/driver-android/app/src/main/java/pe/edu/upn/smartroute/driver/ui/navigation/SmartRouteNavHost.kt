package pe.edu.upn.smartroute.driver.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.credentials.exceptions.GetCredentialCancellationException
import androidx.credentials.exceptions.NoCredentialException
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.lifecycle.viewmodel.initializer
import androidx.lifecycle.viewmodel.viewModelFactory
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import kotlinx.coroutines.launch
import pe.edu.upn.smartroute.driver.di.AppContainer
import pe.edu.upn.smartroute.driver.ui.auth.CredentialManagerSource
import pe.edu.upn.smartroute.driver.ui.screens.dashboard.DashboardScreen
import pe.edu.upn.smartroute.driver.ui.screens.dashboard.DashboardViewModel
import pe.edu.upn.smartroute.driver.ui.screens.route.RouteDetailScreen
import pe.edu.upn.smartroute.driver.ui.screens.route.RouteDetailViewModel
import pe.edu.upn.smartroute.driver.ui.screens.stop.StopDetailScreen
import pe.edu.upn.smartroute.driver.ui.screens.welcome.WelcomeScreen

object Destinations {
    const val WELCOME = "welcome"
    const val DASHBOARD = "dashboard"
    const val ROUTE = "route/{routeId}"
    const val STOP = "route/{routeId}/stop/{orderId}"

    fun route(routeId: String) = "route/$routeId"
    fun stop(routeId: String, orderId: String) = "route/$routeId/stop/$orderId"
}

private fun signInMessage(e: Throwable): String = when (e) {
    is GetCredentialCancellationException -> "Cancelaste el inicio de sesión."
    is NoCredentialException -> "No hay una cuenta de Google en este dispositivo. Agrégala en Ajustes."
    else -> "No se pudo iniciar sesión con Google. Inténtalo de nuevo."
}

@Composable
fun SmartRouteNavHost(container: AppContainer) {
    val nav = rememberNavController()
    val scope = rememberCoroutineScope()
    val context = LocalContext.current
    val driver by container.authRepository.currentDriver.collectAsStateWithLifecycle()
    var busy by remember { mutableStateOf(false) }
    var signInError by remember { mutableStateOf<String?>(null) }

    val signIn: () -> Unit = {
        busy = true
        signInError = null
        scope.launch {
            container.authRepository.signIn(CredentialManagerSource(context))
                .onSuccess {
                    nav.navigate(Destinations.DASHBOARD) {
                        popUpTo(Destinations.WELCOME) { inclusive = true }
                    }
                }
                .onFailure { signInError = signInMessage(it) }
            busy = false
        }
    }

    // Si Firebase conserva una sesión previa, se entra directo al panel.
    val start = remember { if (driver != null) Destinations.DASHBOARD else Destinations.WELCOME }

    NavHost(navController = nav, startDestination = start) {
        composable(Destinations.WELCOME) {
            WelcomeScreen(
                backendEnabled = container.backendEnabled,
                onSignIn = signIn,
                busy = busy,
                errorMessage = signInError,
            )
        }

        composable(Destinations.DASHBOARD) {
            val profile = driver
            if (profile == null) {
                // Sin sesión no se muestran rutas.
                WelcomeScreen(container.backendEnabled, signIn, busy, signInError)
            } else {
                val vm: DashboardViewModel = viewModel(
                    factory = viewModelFactory {
                        initializer { DashboardViewModel(profile.uid, container.routeRepository) }
                    }
                )
                DashboardScreen(
                    driverName = profile.displayName,
                    viewModel = vm,
                    onOpenRoute = { nav.navigate(Destinations.route(it)) },
                    onSignOut = {
                        scope.launch {
                            container.authRepository.signOut()
                            nav.navigate(Destinations.WELCOME) {
                                popUpTo(Destinations.DASHBOARD) { inclusive = true }
                            }
                        }
                    },
                )
            }
        }

        composable(
            Destinations.ROUTE,
            arguments = listOf(navArgument("routeId") { type = NavType.StringType }),
        ) { entry ->
            val routeId = entry.arguments?.getString("routeId").orEmpty()
            val vm: RouteDetailViewModel = viewModel(
                factory = viewModelFactory {
                    initializer { RouteDetailViewModel(routeId, container.routeRepository) }
                }
            )
            RouteDetailScreen(
                routeId = routeId,
                viewModel = vm,
                onBack = { nav.popBackStack() },
                onOpenStop = { orderId -> nav.navigate(Destinations.stop(routeId, orderId)) },
            )
        }

        composable(
            Destinations.STOP,
            arguments = listOf(
                navArgument("routeId") { type = NavType.StringType },
                navArgument("orderId") { type = NavType.StringType },
            ),
        ) { entry ->
            val routeId = entry.arguments?.getString("routeId").orEmpty()
            val orderId = entry.arguments?.getString("orderId").orEmpty()
            val vm: RouteDetailViewModel = viewModel(
                factory = viewModelFactory {
                    initializer { RouteDetailViewModel(routeId, container.routeRepository) }
                }
            )
            StopDetailScreen(orderId = orderId, viewModel = vm, onBack = { nav.popBackStack() })
        }
    }
}
