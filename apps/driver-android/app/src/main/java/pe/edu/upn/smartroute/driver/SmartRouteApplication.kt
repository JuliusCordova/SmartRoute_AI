package pe.edu.upn.smartroute.driver

import android.app.Application
import pe.edu.upn.smartroute.driver.di.AppContainer

class SmartRouteApplication : Application() {
    lateinit var container: AppContainer
        private set

    override fun onCreate() {
        super.onCreate()
        container = AppContainer(this)
    }
}
