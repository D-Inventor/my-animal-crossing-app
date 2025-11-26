package com.dinventor.animalcrossingapp

import android.content.Intent
import android.net.InetAddresses
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.viewModels
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Settings
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import androidx.preference.PreferenceManager
import com.android.volley.Request
import com.android.volley.RequestQueue
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.dinventor.animalcrossingapp.amiibo.AmiiboReader
import com.dinventor.animalcrossingapp.amiibo.GetCharacterByAmiiboIDResponse
import com.dinventor.animalcrossingapp.ui.theme.AnimalCrossingAppTheme
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json
import java.net.InetSocketAddress

class MainActivity : ComponentActivity() {

    private var _requestQueue: RequestQueue? = null

    override fun onResume() {
        super.onResume()

        val viewModel: MainActivityStateViewModel by viewModels()
        viewModel.resetAmiiboLookup()
        AmiiboReader.startReading(this)
    }

    public override fun onPause() {
        super.onPause()

        AmiiboReader.stopReading(this)
    }

    @OptIn(ExperimentalStdlibApi::class)
    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)

        AmiiboReader.handleIntent(intent) { id ->

            val viewModel: MainActivityStateViewModel by viewModels()
            viewModel.beginAmiiboLookup(id)

            val preferences = PreferenceManager.getDefaultSharedPreferences(this)
            val domain =
                preferences.getString("serverDomain", null)
                    ?: throw IllegalStateException("Server address not defined")

            if (!InetAddresses.isNumericAddress(domain)) {
                throw IllegalStateException("server address is not an IP address")
            }

            val port =
                preferences.getInt("serverPort", 0)

            val socketAddress = InetSocketAddress(InetAddresses.parseNumericAddress(domain), port)

            val url = "http://$socketAddress/api/characters?amiibo_id=${id.take(8)}"

            val request = StringRequest(Request.Method.GET, url, { response ->
                try {
                    val decodedResponse =
                        Json.decodeFromString<GetCharacterByAmiiboIDResponse>(response)

                    val newIntent = Intent(this, CharacterActivity::class.java)
                    newIntent.putExtra("amiibo", decodedResponse)

                    startActivity(newIntent)
                } catch (ex: Exception) {
                    Log.d("Something happened", ex.message ?: "Something happened")
                }
            }, { })
            _requestQueue?.add(request)
        }
    }

    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        _requestQueue = Volley.newRequestQueue(this)
        enableEdgeToEdge()

        val viewModel: MainActivityStateViewModel by viewModels()
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    setContent {
                        AnimalCrossingAppTheme {
                            Scaffold(
                                topBar = {
                                    TopAppBar(
                                        colors = TopAppBarDefaults.topAppBarColors(
                                            containerColor = MaterialTheme.colorScheme.primaryContainer,
                                            titleContentColor = MaterialTheme.colorScheme.primary,
                                        ),
                                        title = {},
                                        actions = {
                                            IconButton(onClick = { onNavigateToSettings() }) {
                                                Icon(
                                                    imageVector = Icons.Filled.Settings,
                                                    contentDescription = "Settings"
                                                )
                                            }
                                        }
                                    )
                                },
                                modifier = Modifier.fillMaxSize()
                            ) { innerPadding ->
                                AmiiboScanner(
                                    state = state,
                                    modifier = Modifier
                                        .padding(innerPadding)
                                        .fillMaxSize()
                                )
                            }
                        }
                    }
                }
            }
        }
    }

    private fun onNavigateToSettings() {
        val intent = Intent(this, AnimalCrossingSettingsActivity::class.java)
        startActivity(intent)
    }
}

@Composable
fun AmiiboScanner(
    state: MainActivityState, modifier: Modifier = Modifier
) {
    Column(
        verticalArrangement = Arrangement.Center,
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = modifier.padding(horizontal = 16.dp)
    ) {

        when (state.amiiboState) {
            is ScanningAmiiboState -> WaitForAmiibo()
            is LookupStartedAmiiboState -> WaitForAmiiboLookup()
        }
    }
}

@Composable
fun WaitForAmiibo() {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        CircularProgressIndicator(
            color = MaterialTheme.colorScheme.secondary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
        Text(text = "Looking for Amiibo NFC...")
    }
}

@Composable
fun WaitForAmiiboLookup() {
    Row(
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        CircularProgressIndicator(
            color = MaterialTheme.colorScheme.secondary,
            trackColor = MaterialTheme.colorScheme.surfaceVariant
        )
        Text(text = "Amiibo scanned: looking up data...")
    }
}

@Preview(showBackground = true)
@Composable
fun AmiiboScannerWaitingPreview() {
    AnimalCrossingAppTheme {
        AmiiboScanner(MainActivityState(ScanningAmiiboState()))
    }
}

@Preview(showBackground = true)
@Composable
fun AmiiboScannerLookingUpPreview() {
    AnimalCrossingAppTheme {
        AmiiboScanner(MainActivityState(LookupStartedAmiiboState("12345678")))
    }
}