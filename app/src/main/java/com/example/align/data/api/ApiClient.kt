package com.example.align.data.api

import com.example.align.BuildConfig
import okhttp3.Credentials
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

object ApiClient {
    private val BASE_URL = BuildConfig.BASE_URL


    // This builds the Retrofit api client - bridge between fastapi and kotlin
    fun create(username: String, password: String): AlignApi {
        val cred = Credentials.basic(username, password)
        // Attach Basic Auth header to every outgoing request
        val client = OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                    .header("Authorization", cred)
                    .build()
                chain.proceed(request)
            }
            .build()

        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(client)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(AlignApi::class.java)
    } // whenever an api.blahblahblah is sent a request is sent to an endpoint

}