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
            "played back on a shared clock over a basemap the user chooses (satellite "
            "imagery by default)."
        ),
        p(
            "The workflow produces an interactive HTML map (deck.gl, via pydeck) with a "
            "playback bar and a Camera panel, GeoParquet copies of the relocations and "
            "trajectories, and a dashboard with the map and a Files section. A single "
            "<b>Camera</b> step sets the camera that the interactive map previews while "
            "playing and that the video follows. The workflow can optionally record an "
            "MP4 video frame by frame from that map in a headless browser; video export "
            "is off by default."
        ),
        note(
            "The workflow has no groupers: " + code("set_groupers") + " is configured "
            "with an empty list, so every subject in the group is animated together on "
            "one map."
        ),
        h2("1a. Task Order"),
        p(
            "The tasks run in the order below (task ids in the left column). Tasks in a "
            "task group appear on the configuration form under the group's title; "
            "fixed values set in the spec are not on the form."
        ),
        make_table(
            [
                header_row("Form section", "Task ids, in spec order"),
                [
                    c("Setup"),
                    c(
                        code("workflow_details") + ", " + code("er_client_name") + ", "
                        + code("time_range") + ", " + code("groupers")
                    ),
                ],
                [
                    c("Data ingestion"),
                    c(
                        code("subject_observations") + ", " + code("subject_reloc") + ", "
                        + code("convert_to_trajs") + ", " + code("rename_traj_cols") + ", "
                        + code("persist_relocs_geoparquet") + ", "
                        + code("persist_trajs_geoparquet")
                    ),
                ],
                [
                    c("Terrain (task group)"),
                    c(
                        code("terrain_exaggeration") + ", " + code("terrain_sampling")
                        + ", " + code("terrain_layer")
                    ),
                ],
                [
                    c("Animation data"),
                    c(
                        code("ensure_wgs") + ", " + code("trajs_trips") + ", "
                        + code("drape_terrain")
                    ),
                ],
                [
                    c("Map Zoom &amp; Extent (task group)"),
                    c(code("zoom_to_envelope") + ", " + code("trips_view_state")),
                ],
                [c("Colours"), c(code("rgba_hex"))],
                [
                    c("Animation (task group)"),
                    c(
                        code("trips_animation") + ", " + code("create_controls") + ", "
                        + code("timeline_animation") + ", " + code("video_camera")
                    ),
                ],
                [
                    c("Map"),
                    c(
                        code("trips_layer") + ", " + code("animate_trips") + ", "
                        + code("draw_animation") + ", " + code("map_urls")
                    ),
                ],
                [
                    c("Video Export (task group)"),
                    c(code("export_video_toggle") + ", " + code("create_animation")),
                ],
                [
                    c("Dashboard"),
                    c(
                        code("animated_map_widget") + ", " + code("map_files") + ", "
                        + code("video_files") + ", " + code("animate_dashboard")
                    ),
                ],
            ],
            [4.6 * cm, 12.4 * cm],
        ),
        sp(4),
        note(
            "The earlier <b>Configure Basemap URLs</b> ("
            + code("custom_basemap_urls")
            + ") and <b>Configure basemap</b> ("
            + code("basemap_option")
            + ") steps have been removed. The basemap is now chosen on the Terrain "
            "group's <b>Basemap</b> step (section 4b)."
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
            "The user picks a <b>Subject Group Name</b> from a drop-down of the chosen "
            "data source's subject groups; every subject in that group is included. "
            "A group with mixed subtypes can give unexpected results."
        ),
        h2("2b. External Tile Services &amp; Map Widgets"),
        p(
            "The 3D terrain, its texture and the map's widgets are fetched at run time "
            "from public services:"
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
                    c("Esri basemap (user's choice)"),
                    c(
                        code(
                            "https://server.arcgisonline.com/ArcGIS/rest/services/&lt;service&gt;/MapServer/tile/{z}/{y}/{x}"
                        )
                    ),
                    c(
                        "Texture draped on the terrain mesh. One of the four basemaps in section 4b; "
                        "World Imagery (Satellite) by default"
                    ),
                ],
                [
                    c("Esri World Boundaries and Places"),
                    c("Esri tile service (same tile scheme)"),
                    c("Optional place names, draped on the terrain (<b>Place names</b>, off by default)"),
                ],
                [
                    c("my-deck-widgets (jsDelivr)"),
                    c(
                        code(
                            "https://cdn.jsdelivr.net/gh/ttemu34/my-deck-widgets@v0.21.0/dist/bundle.js"
                        )
                    ),
                    c(
                        "The map's widgets: playback bar, Camera panel, legend, north arrow, "
                        "scale bar. Loaded by ecoscope-workflows-ext-mep"
                    ),
                ],
            ],
            [3.6 * cm, 8.4 * cm, 5 * cm],
        ),
        sp(4),
        p(
            "All are needed by the interactive map and, when enabled, by the video "
            "renderer, so the machine running the workflow (and anyone viewing the HTML "
            "map) needs internet access."
        ),
        h2("2c. Headless Browser"),
        p(
            "Video rendering, which only runs when <b>Export video</b> is on (section 7), "
            "uses Playwright's Chromium. The renderer uses a Chromium bundled in the "
            "environment when there is one; if the browser executable is missing it "
            "runs "
            + code("playwright install chromium")
            + " once and retries. "
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
        p(
            "On the configuration form, " + code("terrain_exaggeration") + ", "
            + code("terrain_sampling") + " and " + code("terrain_layer")
            + " are grouped in a single <b>Terrain</b> task group, shown as the "
            "<b>Terrain Exaggeration</b>, <b>Terrain Sampling</b> and <b>Basemap</b> "
            "sub-sections."
        ),
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
            "TerrainLayer has no elevation-scale property, so <b>Exaggeration</b> "
            "(default 1.0; 2.0 doubles heights) is "
            "applied by multiplying every decoder term. The same decoder feeds both the "
            "terrain mesh and the track sampling, so the tracks always sit on the "
            "exaggerated surface."
        ),
        h2("4b. Terrain Layer &amp; Basemap"),
        p(
            code("create_terrain_layer") + " defines the 3D terrain mesh from the "
            "Terrarium tiles, zoom range 0–15 and wireframe off. Its "
            + code("texture")
            + " is left open on the form as the <b>Basemap</b> field. The spec's "
            + code("rjsf-overrides")
            + " turn it into a drop-down (a "
            + code("oneOf")
            + " list) of four Esri tile services, so users choose by name rather than "
            "typing a URL. The video renderer records the same page, so it uses the "
            "same basemap."
        ),
        make_table(
            [
                header_row("Option", "Esri service", "Notes"),
                [c("Satellite"), c(code("World_Imagery")), c("Default")],
                [c("Terrain"), c(code("World_Topo_Map")), c("Topographic map with contours and labels")],
                [c("Roadmap"), c(code("World_Street_Map")), c("Street map")],
                [
                    c("USGS Hillshade"),
                    c(code("Elevation/World_Hillshade")),
                    c("Grey shaded relief"),
                ],
            ],
            [3.4 * cm, 5.6 * cm, 8 * cm],
        ),
        sp(4),
        p(
            "<b>Place names</b> (off by default) adds the Esri World Boundaries and "
            "Places layer over the chosen basemap, draped on the terrain like the "
            "imagery. The spec also fixes the following values, which are not on the form:"
        ),
        make_table(
            [
                header_row("Setting", "Value"),
                [
                    c("Imagery detail"),
                    c(
                        code("imagery_max_zoom 18")
                        + ": imagery is draped at up to zoom 18 (about 0.6 m a pixel) over the "
                        "zoom-15 terrain. Where the basemap has nothing that deep, the "
                        "terrain's own imagery shows"
                    ),
                ],
                [
                    c("Imagery look"),
                    c(
                        code("natural")
                        + ": slightly lifted contrast and colour, a little warmer. Applies to "
                        "the ground only; tracks and markers keep their legend colours"
                    ),
                ],
                [
                    c("Vignette"),
                    c(code("0.25") + ": soft dark edges on the map and in the video"),
                ],
                [
                    c("Terrain detail"),
                    c(
                        code("mesh_max_error 1")
                        + ": the 3D terrain may stray up to 1 m from the elevation data"
                    ),
                ],
            ],
            [3.4 * cm, 13.6 * cm],
        ),
        h2("4c. Draping Tracks on Terrain"),
        p(
            code("create_terrain_sampling") + " configures how track heights are set; "
            + code("drape_trips_on_terrain") + " then applies it, setting the z "
            "value of every track vertex. The user picks a <b>Track height</b> using "
            "the Google Maps 3D altitude modes. Each mode shows only its own field:"
        ),
        make_table(
            [
                header_row("Track height", "Mode", "Field and effect"),
                [
                    c("On the ground"),
                    c(code("CLAMP_TO_GROUND")),
                    c("No field. Tracks follow the terrain; recorded altitudes are ignored."),
                ],
                [
                    c("Above the ground (default)"),
                    c(code("RELATIVE_TO_GROUND")),
                    c(
                        "<b>Height (m)</b>, default 30: sampled ground height plus the height."
                    ),
                ],
                [
                    c("Recorded altitude (where available)"),
                    c(code("ABSOLUTE")),
                    c(
                        "<b>Height without an altitude (m)</b>, default 30: each fix's own "
                        "altitude is used. Fixes with none (usual for EarthRanger data) are "
                        "drawn that height above the ground, not at sea level."
                    ),
                ],
                [
                    c("Above the 3D terrain"),
                    c(code("RELATIVE_TO_MESH")),
                    c(
                        "<b>Height (m)</b>, default 30: tracks, markers and labels are drawn "
                        "that height above the terrain as rendered, so they stay on the "
                        "surface at every zoom."
                    ),
                ],
            ],
            [4.2 * cm, 4 * cm, 8.8 * cm],
        ),
        sp(4),
        p(
            "The spec sets " + code("densify_m: 150") + ", which is not on the form: "
            "before heights are set, every track gets a point every 150 m, with "
            "timestamps interpolated, so lines follow the terrain between fixes instead "
            "of cutting through hills. Steps across data gaps are left alone. If the "
            "total would be too large, the spacing widens automatically. All vertices "
            "are sampled in one batched call, so each elevation tile is fetched once. "
            "If the elevation tiles cannot be read, every vertex uses a constant "
            "1000 m ground (an internal fallback, not on the form)."
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
                        + ". Breaks of 12 hours or more split a track, and pieces with fewer "
                        "than 5 fixes are dropped."
                    ),
                ],
                [
                    c(code("drape_terrain")),
                    c(code("drape_trips_on_terrain")),
                    c("Densifies tracks and sets terrain heights on every vertex (section 4c)."),
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
                        "plus the user's <b>Pitch</b> (default 45°, 0–90) and <b>Bearing</b> "
                        "(default 0°, −180 to 180). The map opens framed on all tracks, and "
                        "the video cameras use this tilt and heading too."
                    ),
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
            ],
            [3.4 * cm, 5.2 * cm, 8.4 * cm],
        ),
    ]

    # ── 6. Animated Map ───────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("6. Animated Map"),
        hr(),
        p(
            "On the configuration form, " + code("trips_animation") + ", "
            + code("create_controls") + ", " + code("timeline_animation")
            + " and " + code("video_camera")
            + " are grouped in a single <b>Animation</b> task group, shown as the "
            "<b>Create Animation</b>, <b>Playback Control</b>, <b>Playback Length "
            "&amp; Smoothness</b> and <b>Camera</b> sub-sections."
        ),
        h2("6a. Trips Animation"),
        p(
            code("create_trips_animation") + " defines how each track plays back. Each "
            "subject shows a bright comet tail in its own colour covering 95% of the "
            "timeline (" + code("comet_ratio 0.95") + "), over a faded white history line of "
            "the whole path travelled so far (opacity 0.85). Turns are smoothed, and "
            "there is no hover tooltip and no marker label. The user picks the "
            "<b>Marker icon</b> drawn at each subject's current position, either a dot "
            "or a 3D animal:"
        ),
        make_table(
            [
                header_row("Marker", "Rendering"),
                [
                    c("Dot (default)"),
                    c(
                        "ScatterplotLayer circle, 4 px radius, subject colour, 1.5 px white outline"
                    ),
                ],
                [
                    c("3D animal"),
                    c(
                        "Preset ScenegraphLayer model: elephant, giraffe, cheetah, leopard or lion. "
                        "<b>Size</b>, <b>Use subject color</b> and <b>Realistic lighting</b> are adjustable"
                    ),
                ],
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
            code("create_playback_controls") + " configures the playback bar. The user "
            "can set its <b>Position</b> (bottom or top; default bottom), whether it "
            "shows the <b>Camera</b> button (default on) and whether the map buttons are "
            "shown (<b>Show map buttons</b>, default on). The spec fixes everything else:"
        ),
        bullet(
            "Play/pause, restart, time slider, clock (playback position over total "
            "length, for example 0:12 / 0:30) and the data date-time."
        ),
        bullet("Speed button cycling 0.25×, 0.5×, 0.75×, 1×, 2× and 4×."),
        bullet(
            "<b>Preview camera while playing</b> is on, and the how-to-move hint is off."
        ),
        sp(4),
        p(
            code("create_timeline_animation")
            + " builds the shared "
            "clock. The user sets the playback length <b>Duration</b> (default 30 s): "
            "the whole timeline plays in that time, and the video uses it by default. "
            "The spec fixes the redraw rate at 60 fps ("
            + code("fps_limit")
            + "), so it is no longer a form field. "
            + code("auto_rotate_speed")
            + " is 0, so the map does not rotate while it plays."
        ),
        h2("6d. Camera Step &amp; Camera Panel"),
        p(
            code("set_video_camera")
            + " (task id "
            + code("video_camera")
            + ", form step <b>Camera</b>) sets one camera for both the interactive map "
            "and the video. Its output is passed to "
            + code("draw_animated_map")
            + " (so the map's Camera panel opens on it and previews it while playing) and "
            "to "
            + code("render_video_from_settings")
            + ", so the map and the video always agree. The spec restricts the "
            "<b>Camera settings</b> field to a single option, <b>From Camera panel "
            "settings</b>: the settings copied from the map's Camera panel, pasted into "
            "the field, or the path of the downloaded "
            + code(".json")
            + " file. The default is "
            + code('{"type_": "fixed"}')
            + ", a fixed view of the whole scene. The settings are validated when the "
            "step runs, so a missing or bad waypoint file fails there rather than part "
            "way through a video."
        ),
        p(
            "The workflow is therefore: run it, open the interactive map, design a "
            "camera in the Camera panel, copy its settings, paste them into the "
            "workflow's <b>Camera</b> step and re-run. The Camera panel (opened from "
            "the playback bar's camera button) lets the user:"
        ),
        bullet("Pick a camera and set its fields (list in section 6e)."),
        bullet(
            "Press <b>Use current view</b> to fill the centre, range, tilt and heading "
            "from the map as it is now."
        ),
        bullet(
            "Turn <b>Preview camera while playing</b> on (the default) or off. Moving the "
            "map by hand turns it off, with a notice."
        ),
        bullet(
            "<b>Copy settings</b> or <b>Download</b> the camera, to paste into the "
            "workflow's Camera step. The panel opens on the workflow's camera and floats "
            "beside the top-right map buttons."
        ),
        sp(4),
        h2("6e. Camera Options"),
        p(
            "Cameras are described the Google Maps 3D way: a centre the camera looks at, "
            "its range (distance in metres), tilt, heading and field of view. Blank "
            "values frame the whole scene at the map's tilt and heading."
        ),
        make_table(
            [
                header_row("Camera", "Behaviour", "Main settings"),
                [
                    c("Fixed view"),
                    c("One view; blank centre = the whole scene"),
                    c("Centre, Range, Tilt, Heading, Field of view"),
                ],
                [
                    c("Fly to &amp; around"),
                    c("Flies in from the whole scene, then circles the centre"),
                    c("Centre, Range, Tilt, Heading, Fly Frac 0.25 of the clip, Rounds 1"),
                ],
                [
                    c("Follow a subject"),
                    c("Sits behind one subject, facing its travel"),
                    c(
                        "Subject (blank = longest-running track), Range 800 m, Tilt 60"
                    ),
                ],
                [
                    c("Subject tour"),
                    c(
                        "Follows each subject in turn for an equal share of the clip, flying "
                        "between them"
                    ),
                    c(
                        "Subjects list (the order; blank = all by name), Fly between 0.2, "
                        "Name cards (3 s as each subject comes in; on)"
                    ),
                ],
                [
                    c("Follow the action"),
                    c("Frames the recent movement of all (or listed) subjects"),
                    c("Subjects, optional Face travel"),
                ],
                [
                    c("Cinematic fly-through"),
                    c("Whole-scene intro, then a tilted, turning follow of the action"),
                    c(
                        "Fly-in 0.12, Tilt 55, Turning (rotate / face heading / fixed), "
                        "Turn 45°"
                    ),
                ],
                [
                    c("Keyframes"),
                    c(
                        "Flies through waypoints added in the panel, uploaded from a file, or "
                        "derived from a subject's track"
                    ),
                    c("Source (waypoints / file / subject), easing smooth / linear / spline"),
                ],
            ],
            [3.4 * cm, 6.4 * cm, 7.2 * cm],
        ),
        sp(4),
        p(
            "The four following cameras (Follow a subject, Subject tour, Follow the "
            "action and Cinematic fly-through) share these options:"
        ),
        bullet(
            "<b>Lead room</b>: space ahead of moving subjects (0.15 for Follow a "
            "subject and Subject tour, 0.1 for the others)."
        ),
        bullet(
            "<b>Zoom with the action</b>: zooms in while subjects rest and out while "
            "they move fast (0.5 for Follow a subject and Subject tour, 0.3 for the others)."
        ),
        bullet(
            "<b>Keep in view over hills</b> (on): raises the camera when a ridge would "
            "hide the subject."
        ),
        bullet("Smooth, spring-like camera movement."),
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
        h2("6f. Drawing &amp; Saving"),
        p(
            code("draw_animated_map")
            + " combines the animated trips layer, the terrain "
            "tile layer, the view state, the camera and the timeline into a static HTML page (max "
            "zoom 15, legend bottom-right). Every animated layer is rebased onto a common "
            "timeline starting at its earliest timestamp, so all subjects stay in step. "
            "Each layer gets a stable deck.gl id that the page's animation script uses to "
            "find it. "
            + code("persist_text")
            + " writes the page to "
            + code("animated_map.html")
            + "."
        ),
        p(
            "Besides the playback bar and Camera panel, the interactive map has deck.gl "
            "map buttons (zoom in and out; a compass whose needle follows the heading, "
            "where one click sets north up and a second goes flat; reset to the opening "
            "view; fullscreen; and a loading spinner), and a legend of subject names in "
            "their EarthRanger colours. Terrain and 3D animals are lit by the sun "
            "position for the data's date and time. The map buttons are hidden in the video."
        ),
    ]

    # ── 7. Video Rendering ────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("7. Video Rendering"),
        hr(),
        p(
            "Video export is optional and <b>off by default</b>. Both video tasks sit in "
            "the <b>Video Export</b> task group on the form: <b>Include video?</b> ("
            + code("export_video_toggle")
            + "), whose <b>Export video</b> switch is always visible, and <b>Video Settings</b> ("
            + code("create_animation")
            + "), which is only used when the switch is on."
        ),
        p(
            code("export_video_toggle")
            + " uses "
            + code("skip_file")
            + " (ecoscope-workflows-ext-ste) with the user's <b>Export video</b> "
            "switch. When the switch is on, it passes the "
            + code("animated_map.html")
            + " path through. When it is off, it returns a skip sentinel, and "
            + code("create_animation")
            + "'s "
            + code("any_dependency_skipped")
            + " condition then skips the whole render. No other task depends on the video, "
            "so the map, GeoParquet files and dashboard are unaffected."
        ),
        note(
            "The form default comes from an "
            + code("rjsf-overrides")
            + " entry. "
            + code("skip_file")
            + "'s own default is also off, so a config that omits "
            + code("enabled")
            + " skips the video too."
        ),
        p(
            "When enabled, "
            + code("render_video_from_settings")
            + " records "
            + code("animated_map.html")
            + " to "
            + code("animation.mp4")
            + ", using the camera from the Camera step ("
            + code("video_camera")
            + "):"
        ),
        bullet(
            "Launches headless Chromium with ANGLE WebGL (GPU when available; SwiftShader software rendering only if "
            + code("gl")
            + " is set to "
            + code("software")
            + "). The spec leaves it on "
            + code("auto")
            + "."
        ),
        bullet(
            "Reads the timeline span and the animation's natural length. With <b>Duration</b> on Auto the video "
            "matches the playback <b>Duration</b>; otherwise it uses the fixed seconds. Frames = fps × seconds (30 fps; "
            "900 frames by default)."
        ),
        bullet(
            "Computes the whole per-frame camera path in the page from the chosen camera, fitted to the "
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
            "Adds a 1 s hold on the opening frame and a 2 s hold on the closing frame (the completed tracks). "
            "The holds reuse captured frames, so they add no capture time."
        ),
        bullet(
            "Encodes the numbered frames with ffmpeg: libx264, CRF 18, "
            + code("veryfast")
            + " preset, "
            "yuv420p, dimensions rounded to even numbers, "
            + code("+faststart")
            + " for web playback."
        ),
        bullet(
            "Renders are resumable: frames are kept beside the video until it is written, "
            "so a failed or interrupted render with the same settings picks up where it stopped."
        ),
        sp(4),
        h2("7a. Video Settings"),
        p(
            "The user-facing options on the <b>Video Settings</b> step are <b>Duration</b>, "
            "<b>Overlays</b> and <b>Resolution</b>. The camera is set in the Camera step "
            "(section 6d), not here."
        ),
        make_table(
            [
                header_row("Setting", "Options"),
                [
                    c("Duration"),
                    c(
                        "<b>Auto</b> (default) uses the playback length. With Auto off, a fixed "
                        "number of seconds (default 30)."
                    ),
                ],
                [
                    c("Overlays"),
                    c(
                        "Clock (with a clock position; default top-right), legend, north arrow, "
                        "scale bar, title and marker labels. All are on by default. The playback "
                        "bar, Camera panel and map buttons are never shown in the video."
                    ),
                ],
                [
                    c("Resolution"),
                    c(
                        "720p (1280×720, default); 1080p; 4K; 720p vertical 9:16 (720×1280); "
                        "1080p vertical 9:16 (1080×1920); 1080p square 1:1 (1080×1080); or a "
                        "custom width and height."
                    ),
                ],
            ],
            [3.4 * cm, 13.6 * cm],
        ),
        h2("7b. Fixed Encoding Settings"),
        make_table(
            [
                header_row("Setting", "Value"),
                [c("Frame rate"), c("30 fps")],
                [c("Clip range"), c("Whole timeline (start_frac 0, end_frac 1)")],
                [c("Holds"), c("1 s on the opening frame, 2 s on the closing frame")],
                [c("Frame capture"), c("JPEG, quality 92, device scale factor 1")],
                [c("Encoder"), c("H.264 (libx264), CRF 18, preset veryfast")],
                [c("Workers and WebGL"), c("workers auto, GPU auto")],
                [
                    c("Capture timing"),
                    c(
                        "settle 30 ms, tile timeout 8 000 ms, lazy-piece (3D model, filters) timeout "
                        "30 000 ms, base map load timeout 60 000 ms"
                    ),
                ],
                [c("Resume"), c("On: frames kept beside the video until it is written")],
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
            "Two "
            + code("create_files_single_view")
            + " steps build the dashboard's <b>Files</b> section: "
            + code("map_files")
            + " lists "
            + code("animated_map.html")
            + " and "
            + code("video_files")
            + " lists "
            + code("animation.mp4")
            + " when the video was exported (it is empty otherwise). "
            + code("gather_dashboard")
            + " assembles the map, the Files section, the workflow name and "
            "description, the time range and the (empty) groupers. The video is "
            "not a dashboard widget; it is offered as a file."
        ),
    ]

    # ── 9. Output Files ───────────────────────────────────────────────────────
    story += [
        sp(4),
        h1("9. Output Files"),
        hr(),
        p(
            "All outputs are written to " + code("ECOSCOPE_WORKFLOWS_RESULTS") + ", which "
            "can be a local path, a "
            + code("file://")
            + " URL or, on ecoscope-web, a "
            + code("gs://")
            + " folder."
        ),
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
                    c("H.264 video of the animation (only when <b>Export video</b> is on)"),
                ],
            ],
            [6 * cm, 4.6 * cm, 6.4 * cm],
        ),
        sp(4),
        p(
            "With a " + code("gs://") + " results folder, the video is rendered on the "
            "machine running the workflow (the browser and ffmpeg need local files; the "
            "map is downloaded first) and then uploaded to the folder, and the local copy "
            "is removed."
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
                    c(code("export_video_toggle")),
                    c("Default"),
                    c(
                        "Not a skip condition: returns a skip sentinel instead of the HTML path when "
                        "<b>Export video</b> is off."
                    ),
                ],
                [
                    c(code("create_animation")),
                    c(code("any_dependency_skipped")),
                    c(
                        "Its input is a file path, not a dataframe, so only the upstream-skip check applies. "
                        "Skipped whenever video export is off."
                    ),
                ],
                [
                    c(code("animated_map_widget")),
                    c(code("never")),
                    c("Always runs, so the dashboard always has its map widget."),
                ],
                [
                    c(code("video_files")),
                    c(code("never")),
                    c(
                        "Never skipped. With video export off, " + code("create_animation")
                        + " is skipped and this step falls back to no file, so the dashboard "
                        "still builds."
                    ),
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
                    c("Elevation decoder → terrain layer (+ chosen basemap) + terrain sampling"),
                ],
                [
                    c("Animation data"),
                    c(
                        "EPSG:4326 → trips per subject → densified and draped on terrain → RGBA colours"
                    ),
                ],
                [c("Framing"), c("Trips envelope → view state (+ pitch, bearing)")],
                [
                    c("Map"),
                    c(
                        "Trips animation + trips layer → animated layer; controls → timeline; "
                        "camera + all → draw_animated_map → HTML"
                    ),
                ],
                [
                    c("Video (optional)"),
                    c(
                        "HTML → Export video toggle → headless Chromium frames (camera from "
                        "video_camera) → ffmpeg → MP4"
                    ),
                ],
                [
                    c("Dashboard"),
                    c(
                        "HTML → map widget; HTML and video → Files section; all → gather_dashboard"
                    ),
                ],
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
                    c("==2.25.3"),
                    c(
                        "Core runtime and tasks (EarthRanger I/O, preprocessing, CRS, persistence, dashboard)"
                    ),
                ],
                [
                    c("ecoscope-workflows-ext-custom"),
                    c("0.1.5.*"),
                    c("Map layer definitions and " + code("persist_df_wrapper")),
                ],
                [
                    c("ecoscope-workflows-ext-ste"),
                    c("0.0.32.*"),
                    c("Envelope, view state, hex-to-RGBA and video export toggle tasks"),
                ],
                [
                    c("ecoscope-workflows-ext-mep"),
                    c("1.11.0.*"),
                    c(
                        "Terrain, trips, animated map, Camera step and video rendering tasks; "
                        "loads the map widgets (my-deck-widgets v0.21.0) from jsDelivr"
                    ),
                ],
                [c("pydeck"), c("0.9.2"), c("deck.gl map generation")],
                [c("opentelemetry-sdk"), c("&gt;=1.20.0, &lt;2.0.0"), c("Tracing")],
                [
                    c("wt-compiler"),
                    c("==0.10.1"),
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
