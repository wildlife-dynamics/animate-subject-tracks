# Animate Subject Tracks — User Guide

This workflow turns an EarthRanger subject group's GPS history into an animated
3-D map: colored trails that sweep across real terrain as time passes, with an
optional exportable video. It's built and run through the **Ecoscope Workflows**
platform — no coding required to use it.

---

## 1. What this workflow does

For a subject group you choose (e.g. "Elephants"), the workflow:

1. Connects to your EarthRanger site and pulls location fixes for every
   subject in the group over a time range you set.
2. Cleans the data and converts it into movement trajectories.
3. Renders those trajectories as an animated, terrain-aware 3-D map — each
   subject gets its own colored trail with a moving "head" marker.
4. Optionally renders that animation to a downloadable `.mp4` video.
5. Packages everything into a dashboard you can view, share, or revisit later.

## 2. Before you start

You'll need:

- Access to the **Ecoscope Workflows** platform.
- An **EarthRanger connection** already configured on the platform (ask your
  Ecoscope admin if you don't see one in the dropdown).
- The exact **subject group name** as it appears in EarthRanger (e.g.
  `Elephants`) — subject groups are managed in EarthRanger, not in this
  workflow.
- A rough idea of the **date range** you want to animate. Longer ranges take
  longer to fetch and render.

## 3. Running the workflow

1. Open the Ecoscope Workflows platform and select **Animate Subject Tracks**
   from the workflow catalog.
2. Fill in the form (see field-by-field guide below).
3. Click **Run**.
4. Wait for the run to complete — you'll see a status indicator while the
   workflow fetches data and renders the map. Enabling video export adds
   noticeably more time, since the animation is re-rendered frame-by-frame.
5. Open the resulting **dashboard** to view your animated map (and video, if
   you enabled it).

## 4. Filling in the form

The form is organized into sections, top to bottom. Most fields have sensible
defaults — the only things you truly need to set are the **data source**,
**time range**, and **subject group name**. Everything under an "Advanced" /
optional section is safe to leave alone on your first run.

### Set workflow details
| Field | Required? | Notes |
|---|---|---|
| **Workflow Name** | Yes | A label for this run, e.g. `Elephants – July 2026`. Helps you find it again later in your run history. |
| **Workflow Description** | No | Free-text notes about this run. |

### Connect to EarthRanger
| Field | Required? | Notes |
|---|---|---|
| **Data Source** | Yes | Choose the EarthRanger site/connection to pull data from. |

### Define analysis time range
| Field | Required? | Notes |
|---|---|---|
| **Since** | Yes | Start of the period to animate. |
| **Until** | Yes | End of the period to animate. |
| **Timezone** | No | Interpret Since/Until in a specific timezone. |
| **Time Format** *(advanced)* | No | Only affects how times are displayed elsewhere in the dashboard. |

> **Tip:** the wider the range, the more GPS fixes get pulled and animated —
> which means a longer run and a longer video. For a first try, a window of a
> few days to a couple of weeks is a good size.

### Subject Group
| Field | Required? | Notes |
|---|---|---|
| **Subject Group Name** | Yes (default: `Elephants`) | Must exactly match a subject group name configured in EarthRanger. This determines which subjects' tracks get animated. |

### Convert relocations to trajectories *(advanced, optional)*
A **Trajectory Segment Filter** removes GPS noise by discarding movement
segments that are too short, too long, too fast, or too slow to be real
animal movement (e.g. a GPS glitch that implies teleporting 100 km in one
second). The defaults work well for most terrestrial wildlife — you generally
don't need to touch this unless you're animating a species with very
unusual movement patterns (e.g. birds).

### Configure terrain elevation decoder *(advanced, optional)*
- **Exaggeration** — stretches terrain height for visual effect. `1.0` is
  true-to-scale; `2.0` doubles apparent elevation, useful for making subtle
  hills/valleys more visible on flat landscapes.

### Calculate map view bounds *(advanced, optional)*
- **Pitch** — camera tilt, `0` (top-down, default) to `90` (looking at the
  horizon).
- **Bearing** — compass rotation of the map, `-180` to `180`, `0` = north up.

### Configure animation settings *(advanced, optional)*
- **Animation Speed** — how fast simulated time passes per real second of
  playback. Higher = faster playback.
- **Head Radius** / **Head Outline Width** — size and outline thickness of
  the moving dot that marks each subject's current position.

### Draw animated map *(advanced, optional)*
- **Head Layer** — swaps the flat colored dot for a 3-D animal model (a
  bundled elephant model by default) that rotates to face its direction of
  travel. Off by default. Turn on **Enabled** to use it; the other fields
  here (size, model orientation, etc.) fine-tune how that 3-D model looks and
  behaves and can be left at their defaults.

### Video Creation *(optional — off by default)*
Turn this on to also render the animation as a downloadable `.mp4`, in
addition to the interactive map.

| Field | Notes |
|---|---|
| **Enabled** | Turns video rendering on. Leave off if you only want the interactive map (faster run). |
| **Camera** | How the video's camera moves. Choose one: |

- **Static** — camera holds one fixed view for the whole video.
- **Fit** — camera zooms out just enough to keep every point visited so far in frame.
- **Follow** — camera tracks a subject (or the group) from directly above.
- **Follow 3D** — like Follow, but tilted for a 3-D chase-cam feel, rotating to match the subject's heading.
- **Orbit** — camera circles slowly around the center of all the tracks.
- **Cinematic** — a smooth fly-through that leads the subject and banks with its turns.
- **Keyframes** — camera flies through a custom path, either auto-derived by following a chosen subject or built from an uploaded waypoint file.

## 5. Understanding your results

When the run finishes, open the dashboard. You'll see:

- **Subject movements** — the interactive animated 3-D map. Use the built-in
  playback controls to play, pause, and scrub through the time range. Each
  subject appears as its own colored trail with a legend on the map listing
  subject names and colors.
- **Video download** *(only if Video Creation was enabled)* — an `.mp4` file
  of the same animation, suitable for sharing or presentations.

The dashboard also records the workflow name/description, the time range,
and the subject group you selected, so you (or a colleague) can tell at a
glance what a given run covers.

## 6. Troubleshooting

| Symptom | Likely cause |
|---|---|
| The map is empty / no trails appear | The subject group name doesn't match EarthRanger exactly, or there are no location fixes for that group in the chosen time range. |
| Run takes a long time | The time range is very wide, the subject group is large, or Video Creation is enabled — all three multiply how much data is fetched and rendered. |
| A subject's trail looks broken into short disconnected pieces | The Trajectory Segment Filter (advanced) may be discarding segments as noise. Only adjust this if you understand your data's typical fix intervals and speeds. |
| The 3-D animal model doesn't appear | The **Head Layer** toggle under "Draw animated map" is off by default — enable it to render 3-D models instead of flat dots. |