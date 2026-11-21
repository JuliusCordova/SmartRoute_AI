package pe.edu.upn.smartroute.driver.data.remote

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.IOException
import java.net.HttpURLConnection
import java.net.URL

data class HttpResponse(val code: Int, val body: String)

/** Transporte HTTP mínimo; se reemplaza por uno falso en las pruebas. */
fun interface HttpTransport {
    /** Lanza IOException si no hay red o se agota el tiempo. */
    suspend fun get(url: String, headers: Map<String, String>): HttpResponse
    suspend fun post(url: String, headers: Map<String, String>, body: String): HttpResponse {
        throw UnsupportedOperationException("POST no configurado")
    }
}

/** Implementación con HttpURLConnection: sin dependencias extra, solo HTTPS y sin redirecciones. */
class UrlConnectionTransport(
    private val connectTimeoutMs: Int = 10_000,
    private val readTimeoutMs: Int = 15_000,
) : HttpTransport {

    override suspend fun get(url: String, headers: Map<String, String>): HttpResponse =
        request("GET", url, headers, null)

    override suspend fun post(url: String, headers: Map<String, String>, body: String): HttpResponse =
        request("POST", url, headers, body)

    private suspend fun request(method: String, url: String, headers: Map<String, String>, payload: String?): HttpResponse =
        withContext(Dispatchers.IO) {
            require(url.startsWith("https://")) { "Solo se permite HTTPS" }
            val conn = URL(url).openConnection() as HttpURLConnection
            try {
                conn.requestMethod = method
                if (payload != null) {
                    conn.doOutput = true
                    conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
                }
                conn.instanceFollowRedirects = false
                conn.connectTimeout = connectTimeoutMs
                conn.readTimeout = readTimeoutMs
                conn.useCaches = false
                headers.forEach { (k, v) -> conn.setRequestProperty(k, v) }
                if (payload != null) {
                    val bytes = payload.toByteArray(Charsets.UTF_8)
                    require(bytes.size <= 4096) { "Petición demasiado grande" }
                    conn.outputStream.use { it.write(bytes) }
                }
                val code = conn.responseCode
                val stream = if (code in 200..299) conn.inputStream else conn.errorStream
                val body = stream?.bufferedReader(Charsets.UTF_8)?.use { reader ->
                    val text = reader.readText()
                    if (text.length > MAX_BODY_CHARS) throw IOException("Respuesta demasiado grande")
                    text
                }.orEmpty()
                HttpResponse(code, body)
            } finally {
                conn.disconnect()
            }
        }

    private companion object {
        const val MAX_BODY_CHARS = 256 * 1024
    }
}
