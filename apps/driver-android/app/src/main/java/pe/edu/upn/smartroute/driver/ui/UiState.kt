package pe.edu.upn.smartroute.driver.ui

/** Estado genérico de una pantalla que carga datos. */
sealed interface UiState<out T> {
    data object Loading : UiState<Nothing>
    data class Success<T>(val data: T) : UiState<T>
    data class NotFound(val message: String) : UiState<Nothing>
    data class Error(val message: String) : UiState<Nothing>
}
