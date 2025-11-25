package com.dinventor.animalcrossingapp

import android.content.Intent
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
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.lifecycleScope
import androidx.lifecycle.repeatOnLifecycle
import com.android.volley.Request
import com.android.volley.RequestQueue
import com.android.volley.toolbox.StringRequest
import com.android.volley.toolbox.Volley
import com.dinventor.animalcrossingapp.amiibo.AmiiboReader
import com.dinventor.animalcrossingapp.amiibo.GetCharacterByAmiiboIDResponse
import com.dinventor.animalcrossingapp.ui.theme.AnimalCrossingAppTheme
import kotlinx.coroutines.launch
import kotlinx.serialization.json.Json

class MainActivity : ComponentActivity() {

    private var _requestQueue: RequestQueue? = null

    override fun onResume() {
        super.onResume()
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

            val url = "http://192.168.0.109:8000/api/characters?amiibo_id=${id.take(8)}"

            val request = StringRequest(Request.Method.GET, url, { response ->
                try {
                    val decodedResponse =
                        Json.decodeFromString<GetCharacterByAmiiboIDResponse>(response)

                    val viewModel: MainActivityStateViewModel by viewModels()
                    viewModel.amiiboFound(response)

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
                            Scaffold(modifier = Modifier.fillMaxSize()) { innerPadding ->
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
            is NothingAmiiboState -> WaitForAmiibo(state.amiiboState)
            is LookupStartedAmiiboState -> WaitForAmiiboLookup(state.amiiboState)
            is FoundAmiiboState -> AmiiboFound(state.amiiboState)
        }
    }
}

@Composable
fun WaitForAmiibo(state: NothingAmiiboState) {
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
fun WaitForAmiiboLookup(state: LookupStartedAmiiboState) {
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

@Composable
fun AmiiboFound(state: FoundAmiiboState) {
    Text(text = "Amiibo found: ${state.payload}")
}

@Preview(showBackground = true)
@Composable
fun AmiiboScannerWaitingPreview() {
    AnimalCrossingAppTheme {
        AmiiboScanner(MainActivityState(NothingAmiiboState()))
    }
}

@Preview(showBackground = true)
@Composable
fun AmiiboScannerLookingUpPreview() {
    AnimalCrossingAppTheme {
        AmiiboScanner(MainActivityState(LookupStartedAmiiboState("12345678")))
    }
}

@Preview(showBackground = true)
@Composable
fun AmiiboScannerFoundPreview() {
    AnimalCrossingAppTheme {
        AmiiboScanner(MainActivityState(FoundAmiiboState("{\"name\":\"Rocket\"}")))
    }
}