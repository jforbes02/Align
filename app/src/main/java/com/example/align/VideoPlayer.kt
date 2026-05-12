package com.example.align

import android.media.browse.MediaBrowser
import android.os.Bundle
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.ViewCompat
import androidx.core.view.WindowInsetsCompat
import androidx.media3.common.MediaItem
import androidx.media3.exoplayer.ExoPlayer
import androidx.media3.ui.PlayerView

class VideoPlayer : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_video_player)
        val playview = findViewById<PlayerView>(R.id.videoView)
        val player = ExoPlayer.Builder(this).build()
        val excersizeview = findViewById<PlayerView>(R.id.ExcersizeView)
        val excersize = ExoPlayer.Builder(this).build()
        playview.player = player
        excersizeview.player = player
        //Replace this with A File path later, we will need to figure this the fuck out later
        //Like actually we need some sort of file hosting for this to work
        val ClientItem = MediaItem.fromUri("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/WhatCarCanYouGetForAGrand.mp4")
        val Serveritem= MediaItem.fromUri("http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4")
        player.setMediaItem(ClientItem)
        player.prepare()
        player.play()
        excersize.setMediaItem(Serveritem)
        excersize.prepare()
        excersize.play()
    }
}