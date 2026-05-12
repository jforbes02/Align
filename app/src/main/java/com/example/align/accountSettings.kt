package com.example.align

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Button
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import com.example.align.data.api.ApiClient
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext


@Composable
fun AccountSettings(initialUsername: String = "User123", initialPassword: String = "password123") {
    var username by remember { mutableStateOf(initialUsername) }
    var password by remember { mutableStateOf(initialPassword) }

    var newUsername by remember { mutableStateOf("") }
    var newPassword by remember { mutableStateOf("") }
    var statusMessage by remember { mutableStateOf("") }

    val scope = rememberCoroutineScope()
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {

        Text("Account Settings", style = MaterialTheme.typography.headlineMedium)

        Text("Username: $username")

        HorizontalDivider()

        OutlinedTextField(
            value = newUsername,
            onValueChange = { newUsername = it },
            label = { Text("New Username") }
        )

        Button(onClick = {
            if (newUsername.isNotEmpty()) {
                scope.launch {
                    val api = ApiClient.create(username, password)
                    try {
                        val response = withContext(Dispatchers.IO) {
                            api.changeUsername(mapOf("username" to newUsername))
                        }
                        if (response.isSuccessful) {
                            username = newUsername
                            newUsername = ""
                            statusMessage = "Username Updated!"
                        } else {
                            statusMessage = "Failed to change username!"
                        }
                    } catch (e: Exception) {
                        statusMessage = "Network error!"
                    }
                }
            }
        }) {
            Text("Change Username")
        }

        HorizontalDivider()

        OutlinedTextField(
            value = newPassword,
            onValueChange = { newPassword = it },
            label = { Text("New Password") }
        )

        Button(onClick = {
            if (newPassword.isNotEmpty()) {
                scope.launch {
                    val api = ApiClient.create(username, password)
                    try {
                        val response = withContext(Dispatchers.IO) {
                            api.changePassword(mapOf("password" to newPassword))
                        }
                        if (response.isSuccessful) {
                            password = newPassword
                            newPassword = ""
                            statusMessage = "Password updated"
                        } else {
                            statusMessage = "Failed to update password"
                        }
                    } catch (e: Exception) {
                        statusMessage = "Network error!"
                    }
                }
            }
        }) {
            Text("Change Password")
        }

        if (statusMessage.isNotEmpty()) {
            Text(statusMessage, color = MaterialTheme.colorScheme.primary)
        }
    }
}

@Preview(showBackground = true, showSystemUi = true)
@Composable
fun AccSettingsPreview(){
    AccountSettings()
}
