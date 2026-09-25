"""
Generate the Animate Subject Tracks Technical Guide as a PDF using ReportLab.
Run with: python3 generate_technical_guide.py
Output: animate_subject_tracks_technical_guide.pdf
"""

import re
from datetime import date
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT_FILE = "animate_subject_tracks_technical_guide.pdf"
VERSION_FILE = (
    Path(__file__).resolve().parent.parent
    / "ecoscope-workflows-animate-tracks-workflow"
    / "VERSION.yaml"
)


def workflow_version():
    """Read MAJ.MIN.PATCH from the generated workflow's VERSION.yaml."""
    text = VERSION_FILE.read_text()
    parts = [re.search(rf"{k}:\s*(\d+)", text) for k in ("MAJ", "MIN", "PATCH")]
    return ".".join(m.group(1) if m else "0" for m in parts)


# ── Colour palette ────────────────────────────────────────────────────────────
GREEN_DARK = colors.HexColor("#115631")
GREEN_MID = colors.HexColor("#2d6a4f")
AMBER = colors.HexColor("#e7a553")
SLATE = colors.HexColor("#3d3d3d")
LIGHT_GREY = colors.HexColor("#f5f5f5")
MID_GREY = colors.HexColor("#cccccc")
WHITE = colors.white

# ── Styles ────────────────────────────────────────────────────────────────────
styles = getSampleStyleSheet()


def _style(name, parent="Normal", **kw):
    s = ParagraphStyle(name, parent=styles[parent], **kw)
    styles.add(s)
    return s


TITLE = _style(
    "DocTitle",
    fontSize=24,
    leading=30,
    textColor=GREEN_DARK,
    spaceAfter=6,
    alignment=TA_CENTER,
    fontName="Helvetica-Bold",
)
SUBTITLE = _style(
    "DocSubtitle",
    fontSize=12,
    leading=16,
    textColor=SLATE,
    spaceAfter=4,
    alignment=TA_CENTER,
)
META = _style(
    "Meta",
    fontSize=9,
    leading=13,
    textColor=colors.grey,
    alignment=TA_CENTER,
    spaceAfter=2,
)
H1 = _style(
    "H1",
    fontSize=14,
    leading=18,
    textColor=GREEN_DARK,
    spaceBefore=16,
    spaceAfter=5,
    fontName="Helvetica-Bold",
)
H2 = _style(
    "H2",
    fontSize=11,
    leading=15,
    textColor=GREEN_MID,
    spaceBefore=10,
    spaceAfter=4,
    fontName="Helvetica-Bold",
)
BODY = _style(
    "Body", fontSize=9, leading=14, textColor=SLATE, spaceAfter=5, alignment=TA_JUSTIFY
)
BULLET = _style(
    "BulletItem",
    fontSize=9,
    leading=13,
    textColor=SLATE,
    spaceAfter=2,
    leftIndent=14,
    firstLineIndent=-10,
)
CELL = _style(
    "Cell", fontSize=8.5, leading=12, textColor=SLATE, spaceAfter=0, spaceBefore=0
)
HEAD = _style(
    "HeadCell",
    fontSize=8.5,
    leading=12,
    textColor=WHITE,
    fontName="Helvetica-Bold",
    spaceAfter=0,
    spaceBefore=0,
)
NOTE = _style(
    "Note",
    fontSize=8.5,
    leading=13,
    textColor=colors.HexColor("#555555"),
    backColor=colors.HexColor("#fff8e1"),
    leftIndent=10,
    rightIndent=10,
    spaceAfter=6,
    borderPad=4,
)


def hr():
    return HRFlowable(width="100%", thickness=1, color=MID_GREY, spaceAfter=6)


def p(text, style=BODY):
    return Paragraph(text, style)


def h1(text):
    return Paragraph(text, H1)


def h2(text):
    return Paragraph(text, H2)


def sp(n=6):
    return Spacer(1, n)


def bullet(text):
    return Paragraph(f"• {text}", BULLET)


def note(text):
    return Paragraph(f"<b>Note:</b> {text}", NOTE)


def c(text):
    return Paragraph(text, CELL)


def code(text):
    return f'<font face="Courier" size="8">{text}</font>'


def make_table(data, col_widths):
    """Build a table where every cell value is already a Paragraph (use c())."""
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), GREEN_DARK),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GREY]),
                ("GRID", (0, 0), (-1, -1), 0.4, MID_GREY),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    return t


def header_row(*labels):
    return [Paragraph(label, HEAD) for label in labels]


# ── Page template ─────────────────────────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(GREEN_DARK)
    canvas.rect(0, 0, w, 22, fill=1, stroke=0)
    canvas.setFillColor(WHITE)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(1.5 * cm, 7, "Animate Subject Tracks — Technical Guide")
    canvas.drawRightString(w - 1.5 * cm, 7, f"Page {doc.page}")
    canvas.setFillColor(AMBER)
    canvas.rect(0, h - 4, w, 4, fill=1, stroke=0)
    canvas.restoreState()


# ── Build story ───────────────────────────────────────────────────────────────
def build():
    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.5 * cm,
        bottomMargin=2 * cm,
        title="Animate Subject Tracks — Technical Guide",
        author="Ecoscope",
    )

    story = []

    # ── Cover ─────────────────────────────────────────────────────────────────
    story += [
        sp(60),
        p("Animate Subject Tracks", TITLE),
        p("Technical Guide", SUBTITLE),
        sp(8),
        hr(),
        p(
            "Animated 3D Movement Maps &amp; Video — Pipeline &amp; Rendering Reference",
            META,
        ),
        p(
            f"Workflow version {workflow_version()}  ·  Generated {date.today().strftime('%B %d, %Y')}",
            META,
        ),
        hr(),
        PageBreak(),
    ]

    # ── 1. Overview ───────────────────────────────────────────────────────────
    story += [
        h1("1. Overview"),
        hr(),
        p(
            "The <b>Animate Subject Tracks</b> workflow turns the GPS history of an "
            "EarthRanger subject group into an animated, terrain-aware 3D map. Each "
            "subject's track is cleaned into trajectory segments, stitched into one "
            "timestamped path per subject, draped onto a digital elevation model, and "
            "played back on a shared clock over satellite imagery."
        ),
        p(
            "The workflow produces an interactive HTML map (deck.gl, via pydeck) with a "
            "playback bar, an MP4 video recorded frame by frame from that map in a "
            "headless browser, GeoParquet copies of the relocations and trajectories, "
            "and a single-widget dashboard."
        ),
        note(
            "The workflow has no groupers: " + code("set_groupers") + " is configured "
            "with an empty list, so every subject in the group is animated together on "
            "one map."
        ),
    ]

    # ── 2. Dependencies ───────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("2. Dependencies &amp; Prerequisites"),
        hr(),
        h2("2a. EarthRanger"),
        p(
            "Observations are pulled live from EarthRanger through the connection "
            "chosen in <b>Connect to EarthRanger</b> ("
            + code("set_er_connection")
            + "). "
            "The user supplies a subject group name; every subject in that group is "
            "included."
        ),
        h2("2b. External Tile Services"),
        p(
            "The 3D terrain and its texture are fetched at run time from public tile services:"
        ),
        make_table(
            [
                header_row("Service", "URL template", "Used for"),
                [
                    c("AWS Terrarium elevation"),
                    c(
                        code(
                            "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
                        )
                    ),
                    c("Terrain mesh and sampling ground height for draping"),
                ],
                [
                    c("Esri World Imagery"),
                    c(
                        code(
                            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
                        )
                    ),
                    c("Satellite texture draped on the terrain mesh"),
                ],
            ],
            [3.6 * cm, 8.4 * cm, 5 * cm],
        ),
        sp(4),
        p(
            "Both are needed by the interactive map and by the video renderer, so the "
            "machine running the workflow (and anyone viewing the HTML map) needs "
            "internet access."
        ),
        h2("2c. Headless Browser"),
        p(
            "Video rendering uses Playwright's Chromium. The first time "
            + code("render_animation")
            + " runs in an environment it runs "
            + code("playwright install chromium")
            + ", which downloads the browser. "
            "Encoding uses the ffmpeg binary bundled with "
            + code("imageio-ffmpeg")
            + "."
        ),
    ]

    # ── 3. Data Ingestion ─────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("3. Data Ingestion Pipeline"),
        hr(),
        make_table(
            [
                header_row("Step (task id)", "Task", "What it does"),
                [
                    c(code("subject_observations")),
                    c(code("get_subjectgroup_observations")),
                    c(
                        "Fetches observations for the subject group over the time range, with "
                        + code("filter: clean")
                        + " (only fixes with exclusion flag 0), "
                        "observation details and subject-source details. "
                        + code("raise_on_empty: false")
                        + " returns an empty frame instead of "
                        "failing."
                    ),
                ],
                [
                    c(code("subject_reloc")),
                    c(code("process_relocations")),
                    c(
                        "Converts observations to relocations, keeps the subject name, colour, "
                        "sex, subtype and source columns, and drops fixes at the known junk "
                        "coordinates (180, 90), (0, 0) and (1, 1)."
                    ),
                ],
                [
                    c(code("convert_to_trajs")),
                    c(code("relocations_to_trajectory")),
                    c(
                        "Builds trajectory segments between consecutive fixes and applies the "
                        "user's <b>Trajectory Segment Filter</b>."
                    ),
                ],
                [
                    c(code("rename_traj_cols")),
                    c(code("map_columns")),
                    c(
                        "Renames "
                        + code("extra__hex")
                        + " → "
                        + code("hex_color")
                        + ", "
                        + code("extra__name")
                        + " → "
                        + code("subject_name")
                        + ", and the sex, "
                        "subtype and created-at columns. Missing columns are ignored."
                    ),
                ],
                [
                    c(code("persist_relocs_geoparquet")),
                    c(code("persist_df_wrapper")),
                    c(
                        "Writes relocations to "
                        + code("relocations_&lt;hash&gt;.geoparquet")
                        + ", "
                        "sanitising nested objects for Arrow."
                    ),
                ],
                [
                    c(code("persist_trajs_geoparquet")),
                    c(code("persist_df_wrapper")),
                    c(
                        "Writes trajectories to "
                        + code("trajectories_&lt;hash&gt;.geoparquet")
                        + "."
                    ),
                ],
            ],
            [5.1 * cm, 4.8 * cm, 7.1 * cm],
        ),
        sp(4),
        h2("3a. Trajectory Segment Filter Defaults"),
        make_table(
            [
                header_row("Limit", "Minimum", "Maximum"),
                [c("Segment length"), c("0.001 m"), c("100 000 m")],
                [c("Segment duration"), c("1 s"), c("172 800 s (2 days)")],
                [c("Segment speed"), c("0.01 km/h"), c("500 km/h")],
            ],
            [5 * cm, 5 * cm, 7 * cm],
        ),
    ]

    # ── 4. Terrain ────────────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("4. Terrain"),
        hr(),
        h2("4a. Elevation Decoder &amp; Exaggeration"),
        p(
            code("create_elevation_decoder")
            + " builds the RGB-to-elevation decoder for "
            "Terrarium tiles ("
            + code("r_scaler 256")
            + ", "
            + code("g_scaler 1.0")
            + ", "
            + code("b_scaler 1/256")
            + ", "
            + code("offset -32768")
            + "). deck.gl's "
            "TerrainLayer has no elevation-scale property, so <b>Exaggeration</b> is "
            "applied by multiplying every decoder term. The same decoder feeds both the "
            "terrain mesh and the track sampling, so the tracks always sit on the "
            "exaggerated surface."
        ),
        h2("4b. Terrain Layer"),
        p(
            code("create_terrain_layer") + " defines the 3D terrain mesh from the "
            "Terrarium tiles with the Esri World Imagery texture, zoom range 0–15 and "
            "wireframe off."
        ),
        h2("4c. Draping Tracks on Terrain"),
        p(
            code("create_terrain_sampling") + " configures elevation sampling with the "
            "user's <b>Offset</b> (default 30 m) and <b>Ground Elevation</b> fallback "
            "(default 1000 m). " + code("drape_trips_on_terrain") + " then sets the z "
            "value of every track vertex to the sampled ground height plus the offset. "
            "All vertices are sampled in one batched call, so each elevation tile is "
            "fetched once. If sampling fails, every vertex uses the constant ground "
            "elevation."
        ),
        note(
            code("custom_basemap_urls")
            + " ("
            + code("set_basemap_urls")
            + ") and "
            + code("basemap_option")
            + " ("
            + code("set_basemap_option")
            + ") are "
            "evaluated but not consumed by any later step: the terrain layer and "
            "sampling take their tile URLs directly."
        ),
    ]

    # ── 5. Animation Data ─────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("5. Animation Data"),
        hr(),
        make_table(
            [
                header_row("Step (task id)", "Task", "What it does"),
                [
                    c(code("ensure_wgs")),
                    c(code("convert_crs")),
                    c("Reprojects trajectories to EPSG:4326."),
                ],
                [
                    c(code("trajs_trips")),
                    c(code("trajectory_to_trips")),
                    c(
                        "Stitches each subject's segments (grouped by "
                        + code("groupby_col")
                        + ") into one lon/lat LineString with per-vertex timestamps, keeping "
                        + code("subject_name")
                        + " and "
                        + code("hex_color")
                        + "."
                    ),
                ],
                [
                    c(code("drape_terrain")),
                    c(code("drape_trips_on_terrain")),
                    c("Adds terrain heights to every vertex (section 4c)."),
                ],
                [
                    c(code("rgba_hex")),
                    c(code("add_rgba_from_hex")),
                    c(
                        "Converts each subject's EarthRanger hex colour to an RGBA "
                        + code("rgba_color")
                        + " column for the trail and legend."
                    ),
                ],
                [
                    c(code("zoom_to_envelope")),
                    c(code("envelope_gdf")),
                    c(
                        "Takes the bounding envelope of all trips (expansion factor 1.0)."
                    ),
                ],
                [
                    c(code("trips_view_state")),
                    c(code("compute_view_state_from_gdf")),
                    c(
                        "Computes the centre and zoom that fit the envelope (max zoom 15), "
                        "plus the user's <b>Pitch</b> and <b>Bearing</b>."
                    ),
                ],
            ],
            [3.4 * cm, 5.2 * cm, 8.4 * cm],
        ),
    ]

    # ── 6. Animated Map ───────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("6. Animated Map"),
        hr(),
        h2("6a. Trips Animation"),
        p(
            code("create_trips_animation") + " defines how each track plays back. Each "
            "subject shows a bright comet tail in its own colour covering 95% of the "
            "timeline (" + code("comet_ratio 0.95") + "), over a white history line of "
            "the whole path travelled so far (opacity 0.85, fading). The user picks the "
            "<b>Marker icon</b> drawn at each subject's current position:"
        ),
        make_table(
            [
                header_row("Marker", "Rendering"),
                [
                    c("Dot (default)"),
                    c(
                        "ScatterplotLayer circle, 6 px radius, track colour, 1.5 px white outline"
                    ),
                ],
                [
                    c("3D animal"),
                    c(
                        "Preset ScenegraphLayer model: elephant, giraffe, cheetah, leopard or lion; size and lighting adjustable"
                    ),
                ],
                [
                    c("3D model (custom)"),
                    c(
                        "ScenegraphLayer from a user GLB (URL, data URI or path). Faces the direction of travel, "
                        "with heading smoothing, optional terrain-slope pitch and size clamps (12–75 px by default)"
                    ),
                ],
                [c("None"), c("Trails only")],
            ],
            [3.4 * cm, 13.6 * cm],
        ),
        h2("6b. Trips Layer"),
        p(
            code("create_trips_layer") + " draws the draped trips as a deck.gl "
            "TripsLayer: "
            + code("timestamps")
            + " as the time accessor, "
            + code("rgba_color")
            + " as the colour, 2.15 px width (clamped to 1–4 px), "
            "rounded caps and joints. The legend is titled <b>Subjects</b>, labelled by "
            + code("subject_name")
            + " and sorted ascending. "
            + code("animate_layer")
            + " attaches the trips animation to this layer."
        ),
        h2("6c. Playback Controls &amp; Timeline"),
        p(
            code("create_playback_controls") + " configures the playback bar (play, "
            "restart, scrubber, clock, data time, speed button cycling 0.5×/1×/2×/4×, "
            "bottom or top). "
            + code("create_timeline_animation")
            + " builds the shared "
            "clock: playback length <b>Duration S</b> (default 30 s), a 30 fps cap for "
            "the interactive map, and optional <b>Auto Rotate Speed</b>."
        ),
        h2("6d. Drawing &amp; Saving"),
        p(
            code("draw_animated_map")
            + " combines the animated trips layer, the terrain "
            "tile layer, the view state and the timeline into a static HTML page (max "
            "zoom 15, legend bottom-right). Every animated layer is rebased onto a common "
            "timeline starting at its earliest timestamp, so all subjects stay in step. "
            "Each layer gets a stable deck.gl id that the page's animation script uses to "
            "find it. "
            + code("persist_text")
            + " writes the page to "
            + code("animated_map.html")
            + "."
        ),
    ]

    # ── 7. Video Rendering ────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("7. Video Rendering"),
        hr(),
        p(
            code("render_animation")
            + " records "
            + code("animated_map.html")
            + " to "
            + code("animation.mp4")
            + ":"
        ),
        bullet(
            "Launches headless Chromium with ANGLE WebGL (GPU when available; SwiftShader software rendering when "
            + code("gl: software")
            + ")."
        ),
        bullet(
            "Reads the timeline span and the animation's natural length. With <b>Duration</b> on Auto the video "
            "matches <b>Duration S</b>; otherwise it uses the fixed seconds. Frames = fps × seconds (30 fps; "
            "900 frames by default)."
        ),
        bullet(
            "Computes the whole per-frame camera path in the page from the chosen <b>Camera</b>, fitted to the "
            "video size and the map's pitch and bearing."
        ),
        bullet(
            "Splits frames into contiguous chunks across parallel browser pages. "
            + code("workers: auto")
            + " uses half the CPU cores, capped by GPU sharing, free memory and frame count."
        ),
        bullet(
            "For each frame: sets the view state, renders the animation at that time, waits two animation "
            "frames plus any pending tile requests (up to 8 s, then 30 ms settle), and screenshots the map canvas."
        ),
        bullet(
            "Encodes the numbered frames with ffmpeg: libx264, CRF 18, "
            + code("veryfast")
            + " preset, "
            "yuv420p, dimensions rounded to even numbers, "
            + code("+faststart")
            + " for web playback."
        ),
        sp(4),
        h2("7a. Camera Options"),
        make_table(
            [
                header_row("Camera", "Behaviour", "Main settings"),
                [
                    c("Static"),
                    c("One view fitting all animated data"),
                    c("Zoom Offset"),
                ],
                [
                    c("Follow the action"),
                    c("Frames recent movement and re-fits smoothly"),
                    c(
                        "Follow Window 0.1, Follow Smoothing 0.25, Heading Lock, Fit Padding 80 px"
                    ),
                ],
                [c("Orbit"), c("Circles the centre of the data"), c("Rounds 1.0")],
                [
                    c("Fit everything so far"),
                    c("Zooms to keep all data shown so far in frame"),
                    c("Fit Padding 80 px"),
                ],
                [
                    c("Cinematic fly-through"),
                    c("Intro from the whole scene, then a turning, tilted follow"),
                    c(
                        "Intro Frac 0.12, Lead Frac 0, Bearing Mode rotate/heading/fixed, Rotate Deg 45"
                    ),
                ],
                [
                    c("Keyframes"),
                    c(
                        "Flies through waypoints; inline, from a subject, or from a file"
                    ),
                    c("Source (subject / file), Keyframe Easing smooth/linear/spline"),
                ],
                [
                    c("Fly to &amp; around"),
                    c("Flies to a point, then circles it"),
                    c(
                        "Lon/Lat, Altitude, Range, Tilt, Heading (blank = from data or map), Fly Frac 0.25, Rounds 1.0"
                    ),
                ],
            ],
            [3.4 * cm, 5.8 * cm, 7.8 * cm],
        ),
        sp(4),
        p(
            "Keyframe files may be a "
            + code(".json")
            + " list of {lon, lat, t?, zoom?, pitch?, bearing?} "
            "objects, a "
            + code(".geojson")
            + " of Point features (extras read from properties), or a "
            + code(".csv")
            + "/"
            + code(".tsv")
            + " with lon/lat columns. At least two keyframes are needed. "
            "Missing zoom, pitch or bearing values are interpolated between neighbouring keyframes, or fall "
            "back to the whole-scene framing and the map's pitch and bearing."
        ),
        h2("7b. Fixed Encoding Settings"),
        make_table(
            [
                header_row("Setting", "Value"),
                [c("Frame rate"), c("30 fps")],
                [c("Clip range"), c("Whole timeline (start_frac 0, end_frac 1)")],
                [c("Frame capture"), c("JPEG, quality 92, device scale factor 1")],
                [c("Encoder"), c("libx264, CRF 18, preset veryfast")],
                [
                    c("Capture timing"),
                    c(
                        "settle 30 ms, tile timeout 8 000 ms, 3D-model load timeout 30 000 ms"
                    ),
                ],
            ],
            [5 * cm, 12 * cm],
        ),
    ]

    # ── 8. Dashboard ──────────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("8. Interactive Dashboard"),
        hr(),
        p(
            code("create_map_widget_single_view")
            + " wraps "
            + code("animated_map.html")
            + " as the <b>Subject movements</b> widget. "
            + code("gather_dashboard")
            + " assembles it with the workflow details, time range and (empty) groupers. "
            "The video is not a dashboard widget; it is written to the results folder."
        ),
    ]

    # ── 9. Output Files ───────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("9. Output Files"),
        hr(),
        p("All outputs are written to " + code("ECOSCOPE_WORKFLOWS_RESULTS") + "."),
        make_table(
            [
                header_row("File", "Written by", "Contents"),
                [
                    c(code("relocations_&lt;hash&gt;.geoparquet")),
                    c(code("persist_relocs_geoparquet")),
                    c("Cleaned GPS fixes"),
                ],
                [
                    c(code("trajectories_&lt;hash&gt;.geoparquet")),
                    c(code("persist_trajs_geoparquet")),
                    c("Filtered trajectory segments with renamed columns"),
                ],
                [
                    c(code("animated_map.html")),
                    c(code("map_urls")),
                    c("Interactive animated 3D map"),
                ],
                [
                    c(code("animation.mp4")),
                    c(code("create_animation")),
                    c("H.264 video of the animation"),
                ],
            ],
            [6 * cm, 4.6 * cm, 6.4 * cm],
        ),
    ]

    # ── 10. Execution Logic ───────────────────────────────────────────────────
    story += [
        sp(4),
        h1("10. Workflow Execution Logic"),
        hr(),
        h2("10a. Skip Conditions"),
        make_table(
            [
                header_row("Scope", "Conditions", "Effect"),
                [
                    c("Default (all tasks)"),
                    c(code("any_is_empty_df") + ", " + code("any_dependency_skipped")),
                    c(
                        "A task is skipped if any input dataframe is empty or any upstream task was skipped. An empty "
                        "EarthRanger result therefore skips the whole chain rather than raising an error."
                    ),
                ],
                [
                    c(code("create_animation")),
                    c(code("any_dependency_skipped")),
                    c(
                        "Its input is a file path, not a dataframe, so only the upstream-skip check applies."
                    ),
                ],
                [
                    c(code("animated_map_widget")),
                    c(code("never")),
                    c("Always runs, so the dashboard always has its map widget."),
                ],
            ],
            [3.8 * cm, 4.8 * cm, 8.4 * cm],
        ),
        h2("10b. Data Flow Summary"),
        make_table(
            [
                header_row("Stage", "Flow"),
                [
                    c("Ingestion"),
                    c(
                        "Observations → relocations → trajectories → renamed columns → GeoParquet"
                    ),
                ],
                [
                    c("Terrain"),
                    c("Elevation decoder → terrain layer + terrain sampling"),
                ],
                [
                    c("Animation data"),
                    c(
                        "EPSG:4326 → trips per subject → draped on terrain → RGBA colours"
                    ),
                ],
                [c("Framing"), c("Trips envelope → view state (+ pitch, bearing)")],
                [
                    c("Map"),
                    c(
                        "Trips animation + trips layer → animated layer; controls → timeline; all → draw_animated_map → HTML"
                    ),
                ],
                [c("Video"), c("HTML → headless Chromium frames → ffmpeg → MP4")],
                [c("Dashboard"), c("HTML → map widget → gather_dashboard")],
            ],
            [3.6 * cm, 13.4 * cm],
        ),
    ]

    # ── 11. Software Versions ─────────────────────────────────────────────────
    story += [
        sp(4),
        h1("11. Software Versions"),
        hr(),
        make_table(
            [
                header_row("Package", "Version", "Role"),
                [
                    c("ecoscope-platform"),
                    c("&gt;=2.15.0, &lt;2.16.0"),
                    c(
                        "Core runtime and tasks (EarthRanger I/O, preprocessing, CRS, persistence, dashboard)"
                    ),
                ],
                [
                    c("ecoscope-workflows-ext-custom"),
                    c("0.1.0rc14.*"),
                    c("Map layer definitions and " + code("persist_df_wrapper")),
                ],
                [
                    c("ecoscope-workflows-ext-ste"),
                    c("0.0.0rc1.*"),
                    c("Envelope, view state and hex-to-RGBA tasks"),
                ],
                [
                    c("ecoscope-workflows-ext-mep"),
                    c("1.0.4.*"),
                    c("Terrain, trips, animated map and video rendering tasks"),
                ],
                [c("pydeck"), c("0.9.2"), c("deck.gl map generation")],
                [c("opentelemetry-sdk"), c("&gt;=1.20.0, &lt;2.0.0"), c("Tracing")],
                [
                    c("wt-compiler"),
                    c("&gt;=0.8.2, &lt;0.9"),
                    c("Compiles " + code("spec.yaml") + " (development only)"),
                ],
            ],
            [5.2 * cm, 3.2 * cm, 8.6 * cm],
        ),
        sp(4),
        p(
            "Packages are distributed via the <b>prefix.dev</b> conda channels and "
            "conda-forge. The runtime environment is managed by <b>pixi</b>."
        ),
    ]

    # ── Build ─────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
    print(f"PDF written → {OUTPUT_FILE}")


if __name__ == "__main__":
    build()
