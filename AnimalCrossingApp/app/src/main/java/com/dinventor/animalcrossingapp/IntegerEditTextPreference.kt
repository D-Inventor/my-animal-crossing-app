package com.dinventor.animalcrossingapp

import android.content.Context
import android.text.InputType
import android.util.AttributeSet
import androidx.preference.EditTextPreference
import java.lang.ClassCastException

class IntegerEditTextPreference : EditTextPreference {
    constructor(context: Context) : super(context) {

        setOnBindEditTextListener { it ->
            it.inputType = InputType.TYPE_CLASS_NUMBER
        }
    }

    constructor(context: Context, attributeSet: AttributeSet) : super(context, attributeSet) {
        setOnBindEditTextListener { it ->
            it.inputType = InputType.TYPE_CLASS_NUMBER
        }
    }

    override fun getPersistedInt(defaultReturnValue: Int): Int {
        return try {
            super.getPersistedInt(defaultReturnValue)
        } catch (e: ClassCastException) {
            0
        }
    }

    override fun getPersistedString(defaultReturnValue: String?): String? {
        val defaultInt = defaultReturnValue?.toInt() ?: -1
        val storedInt = getPersistedInt(defaultInt)
        return storedInt.toString()
    }

    override fun persistString(value: String?): Boolean {
        try {
            val intValue = value?.toInt() ?: 0
            return persistInt(intValue)
        } catch (e: NumberFormatException) {
            return false
        }
    }
}