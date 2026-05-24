import streamlit as st
import requests
import plotly.graph_objects as go
import math

try:
    res = requests.get("http://back:8000/", timeout=2)
    API_URL = "http://back:8000"
except:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="STARS SDA Dashboard", layout="wide")

st.title("STARS")
st.caption("Satellite Tracking and Anomaly Response System · SDA Prototype v1.0")
st.markdown("---")

@st.cache_data(ttl=5)
def load_satellites():
    try:
        res = requests.get(f"{API_URL}/satellites", timeout=5)
        return res.json()
    except:
        return []

@st.cache_data(ttl=5)
def load_groups():
    try:
        res = requests.get(f"{API_URL}/groups", timeout=5)
        return res.json()
    except:
        return {}

satellites = load_satellites()
groups = load_groups()

def draw_orbits(satellites, selected_name=None):
    fig = go.Figure()

    orbit_colors = {"LEO": "#4fc3f7", "MEO": "#ffb74d", "GEO": "#ce93d8", "HEO": "#ef9a9a"}
    orbit_radius = {"LEO": 1.5, "MEO": 2.5, "GEO": 3.5, "HEO": 3.0}

    theta = [i * 2 * math.pi / 200 for i in range(201)]

    # 우주 배경 별
    import random
    random.seed(42)
    star_x = [random.uniform(-4.5, 4.5) for _ in range(120)]
    star_y = [random.uniform(-2.2, 2.2) for _ in range(120)]
    fig.add_trace(go.Scatter(
        x=star_x, y=star_y,
        mode="markers",
        marker=dict(size=[random.uniform(0.5, 2) for _ in range(120)], color="white", opacity=0.4),
        hoverinfo="skip", showlegend=False
    ))

    # 대기권 glow
    for r_glow, opacity in [(1.12, 0.04), (1.08, 0.08), (1.04, 0.12)]:
        fig.add_trace(go.Scatter(
            x=[math.cos(t) * r_glow for t in theta],
            y=[math.sin(t) * r_glow for t in theta],
            fill="toself",
            fillcolor=f"rgba(100,180,255,{opacity})",
            line=dict(color="rgba(0,0,0,0)", width=0),
            hoverinfo="skip", showlegend=False
        ))

    # 지구 본체 (완전한 원)
    fig.add_trace(go.Scatter(
        x=[math.cos(t) for t in theta],
        y=[math.sin(t) for t in theta],
        fill="toself",
        fillcolor="#1565c0",
        line=dict(color="#1976d2", width=2),
        hoverinfo="skip", showlegend=False
    ))

    # 대륙
    continents = [
        [(-0.35, 0.38), (-0.18, 0.48), (-0.08, 0.42), (-0.02, 0.25), (-0.12, 0.08), (-0.28, 0.12), (-0.42, 0.22)],
        [(-0.22, 0.02), (-0.10, 0.05), (-0.07, -0.18), (-0.18, -0.32), (-0.28, -0.22), (-0.25, -0.08)],
        [(0.05, 0.42), (0.20, 0.45), (0.28, 0.30), (0.22, 0.12), (0.12, -0.15), (0.05, -0.38), (-0.03, -0.42), (-0.07, -0.15), (0.0, 0.15)],
        [(0.22, 0.45), (0.50, 0.48), (0.68, 0.33), (0.62, 0.18), (0.45, 0.12), (0.28, 0.18), (0.20, 0.30)],
        [(0.50, -0.12), (0.68, -0.09), (0.72, -0.27), (0.58, -0.33), (0.48, -0.24)],
    ]

    for continent in continents:
        cx_pts = [p[0] for p in continent] + [continent[0][0]]
        cy_pts = [p[1] for p in continent] + [continent[0][1]]
        fig.add_trace(go.Scatter(
            x=cx_pts, y=cy_pts,
            fill="toself",
            fillcolor="#2e7d32",
            line=dict(color="#388e3c", width=0.5),
            hoverinfo="skip", showlegend=False
        ))

    # 궤도 링
    for s in satellites:
        orbit = s.get("orbit", "LEO")
        r = orbit_radius.get(orbit, 1.5)
        color = orbit_colors.get(orbit, "#4fc3f7")
        is_selected = s["name"] == selected_name

        fig.add_trace(go.Scatter(
            x=[math.cos(t) * r for t in theta],
            y=[math.sin(t) * r for t in theta],
            mode="lines",
            line=dict(color=color, width=2 if is_selected else 0.4, dash="solid" if is_selected else "dot"),
            opacity=0.9 if is_selected else 0.2,
            hoverinfo="skip", showlegend=False
        ))

    # 위성 점
    for s in satellites:
        orbit = s.get("orbit", "LEO")
        r = orbit_radius.get(orbit, 1.5)
        color = orbit_colors.get(orbit, "#4fc3f7")
        is_selected = s["name"] == selected_name

        angle = (hash(s["name"]) % 628) / 100
        sx = math.cos(angle) * r
        sy = math.sin(angle) * r

        if is_selected:
            fig.add_trace(go.Scatter(
                x=[sx], y=[sy],
                mode="markers",
                marker=dict(size=26, color=color, opacity=0.2),
                hoverinfo="skip", showlegend=False
            ))

        fig.add_trace(go.Scatter(
            x=[sx], y=[sy],
            mode="markers+text",
            marker=dict(
                size=13 if is_selected else 8,
                color=color,
                line=dict(width=2 if is_selected else 1, color="white"),
                symbol="circle"
            ),
            text=[f"  {s['name']}"] if is_selected else [""],
            textposition="middle right",
            textfont=dict(size=12, color="white"),
            name=s["name"],
            hovertemplate=f"<b>{s['name']}</b><br>Orbit: {orbit}<br>Alt: {s['alt']} km<br>Mission: {s['mission']}<extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor="#0a0f1e",
        plot_bgcolor="#0a0f1e",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4.5, 4.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4.5, 4.5], scaleanchor="x", scaleratio=1),
        height=480,
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        font=dict(color="white"),
        hoverlabel=dict(bgcolor="#1a2035", font_color="white", bordercolor="#4fc3f7")
    )
    return fig

col_viz, col_right = st.columns([2, 1])

with col_viz:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        search = st.text_input("Search satellite", placeholder="e.g. ISS, NOAA-20...")
    with filter_col2:
        group_options = ["All", "LEO", "MEO", "GEO", "HEO"] + list(groups.keys())
        selected_filter = st.selectbox("Filter by orbit / group", group_options)

    if selected_filter == "All":
        filtered = [s for s in satellites if not search or search.lower() in s["name"].lower()]
    elif selected_filter in ["LEO", "MEO", "GEO", "HEO"]:
        filtered = [s for s in satellites if s["orbit"] == selected_filter and (not search or search.lower() in s["name"].lower())]
    else:
        group_sats = groups.get(selected_filter, [])
        filtered = [s for s in satellites if s["name"] in group_sats and (not search or search.lower() in s["name"].lower())]

    selected = st.selectbox(
        "Select satellite to analyze",
        options=["Select"] + [s["name"] for s in filtered]
    )

    selected_sat = next((s for s in satellites if s["name"] == selected), None)
    fig = draw_orbits(filtered if selected_filter != "All" else satellites, selected if selected != "Select" else None)
    st.plotly_chart(fig, use_container_width=True)

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.markdown("<span style='color:#4fc3f7'>● LEO</span>", unsafe_allow_html=True)
    col_l2.markdown("<span style='color:#ffb74d'>● MEO</span>", unsafe_allow_html=True)
    col_l3.markdown("<span style='color:#ce93d8'>● GEO</span>", unsafe_allow_html=True)
    col_l4.markdown("<span style='color:#ef9a9a'>● HEO</span>", unsafe_allow_html=True)

with col_right:
    tab1, tab2, tab3 = st.tabs(["Analysis", "Register", "Groups"])

    with tab1:
        if selected_sat:
            st.markdown(f"### {selected_sat['name']}")
            st.caption(f"NORAD {selected_sat['norad']} · {selected_sat['mission']}")

            st.markdown("**Satellite Info**")
            info_cols = st.columns(2)
            info_cols[0].metric("Orbit", selected_sat["orbit"])
            info_cols[0].metric("Altitude", f"{selected_sat['alt']} km")
            info_cols[0].metric("Inclination", f"{selected_sat['inc']} deg")
            info_cols[1].metric("Eccentricity", selected_sat["ecc"])
            info_cols[1].metric("Mean Motion", f"{selected_sat['mm']} rev/day")
            info_cols[1].metric("MMC", selected_sat["mmc"])

            st.markdown("---")

            if st.button("Analyze and Recommend", use_container_width=True):
                with st.spinner("Analyzing orbital parameters..."):
                    try:
                        res = requests.post(f"{API_URL}/analyze", json={
                            "name": selected_sat["name"],
                            "orbit": selected_sat["orbit"],
                            "alt": selected_sat["alt"],
                            "inc": selected_sat["inc"],
                            "ecc": selected_sat["ecc"],
                            "mm": selected_sat["mm"],
                            "mmc": selected_sat["mmc"],
                            "mission": selected_sat["mission"]
                        }, timeout=5)
                        result = res.json()
                        st.session_state["last_result"] = result
                        st.session_state["last_sat"] = selected_sat["name"]
                    except Exception as e:
                        st.error(f"Cannot connect to API: {e}")

            if "last_result" in st.session_state and st.session_state.get("last_sat") == selected_sat["name"]:
                r = st.session_state["last_result"]
                score = r["risk_score"]
                level = r["risk_level"]
                color_map = {"Low": "green", "Medium": "orange", "High": "red"}

                st.markdown("**Risk Assessment**")
                st.markdown(f":{color_map[level]}[**{level.upper()} RISK - Score: {score}/100**]")
                st.progress(score / 100)
                st.markdown(f"**Status:** {r['anomaly_status']}")
                st.caption(r["anomaly_reason"])
                st.markdown("---")
                st.markdown("**Recommended Strategy**")
                for strategy in r["recommended_strategy"]:
                    st.markdown(f"- {strategy}")
                st.markdown("**Follow-up Action**")
                st.info(r["follow_up_action"])
                with st.expander("Validation Plan"):
                    for v in r["validation_plan"]:
                        st.markdown(f"- {v}")
        else:
            st.caption("Select a satellite from the list to analyze.")

    with tab2:
        with st.form("register_form"):
            f_name = st.text_input("Satellite name")
            f_norad = st.text_input("NORAD ID")
            f_orbit = st.selectbox("Orbit type", ["LEO", "MEO", "GEO", "HEO"])
            f_mission = st.selectbox("Mission type", [
                "Earth Observation", "Communication", "Navigation",
                "Scientific", "Technology Demo", "Unknown Object"
            ])
            f_alt = st.number_input("Altitude (km)", min_value=160, max_value=42000, value=500)
            f_inc = st.number_input("Inclination (deg)", min_value=0.0, max_value=180.0, value=51.6)
            f_ecc = st.number_input("Eccentricity", min_value=0.0, max_value=0.99, value=0.001, step=0.001, format="%.4f")
            f_mm = st.number_input("Mean motion (rev/day)", min_value=0.1, max_value=17.0, value=15.0)
            f_mmc = st.selectbox("Mean motion change", ["Low", "Medium", "High"])
            f_tle1 = st.text_input("TLE Line 1 (optional)")
            f_tle2 = st.text_input("TLE Line 2 (optional)")
            submitted = st.form_submit_button("Register satellite")

            if submitted and f_name:
                payload = {
                    "name": f_name, "norad": f_norad,
                    "orbit": f_orbit, "mission": f_mission,
                    "alt": f_alt, "inc": f_inc, "ecc": f_ecc,
                    "mm": f_mm, "mmc": f_mmc,
                    "tle1": f_tle1, "tle2": f_tle2
                }
                try:
                    res = requests.post(f"{API_URL}/satellites", json=payload, timeout=5)
                    if res.status_code == 200:
                        st.success(f"{f_name} registered successfully.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Registration failed.")
                except Exception as e:
                    st.error(f"Cannot connect to API: {e}")

    with tab3:
        st.markdown("**Create new group**")
        with st.form("group_form"):
            g_name = st.text_input("Group name")
            sat_names = [s["name"] for s in satellites]
            g_sats = st.multiselect("Select satellites", options=sat_names)
            g_submitted = st.form_submit_button("Create group")

            if g_submitted and g_name and g_sats:
                try:
                    res = requests.post(f"{API_URL}/groups", json={
                        "group_name": g_name,
                        "satellite_names": g_sats
                    }, timeout=5)
                    if res.status_code == 200:
                        st.success(f"Group {g_name} created.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("Failed to create group.")
                except Exception as e:
                    st.error(f"Cannot connect to API: {e}")

        if groups:
            st.markdown("**Existing groups**")
            for g_name, g_sats in groups.items():
                with st.expander(f"{g_name} ({len(g_sats)} satellites)"):
                    for s in g_sats:
                        st.markdown(f"- {s}")
                    if st.button(f"Delete {g_name}", key=f"del_{g_name}"):
                        try:
                            requests.delete(f"{API_URL}/groups/{g_name}", timeout=5)
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"Cannot connect to API: {e}")