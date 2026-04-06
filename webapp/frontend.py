import streamlit as st
import asyncio
import uuid
import sys
import os
import time
import nest_asyncio


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from workflows.main import workflow

nest_asyncio.apply()

st.set_page_config(page_title="Data Analysis Agent", layout="wide")

st.markdown("""
    <style>
        .block-container { padding-top: 1.5rem; }

        .status-log {
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            border-radius: 10px;
            padding: 1rem 1.2rem;
            font-family: monospace;
            font-size: 13.5px;
            max-height: 320px;
            overflow-y: auto;
        }

        .log-entry {
            display: flex;
            align-items: flex-start;
            gap: 10px;
            padding: 5px 0;
            border-bottom: 1px solid #ececec;
            color: #1a1a2e;
        }

        .log-entry:last-child { border-bottom: none; }

        .log-dot {
            width: 9px;
            height: 9px;
            border-radius: 50%;
            margin-top: 4px;
            flex-shrink: 0;
        }

        .dot-done  { background: #2ecc71; }
        .dot-run   { background: #3498db; animation: blink 1s infinite; }
        .dot-err   { background: #e74c3c; }

        @keyframes blink {
            0%, 100% { opacity: 1; } 50% { opacity: 0.2; }
        }

        .log-time {
            color: #7f8c8d;
            font-size: 12px;
            min-width: 52px;
            padding-top: 1px;
        }

        .timer-box {
            background: #1a1a2e;
            color: #00d4aa;
            border-radius: 10px;
            padding: 0.6rem 1.2rem;
            font-family: monospace;
            font-size: 22px;
            letter-spacing: 3px;
            text-align: center;
            margin-bottom: 0.5rem;
        }

        .status-badge {
            display: inline-block;
            padding: 3px 12px;
            border-radius: 20px;
            font-size: 12.5px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }
        .badge-running { background: #d6eaf8; color: #1a6fa3; }
        .badge-done    { background: #d5f5e3; color: #1a6a3e; }
        .badge-idle    { background: #eaecee; color: #555; }
        .badge-error   { background: #fadbd8; color: #922b21; }

        .node-pill {
            display: inline-block;
            background: #eaf0fb;
            color: #1a3a6e;
            border-radius: 6px;
            padding: 1px 8px;
            font-size: 12px;
            font-weight: 500;
            margin-left: 2px;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center; margin-bottom:0;'>Data Analysis Agent</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#888; margin-top:4px;'>Created by Pankaj Maulekhi</p>", unsafe_allow_html=True)
st.markdown("<hr style='margin: 0.8rem 0 1.4rem;'>", unsafe_allow_html=True)

FOLDER = "C:\\Users\\panka\\genai_project\\data_analysis_agent\\data"

# ── Session state ────────────────────────────────────────────────────────────
for key, default in {
    "log_entries": [],
    "elapsed": 0.0,
    "running": False,
    "status": "idle",
    "start_time": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


def _fmt_elapsed(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(seconds) % 60
    ms = int((seconds - int(seconds)) * 10)
    return f"{m:02d}:{s:02d}.{ms}"


async def run_workflow(file_path, log_placeholder, timer_placeholder, badge_placeholder):
    input_for_workflow = {"file_path": file_path}
    config = {"configurable": {"thread_id": uuid.uuid4()}}

    st.session_state.start_time = time.time()
    st.session_state.running = True
    st.session_state.status = "running"
    st.session_state.log_entries = []

    try:
        async for chunk in workflow.astream(input_for_workflow, config=config, stream_mode=["updates"]):
            a, b = chunk
            if a == "updates":
                node_name = list(b.keys())[0]
                elapsed = time.time() - st.session_state.start_time
                st.session_state.elapsed = elapsed

                st.session_state.log_entries.append({
                    "node": node_name,
                    "elapsed": elapsed,
                    "status": "done",
                })

                # Rebuild log HTML
                log_html = '<div class="status-log">'
                for entry in st.session_state.log_entries:
                    dot_cls = "dot-done" if entry["status"] == "done" else "dot-run"
                    t = _fmt_elapsed(entry["elapsed"])
                    log_html += f'''
                    <div class="log-entry">
                        <div class="log-dot {dot_cls}"></div>
                        <span class="log-time">{t}</span>
                        <span>Node <span class="node-pill">{entry["node"]}</span> completed</span>
                    </div>'''
                log_html += "</div>"
                log_placeholder.markdown(log_html, unsafe_allow_html=True)

                timer_placeholder.markdown(
                    f'<div class="timer-box">{_fmt_elapsed(elapsed)}</div>',
                    unsafe_allow_html=True,
                )
                badge_placeholder.markdown(
                    '<span class="status-badge badge-running">RUNNING</span>',
                    unsafe_allow_html=True,
                )

        st.session_state.status = "done"
        st.session_state.running = False
        final_elapsed = time.time() - st.session_state.start_time
        st.session_state.elapsed = final_elapsed

        timer_placeholder.markdown(
            f'<div class="timer-box">{_fmt_elapsed(final_elapsed)}</div>',
            unsafe_allow_html=True,
        )
        badge_placeholder.markdown(
            '<span class="status-badge badge-done">COMPLETED</span>',
            unsafe_allow_html=True,
        )

    except Exception as e:
        st.session_state.status = "error"
        st.session_state.running = False
        st.session_state.log_entries.append({
            "node": f"ERROR: {str(e)}",
            "elapsed": time.time() - st.session_state.start_time,
            "status": "error",
        })
        badge_placeholder.markdown(
            '<span class="status-badge badge-error">ERROR</span>',
            unsafe_allow_html=True,
        )
        st.error(f"Workflow error: {e}")


# ── Layout ───────────────────────────────────────────────────────────────────
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("#### Upload file")
    file = st.file_uploader(
        label="Drop your CSV file here",
        type="csv",
        accept_multiple_files=False,
        label_visibility="collapsed",
    )

    if file:
        st.success(f"**{file.name}** ready")
        run_btn = st.button("Run Analysis Agent", type="primary", use_container_width=True)
    else:
        st.info("Upload a CSV file to begin.")
        run_btn = False

with right_col:
    st.markdown("#### Workflow status")

    status_text = {
        "idle": "IDLE",
        "running": "RUNNING",
        "done": "COMPLETED",
        "error": "ERROR",
    }.get(st.session_state.status, "IDLE")

    badge_cls = {
        "idle": "badge-idle",
        "running": "badge-running",
        "done": "badge-done",
        "error": "badge-error",
    }.get(st.session_state.status, "badge-idle")

    badge_placeholder = st.empty()
    badge_placeholder.markdown(
        f'<span class="status-badge {badge_cls}">{status_text}</span>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)

    timer_placeholder = st.empty()
    timer_placeholder.markdown(
        f'<div class="timer-box">{_fmt_elapsed(st.session_state.elapsed)}</div>',
        unsafe_allow_html=True,
    )

    st.markdown("**Activity log**")
    log_placeholder = st.empty()

    # Render existing log entries (e.g. after re-run)
    if st.session_state.log_entries:
        log_html = '<div class="status-log">'
        for entry in st.session_state.log_entries:
            dot_cls = "dot-err" if entry["status"] == "error" else "dot-done"
            t = _fmt_elapsed(entry["elapsed"])
            log_html += f'''
            <div class="log-entry">
                <div class="log-dot {dot_cls}"></div>
                <span class="log-time">{t}</span>
                <span>Node <span class="node-pill">{entry["node"]}</span> completed</span>
            </div>'''
        log_html += "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)
    else:
        log_placeholder.markdown(
            '<div class="status-log" style="color:#aaa; text-align:center; padding:2rem 0;">'
            "No activity yet — run the agent to see updates."
            "</div>",
            unsafe_allow_html=True,
        )

# ── Trigger ──────────────────────────────────────────────────────────────────
if run_btn and file:
    file_path = os.path.join(FOLDER, file.name)
    loop = asyncio.get_event_loop()
    with open(file_path, "wb") as f:
        f.write(file.getbuffer())

    loop.run_until_complete(
        run_workflow(file_path, log_placeholder, timer_placeholder, badge_placeholder)
    )
    
    st.markdown("<h1 style='text-align:center; margin-bottom:0;'>Analysis Report</h1>", unsafe_allow_html=True)
    
    with open(FOLDER+"\\"+"markdown.md",'r') as f:
        md=f.read()
        
    st.markdown(md)