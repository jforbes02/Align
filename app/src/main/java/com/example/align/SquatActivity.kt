package com.example.align

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.ImageFormat
import android.graphics.YuvImage
import android.os.Bundle
import android.util.Base64
import android.util.Log
import android.widget.Button
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageAnalysis
import androidx.camera.core.ImageProxy
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import android.content.Intent
import com.example.align.data.models.WorkoutResult
import com.google.gson.Gson
import okhttp3.*
import java.io.ByteArrayOutputStream
import java.util.concurrent.Executors


class SquatActivity : AppCompatActivity() {
    //initialize camera preview onCreate
    private lateinit var cPreview : PreviewView
    private lateinit var infernoNaming : TextView
    private lateinit var poseOverlay : PoseOverlayView

    //Button Start Stpo
    private lateinit var startStopButton : Button
    var sessionActive = false

    // Websocket connection that sends and receives backend server data
    private var webSocket: WebSocket? = null
    private var readySend = true

    // for converting data to JSON
    private val gson = Gson()

    override fun onCreate(savedInstanceState: Bundle?) {

        super.onCreate(savedInstanceState)
        //init
        setContentView(R.layout.activity_squat)
        startStopButton = findViewById(R.id.btnStartStop)
        cPreview = findViewById(R.id.camPreview)
        cPreview.implementationMode = PreviewView.ImplementationMode.COMPATIBLE
        infernoNaming = findViewById(R.id.infernoNaming)
        poseOverlay = findViewById(R.id.poseOverlay)
        if(hasCameraPermission()) {
            startCamera()
        } else {
            ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.CAMERA), 100)
        }
        startStopButton.setOnClickListener {
            if (!sessionActive) {
                sessionActive = true
                startStopButton.text = "Stop"
                connectWebScoket()
            } else {
                sessionActive = false
                startStopButton.isEnabled = false
                val stopJson = gson.toJson(mapOf("action" to "stop"))
                webSocket?.send(stopJson)
                // don't close yet — wait for summary in onMessage
            }
        }




    }
    private fun sendFrame(imageProxy: ImageProxy) {
        readySend = false
        Log.d("SquatActivity", "sendFrame called, rotation: ${imageProxy.imageInfo.rotationDegrees}")

        val bitmap = imageProxyToBitmap(imageProxy)
        imageProxy.close()

        if (bitmap == null) {
            Log.d("SquatActivity", "bitmap is null!")
            readySend = true
            return
        }

        // encode to JPEG then base64 — matches what proccess_frame() expects
        val stream = ByteArrayOutputStream()
        bitmap.compress(Bitmap.CompressFormat.JPEG, 80, stream)
        val b64 = Base64.encodeToString(stream.toByteArray(), Base64.NO_WRAP)
        Log.d("SquatActivity", "Sending frame, b64 length: ${b64.length}")

        val json = gson.toJson(mapOf("frame" to b64))
        webSocket?.send(json)
    }

    private fun startCamera() {
        val cameraProviderFuture = ProcessCameraProvider.getInstance(this)

        cameraProviderFuture.addListener({
            val cameraProvider = cameraProviderFuture.get()

            val preview = Preview.Builder().build().also {
                it.surfaceProvider = cPreview.surfaceProvider
            }

            val analysis = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build()

            analysis.setAnalyzer(Executors.newSingleThreadExecutor()) { imageProxy
                ->
                if (sessionActive && readySend) {
                    sendFrame(imageProxy)
                } else {
                    imageProxy.close()
                }
            }

            cameraProvider.unbindAll()
            cameraProvider.bindToLifecycle(
                this,
                CameraSelector.DEFAULT_BACK_CAMERA,
                preview,
                analysis
            )
        }, ContextCompat.getMainExecutor(this))
    }


    private fun imageProxyToBitmap(image: ImageProxy): Bitmap? {
        val yBuffer = image.planes[0].buffer
        val uBuffer = image.planes[1].buffer
        val vBuffer = image.planes[2].buffer

        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()

        val nv21 = ByteArray(ySize + uSize + vSize)
        yBuffer.get(nv21, 0, ySize)
        vBuffer.get(nv21, ySize, vSize)
        uBuffer.get(nv21, ySize + vSize, uSize)

        val yuvImage = YuvImage(nv21, ImageFormat.NV21, image.width, image.height,
            null)
        val out = ByteArrayOutputStream()
        yuvImage.compressToJpeg(android.graphics.Rect(0, 0, image.width,
            image.height), 80, out)
        val bytes = out.toByteArray()
        val bitmap = BitmapFactory.decodeByteArray(bytes, 0, bytes.size) ?: return null

        val rotation = image.imageInfo.rotationDegrees
        if (rotation == 0) return bitmap

        val matrix = android.graphics.Matrix()
        matrix.postRotate(rotation.toFloat())
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }


    private fun connectWebScoket() {
        val baseUrl = BuildConfig.BASE_URL.trimEnd('/')
        val wsUrl = baseUrl.replace("http://", "ws://")
        val username = intent.getStringExtra("Username") ?: ""
        val url = "$wsUrl/ws/workout?username=$username"
        Log.d("SquatActivity", "Connecting to: $url")

        val client = OkHttpClient()
        val request = Request.Builder().url(url).build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d("SquatActivity", "Squat Started")
            }
            override fun onMessage(webSocket: WebSocket, text: String) {
                Log.d("SquatActivity", "Raw WS response: $text")

                val jsonObj = gson.fromJson(text, Map::class.java) as Map<*, *>

                if (jsonObj.containsKey("summary")) {
                    Log.d("SquatActivity", "Session summary: $text")
                    val score = (jsonObj["final_score"] as? Double ?: 0.0).toFloat()
                    val repCount = (jsonObj["rep_count"] as? Double)?.toInt() ?: 0
                    val goodReps = (jsonObj["good_reps"] as? Double)?.toInt() ?: 0
                    val badReps = (jsonObj["bad_reps"] as? Double)?.toInt() ?: 0
                    val repsRaw = jsonObj["reps"] as? List<*> ?: emptyList<Any>()
                    val repForms = repsRaw.map { rep ->
                        val repMap = rep as? Map<*, *>
                        repMap?.get("form") as? String ?: "unknown"
                    }.toTypedArray()

                    webSocket.close(1000, null)
                    this@SquatActivity.webSocket = null
                    readySend = true

                    runOnUiThread {
                        poseOverlay.updateJoints(emptyMap())
                        startStopButton.text = "Start"
                        startStopButton.isEnabled = true

                        val intent = Intent(this@SquatActivity, WorkoutResultsActivity::class.java).apply {
                            putExtra("final_score", score)
                            putExtra("rep_count", repCount)
                            putExtra("good_reps", goodReps)
                            putExtra("bad_reps", badReps)
                            putExtra("rep_forms", repForms)
                            putExtra("Username", this@SquatActivity.intent.getStringExtra("Username"))
                        }
                        startActivity(intent)
                    }
                } else {
                    // normal frame result
                    val res = gson.fromJson(text, WorkoutResult::class.java)
                    Log.d("SquatActivity", "Parsed joints: ${res.joints}")

                    runOnUiThread {
                        infernoNaming.text = "Reps: %d | L: %.0f° R: %.0f°".format(
                            res.rep_count, res.l_knee_angle, res.r_knee_angle
                        )
                        poseOverlay.updateJoints(res.joints)
                    }
                    readySend = true
                }
            }
            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                Log.d("SquatActivity", "Squat Closing")
            }
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e("SquatActivity", "WebSocket failed: ${t.message}", t)
            }
        })
    }

    private fun hasCameraPermission(): Boolean {
        return ContextCompat.checkSelfPermission(this, Manifest.permission.CAMERA) == PackageManager.PERMISSION_GRANTED
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray){
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 100 && grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            startCamera()
        } else {
            Toast.makeText(this, "Permission denied", Toast.LENGTH_SHORT).show()
            finish()
    }
}
    override fun onDestroy() {
        super.onDestroy()
        webSocket?.close(1000, null)
    }
}
