package com.dinventor.animalcrossingapp.amiibo

import android.app.Activity
import android.app.PendingIntent
import android.content.Intent
import android.content.IntentFilter
import android.nfc.NfcAdapter
import android.nfc.NfcAdapter.ACTION_TECH_DISCOVERED
import android.nfc.Tag
import android.nfc.tech.MifareUltralight
import android.nfc.tech.NdefFormatable
import android.nfc.tech.NfcA

class AmiiboReader {

    companion object {

        fun startReading(activity: Activity) {

            NfcAdapter.getDefaultAdapter(activity)?.let { it ->
                val launchIntent = Intent(activity, activity.javaClass)
                launchIntent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP)

                val pendingIntent = PendingIntent.getActivity(
                    activity, 0, launchIntent,
                    PendingIntent.FLAG_CANCEL_CURRENT or PendingIntent.FLAG_MUTABLE
                )

                val filters = arrayOf(IntentFilter(ACTION_TECH_DISCOVERED))
                val techTypes = arrayOf(
                    arrayOf(
                        NfcA::class.java.name,
                        MifareUltralight::class.java.name,
                        NdefFormatable::class.java.name
                    )
                )

                it.enableForegroundDispatch(activity, pendingIntent, filters, techTypes)
            }
        }

        fun stopReading(activity: Activity) {
            NfcAdapter.getDefaultAdapter(activity)?.disableForegroundDispatch(activity)
        }

        @OptIn(ExperimentalStdlibApi::class)
        fun handleIntent(intent: Intent, callback: (id: String) -> Unit): Boolean {
            if (NfcAdapter.ACTION_TECH_DISCOVERED != intent.action) {
                return false
            }

            val tag = intent.getParcelableExtra(NfcAdapter.EXTRA_TAG, Tag::class.java)

            MifareUltralight.get(tag)?.use { it ->
                it.connect()

                // according to https://kevinbrewster.github.io/Amiibo-Reverse-Engineering/
                // The model information is encoded in page 21, 22 and 23
                val bytes = it.readPages(21)
                val amiiboIdentifier =
                    bytes.take(4 * 2).toByteArray().toHexString(HexFormat.Default)

                callback(amiiboIdentifier)
            }

            return true
        }
    }
}