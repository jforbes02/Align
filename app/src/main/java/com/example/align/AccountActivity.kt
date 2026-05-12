package com.example.align

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent

class AccountActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val username = intent.getStringExtra("Username") ?: ""
        val password = intent.getStringExtra("Password") ?: ""
        setContent {
            AccountSettings(username, password)
        }
    }
}