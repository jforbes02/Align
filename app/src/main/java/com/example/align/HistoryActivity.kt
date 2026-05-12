package com.example.align

import android.graphics.Color
import android.os.Bundle
import android.text.Spannable
import android.text.SpannableString
import android.text.SpannableStringBuilder
import android.text.style.ForegroundColorSpan
import android.widget.TextView
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import com.example.align.data.api.ApiClient
import com.example.align.data.models.ExerciseSession
import com.github.mikephil.charting.charts.LineChart
import com.github.mikephil.charting.components.XAxis
import com.github.mikephil.charting.data.Entry
import com.github.mikephil.charting.data.LineData
import com.github.mikephil.charting.data.LineDataSet
import com.github.mikephil.charting.formatter.ValueFormatter
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class HistoryActivity : AppCompatActivity() {

    private lateinit var lineChart: LineChart
    // added for text view
    private lateinit var dataText: TextView


    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_history)

        lineChart = findViewById(R.id.lineChart)
        // added for data text
        dataText = findViewById(R.id.dataText)


        val username = intent.getStringExtra("Username") ?: ""
        val password = intent.getStringExtra("Password") ?: ""

        if (username.isBlank() || password.isBlank()) {
            Toast.makeText(this, "Unable to load history", Toast.LENGTH_SHORT).show()
            return
        }

        setupChart()
        fetchHistory(username, password)
    }

    private fun setupChart() {
        lineChart.description.isEnabled = false
        lineChart.setTouchEnabled(true)
        lineChart.setDragEnabled(true)
        lineChart.setScaleEnabled(false)
        lineChart.setPinchZoom(false)
        lineChart.setDrawGridBackground(false)
        lineChart.legend.isEnabled = false

        // Y axis (score 0-100)
        lineChart.axisLeft.apply {
            axisMinimum = 0f
            axisMaximum = 100f
            textColor = Color.parseColor("#00695C")
            gridColor = Color.parseColor("#B2DFDB")
        }
        lineChart.axisRight.isEnabled = false

        // X axis
        lineChart.xAxis.apply {
            position = XAxis.XAxisPosition.BOTTOM
            textColor = Color.parseColor("#00695C")
            gridColor = Color.parseColor("#B2DFDB")
            granularity = 1f
        }
    }

    private fun fetchHistory(username: String, password: String) {
        val api = ApiClient.create(username, password)

        CoroutineScope(Dispatchers.IO).launch {
            try {
                val sessions = api.getHistory(0)

                withContext(Dispatchers.Main) {
                    if (sessions.isEmpty()) {
                        Toast.makeText(this@HistoryActivity, "No workout history yet", Toast.LENGTH_SHORT).show()
                    } else {
                        displayChart(sessions)
                    }
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    Toast.makeText(this@HistoryActivity, "Error loading history: ${e.message}", Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun displayChart(sessions: List<ExerciseSession>) {
        // Sessions come newest-first from the API, reverse for chronological order
        val sorted = sessions.reversed()

        // Build date labels for x-axis
        val dateLabels = sorted.map { session ->
            // created_at is ISO format like "2026-03-20T14:30:00"
            val datePart = session.created_at.substringBefore("T")
            // Show as MM/DD
            val parts = datePart.split("-")
            if (parts.size == 3) "${parts[1]}/${parts[2]}" else datePart
        }

        // Build chart entries
        val entries = sorted.mapIndexed { index, session ->
            Entry(index.toFloat(), session.final_score)
        }

        val dataSet = LineDataSet(entries, "Score").apply {
            color = Color.parseColor("#00897B")          // align_teal
            setCircleColor(Color.parseColor("#00695C"))   // align_dark_teal
            lineWidth = 3f
            circleRadius = 6f
            setDrawCircleHole(true)
            circleHoleRadius = 3f
            valueTextSize = 12f
            valueTextColor = Color.parseColor("#00695C")
            mode = LineDataSet.Mode.CUBIC_BEZIER
            setDrawFilled(true)
            fillColor = Color.parseColor("#B2DFDB")
            fillAlpha = 100
        }

        // Set date labels on x-axis
        lineChart.xAxis.valueFormatter = object : ValueFormatter() {
            override fun getFormattedValue(value: Float): String {
                val index = value.toInt()
                return if (index in dateLabels.indices) dateLabels[index] else ""
            }
        }

        lineChart.data = LineData(dataSet)
        lineChart.animateX(500)
        lineChart.invalidate()

        // logic of the text summary table, using exisitng data from graph

        val builder = SpannableStringBuilder()

        sorted.forEachIndexed { index, session ->
            val score = session.final_score.toInt()

            val label = when {
                score >= 85 -> "Great"
                score >= 70 -> "Good"
                else -> "Poor"
            }

            val color = when (label) {
                "Great" -> Color.GREEN
                "Good" -> Color.rgb(255,165,0)
                else -> Color.RED
            }

            val line = "${dateLabels[index]} - Score: $score - $label\n"
            val spannable = SpannableString(line)

            spannable.setSpan(
                ForegroundColorSpan(color),
                line.indexOf(label),
                line.length,
                Spannable.SPAN_EXCLUSIVE_EXCLUSIVE
            )

            builder.append(spannable)
        }

        dataText.text = builder
    }
}
