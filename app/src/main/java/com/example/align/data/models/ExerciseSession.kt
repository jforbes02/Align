package com.example.align.data.models

data class ExerciseSession(
    val id: Int,
    val user_id: Int,
    val exercise_type: String,
    val final_score: Float,
    val created_at: String
)
