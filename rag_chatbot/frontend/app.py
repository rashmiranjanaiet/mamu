import os
import time

import requests
import streamlit as st
import streamlit.components.v1 as components

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ENABLE_ADMIN_UI = os.getenv("ENABLE_ADMIN_UI", "false").strip().lower() in {
    "1",
    "true",
    "yes",
    "on",
}

st.set_page_config(page_title="Atlas Book AI", page_icon=":book:", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500&display=swap');

:root {
  --bg-0: #040b16;
  --bg-1: #0a1628;
  --panel: rgba(8, 18, 35, 0.72);
  --panel-strong: rgba(6, 15, 30, 0.9);
  --line: rgba(143, 213, 255, 0.25);
  --text: #e8f5ff;
}

[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at 15% 12%, rgba(86, 231, 255, 0.07), transparent 36%),
    radial-gradient(circle at 88% 76%, rgba(156, 255, 154, 0.06), transparent 32%),
    linear-gradient(130deg, var(--bg-0), var(--bg-1));
}

[data-testid="stHeader"] {
  background: transparent;
  z-index: 4;
}

[data-testid="stMainBlockContainer"] {
  max-width: 1200px;
  padding-top: 1.2rem;
  position: relative;
  z-index: 3;
}

html, body, [class*="css"] {
  font-family: "Space Grotesk", sans-serif;
  color: var(--text);
}

.hero-wrap {
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(10, 26, 44, 0.65), rgba(8, 18, 35, 0.85));
  border-radius: 20px;
  padding: 18px 20px;
  backdrop-filter: blur(10px);
  box-shadow: 0 12px 45px rgba(0, 0, 0, 0.35);
}

.hero-kicker {
  font-family: "IBM Plex Mono", monospace;
  font-size: 12px;
  letter-spacing: 1px;
  opacity: 0.9;
  margin-bottom: 6px;
}

.hero-title {
  font-size: clamp(1.5rem, 2.8vw, 2.6rem);
  font-weight: 700;
  line-height: 1.15;
  margin: 0;
}

.hero-sub {
  opacity: 0.9;
  margin-top: 8px;
  margin-bottom: 0;
}

[data-testid="stChatMessage"] {
  border: 1px solid var(--line);
  background: var(--panel);
  border-radius: 16px;
  backdrop-filter: blur(8px);
}

[data-testid="stSidebar"] {
  background: var(--panel-strong);
  border-right: 1px solid var(--line);
  z-index: 4;
}

[data-testid="stBottomBlockContainer"],
[data-testid="stChatInput"] {
  z-index: 4;
}

.status-pill {
  display: inline-block;
  font-family: "IBM Plex Mono", monospace;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: rgba(0, 0, 0, 0.15);
  font-size: 12px;
}
</style>
    """,
    unsafe_allow_html=True,
)

components.html(
    """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8" />
    <style>html,body{margin:0;background:transparent;}</style>
  </head>
  <body>
    <script src="https://unpkg.com/three@0.160.0/build/three.min.js"></script>
    <script>
      const parentDoc = window.parent.document;
      if (!parentDoc.getElementById("atlas-3d-bg")) {
        const canvas = parentDoc.createElement("canvas");
        canvas.id = "atlas-3d-bg";
        canvas.style.position = "fixed";
        canvas.style.inset = "0";
        canvas.style.width = "100vw";
        canvas.style.height = "100vh";
        canvas.style.zIndex = "1";
        canvas.style.pointerEvents = "none";
        parentDoc.body.appendChild(canvas);

        const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
        renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

        const scene = new THREE.Scene();
        const camera = new THREE.PerspectiveCamera(62, 1, 0.1, 250);
        camera.position.z = 2.2;

        const starCount = 2400;
        const positions = new Float32Array(starCount * 3);
        const colors = new Float32Array(starCount * 3);
        const phases = new Float32Array(starCount);
        const scales = new Float32Array(starCount);
        const baseColor = new THREE.Color();

        for (let i = 0; i < starCount; i += 1) {
          const i3 = i * 3;
          positions[i3 + 0] = (Math.random() - 0.5) * 190;
          positions[i3 + 1] = (Math.random() - 0.5) * 150;
          positions[i3 + 2] = -Math.random() * 190;

          baseColor.setHSL(0.56 + Math.random() * 0.14, 0.55, 0.72 + Math.random() * 0.2);
          colors[i3 + 0] = baseColor.r;
          colors[i3 + 1] = baseColor.g;
          colors[i3 + 2] = baseColor.b;

          phases[i] = Math.random() * Math.PI * 2;
          scales[i] = 0.35 + Math.random() * 0.95;
        }

        const starsGeo = new THREE.BufferGeometry();
        starsGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
        starsGeo.setAttribute("color", new THREE.BufferAttribute(colors, 3));
        starsGeo.setAttribute("aPhase", new THREE.BufferAttribute(phases, 1));
        starsGeo.setAttribute("aScale", new THREE.BufferAttribute(scales, 1));

        const starsMat = new THREE.ShaderMaterial({
          transparent: true,
          depthWrite: false,
          vertexColors: true,
          blending: THREE.AdditiveBlending,
          uniforms: {
            uTime: { value: 0.0 },
            uPixelRatio: { value: Math.min(window.devicePixelRatio || 1, 2) },
          },
          vertexShader: `
            attribute float aPhase;
            attribute float aScale;
            uniform float uTime;
            uniform float uPixelRatio;
            varying vec3 vColor;
            varying float vBlink;
            void main() {
              vec3 p = position;
              p.z += mod(uTime * 8.0 + aPhase * 9.0, 190.0);
              p.y += sin(uTime * 0.35 + aPhase) * 0.8;
              vec4 mv = modelViewMatrix * vec4(p, 1.0);
              float d = max(0.15, -mv.z);
              vBlink = 0.45 + 0.55 * sin(uTime * (1.3 + aScale) + aPhase * 2.0);
              gl_PointSize = (1.1 + 2.9 * aScale) * uPixelRatio / d * 18.0;
              vColor = color;
              gl_Position = projectionMatrix * mv;
            }
          `,
          fragmentShader: `
            varying vec3 vColor;
            varying float vBlink;
            void main() {
              vec2 uv = gl_PointCoord - vec2(0.5);
              float dist = length(uv);
              float glow = smoothstep(0.5, 0.0, dist);
              float alpha = glow * (0.25 + vBlink * 0.95);
              gl_FragColor = vec4(vColor, alpha);
            }
          `,
        });
        const stars = new THREE.Points(starsGeo, starsMat);
        scene.add(stars);

        const nebula = new THREE.Mesh(
          new THREE.PlaneGeometry(220, 160),
          new THREE.MeshBasicMaterial({
            color: 0x2f6ca8,
            transparent: true,
            opacity: 0.08,
          }),
        );
        nebula.position.z = -80;
        scene.add(nebula);

        function resize() {
          const w = window.parent.innerWidth;
          const h = window.parent.innerHeight;
          renderer.setSize(w, h, false);
          camera.aspect = w / h;
          camera.updateProjectionMatrix();
        }

        resize();
        window.parent.addEventListener("resize", resize);

        function tick(t) {
          const s = t * 0.001;
          starsMat.uniforms.uTime.value = s;
          nebula.rotation.z = s * 0.01;
          nebula.position.y = Math.sin(s * 0.06) * 2.5;
          renderer.render(scene, camera);
          window.parent.requestAnimationFrame(tick);
        }

        window.parent.requestAnimationFrame(tick);
      }
    </script>
  </body>
</html>
    """,
    height=0,
)

st.markdown(
    """
<div class="hero-wrap">
  <div class="hero-kicker">SPACE RAG INTERFACE</div>
  <h1 class="hero-title">Atlas Book AI</h1>
  <p class="hero-sub">Full-screen space scene with blinking stars, plus grounded answers from your indexed PDF.</p>
</div>
    """,
    unsafe_allow_html=True,
)

if "messages" not in st.session_state:
    st.session_state.messages = []

health_badge = "Index status: unknown"
try:
    health = requests.get(f"{API_URL}/health", timeout=8)
    if health.status_code < 400:
        indexed = bool(health.json().get("indexed"))
        health_badge = "Index status: ready" if indexed else "Index status: not indexed"
except Exception:  # noqa: BLE001
    pass

st.markdown(f'<span class="status-pill">{health_badge}</span>', unsafe_allow_html=True)
st.write("")

with st.sidebar:
    st.header("Control")
    if ENABLE_ADMIN_UI:
        local_pdf_path = st.text_input(
            "Local PDF path",
            value="",
            placeholder=r"c:\Users\It Computer Point\Downloads\book.pdf",
        )
        pdf_file = st.file_uploader("Upload PDF", type=["pdf"])
        force_reindex = st.checkbox("Replace existing index", value=False)

        if st.button("Index Local Path", disabled=not local_pdf_path.strip()):
            body = {"pdf_path": local_pdf_path.strip(), "force": force_reindex}
            res = requests.post(f"{API_URL}/admin/index-local", json=body, timeout=60)
            if res.status_code >= 400:
                st.error(res.json().get("detail", "Local indexing failed"))
            else:
                payload = res.json()
                job_id = payload["job_id"]
                st.info(f"Job {job_id} started. Waiting for completion...")
                while True:
                    status_res = requests.get(f"{API_URL}/admin/status/{job_id}", timeout=30)
                    status = status_res.json()
                    if status["status"] in {"completed", "failed"}:
                        if status["status"] == "completed":
                            st.success(status["detail"])
                        else:
                            st.error(status["detail"])
                        break
                    time.sleep(2)

        if st.button("Upload and Index", disabled=pdf_file is None):
            files = {"file": (pdf_file.name, pdf_file.getvalue(), "application/pdf")}
            params = {"force": str(force_reindex).lower()}
            res = requests.post(f"{API_URL}/admin/upload", files=files, params=params, timeout=120)
            if res.status_code >= 400:
                st.error(res.json().get("detail", "Upload failed"))
            else:
                payload = res.json()
                job_id = payload["job_id"]
                st.info(f"Job {job_id} started. Waiting for completion...")
                while True:
                    status_res = requests.get(f"{API_URL}/admin/status/{job_id}", timeout=30)
                    status = status_res.json()
                    if status["status"] in {"completed", "failed"}:
                        if status["status"] == "completed":
                            st.success(status["detail"])
                        else:
                            st.error(status["detail"])
                        break
                    time.sleep(2)
    else:
        st.info("Upload disabled. Admin indexes a PDF outside the public UI.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("meta"):
            st.caption(msg["meta"])

question = st.chat_input("Ask a question from your indexed book")
if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Searching source pages..."):
            res = requests.post(f"{API_URL}/chat", json={"question": question}, timeout=120)
        if res.status_code >= 400:
            answer_text = res.json().get("detail", "Request failed")
            meta = ""
        else:
            payload = res.json()
            answer_text = payload["answer"]
            confidence = payload["confidence"]
            pages = sorted({str(item["page"]) for item in payload.get("sources", [])})
            pages_text = ", ".join(pages) if pages else "-"
            meta = f"Confidence: {confidence:.2f} | Source pages: {pages_text}"
        st.markdown(answer_text)
        if meta:
            st.caption(meta)

    st.session_state.messages.append({"role": "assistant", "content": answer_text, "meta": meta})
