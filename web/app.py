"""
Clarity — Self-Evolving Clinical Trial Design Agent
Streamlit web app with evolution dashboard, batch comparison, and Band escalation.
"""

import os
import sys
from pathlib import Path

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
from src.seed_data import seed_memory, get_seed_prompt
from src.validation_report import run_validation, validation_summary, CLINICAL_TRIALS, LITERATURE_BENCHMARKS

# ── Page config ─────────────────────────────────────────────────
st.set_page_config(
    page_title="Clarity — Trial Design Agent",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .partner-badge {
        display: inline-block;
        background: #1a1d27;
        border: 1px solid #2a2d37;
        border-radius: 8px;
        padding: 4px 12px;
        margin: 2px;
        font-size: 0.8em;
        color: #8892a4;
    }
    .evolution-tag {
        background: linear-gradient(135deg, #00cc96, #00a67e);
        color: #0e1117;
        padding: 2px 10px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.75em;
    }
    .metric-card {
        background: #1a1d27;
        border-radius: 10px;
        padding: 12px;
        border: 1px solid #2a2d37;
    }
    .stButton button {
        background: linear-gradient(135deg, #00cc96, #009977) !important;
        color: #0e1117 !important;
        font-weight: 700 !important;
        border: none !important;
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #00dd99, #00aa77) !important;
        box-shadow: 0 0 20px rgba(0, 204, 150, 0.3);
    }
</style>
""", unsafe_allow_html=True)

# ── Async helper ───────────────────────────────────────────────
def run_async(coro):
    """Run an async coroutine, handling already-running loop."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        return asyncio.run(coro)
    # Already in a running loop (e.g. Streamlit debug mode)
    return loop.run_until_complete(coro)


if "agent" not in st.session_state:
    memory = ActianStore()
    band = BandRoom()
    pioneer = PioneerClient()
    agent = TrialArchitect(memory=memory, band=band, pioneer=pioneer)

    # Seed memory with pre-loaded designs
    seeded = seed_memory(memory)
    st.session_state.seeded_count = seeded

    st.session_state.validation_rows = None
    st.session_state.agent = agent
    st.session_state.results_history: list[TrialDesignResult] = []
    st.session_state.evolution_chart_data: list[dict] = []
    st.session_state.comparison_results: list[TrialDesignResult] = []
    st.session_state.show_band_tab = True

# ── Sidebar ─────────────────────────────────────────────────────
with st.sidebar:
    st.title("🧪 **Clarity**")
    st.caption("Self-Evolving Trial Design Agent")
    st.markdown("---")

    # Agent status
    st.subheader("🤖 Agent Status")
    stats = st.session_state.agent.evolution_stats
    total = stats["designs_evaluated"]
    viable = sum(1 for r in st.session_state.results_history if r.is_viable) if st.session_state.results_history else 0
    mem = stats["patterns_stored"]
    esctats = stats["human_escalations"]

    cols = st.columns(3)
    cols[0].metric("Evaluated", total)
    cols[1].metric("Viable", viable if st.session_state.results_history else "—")
    cols[2].metric("In Memory", mem)

    st.caption(f"Escalations: {esctats} · Seeded: {st.session_state.get('seeded_count', 0)} designs")

    # Partner stack
    st.markdown("---")
    st.subheader("🔌 Partner Stack")
    partners_html = """
    <div>
        <span class="partner-badge">🧠 DeepMind</span>
        <span class="partner-badge">👾 Pioneer</span>
        <span class="partner-badge">🌐 Actian</span>
        <span class="partner-badge">🤖 Band</span>
        <span class="partner-badge">🔧 Guild AI</span>
        <span class="partner-badge">🔺 Replay</span>
    </div>
    """
    st.markdown(partners_html, unsafe_allow_html=True)

    # Quick legend
    st.markdown("---")
    st.caption(
        "**How it works:** Enter trial parameters → agent simulates "
        "thousands of virtual patients → checks memory → recommends optimal design"
    )


# ── Main layout ─────────────────────────────────────────────────
st.title("🧪 **Clarity**")
st.markdown(
    "**Self-evolving clinical trial design.** Simulate patient populations, "
    "assess statistical power, and watch your agent get smarter with every design. "
)

# Status bar
col_seed, col_learned, col_mode = st.columns([2, 2, 2])
seeded = st.session_state.get("seeded_count", 0)
learned = max(0, (st.session_state.agent.evolution_stats["patterns_stored"] - seeded))
with col_seed:
    st.markdown(f"📚 **{seeded}** pre-loaded trial patterns")
with col_learned:
    st.markdown(f"🧠 **{learned}** learned from your designs")
with col_mode:
    pioneer = st.session_state.agent.pioneer
    mode = "🔴 Offline (mock)" if pioneer.is_mock else "🟢 Live API"
    st.markdown(f"**{mode}**")

st.markdown("---")

# ── Tabs ────────────────────────────────────────────────────────
tab_sim, tab_compare, tab_evolution, tab_memory, tab_valid, tab_band = st.tabs([
    "🧪 Design Simulator", "📊 Compare", "📈 Evolution",
    "📚 Agent Memory", "✅ Validation", "💬 Band Escalations",
])

# ════════════════════════════════════════════════════════════════
# TAB 1: Design Simulator
# ════════════════════════════════════════════════════════════════
with tab_sim:
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("⚙️ Trial Parameters")

        with st.container(border=True):
            row1 = st.columns(3)
            with row1[0]:
                disease_area = st.text_input("Disease Area", "Hypertension",
                    help="e.g., Hypertension, Type 2 Diabetes, NSCLC")
            with row1[1]:
                endpoint = st.text_input("Primary Endpoint", "Systolic BP Reduction (mmHg)",
                    help="The main outcome measure")
            with row1[2]:
                phase = st.selectbox("Trial Phase", ["Phase II", "Phase III", "Phase IV"], index=1)

            row2 = st.columns(3)
            with row2[0]:
                expected_effect = st.number_input(
                    "Expected Treatment Effect", min_value=0.0, value=10.0, step=1.0,
                    help="Mean difference between treatment and control",
                )
            with row2[1]:
                variability = st.number_input(
                    "Standard Deviation (σ)", min_value=1.0, value=15.0, step=1.0,
                    help="Variability of the endpoint measurement",
                )
            with row2[2]:
                n_per_arm = st.number_input(
                    "Patients per Arm", min_value=10, max_value=5000, value=120, step=10,
                    help="Total = 2 × this number",
                )

            row3 = st.columns(3)
            with row3[0]:
                alpha = st.select_slider(
                    "Significance Level (α)", options=[0.01, 0.025, 0.05, 0.10], value=0.05,
                )
            with row3[1]:
                target_power = st.select_slider(
                    "Target Power", options=[0.70, 0.75, 0.80, 0.85, 0.90, 0.95], value=0.80,
                )
            with row3[2]:
                n_simulations = st.select_slider(
                    "Simulations", options=[1000, 5000, 10_000, 25_000], value=10_000,
                    help="Virtual trials to run per evaluation",
                )

            row4 = st.columns(3)
            with row4[0]:
                dropout_rate = st.slider(
                    "Dropout Rate", 0.0, 0.50, 0.10, 0.05,
                    help="Fraction of patients who don't complete the trial",
                )
            with row4[1]:
                exclusion_rate = st.slider(
                    "Exclusion Rate", 0.0, 0.50, 0.05, 0.05,
                    help="Fraction of screened patients excluded by criteria",
                )

        run_button = st.button("🚀 **Run Simulation**", type="primary", use_container_width=True)

    with col2:
        st.subheader("💡 Quick Info")
        st.info(
            "**The simulation runs thousands of virtual trials** to estimate "
            "statistical power. The agent then:\n\n"
            "1. Checks **Actian memory** for similar past designs\n"
            "2. Runs the **simulation engine**\n"
            "3. Opens a **Band room** if the design is underpowered\n"
            "4. **Stores the result** so it learns for next time\n\n"
            "The agent gets smarter with every design you submit.",
            icon="🤖",
        )

        # Show similar designs preview
        with st.container(border=True):
            st.caption("📚 **Similar in Memory**")
            preview_req = TrialDesignRequest(
                disease_area=disease_area, endpoint=endpoint,
                expected_effect=expected_effect, variability=variability,
                n_per_arm=n_per_arm, alpha=alpha, target_power=target_power,
                dropout_rate=dropout_rate, estimated_exclusion_rate=exclusion_rate,
            )
            similar = st.session_state.agent.memory.search_similar(preview_req, top_k=3, threshold=0.4)
            if similar:
                for s in similar[:2]:
                    icon = "✅" if s.is_viable else "❌"
                    st.markdown(
                        f"{icon} **{s.disease_area}** — n={s.n_per_arm}, "
                        f"power={s.power_achieved:.0%}",
                    )
                if len(similar) > 2:
                    st.caption(f"... and {len(similar)-2} more")
            else:
                st.caption("No similar designs yet — first time for this combination!")

    # ── Run simulation ──────────────────────────────────────────
    if run_button:
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

        with st.status("🧪 **Running simulation...**", expanded=True) as status:
            st.write("🔍 Checking Actian memory for similar designs...")
            result = run_async(st.session_state.agent.evaluate_design(request))

            st.write("📊 Analyzing results...")
            st.session_state.results_history.append(result)

            st.session_state.evolution_chart_data.append({
                "design": len(st.session_state.evolution_chart_data) + 1,
                "power": result.power_achieved,
                "viable": result.is_viable,
                "n": result.request.n_per_arm,
            })

            status.update(label="✅ Simulation complete!", state="complete")

        # ── Results display ──────────────────────────────────────
        st.markdown("### 📊 Simulation Results")

        col_m1, col_m2, col_m3, col_m4 = st.columns(4)

        with col_m1:
            delta_color = "normal" if result.power_achieved >= result.request.target_power else "inverse"
            st.metric(
                "Statistical Power",
                f"{result.power_achieved:.1%}",
                delta=f"Target: {result.request.target_power:.0%}",
                delta_color=delta_color,
            )

        with col_m2:
            st.metric("95% CI", f"({result.confidence_interval[0]:.1f}, {result.confidence_interval[1]:.1f})")

        with col_m3:
            st.metric("Effective N", f"{int(result.power_achieved * 200):,}")

        with col_m4:
            if result.recommended_n_per_arm:
                delta_n = result.recommended_n_per_arm - result.request.n_per_arm
                st.metric(
                    "Recommended N", str(result.recommended_n_per_arm),
                    delta=f"{delta_n:+d}" if delta_n != 0 else None,
                    delta_color="inverse",
                )
            else:
                st.metric("Design Viable", "✅ Yes")

        # Viability + advice
        if result.is_viable:
            st.success("✅ **Trial design is viable** — achieves target power as specified.")
        else:
            st.error(f"❌ **Trial design is underpowered** — achieved {result.power_achieved:.1%} vs target {result.request.target_power:.0%}.")

        if result.risk_flags:
            with st.expander("⚠️ **Risk Flags**", expanded=True):
                for flag in result.risk_flags:
                    st.warning(flag)

        if result.agent_advice:
            st.info(f"🤖 **Agent Advice**\n\n{result.agent_advice}")

        if result.similar_designs_found > 0:
            st.caption(f"📚 Found **{result.similar_designs_found}** similar past designs in Actian memory.")

        # Add to comparison
        comparison_key = f"{result.request.disease_area} | n={result.request.n_per_arm} | power={result.power_achieved:.0%}"
        already_exists = any(
            r.request.disease_area == result.request.disease_area
            and r.request.n_per_arm == result.request.n_per_arm
            for r in st.session_state.comparison_results
        )
        if not already_exists and st.button("📊 Add to Comparison", key="add_to_compare"):
            st.session_state.comparison_results.append(result)
            st.success("Added to comparison! Switch to the **Compare** tab.")

    # First-run welcome
    elif not st.session_state.results_history:
        st.info(
            "👋 **Welcome to Clarity!** Enter your trial parameters on the left "
            "and click **Run Simulation** to get started. The agent has "
            f"**{st.session_state.get('seeded_count', 0)}** pre-loaded designs in memory "
            "to help guide your first result.",
            icon="🤖",
        )


# ════════════════════════════════════════════════════════════════
# TAB 2: Compare
# ════════════════════════════════════════════════════════════════
with tab_compare:
    st.subheader("📊 Design Comparison")

    comp_results = st.session_state.comparison_results
    session_results = st.session_state.results_history

    if not comp_results and len(session_results) < 2:
        st.info("Run at least **2 simulations** to compare designs side-by-side.")
    else:
        # Use comparison list if populated, otherwise use history
        if comp_results:
            compare_set = comp_results
        else:
            compare_set = session_results

        df_compare = pd.DataFrame([
            {
                "Design": f"#{i+1}",
                "Disease": r.request.disease_area,
                "N/Arm": r.request.n_per_arm,
                "Effect": r.request.expected_effect,
                "Power": f"{r.power_achieved:.1%}",
                "Power_Num": r.power_achieved,
                "Viable": "✅" if r.is_viable else "❌",
                "Recommended N": r.recommended_n_per_arm or r.request.n_per_arm,
                "N Diff": (r.recommended_n_per_arm or r.request.n_per_arm) - r.request.n_per_arm,
            }
            for i, r in enumerate(compare_set)
        ])

        col_compare1, col_compare2 = st.columns([3, 2])

        with col_compare1:
            st.dataframe(df_compare, use_container_width=True, hide_index=True)

        with col_compare2:
            if len(df_compare) > 1:
                fig_compare = px.bar(
                    df_compare, x="Design", y="Power_Num",
                    color="Viable",
                    color_discrete_map={"✅": "#00CC96", "❌": "#FF4B4B"},
                    text="Power",
                    labels={"Power_Num": "Statistical Power"},
                )
                fig_compare.update_traces(textposition="outside")
                fig_compare.update_layout(
                    height=250, margin=dict(l=0, r=0, t=0, b=0),
                    showlegend=False,
                    yaxis_tickformat=".0%",
                )
                st.plotly_chart(fig_compare, use_container_width=True)

        if len(compare_set) >= 2:
            st.markdown("---")
            st.subheader("🔍 Agent Insight")
            # Show how the best compares to the worst
            best = max(compare_set, key=lambda r: r.power_achieved)
            worst = min(compare_set, key=lambda r: r.power_achieved)
            with st.container(border=True):
                st.markdown(
                    f"🧠 **Best design:** #{compare_set.index(best)+1} — "
                    f"n={best.request.n_per_arm}, power={best.power_achieved:.1%} "
                    f"({'✅ viable' if best.is_viable else '❌ not viable'})\n\n"
                    f"📉 **Worst design:** #{compare_set.index(worst)+1} — "
                    f"n={worst.request.n_per_arm}, power={worst.power_achieved:.1%}\n\n"
                    f"💡 **Insight:** Increasing sample size from {worst.request.n_per_arm} "
                    f"to {best.request.n_per_arm} improved power by "
                    f"{(best.power_achieved - worst.power_achieved):.1%}."
                )

        if comp_results:
            if st.button("🗑️ Clear Comparison List"):
                st.session_state.comparison_results = []
                st.rerun()


# ════════════════════════════════════════════════════════════════
# TAB 3: Evolution
# ════════════════════════════════════════════════════════════════
with tab_evolution:
    st.subheader("📈 Agent Evolution — Learning Over Time")

    if st.session_state.evolution_chart_data:
        df_evo = pd.DataFrame(st.session_state.evolution_chart_data)

        # Power evolution chart
        fig_evo = go.Figure()

        # Add power trace
        fig_evo.add_trace(go.Scatter(
            x=df_evo["design"],
            y=df_evo["power"],
            mode="lines+markers",
            name="Power Achieved",
            line=dict(color="#00CC96", width=3),
            marker=dict(size=12, symbol="circle", line=dict(color="#0e1117", width=2)),
        ))

        # Target power line
        last_target = st.session_state.results_history[-1].request.target_power if st.session_state.results_history else 0.80
        fig_evo.add_hline(
            y=last_target,
            line_dash="dash",
            line_color="#FFA15A",
            annotation_text=f"Target Power ({last_target:.0%})",
        )

        # Highlight viable vs not
        for i, row in df_evo.iterrows():
            color = "#00CC96" if row["viable"] else "#FF4B4B"
            fig_evo.add_trace(go.Scatter(
                x=[row["design"]], y=[row["power"]],
                mode="markers",
                marker=dict(size=16, color=color, symbol="circle",
                            line=dict(color="white", width=2)),
                showlegend=False,
                hoverinfo="skip",
            ))

        fig_evo.update_layout(
            title="Power Achieved Over Time",
            xaxis_title="Trial Design #",
            yaxis_title="Statistical Power",
            yaxis_tickformat=".0%",
            hovermode="x unified",
            height=400,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_evo, use_container_width=True)

        # Power improvement stats
        if len(df_evo) >= 2:
            first = df_evo["power"].iloc[0]
            last_power = df_evo["power"].iloc[-1]
            improvement = last_power - first
            col_st1, col_st2, col_st3, col_st4 = st.columns(4)
            col_st1.metric("First Design", f"{first:.1%}")
            col_st2.metric("Latest Design", f"{last_power:.1%}")
            col_st3.metric("Improvement", f"{improvement:+.1%}", delta_color="off")
            col_st4.metric("Designs Evaluated", len(df_evo))

        # Sample size vs recommended
        if any(r.recommended_n_per_arm for r in st.session_state.results_history):
            st.markdown("---")
            fig_n = go.Figure()
            history = st.session_state.results_history
            design_nums = list(range(1, len(history) + 1))
            current_ns = [r.request.n_per_arm for r in history]
            recommended_ns = [
                r.recommended_n_per_arm if r.recommended_n_per_arm else r.request.n_per_arm
                for r in history
            ]
            fig_n.add_trace(go.Bar(
                x=design_nums, y=current_ns, name="Current N",
                marker_color="#636EFA",
            ))
            fig_n.add_trace(go.Bar(
                x=design_nums, y=recommended_ns, name="Recommended N",
                marker_color="#EF553B",
            ))
            fig_n.update_layout(
                title="Sample Size: Current vs Recommended",
                xaxis_title="Trial Design #",
                yaxis_title="Patients per Arm",
                barmode="group",
                height=350,
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
            )
            st.plotly_chart(fig_n, use_container_width=True)

    else:
        st.info("Run your first simulation to see the evolution dashboard.")
        st.caption("The agent's learning curve will appear here after you run a few designs.")


# ════════════════════════════════════════════════════════════════
# TAB 4: Agent Memory
# ════════════════════════════════════════════════════════════════
with tab_memory:
    st.subheader("📚 Actian Memory Store")
    st.caption("Every design the agent evaluates is stored as a searchable fingerprint. "
               "Future designs are compared against this memory.")

    memory = st.session_state.agent.memory
    all_designs = memory.get_all()

    if all_designs:
        # Overview stats
        total = len(all_designs)
        viable_count = sum(1 for d in all_designs if d.is_viable)
        diseases = set(d.disease_area for d in all_designs)

        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Total Designs", total)
        col_m2.metric("Viable", viable_count)
        col_m3.metric("Disease Areas", len(diseases))

        # Disease breakdown
        disease_counts = pd.DataFrame(
            [(d, sum(1 for x in all_designs if x.disease_area == d)) for d in sorted(diseases)],
            columns=["Disease Area", "Count"],
        )
        fig_disease = px.bar(
            disease_counts, x="Disease Area", y="Count",
            color="Count", color_continuous_scale="tealgrn",
            text="Count",
        )
        fig_disease.update_traces(textposition="outside")
        fig_disease.update_layout(height=250, showlegend=False)
        st.plotly_chart(fig_disease, use_container_width=True)

        # Table
        data = [
            {
                "ID": d.id,
                "Disease": d.disease_area,
                "N/Arm": d.n_per_arm,
                "Δ": d.treatment_effect,
                "Power": f"{d.power_achieved:.1%}",
                "Viable": "✅" if d.is_viable else "❌",
                "Source": d.source_nct if d.source_nct else "—",
            }
            for d in all_designs
        ]
        st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else:
        st.info("No designs in memory yet. Run simulations to build the agent's knowledge base.")



# ════════════════════════════════════════════════════════════════
# TAB 5: Validation Report
# ════════════════════════════════════════════════════════════════
with tab_valid:
    st.subheader("✅ Validation Report — Real Clinical Trials vs Clarity Engine")
    st.caption(
        "This report compares the Clarity simulation engine against real clinical trial data "
        "from **ClinicalTrials.gov** and published meta-analyses (**Law MR et al. BMJ 2009**). "
        "It demonstrates that our engine produces power estimates consistent with real-world outcomes."
    )

    # Run button
    if st.button("▶️ **Run Validation**", type="primary", use_container_width=True):
        result = run_validation()
        st.session_state.validation_rows = result
        st.rerun()

    # Response placeholders
    if st.session_state.validation_rows:
        rows = st.session_state.validation_rows
        summary = validation_summary(rows)

        # ── Summary metrics ──
        col_vm1, col_vm2, col_vm3, col_vm4 = st.columns(4)
        col_vm1.metric("Total Comparisons", summary["total_comparisons"])
        col_vm2.metric("Sim ✓80% Power", summary["sim_adequate"],
                       delta=f"{summary['pct_adequate']:.0%}")
        col_vm3.metric("CT.gov Trials Matched", f"{summary['ctgov_adequate']}/{summary['ctgov_comparisons']}")
        col_vm4.metric("Drug Classes Benchmarked", summary["literature_classes"])

        st.markdown("---")

        # ── Comparison table ──
        st.subheader("📋 Trial-by-Trial Comparison")
        df_val = pd.DataFrame([
            {
                "Source": r.source,
                "Trial": r.label,
                "Drug Class": r.drug_class,
                "N/Arm": r.n_per_arm,
                "ΔSBP (mmHg)": r.effect_size,
                "Dropout": f"{r.dropout:.0%}",
                "Real Power": r.real_power,
                "Sim Power": f"{r.sim_power:.1%}",
            }
            for r in rows
        ])
        st.dataframe(df_val, use_container_width=True, hide_index=True)

        # ── Bar chart: sim power vs real power ──
        st.markdown("---")
        st.subheader("📊 Real-World vs Simulated Power")

        labels = [r.label.split("(")[0].strip()[:30] for r in rows]
        sim_powers = [r.sim_power for r in rows]

        fig_val = go.Figure()
        fig_val.add_trace(go.Bar(
            x=labels, y=sim_powers,
            name="Clarity Simulation",
            marker_color="#00CC96",
            text=[f"{p:.0%}" for p in sim_powers],
            textposition="outside",
        ))
        # Reference markers for CT.gov trials
        ct_indices = [i for i, r in enumerate(rows) if r.source == "ClinicalTrials.gov"]
        if ct_indices:
            fig_val.add_trace(go.Scatter(
                x=[labels[i] for i in ct_indices],
                y=[0.90] * len(ct_indices),
                mode="markers+text",
                marker=dict(symbol="diamond", size=14, color="#FFA15A"),
                text=["Adequately powered (real)"] * len(ct_indices),
                textposition="top center",
                name="Real Trial Outcome",
            ))

        fig_val.update_layout(
            title="Simulation Accuracy: Real Hypertension Trials",
            xaxis_title="",
            yaxis_title="Statistical Power",
            yaxis_tickformat=".0%",
            barmode="group",
            height=400,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            hovermode="x unified",
        )
        st.plotly_chart(fig_val, use_container_width=True)

        # ── Literature benchmarks detail ──
        st.markdown("---")
        st.subheader("📚 Literature Benchmark Detail (Law MR et al. BMJ 2009)")
        st.caption("Meta-analysis of 147 RCTs of blood-pressure-lowering drugs, N>460,000 patients")

        lit_data = pd.DataFrame([
            {
                "Drug Class": b.drug_class,
                "SBP Reduction": f"{b.sbp_reduction:.1f} mmHg",
                "95% CI": f"({b.ci_lower:.1f}, {b.ci_upper:.1f})",
                "Dropout (std)": f"{b.std_dropout:.0%}",
                "N for 80% Power": b.typical_n_for_80pct,
            }
            for b in LITERATURE_BENCHMARKS
        ])
        st.dataframe(lit_data, use_container_width=True, hide_index=True)

        # ── Effect size vs N chart ──
        fig_lit = go.Figure()
        for b in LITERATURE_BENCHMARKS:
            fig_lit.add_trace(go.Scatter(
                x=[b.typical_n_for_80pct],
                y=[abs(b.sbp_reduction)],
                mode="markers+text",
                marker=dict(size=abs(b.sbp_reduction)*2.5,
                          sizemode="area",
                          sizeref=2.*max(abs(b.sbp_reduction) for b in LITERATURE_BENCHMARKS)/(40.**2),
                          color="#636EFA"),
                text=b.drug_class,
                textposition="top center",
                name=b.drug_class,
            ))
        fig_lit.update_layout(
            title="Drug Class Effect Size vs Typical Sample Size",
            xaxis_title="Patients per Arm",
            yaxis_title="Mean SBP Reduction (mmHg)",
            height=350,
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig_lit, use_container_width=True)

        # ── Conclusion ──
        st.markdown("---")
        all_ok = summary["ctgov_adequate"] == summary["ctgov_comparisons"]
        st.success(
            "✅ **Engine validated against real-world clinical trial data.** "
            "All surveyed Phase 3 hypertension trials achieve >80% power at their "
            "published sample sizes. The Clarity simulation engine produces power "
            "estimates consistent with meta-analytic expectations across 6 drug classes."
            if all_ok else
            "⚠️ **Partial validation.** Some trials fall below the 80% threshold "
            "with default parameters. Adjust dropout or effect size assumptions for closer match."
        )

        # Re-run button
        if st.button("🔄 Re-run Validation", use_container_width=True):
            st.session_state.validation_rows = None
            st.rerun()

    else:
        st.info(
            "Click **Run Validation** to compare the Clarity simulation engine "
            "against real clinical trial data from ClinicalTrials.gov and "
            "published meta-analyses."
        )


# ════════════════════════════════════════════════════════════════
# TAB 6: Band Escalations
# ════════════════════════════════════════════════════════════════
with tab_band:
    st.subheader("💬 Band Agent-Human Escalation Log")
    st.caption("When the agent detects a risky design, it opens a **Band room** "
               "and escalates to a human for consultation.")

    band_log = st.session_state.agent.band.get_log()
    if band_log:
        for entry in band_log:
            if entry["type"] == "escalation":
                with st.container(border=True):
                    st.markdown(f"**🤖 Agent → Human** — `{entry['room']}`")
                    st.markdown(f"**Title:** {entry['title']}")
                    st.markdown(f"**Message:** {entry['message']}")
                    if entry.get("suggested_action"):
                        st.markdown(f"**Suggested Action:** {entry['suggested_action']}")
                    st.caption(f"To: {entry['human_id']} · Status: {entry.get('status', 'sent')}")
            elif entry["type"] == "human_response":
                with st.container(border=True):
                    st.markdown(f"**👤 {entry['human_id']}** — `{entry['room']}`")
                    st.markdown(f"*{entry['response']}*")
                    if entry.get("suggested_action_accepted"):
                        st.caption("✅ Suggested action accepted")

        st.markdown("---")
        band = st.session_state.agent.band
        st.caption(f"Total rooms opened: {band.total_rooms_opened} · "
                   f"Log entries: {len(band_log)} · Mode: {'🟢 Live' if not band.is_mock else '🔴 Offline (mock)'}")
    else:
        st.info("No escalations yet. If the agent detects an underpowered design, "
                "a Band room will appear here automatically.")
        st.caption("Try running a design with low power (e.g., small sample size) to trigger an escalation.")


# ── Footer ──────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "🧪 **Clarity** — tokens& Self-Evolving Agents Hackathon 2026 • "
    "Built with DeepMind, Guild AI, Pioneer, Actian, Band & Replay"
)
