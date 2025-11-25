package com.dinventor.animalcrossingapp.amiibo

import kotlinx.serialization.ExperimentalSerializationApi
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.JsonIgnoreUnknownKeys

class AmiiboClient {
}

@OptIn(ExperimentalSerializationApi::class)
@Serializable
@JsonIgnoreUnknownKeys
data class GetCharacterByAmiiboIDResponse(
    val id: Int,
    @SerialName("external_id") val externalId: String,
    val name: String,
    val species: String,
    val personality: String,
    val gender: String,
    val hobby: String,
    @SerialName("image_url") val imageUrl: String
): java.io.Serializable