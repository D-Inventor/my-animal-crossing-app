package com.dinventor.animalcrossingapp

import androidx.lifecycle.ViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

data class MainActivityState(val amiiboState: AmiiboState)

interface AmiiboState { }

class ScanningAmiiboState : AmiiboState

data class LookupStartedAmiiboState(val id: String) : AmiiboState

class MainActivityStateViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(MainActivityState(ScanningAmiiboState()))
    val uiState: StateFlow<MainActivityState> = _uiState.asStateFlow()

    fun beginAmiiboLookup(id: String) {
        _uiState.update { currentState ->
            currentState.copy(amiiboState = LookupStartedAmiiboState(id))
        }
    }

    fun resetAmiiboLookup() {
        _uiState.update { currentState ->
            currentState.copy(amiiboState = ScanningAmiiboState())
        }
    }
}