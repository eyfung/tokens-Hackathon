"""
Streamlit web app for the Clarity trial design agent.

Provides a clean UI for:
1. Inputting trial design parameters
2. Running simulations
3. Viewing results (power, CIs, risk flags)
4. Seeing the agent's evolution over time
5. Viewing Band human-in-the-loop conversations
"""

import os
import sys
from pathlib import Path

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

from src.simulation.engine import simulate_trial, TrialDesign
from src.simulation.models import TrialDesignRequest, TrialDesignResult
from src.memory.actian_store import ActianStore
from src.communication.band import BandRoom
from src.inference.pioneer import PioneerClient
from src.agent.trial_architect import TrialArchitect


# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Clarity — Trial Design Agent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Initialize session state ────────────────────────────────────
if "agent" not in st.session_state:
    memory = ActianStore()
    band = BandRoom()
    pioneer = PioneerClient()
    st.session_state.agent = TrialArchitect(memory=memory, band=band, pioneer=pioneer)
    st.session_state.results_history: list[TrialDesignResult] = []
    st.session_state.evolution_chart_data: list[dict] = []


# ── Sidebar ─────────────────────────────────────────────────────
st.sidebar.title("🧪 Clarity")
st.sidebar.caption("Self-Evolving Trial Design Agent")

st.sidebar.header("Agent Status")
stats = st.session_state.agent.evolution_stats
st.sidebar.metric("Designs Evaluated", stats["designs_evaluated"])
st.sidebar.metric("Patterns in Memory", stats["patterns_stored"])
st.sidebar.metric("Human Escalations", stats["human_escalations"])

st.sidebar.markdown("---")
st.sidebar.header("Partner Stack")
st.sidebar.markdown("""
- 🧠 **DeepMind** — advanced reasoning
- 🔧 **Guild AI** — agent lifecycle
- 👾 **Pioneer** — routine inference
- 🌐 **Actian** — vector memory
- 🤖 **Band** — human escalation
- 🔺 **Replay** — QA capture
""")


# ── Main layout ─────────────────────────────────────────────────
st.title("🧪 Clarity")
st.markdown(
    "**Design better clinical trials.** Simulate patient populations, "
    "assess statistical power, and evolve your agent with every design. "
    "Powered by DeepMind, Guild AI, Pioneer, Actian, Band & Replay."
)

# Input form
with st.expander("⚙️ **Trial Design Parameters**", expanded=True):
    col1, col2, col3 = st.columns(3)

    with col1:
        disease_area = st.text_input("Disease Area", "Hypertension")
        endpoint = st.text_input("Primary Endpoint", "Systolic BP Reduction (mmHg)")
        expected_effect = st.number_input(
            "Expected Treatment Effect", min_value=0.0, value=10.0, step=1.0,
            help="Mean difference between treatment and control",
        )

    with col2:
        variability = st.number_input(
            "Standard Deviation", min_value=1.0, value=15.0, step=1.0,
            help="Variability of the endpoint measurement",
        )
        n_per_arm = st.number_input(
            "Patients per Arm", min_value=10, max_value=5000, value=100, step=10
        )
        alpha = st.select_slider(
            "Significance Level (α)", options=[0.01, 0.025, 0.05, 0.10], value=0.05
        )

    with col3:
        target_power = st.select_slider(
            "Target Power", options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95], value=0.80
        )
        dropout_rate = st.slider(
            "Estimated Dropout Rate", 0.0, 0.50, 0.10, 0.05,
            help="Fraction of patients expected to drop out",
        )
        exclusion_rate = st.slider(
            "Estimated Exclusion Rate", 0.0, 0.50, 0.05, 0.05,
            help="Fraction of screened patients expected to be excluded",
        )

    run_button = st.button("🚀 **Run Simulation**", type="primary", use_container_width=True)


# ── Simulation runner ───────────────────────────────────────────
if run_button:
    with st.spinner("🧪 Simulating 10,000 virtual trials..."):
        request = TrialDesignRequest(
            disease_area=disease_area,
            endpoint=endpoint,
            expected_effect=expected_effect,
            variability=variability,
            n_per_arm=n_per_arm,
            alpha=alpha,
            target_power=target_power,
            dropout_rate=dropout_rate,
            estimated_exclusion_rate=exclusion_rate,
        )

        # Run the agent
        import asyncio
        result = asyncio.run(st.session_state.agent.evaluate_design(request))

        # Store in history
        st.session_state.results_history.append(result)

        # Track evolution
        st.session_state.evolution_chart_data.append({
            "design": len(st.session_state.evolution_chart_data) + 1,
            "power": result.power_achieved,
            "viable": result.is_viable,
            "n": result.request.n_per_arm,
        })

    # ── Results display ─────────────────────────────────────────
    st.markdown("---")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_color = "normal" if result.power_achieved >= result.request.target_power else "inverse"
        st.metric(
            "Statistical Power",
            f"{result.power_achieved:.1%}",
            delta=f"Target: {result.request.target_power:.0%}",
            delta_color=delta_color,
        )

    with col2:
        st.metric(
            "95% CI (Lower)",
            f"{result.confidence_interval[0]:.1f}",
        )

    with col3:
        st.metric(
            "95% CI (Upper)",
            f"{result.confidence_interval[1]:.1f}",
        )

    with col4:
        if result.recommended_n_per_arm:
            st.metric(
                "Recommended N (per arm)",
                str(result.recommended_n_per_arm),
                delta=f"Current: {result.request.n_per_arm}",
                delta_color="inverse",
            )
        else:
            st.metric("Design Viable", "✅ Yes")

    # Viability
    if result.is_viable:
        st.success("✅ **Trial design is viable** — achieves target power as specified.")
    else:
        st.error("❌ **Trial design is underpowered** — consider increasing sample size.")

    # Risk flags
    if result.risk_flags:
        st.warning("⚠️ **Risk Flags**")
        for flag in result.risk_flags:
            st.markdown(f"- {flag}")

    # Agent advice
    if result.agent_advice:
        st.info(f"🤖 **Agent Advice**\n\n{result.agent_advice}")

    # Similar designs
    if result.similar_designs_found > 0:
        st.caption(f"📚 Found {result.similar_designs_found} similar past designs in Actian memory.")

    # Band conversation
    band_log = st.session_state.agent.band.get_log()
    if band_log:
        with st.expander("💬 **Band — Human Escalation Log**"):
            for entry in band_log:
                if entry["type"] == "escalation":
                    st.markdown(f"**🤖 Agent → Human** ({entry['room']})")
                    st.markdown(f"*{entry['message']}*")
                elif entry["type"] == "human_response":
                    st.markdown(f"**👤 {entry['human_id']}**")
                    st.markdown(f"*{entry['response']}*")
                st.markdown("---")


# ── Evolution dashboard ─────────────────────────────────────────
st.markdown("---")
st.header("📈 Agent Evolution")

if st.session_state.evolution_chart_data:
    df = pd.DataFrame(st.session_state.evolution_chart_data)

    # Power evolution chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["design"],
        y=df["power"],
        mode="lines+markers",
        name="Power Achieved",
        line=dict(color="#00CC96", width=3),
        marker=dict(size=10),
    ))
    fig.add_hline(
        y=df["power"].iloc[-1],  # Use last design's target_power
        line_dash="dash",
        line_color="orange",
        annotation_text=f"Target: {st.session_state.results_history[-1].request.target_power:.0%}",
    )
    fig.update_layout(
        title="Power Achieved Over Time (Learning Curve)",
        xaxis_title="Trial Design #",
        yaxis_title="Statistical Power",
        yaxis_tickformat=".0%",
        hovermode="x unified",
        height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sample size comparison
    if any(r.recommended_n_per_arm for r in st.session_state.results_history):
        fig2 = go.Figure()
        history = st.session_state.results_history
        design_nums = list(range(1, len(history) + 1))
        current_ns = [r.request.n_per_arm for r in history]
        recommended_ns = [
            r.recommended_n_per_arm if r.recommended_n_per_arm else r.request.n_per_arm
            for r in history
        ]
        fig2.add_trace(go.Bar(
            x=design_nums, y=current_ns, name="Current N",
            marker_color="#636EFA",
        ))
        fig2.add_trace(go.Bar(
            x=design_nums, y=recommended_ns, name="Recommended N",
            marker_color="#EF553B",
        ))
        fig2.update_layout(
            title="Sample Size: Current vs Recommended",
            xaxis_title="Trial Design #",
            yaxis_title="Patients per Arm",
            barmode="group",
            height=350,
        )
        st.plotly_chart(fig2, use_container_width=True)

else:
    st.info("Run your first simulation to see the evolution dashboard.")

# Memory viewer
with st.expander("📚 **Actian Memory Store**"):
    memory = st.session_state.agent.memory
    all_designs = memory.get_all()
    if all_designs:
        data = [
            {
                "ID": d.id,
                "Disease": d.disease_area,
                "N/Arm": d.n_per_arm,
                "Effect": d.treatment_effect,
                "Power": f"{d.power_achieved:.1%}",
                "Viable": "✅" if d.is_viable else "❌",
            }
            for d in all_designs
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True)
    else:
        st.caption("No designs stored yet. Run simulations to build memory.")

# Footer
st.markdown("---")
st.caption(
    "🧪 Clarity for tokens& Self-Evolving Agents Hackathon 2026 • "
    "Built with DeepMind, Guild AI, Pioneer, Actian, Band & Replay"
)
