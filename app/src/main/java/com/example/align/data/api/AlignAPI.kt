package com.example.align.data.api

import com.example.align.data.models.ExerciseSession
import com.example.align.data.models.User
import retrofit2.http.*

interface AlignApi {
    @POST("/register")
    suspend fun register(@Body cred: Map<String, String>): retrofit2.Response<User>

    @POST("/login")
    suspend fun login(): retrofit2.Response<User>

    @POST("/change-password")
    suspend fun changePassword(@Body newPassword: Map<String, String>): retrofit2.Response<User>

    @POST("/change-username")
    suspend fun changeUsername(@Body newUsername: Map<String, String>): retrofit2.Response<User>

    @GET("/history/{user_id}")
    suspend fun getHistory(@Path("user_id") userId: Int): List<ExerciseSession>
}
