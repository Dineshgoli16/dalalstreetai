package com.example.dalalstreetai

import android.annotation.SuppressLint
import android.content.Context
import android.graphics.Bitmap
import android.os.Bundle
import android.speech.tts.TextToSpeech
import android.view.ViewGroup
import android.webkit.JavascriptInterface
import android.webkit.WebChromeClient
import android.webkit.WebResourceError
import android.webkit.WebResourceRequest
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.BackHandler
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import org.json.JSONObject
import java.io.BufferedReader
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL
import java.util.Locale

class MainActivity : ComponentActivity(), TextToSpeech.OnInitListener {

    private var tts: TextToSpeech? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        try {
            tts = TextToSpeech(this, this)
        } catch (_: Exception) {}

        setContent {
            MaterialTheme(
                colorScheme = lightColorScheme(
                    primary = Color(0xFF2563EB),
                    surface = Color.White,
                    background = Color(0xFFF8FAFC)
                )
            ) {
                Surface(
                    modifier = Modifier
                        .fillMaxSize()
                        .statusBarsPadding(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    StandaloneAppScreen(activity = this)
                }
            }
        }
    }

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            tts?.language = Locale.ENGLISH
        }
    }

    fun speak(text: String) {
        tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "dalal_tts")
    }

    fun stopSpeak() {
        tts?.stop()
    }

    override fun onDestroy() {
        tts?.stop()
        tts?.shutdown()
        super.onDestroy()
    }
}

class DalalBridge(private val activity: MainActivity) {
    private val prefs = activity.getSharedPreferences("dalal_storage", Context.MODE_PRIVATE)
    private val defaultGeminiKey = ""

    @JavascriptInterface
    fun speakText(text: String) {
        activity.runOnUiThread {
            activity.speak(text)
        }
    }

    @JavascriptInterface
    fun stopSpeech() {
        activity.runOnUiThread {
            activity.stopSpeak()
        }
    }

    @JavascriptInterface
    fun httpGet(urlStr: String, headersJson: String?): String {
        return try {
            val cleanUrl = urlStr.substringBefore("?").removePrefix("./")
            if (cleanUrl.startsWith("file:///android_asset/") || cleanUrl.endsWith(".json") || cleanUrl.endsWith(".js") || cleanUrl.endsWith(".html")) {
                val assetPath = if (cleanUrl.startsWith("file:///android_asset/")) {
                    cleanUrl.removePrefix("file:///android_asset/")
                } else {
                    "www/" + cleanUrl
                }
                try {
                    return activity.assets.open(assetPath).bufferedReader().use { it.readText() }
                } catch (_: Exception) {}
            }
            val url = URL(urlStr)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "GET"
            conn.connectTimeout = 5000
            conn.readTimeout = 5000
            conn.instanceFollowRedirects = true
            conn.setRequestProperty(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            conn.setRequestProperty("Accept", "*/*")

            if (!headersJson.isNullOrBlank()) {
                try {
                    val headersObj = JSONObject(headersJson)
                    val keys = headersObj.keys()
                    while (keys.hasNext()) {
                        val key = keys.next()
                        conn.setRequestProperty(key, headersObj.getString(key))
                    }
                } catch (_: Exception) {}
            }

            val responseCode = conn.responseCode
            val stream = if (responseCode in 200..299) conn.inputStream else (conn.errorStream ?: conn.inputStream)
            BufferedReader(InputStreamReader(stream)).use { it.readText() }
        } catch (e: Exception) {
            """{"error": "${e.localizedMessage?.replace("\"", "\\\"") ?: "Network request failed"}"}"""
        }
    }

    @JavascriptInterface
    fun httpPost(urlStr: String, bodyStr: String, headersJson: String?): String {
        return try {
            val url = URL(urlStr)
            val conn = url.openConnection() as HttpURLConnection
            conn.requestMethod = "POST"
            conn.connectTimeout = 20000
            conn.readTimeout = 30000
            conn.instanceFollowRedirects = true
            conn.doOutput = true
            conn.setRequestProperty("Content-Type", "application/json; charset=utf-8")
            conn.setRequestProperty(
                "User-Agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )

            if (!headersJson.isNullOrBlank()) {
                try {
                    val headersObj = JSONObject(headersJson)
                    val keys = headersObj.keys()
                    while (keys.hasNext()) {
                        val key = keys.next()
                        conn.setRequestProperty(key, headersObj.getString(key))
                    }
                } catch (_: Exception) {}
            }

            OutputStreamWriter(conn.outputStream, "UTF-8").use {
                it.write(bodyStr)
                it.flush()
            }

            val responseCode = conn.responseCode
            val stream = if (responseCode in 200..299) conn.inputStream else (conn.errorStream ?: conn.inputStream)
            BufferedReader(InputStreamReader(stream)).use { it.readText() }
        } catch (e: Exception) {
            """{"error": "${e.localizedMessage?.replace("\"", "\\\"") ?: "Network request failed"}"}"""
        }
    }

    @JavascriptInterface
    fun saveData(key: String, value: String): Boolean {
        return try {
            prefs.edit().putString(key, value).apply()
            true
        } catch (e: Exception) {
            false
        }
    }

    @JavascriptInterface
    fun loadData(key: String, defaultValue: String): String {
        return prefs.getString(key, defaultValue) ?: defaultValue
    }

    @JavascriptInterface
    fun getGeminiKey(): String {
        return prefs.getString("gemini_api_key", defaultGeminiKey) ?: defaultGeminiKey
    }

    @JavascriptInterface
    fun setGeminiKey(key: String): Boolean {
        return try {
            prefs.edit().putString("gemini_api_key", key).apply()
            true
        } catch (e: Exception) {
            false
        }
    }

    @JavascriptInterface
    fun showToast(msg: String) {
        activity.runOnUiThread {
            Toast.makeText(activity.applicationContext, msg, Toast.LENGTH_SHORT).show()
        }
    }
}

@SuppressLint("SetJavaScriptEnabled")
@Composable
fun StandaloneAppScreen(activity: MainActivity) {
    var webViewInstance by remember { mutableStateOf<WebView?>(null) }
    var canGoBack by remember { mutableStateOf(false) }
    var isLoading by remember { mutableStateOf(true) }

    BackHandler(enabled = canGoBack) {
        webViewInstance?.goBack()
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            modifier = Modifier.fillMaxSize(),
            factory = { context ->
                WebView(context).apply {
                    layoutParams = ViewGroup.LayoutParams(
                        ViewGroup.LayoutParams.MATCH_PARENT,
                        ViewGroup.LayoutParams.MATCH_PARENT
                    )
                    setLayerType(android.view.View.LAYER_TYPE_HARDWARE, null)

                    settings.apply {
                        javaScriptEnabled = true
                        domStorageEnabled = true
                        databaseEnabled = true
                        allowFileAccess = true
                        allowContentAccess = true
                        useWideViewPort = true
                        loadWithOverviewMode = true
                        builtInZoomControls = false
                        displayZoomControls = false
                        mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
                        cacheMode = WebSettings.LOAD_DEFAULT
                        @Suppress("DEPRECATION")
                        allowFileAccessFromFileURLs = true
                        @Suppress("DEPRECATION")
                        allowUniversalAccessFromFileURLs = true
                    }

                    addJavascriptInterface(DalalBridge(activity), "DalalBridge")

                    webViewClient = object : WebViewClient() {
                        override fun onPageStarted(view: WebView?, url: String?, favicon: Bitmap?) {
                            isLoading = true
                            canGoBack = view?.canGoBack() ?: false
                        }

                        override fun onPageFinished(view: WebView?, url: String?) {
                            isLoading = false
                            canGoBack = view?.canGoBack() ?: false
                        }

                        override fun onReceivedError(
                            view: WebView?,
                            request: WebResourceRequest?,
                            error: WebResourceError?
                        ) {
                            if (request?.isForMainFrame == true) {
                                isLoading = false
                            }
                        }
                    }

                    webChromeClient = object : WebChromeClient() {
                        override fun onConsoleMessage(consoleMessage: android.webkit.ConsoleMessage?): Boolean {
                            android.util.Log.d("DalalJS", "${consoleMessage?.message()} -- line ${consoleMessage?.lineNumber()} of ${consoleMessage?.sourceId()}")
                            return super.onConsoleMessage(consoleMessage)
                        }
                    }

                    loadUrl("file:///android_asset/www/index.html")
                    webViewInstance = this
                }
            }
        )

        if (isLoading) {
            LinearProgressIndicator(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(3.dp),
                color = Color(0xFF2563EB)
            )
        }
    }
}
