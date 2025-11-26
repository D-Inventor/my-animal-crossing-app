package com.dinventor.animalcrossingapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Card
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
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.em
import coil3.compose.AsyncImage
import com.dinventor.animalcrossingapp.amiibo.GetCharacterByAmiiboIDResponse
import com.dinventor.animalcrossingapp.ui.theme.AnimalCrossingAppTheme

class CharacterActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()

        val amiiboModel =
            intent.getSerializableExtra("amiibo", GetCharacterByAmiiboIDResponse::class.java)
                ?: return

        setContent {
            AnimalCrossingAppTheme {
                Scaffold(
                    topBar = {
                        TopAppBar(
                            colors = TopAppBarDefaults.topAppBarColors(
                                containerColor = MaterialTheme.colorScheme.primaryContainer,
                                titleContentColor = MaterialTheme.colorScheme.primary,
                            ),
                            title = {
                                Text(text = "Villager")
                            },
                            navigationIcon = {
                                IconButton(onClick = { finish() }) {
                                    Icon(
                                        imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                                        contentDescription = "Back"
                                    )
                                }
                            })
                    },
                    modifier = Modifier.fillMaxSize()
                ) { innerPadding ->
                    CharacterCard(
                        amiiboModel,
                        modifier = Modifier
                            .padding(innerPadding)
                            .padding(16.dp)
                    )
                }
            }
        }
    }
}

@Composable
fun CharacterCard(data: GetCharacterByAmiiboIDResponse, modifier: Modifier = Modifier) {
    Card(modifier = modifier) {
        @Suppress("COMPOSE_APPLIER_CALL_MISMATCH")
        BoxWithConstraints(modifier = Modifier.padding(16.dp)) {
            if (maxWidth < 600.dp) {
                Column(
                    verticalArrangement = Arrangement.spacedBy(16.dp),
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    CharacterCardContent(data)
                }
            } else {
                Row(horizontalArrangement = Arrangement.spacedBy(16.dp)) {
                    CharacterCardContent(data)
                }
            }
        }
    }
}

@Composable
fun CharacterCardContent(data: GetCharacterByAmiiboIDResponse) {
    AsyncImage(
        model = data.imageUrl,
        contentDescription = "Villager: ${data.name}",
        modifier = Modifier.heightIn(max = 240.dp)
    )

    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = Modifier.widthIn(0.dp, 360.dp)
    ) {
        Text(text = data.name, fontSize = 8.em, fontWeight = FontWeight.Bold)

        Row {
            Text(text = "Personality", modifier = Modifier.weight(1f))
            Text(text = data.personality, modifier = Modifier.weight(1f))
        }
        Row {
            Text(text = "Gender", modifier = Modifier.weight(1f))
            Text(text = data.gender, modifier = Modifier.weight(1f))
        }
        Row {
            Text(text = "Species", modifier = Modifier.weight(1f))
            Text(text = data.species, modifier = Modifier.weight(1f))
        }
        Row {
            Text(text = "Hobby", modifier = Modifier.weight(1f))
            Text(text = data.hobby, modifier = Modifier.weight(1f))
        }
    }
}

@Composable
@Preview(name = "Card preview", showBackground = true)
fun CharacterCardPreview() {
    AnimalCrossingAppTheme {
        CharacterCard(
            GetCharacterByAmiiboIDResponse(
                1,
                "flg01",
                "Ribbot",
                "Frog",
                "Jock",
                "Male",
                "Fitness",
                "https://dodo.ac/np/images/thumb/5/58/Rocket_NH.png/225px-Rocket_NH.png"
            )
        )
    }
}