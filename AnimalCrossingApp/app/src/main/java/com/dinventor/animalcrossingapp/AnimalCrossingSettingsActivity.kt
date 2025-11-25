package com.dinventor.animalcrossingapp

import android.os.Bundle
import androidx.activity.compose.setContent
import androidx.appcompat.app.AppCompatActivity
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.asPaddingValues
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.systemBars
import androidx.compose.ui.Modifier
import androidx.fragment.compose.AndroidFragment

class AnimalCrossingSettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val insets = WindowInsets.systemBars.asPaddingValues()
            AndroidFragment<AnimalCrossingSettingsFragment>(modifier = Modifier.padding(insets))
        }
    }
}