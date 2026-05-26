import streamlit as st
import requests
import plotly.graph_objects as go
import math

try:
    res = requests.get("http://back:8000/", timeout=2)
    API_URL = "http://back:8000"
except:
    API_URL = "http://localhost:8000"

st.set_page_config(page_title="STARS SDA 대시보드", layout="wide")

st.title("STARS")
st.caption("위성 추적 및 이상 대응 추천 시스템 · SDA 프로토타입 v1.0")
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

    import random
    random.seed(42)
    star_x = [random.uniform(-4.5, 4.5) for _ in range(120)]
    star_y = [random.uniform(-2.2, 2.2) for _ in range(120)]
    fig.add_trace(go.Scatter(
        x=star_x, y=star_y, mode="markers",
        marker=dict(size=[random.uniform(0.5, 2) for _ in range(120)], color="white", opacity=0.4),
        hoverinfo="skip", showlegend=False
    ))

    for r_glow, opacity in [(1.12, 0.04), (1.08, 0.08), (1.04, 0.12)]:
        fig.add_trace(go.Scatter(
            x=[math.cos(t) * r_glow for t in theta],
            y=[math.sin(t) * r_glow for t in theta],
            fill="toself", fillcolor=f"rgba(100,180,255,{opacity})",
            line=dict(color="rgba(0,0,0,0)", width=0),
            hoverinfo="skip", showlegend=False
        ))

    fig.add_trace(go.Scatter(
        x=[math.cos(t) for t in theta],
        y=[math.sin(t) for t in theta],
        fill="toself", fillcolor="#1565c0",
        line=dict(color="#1976d2", width=2),
        hoverinfo="skip", showlegend=False
    ))

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
            x=cx_pts, y=cy_pts, fill="toself", fillcolor="#2e7d32",
            line=dict(color="#388e3c", width=0.5),
            hoverinfo="skip", showlegend=False
        ))

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
                x=[sx], y=[sy], mode="markers",
                marker=dict(size=26, color=color, opacity=0.2),
                hoverinfo="skip", showlegend=False
            ))
        fig.add_trace(go.Scatter(
            x=[sx], y=[sy], mode="markers+text",
            marker=dict(size=13 if is_selected else 8, color=color,
                        line=dict(width=2 if is_selected else 1, color="white")),
            text=[f"  {s['name']}"] if is_selected else [""],
            textposition="middle right",
            textfont=dict(size=12, color="white"),
            name=s["name"],
            hovertemplate=f"<b>{s['name']}</b><br>궤도: {orbit}<br>고도: {s['alt']} km<br>임무: {s['mission']}<extra></extra>"
        ))

    fig.update_layout(
        paper_bgcolor="#0a0f1e", plot_bgcolor="#0a0f1e",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4.5, 4.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-4.5, 4.5], scaleanchor="x", scaleratio=1),
        height=480, margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False, font=dict(color="white"),
        hoverlabel=dict(bgcolor="#1a2035", font_color="white", bordercolor="#4fc3f7")
    )
    return fig

col_viz, col_right = st.columns([2, 1])

with col_viz:
    filter_col1, filter_col2 = st.columns(2)
    with filter_col1:
        search = st.text_input("위성 검색", placeholder="예: ISS, NOAA-20...")
    with filter_col2:
        group_options = ["전체", "LEO", "MEO", "GEO", "HEO"] + list(groups.keys())
        selected_filter = st.selectbox("궤도 / 그룹 필터", group_options)

    if selected_filter == "전체":
        filtered = [s for s in satellites if not search or search.lower() in s["name"].lower()]
    elif selected_filter in ["LEO", "MEO", "GEO", "HEO"]:
        filtered = [s for s in satellites if s["orbit"] == selected_filter and (not search or search.lower() in s["name"].lower())]
    else:
        group_sats = groups.get(selected_filter, [])
        filtered = [s for s in satellites if s["name"] in group_sats and (not search or search.lower() in s["name"].lower())]

    selected = st.selectbox(
        "분석할 위성 선택",
        options=["선택"] + [s["name"] for s in filtered]
    )

    selected_sat = next((s for s in satellites if s["name"] == selected), None)
    fig = draw_orbits(filtered if selected_filter != "전체" else satellites, selected if selected != "선택" else None)
    st.plotly_chart(fig, use_container_width=True)

    col_l1, col_l2, col_l3, col_l4 = st.columns(4)
    col_l1.markdown("<span style='color:#4fc3f7'>● LEO 저궤도</span>", unsafe_allow_html=True)
    col_l2.markdown("<span style='color:#ffb74d'>● MEO 중궤도</span>", unsafe_allow_html=True)
    col_l3.markdown("<span style='color:#ce93d8'>● GEO 정지궤도</span>", unsafe_allow_html=True)
    col_l4.markdown("<span style='color:#ef9a9a'>● HEO 타원궤도</span>", unsafe_allow_html=True)

with col_right:
    tab1, tab2, tab3 = st.tabs(["분석", "위성 등록", "그룹 관리"])

    with tab1:
        if selected_sat:
            st.markdown(f"### {selected_sat['name']}")
            st.caption(f"NORAD {selected_sat['norad']} · {selected_sat['mission']}")

            st.markdown("**위성 정보**")
            info_cols = st.columns(2)
            info_cols[0].metric("궤도 유형", selected_sat["orbit"])
            info_cols[0].metric("고도", f"{selected_sat['alt']} km")
            info_cols[0].metric("경사각", f"{selected_sat['inc']}도")
            info_cols[1].metric("이심률", selected_sat["ecc"])
            info_cols[1].metric("평균 운동", f"{selected_sat['mm']} rev/day")
            info_cols[1].metric("평균운동 변화량", selected_sat["mmc"])

            st.markdown("---")

            if st.button("이상 분석 및 대응 전략 추천", use_container_width=True):
                with st.spinner("궤도 파라미터 분석 중..."):
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
                        st.error(f"API 연결 오류: {e}")

            if "last_result" in st.session_state and st.session_state.get("last_sat") == selected_sat["name"]:
                r = st.session_state["last_result"]
                score = r["risk_score"]
                level = r["risk_level"]
                color_map = {"Low": "green", "Medium": "orange", "High": "red"}
                level_kor = {"Low": "낮음", "Medium": "보통", "High": "높음"}

                st.markdown("**위험도 평가**")
                st.markdown(f":{color_map[level]}[**위험 등급: {level_kor[level]} ({level}) — 점수: {score}/100**]")
                st.progress(score / 100)
                st.markdown(f"**이상 상태:** {r['anomaly_status']}")
                st.caption(r["anomaly_reason"])
                st.markdown("---")
                st.markdown("**대응 전략 추천**")
                for strategy in r["recommended_strategy"]:
                    st.markdown(f"- {strategy}")
                st.markdown("**후속 조치**")
                st.info(r["follow_up_action"])
                with st.expander("검증 계획 보기"):
                    for v in r["validation_plan"]:
                        st.markdown(f"- {v}")
        else:
            st.markdown("---")
            st.caption("왼쪽에서 분석할 위성을 선택해주세요.")

    with tab2:
        with st.form("register_form"):
            f_name = st.text_input("위성 이름")
            f_norad = st.text_input("NORAD ID")
            f_orbit = st.selectbox("궤도 유형", ["LEO", "MEO", "GEO", "HEO"])
            f_mission = st.selectbox("임무 유형", [
                "Earth Observation", "Communication", "Navigation",
                "Scientific", "Technology Demo", "Unknown Object"
            ])
            f_alt = st.number_input("고도 (km)", min_value=160, max_value=42000, value=500)
            f_inc = st.number_input("경사각 (도)", min_value=0.0, max_value=180.0, value=51.6)
            f_ecc = st.number_input("이심률", min_value=0.0, max_value=0.99, value=0.001, step=0.001, format="%.4f")
            f_mm = st.number_input("평균 운동 (rev/day)", min_value=0.1, max_value=17.0, value=15.0)
            f_mmc = st.selectbox("평균운동 변화량", ["Low", "Medium", "High"])
            f_tle1 = st.text_input("TLE 1행 (선택)")
            f_tle2 = st.text_input("TLE 2행 (선택)")
            submitted = st.form_submit_button("위성 등록")

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
                        st.success(f"{f_name} 등록 완료.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("등록 실패.")
                except Exception as e:
                    st.error(f"API 연결 오류: {e}")

    with tab3:
        st.markdown("**새 그룹 생성**")
        with st.form("group_form"):
            g_name = st.text_input("그룹 이름")
            sat_names = [s["name"] for s in satellites]
            g_sats = st.multiselect("위성 선택", options=sat_names)
            g_submitted = st.form_submit_button("그룹 생성")

            if g_submitted and g_name and g_sats:
                try:
                    res = requests.post(f"{API_URL}/groups", json={
                        "group_name": g_name,
                        "satellite_names": g_sats
                    }, timeout=5)
                    if res.status_code == 200:
                        st.success(f"그룹 {g_name} 생성 완료.")
                        st.cache_data.clear()
                        st.rerun()
                    else:
                        st.error("그룹 생성 실패.")
                except Exception as e:
                    st.error(f"API 연결 오류: {e}")

        if groups:
            st.markdown("**등록된 그룹**")
            for g_name, g_sats in groups.items():
                with st.expander(f"{g_name} ({len(g_sats)}개 위성)"):
                    for s in g_sats:
                        st.markdown(f"- {s}")
                    if st.button(f"{g_name} 삭제", key=f"del_{g_name}"):
                        try:
                            requests.delete(f"{API_URL}/groups/{g_name}", timeout=5)
                            st.cache_data.clear()
                            st.rerun()
                        except Exception as e:
                            st.error(f"API 연결 오류: {e}")