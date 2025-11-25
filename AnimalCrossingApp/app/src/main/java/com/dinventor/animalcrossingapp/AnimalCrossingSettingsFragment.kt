package com.dinventor.animalcrossingapp

import android.os.Bundle
import android.view.inputmethod.EditorInfo
import androidx.preference.EditTextPreference
import androidx.preference.PreferenceFragmentCompat

class AnimalCrossingSettingsFragment : PreferenceFragmentCompat() {
    override fun onCreatePreferences(
        savedInstanceState: Bundle?,
        rootKey: String?
    ) {
        setPreferencesFromResource(R.xml.preferences, rootKey)

        val domainPreference = findPreference<EditTextPreference>("serverDomain")
        domainPreference?.summaryProvider = EditTextPreference.SimpleSummaryProvider.getInstance()

        val portPreference = findPreference<IntegerEditTextPreference>("serverPort")
        portPreference?.summaryProvider = EditTextPreference.SimpleSummaryProvider.getInstance()
    }
}