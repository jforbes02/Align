package com.example.align

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import android.widget.ImageButton
import android.widget.Toast

class HomeScreen : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_home_screen)
        val welcomeText = findViewById<TextView>(R.id.infernoNaming)
        val name = intent.getStringExtra("Username")
        if(!name.isNullOrBlank()){
            welcomeText.text = "Hello $name!"
        } else{
            //temporary until we can get stuff working
            welcomeText.text = "it appears something has gone terribly wrong. Perhaps you delved too deep"
        }
        // buttons to the rest of the screens
        val squatButton = findViewById<ImageButton>(R.id.squat_button)
        val benchButton = findViewById<ImageButton>(R.id.bench_button)
        val accountButton = findViewById<ImageButton>(R.id.accountbutton)
        val historyButton = findViewById<ImageButton>(R.id.historybutton)
        val videoplayer = findViewById<ImageButton>(R.id.videoView)
            //we be playing our videos here
        videoplayer.setOnClickListener {
            val intent =Intent(this@HomeScreen, VideoPlayer::class.java)
            startActivity(intent)
        }

        // screen for squat
        squatButton.setOnClickListener {
            val squatIntent = Intent(this, SquatActivity::class.java)
            squatIntent.putExtra("Username", intent.getStringExtra("Username"))
            startActivity(squatIntent)
        }

        // popup for bench
        benchButton.setOnClickListener {
            Toast.makeText(this, "To be added SOON", Toast.LENGTH_SHORT).show()
        }

        // screen for account
        accountButton.setOnClickListener {
            val accountIntent = Intent(this, AccountActivity::class.java)
            accountIntent.putExtra("Username", intent.getStringExtra("Username"))
            accountIntent.putExtra("Password", intent.getStringExtra("Password"))
            startActivity(accountIntent)
        }

        // screen for history
        historyButton.setOnClickListener {
            val historyIntent = Intent(this, HistoryActivity::class.java)
            historyIntent.putExtra("Username", intent.getStringExtra("Username"))
            historyIntent.putExtra("Password", intent.getStringExtra("Password"))
            startActivity(historyIntent)
        }
    }
}