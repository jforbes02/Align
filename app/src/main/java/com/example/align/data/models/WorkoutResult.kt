package com.example.align.data.models

data class WorkoutResult(
    val joints: Map<String, List<Float>>,
    val l_knee_angle: Float,
    val r_knee_angle: Float,
    val rep_count: Int = 0
)