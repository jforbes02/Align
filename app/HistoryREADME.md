# History Feature


Displays a line chart showing the user's workout score trend over their last 5 sessions. It uses MPAndroidChart's `LineChart` to visualize `final_score` values from the backend's `/history/{user_id}` endpoint.
Used MPAndroidChart because its light and easy to use

### Data Flow


LoginActivity → HomeScreen → HistoryActivity


Credentials (`Username`, `Password`) are passed through Intent extras at each step.


Requires HTTP Basic Auth.

### Added Files and Tweaks


`data/models/ExerciseSession.kt` - Kotlin data class matching the API response 

`data/api/AlignAPI.kt` - Retrofit interface with `getHistory(userId)` 

`res/layout/activity_history.xml` - Layout with title TextView and LineChart

`HistoryActivity.kt` - Fetches data, configures and populates the chart 

## How It Works

1. **HistoryActivity** receives `Username`, `Password` from the Intent
2. Creates an authenticated API client via `ApiClient.create(username, password)` - reuses the existing ApiClient rather than creating a new HTTP setup, keeping things consistent
3. Calls `api.getHistory(userId)` on a background coroutine (IO dispatcher) so the UI thread isn't blocked during the network request
4. Reverses the response into chronological order - the API returns newest-first for efficiency (it's a `LIMIT 5` with `ORDER BY created_at DESC`), but a chart reads left-to-right so oldest should come first
5. Maps each session to a chart `Entry(index, final_score)` - uses index-based x values rather than timestamps because the sessions may be unevenly spaced in time, and index-based spacing keeps the chart readable
6. Parses `created_at` (ISO format) into `MM/DD` labels for the x-axis - short format keeps labels from overlapping on small screens
7. Configures the `LineDataSet` with cubic bezier curves and a filled area under the line - the smooth curve and fill make the trend easier to read at a glance compared to sharp lines
8. Displays the chart with a short 500ms animation to make the data feel responsive without being distracting


## Dependencies

MPAndroidChart. It's declared in `app/build.gradle.kts`:


implementation("com.github.PhilJay:MPAndroidChart:v3.1.0")


The JitPack repository is configured in `settings.gradle.kts`.

## Edge Cases

- **No sessions**: Shows a Toast "No chart data available"
- **Network error**: Shows a Toast with the error message
- **Missing credentials**: Shows "Unable to load history" and returns early