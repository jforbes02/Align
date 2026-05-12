package com.example.align

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import android.widget.Button

class Landingscreen : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        //For future refence the following code must exist in every landing screen application
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_landingscreen)
        //assign variables to the xml file buttons
        val loginButton = findViewById<Button>(R.id.btnLogin)
        val signupButton = findViewById<Button>(R.id.btnsignup)
        //transition over to MainActivity
        loginButton.setOnClickListener{
            val intent = Intent(this, LoginActivity::class.java)
            startActivity(intent)
        }
        signupButton.setOnClickListener{
            val intent = Intent(this, SignupActivity::class.java)
            startActivity(intent)
        }
    }
}