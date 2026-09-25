# Animate Subject Tracks Workflow

Turns an EarthRanger subject group's GPS history into an animated 3D map: each subject's track sweeps across real terrain as time passes, and the same animation is exported as an MP4 video.

Full documentation: **[wildlife-dynamics.github.io/animate-subject-tracks](https://wildlife-dynamics.github.io/animate-subject-tracks/)** (User Guide, Technical Guide and Troubleshooting).

## What it produces

- An **interactive animated 3D map** (`animated_map.html`). Each subject is drawn as a trail in its EarthRanger colour, with a marker at its current position, over satellite imagery draped on 3D terrain. It has a playback bar (play/pause, restart, time slider, speed) and a legend of subject names.
- An **MP4 video** (`animation.mp4`) of the same animation, recorded with the camera movement you choose.
- **GeoParquet files** of the cleaned relocations and trajectories, for further analysis.
- A **dashboard** showing the animated map, with the workflow details and time range.

## Requirements

- An **EarthRanger connection** configured in the workflow runner.
- The name of a **subject group** in EarthRanger, e.g. `Elephants`. Every subject in the group gets its own track.
- Internet access while the workflow runs. Terrain elevation tiles (AWS Terrarium) and satellite imagery (Esri World Imagery) are fetched live.

> Longer time ranges and larger subject groups take longer to fetch and to record as video. For a first run, a range of a few days to a few weeks works well.

---

## 1. Load the Workflow

In the workflow runner, go to **Workflow Templates** and click **Add Workflow Template**. Paste this repository's URL into the **Github Link** field, then click **Add Template**:

```
https://github.com/wildlife-dynamics/animate-subject-tracks.git
```

Once added, the workflow appears in the **Workflow Templates** list. Click it to open the configuration form.

> The card may show **Initializing…** briefly while the environment is set up.

---

## 2. Configure the Workflow

Only the **Workflow Name**, **Data Source**, **Time Range** and **Subject Group Name** need to be filled in. Every other section is pre-filled with defaults and can be left alone on a first run. Fields marked *advanced* are collapsed on the form.

### Workflow Details

| Field | Description |
|-------|-------------|
| Workflow Name | A short name to identify this run, e.g. `Elephants – July 2026` |
| Workflow Description | Optional notes about the run |

### Connect to EarthRanger

| Field | Description |
|-------|-------------|
| Data Source | The EarthRanger connection to pull tracking data from |

### Time Range

| Field | Description |
|-------|-------------|
| Since | Start of the period to animate |
| Until | End of the period to animate |
| Timezone | Optional timezone for Since/Until |
| Time Format *(advanced)* | How times are displayed on the dashboard. Default `%d %b %Y %H:%M:%S` |

### Subject Group

| Field | Description |
|-------|-------------|
| Subject Group Name | The EarthRanger subject group to animate. Must match the group name exactly. A group with mixed subject subtypes can give unexpected results. |

### Trajectory Segment Filter *(advanced)*

Removes GPS noise by dropping track segments whose length, duration or speed falls outside these limits. The defaults suit most terrestrial wildlife.

| Field | Default |
|-------|---------|
| Min / Max length | `0.001` m / `100 000` m |
| Min / Max time | `1` s / `172 800` s (2 days) |
| Min / Max speed | `0.01` km/h / `500` km/h |

### Terrain Exaggeration *(advanced)*

| Field | Default | Description |
|-------|---------|-------------|
| Exaggeration | `1.0` | Vertical scale of the 3D terrain. `1.0` is true scale; `2.0` doubles apparent heights, which helps on flat landscapes. |

### Terrain Sampling *(advanced)*

| Field | Default | Description |
|-------|---------|-------------|
| Offset | `30` m | Height added above the ground at every track point, so trails sit on top of the terrain rather than inside it |
| Ground Elevation | `1000` m | Constant ground height used only if elevation tiles can't be read |

### Map Zoom & Extent *(advanced)*

The map is automatically centred and zoomed to fit every track. These two fields set the viewing angle, which the video cameras also use.

| Field | Default | Description |
|-------|---------|-------------|
| Pitch | `0` | Tilt in degrees (0–90). `0` looks straight down; higher values tilt towards the horizon for a 3D view. |
| Bearing | `0` | Rotation in degrees clockwise from north (−180 to 180). `90` puts east at the top. |

### Create Animation *(advanced)*

**Marker icon** sets what is drawn at each subject's current position:

| Option | Description |
|--------|-------------|
| Dot *(default)* | A flat circle in the subject's colour with a white outline |
| 3D animal | A ready-tuned 3D model: elephant, giraffe, cheetah, leopard or lion |
| 3D model (custom) | Your own glTF/GLB model (URL or file path), with controls for size, heading and tilt |
| None | No marker; only the trails are drawn |

### Create Controls *(advanced)*

Sets which parts of the playback bar appear on the interactive map: play/pause, restart, time slider, playback clock, data time, speed button (0.5×, 1×, 2×, 4×), and whether the bar sits at the **bottom** or **top**. All are shown by default. **Time Format** shows the data time as a full date-time, a date (default), or time elapsed since the start.

### Create Timeline Animation *(advanced)*

| Field | Default | Description |
|-------|---------|-------------|
| Duration S | `30` s | How long playback takes from the first location to the last. The video uses the same length by default. |
| Auto Rotate Speed | `0` | Slowly rotates the map while it plays, in degrees per second. `0` is off; negative values rotate counter-clockwise. |

### Animation Video *(advanced)*

| Field | Default | Description |
|-------|---------|-------------|
| Camera | Static | How the video camera moves (see below) |
| Duration | Auto | **Auto** matches the animation's playback length. Uncheck it to set a fixed length in seconds. |
| Resolution | 720p | A preset (720p, 1080p, 4K) or a custom width and height in pixels |

Every camera frames whatever is animating at the video's size, using the map's pitch and bearing. **Zoom Offset** nudges the automatic framing closer (`+1` is twice as close) or further away.

| Camera | What it does |
|--------|--------------|
| Static | Holds one view that fits all the tracks for the whole clip |
| Follow the action | Frames the most recent movement and follows it smoothly. Can rotate to face the direction of travel. |
| Orbit | Circles the centre of all the tracks |
| Fit everything so far | Zooms out as needed to keep everything shown so far in frame |
| Cinematic fly-through | Opens on the whole scene, then follows the action with a slowly turning, tilted camera |
| Keyframes | Flies through waypoints: follow one subject (blank = the longest-running track), or upload a waypoint file (`.json`, `.geojson`, `.csv` or `.tsv` with lon/lat columns) |
| Fly to & around | Flies to a point (blank = the centre of the data), then circles it |

---

## 3. Run the Workflow

Click **Submit**. The workflow fetches the observations, cleans them into trajectories, drapes them on the terrain, builds the animated map, then records the video frame by frame in a headless browser.

Recording the video is usually the slowest step. The default settings give 900 frames (30 seconds at 30 fps). Higher resolutions and longer durations take proportionally longer.

---

## 4. Outputs

All files are written to the workflow's results folder (`ECOSCOPE_WORKFLOWS_RESULTS`).

| File | Description |
|------|-------------|
| `animated_map.html` | The interactive animated 3D map, also shown on the dashboard as **Subject movements** |
| `animation.mp4` | H.264 video of the animation |
| `relocations_<hash>.geoparquet` | Cleaned GPS fixes |
| `trajectories_<hash>.geoparquet` | Trajectory segments after the segment filter |

The dashboard shows the **Subject movements** map along with the workflow name, description and time range.

---

## 5. Troubleshooting

| Symptom | Likely cause |
|---------|--------------|
| No tracks appear | The subject group name doesn't match EarthRanger exactly, or the group has no fixes in the time range |
| A track is broken into disconnected pieces | The Trajectory Segment Filter is dropping segments as noise; loosen its limits if your data has long gaps or unusual speeds |
| Trails float above or sink into the terrain | Adjust **Terrain Sampling → Offset**. If you changed **Terrain Exaggeration**, the trails are re-draped to match automatically. |
| The run takes a long time | A wide time range, a large group, or a long/high-resolution video. Try 720p and a shorter duration first. |
| The 3D model doesn't appear | Check the **Marker icon** setting. For a custom model, the GLB URL or file must be reachable from the machine running the workflow. |

More in the [Troubleshooting guide](https://wildlife-dynamics.github.io/animate-subject-tracks/troubleshooting.html).
