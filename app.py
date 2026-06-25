"""
app.py
------
AI Business Idea Generator - Main Streamlit Application.

This is the entry point of the app. It is responsible for:
    1. Page configuration and global styling (custom CSS).
    2. Rendering the sidebar input form (budget, location, category,
       experience, weekly hours).
    3. Triggering idea generation when the user clicks the button.
    4. Rendering results as expandable, ranked cards with charts.
    5. Offering a PDF download of the full report.

Run locally with:
    streamlit run app.py
"""

import streamlit as st

from idea_generator import generate_ideas
from charts import build_startup_cost_chart, build_income_chart, build_score_chart
from pdf_export import generate_pdf_report


# ==========================================================================
# 1. PAGE CONFIGURATION
# ==========================================================================
st.set_page_config(
    page_title="AI Business Idea Generator",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ==========================================================================
# 2. GLOBAL CUSTOM CSS (modern, professional look)
# ==========================================================================
CUSTOM_CSS = """
<style>
    /* ---- General page polish ---- */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    /* ---- Hero header ---- */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(90deg, #6C5CE7, #00B894);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #636E72;
        margin-bottom: 1.5rem;
    }

    /* ---- Section headers ---- */
    .section-header {
        font-size: 1.4rem;
        font-weight: 700;
        color: #2D3436;
        margin-top: 1.2rem;
        margin-bottom: 0.6rem;
        border-left: 5px solid #6C5CE7;
        padding-left: 10px;
    }

    /* ---- Idea card rank badge ---- */
    .rank-badge {
        display: inline-block;
        background: linear-gradient(135deg, #6C5CE7, #a29bfe);
        color: white;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 4px 12px;
        border-radius: 20px;
        margin-right: 8px;
    }
    .score-badge-high {
        background: rgba(0, 184, 148, 0.15);
        color: #00B894;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .score-badge-mid {
        background: rgba(253, 203, 110, 0.2);
        color: #d68910;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }
    .score-badge-low {
        background: rgba(255, 118, 117, 0.15);
        color: #d63031;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
    }

    /* ---- Metric mini-cards inside expanders ---- */
    .mini-metric {
        background-color: rgba(108, 92, 231, 0.06);
        border-radius: 10px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .mini-metric-label {
        font-size: 0.78rem;
        color: #636E72;
        text-transform: uppercase;
        letter-spacing: 0.03em;
    }
    .mini-metric-value {
        font-size: 1.1rem;
        font-weight: 700;
        color: #2D3436;
    }

    /* ---- Sidebar polish ---- */
    section[data-testid="stSidebar"] {
        background-color: #FAFAFE;
    }

    /* ---- Footer ---- */
    .app-footer {
        text-align: center;
        color: #B2BEC3;
        font-size: 0.85rem;
        margin-top: 3rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ==========================================================================
# 3. SESSION STATE INITIALIZATION
# ==========================================================================
# We store generated ideas and input metadata in session_state so that
# results persist across reruns (e.g. when expanding a card or downloading
# the PDF), instead of being regenerated/lost on every interaction.
if "ideas" not in st.session_state:
    st.session_state.ideas = None
if "last_inputs" not in st.session_state:
    st.session_state.last_inputs = {}


# ==========================================================================
# 4. SIDEBAR - USER INPUT FORM
# ==========================================================================
with st.sidebar:
    st.markdown("## 💡 Your Profile")
    st.markdown(
        "Fill in your details below and let the AI generate tailored "
        "business ideas for you."
    )
    st.divider()

    budget = st.number_input(
        "💰 Available Budget (USD)",
        min_value=10,
        max_value=1_000_000,
        value=1000,
        step=50,
        help="The total amount of money you are able to invest to start the business.",
    )

    location = st.text_input(
        "📍 Country or City",
        value="Tashkent, Uzbekistan",
        placeholder="e.g. Tashkent, Uzbekistan",
        help="Used to tailor context such as local market validation steps.",
    )

    category = st.selectbox(
        "🎯 Area of Interest",
        options=[
            "Technology",
            "Agriculture",
            "Education",
            "Food",
            "E-commerce",
            "Health",
            "Other",
        ],
        index=0,
        help="Pick the industry you are most interested in starting a business in.",
    )

    experience = st.selectbox(
        "🧠 Experience Level",
        options=["Beginner", "Intermediate", "Advanced"],
        index=0,
        help="Your current level of business or industry experience.",
    )

    weekly_hours = st.slider(
        "⏰ Time Available per Week (hours)",
        min_value=1,
        max_value=80,
        value=15,
        help="How many hours per week you can realistically dedicate to this business.",
    )

    st.divider()

    generate_clicked = st.button(
        "🚀 Generate Business Ideas", use_container_width=True, type="primary"
    )

    st.markdown(
        "<div style='font-size:0.8rem; color:#888; margin-top: 1rem;'>"
        "Ideas are generated using a rule-based recommendation engine "
        "tailored to your budget, location, and goals."
        "</div>",
        unsafe_allow_html=True,
    )


# ==========================================================================
# 5. HERO HEADER
# ==========================================================================
st.markdown(
    '<div class="hero-title">AI Business Idea Generator 💡</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="hero-subtitle">Get 5 personalized, ranked business ideas '
    "based on your budget, location, interests, experience, and available time.</div>",
    unsafe_allow_html=True,
)


# ==========================================================================
# 6. IDEA GENERATION TRIGGER
# ==========================================================================
if generate_clicked:
    if not location.strip():
        st.warning("Please enter a country or city before generating ideas.")
    else:
        with st.spinner("Analyzing your profile and generating tailored business ideas..."):
            ideas = generate_ideas(
                budget=float(budget),
                location=location.strip(),
                category=category,
                experience=experience,
                weekly_hours=int(weekly_hours),
                num_ideas=5,
            )
        st.session_state.ideas = ideas
        st.session_state.last_inputs = {
            "budget": budget,
            "location": location.strip(),
            "category": category,
            "experience": experience,
            "weekly_hours": weekly_hours,
        }


# ==========================================================================
# 7. RESULTS DISPLAY
# ==========================================================================
ideas = st.session_state.ideas

if ideas is None:
    # ---- Empty state: shown before the user generates anything ----------
    st.info(
        "👈 Fill in your profile in the sidebar and click **Generate Business "
        "Ideas** to get started."
    )
    st.markdown("### What you'll get:")
    cols = st.columns(4)
    feature_list = [
        ("📊", "5 ranked business ideas", "Sorted from best to worst fit for your profile."),
        ("💵", "Cost & income estimates", "Startup cost and monthly income ranges."),
        ("📈", "Visual comparisons", "Interactive charts comparing all 5 ideas."),
        ("📄", "Downloadable PDF", "Take your personalized report anywhere."),
    ]
    for col, (icon, title, desc) in zip(cols, feature_list):
        with col:
            st.markdown(
                f"<div class='mini-metric'>"
                f"<div style='font-size:1.6rem'>{icon}</div>"
                f"<div class='mini-metric-value' style='font-size:0.95rem'>{title}</div>"
                f"<div class='mini-metric-label' style='text-transform:none; font-size:0.8rem'>{desc}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

else:
    inputs = st.session_state.last_inputs

    # ---- Summary banner of the user's profile -----------------------------
    st.markdown('<div class="section-header">Your Profile Summary</div>', unsafe_allow_html=True)
    summary_cols = st.columns(5)
    summary_items = [
        ("Budget", f"${inputs['budget']:,.0f}"),
        ("Location", inputs["location"]),
        ("Interest", inputs["category"]),
        ("Experience", inputs["experience"]),
        ("Time/Week", f"{inputs['weekly_hours']} hrs"),
    ]
    for col, (label, value) in zip(summary_cols, summary_items):
        with col:
            st.markdown(
                f"<div class='mini-metric'>"
                f"<div class='mini-metric-label'>{label}</div>"
                f"<div class='mini-metric-value'>{value}</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    # ---- Charts section -----------------------------------------------------
    st.markdown('<div class="section-header">📊 Visual Comparison</div>', unsafe_allow_html=True)

    chart_tab1, chart_tab2, chart_tab3 = st.tabs(
        ["💰 Startup Cost", "📈 Monthly Income", "🏆 Viability Score"]
    )
    with chart_tab1:
        st.plotly_chart(build_startup_cost_chart(ideas), use_container_width=True)
    with chart_tab2:
        st.plotly_chart(build_income_chart(ideas), use_container_width=True)
    with chart_tab3:
        st.plotly_chart(build_score_chart(ideas), use_container_width=True)

    # ---- Ranked idea cards ---------------------------------------------------
    st.markdown('<div class="section-header">🏆 Your Ranked Business Ideas</div>', unsafe_allow_html=True)

    def _score_badge_html(score: int) -> str:
        """Return the appropriate colored HTML badge for a given score."""
        if score >= 75:
            css_class = "score-badge-high"
        elif score >= 50:
            css_class = "score-badge-mid"
        else:
            css_class = "score-badge-low"
        return f"<span class='{css_class}'>Score: {score}/100</span>"

    for idea in ideas:
        # Medal emoji for the top 3 ranked ideas, for a nice visual touch.
        medal = {1: "🥇", 2: "🥈", 3: "🥉"}.get(idea.rank, "🔹")

        header = (
            f"{medal} #{idea.rank} — {idea.name}  |  Score: {idea.score}/100"
        )
        with st.expander(header, expanded=(idea.rank == 1)):
            # Rank + score badges row
            st.markdown(
                f"<span class='rank-badge'>Rank #{idea.rank}</span>"
                f"{_score_badge_html(idea.score)}",
                unsafe_allow_html=True,
            )
            st.write("")

            # 1. & 2. Business name & description
            st.markdown(f"**{idea.name}**")
            st.write(idea.description)

            # Key metrics in 4 mini-columns: cost, income, difficulty, customers
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.markdown(
                    f"<div class='mini-metric'>"
                    f"<div class='mini-metric-label'>3. Estimated Startup Cost</div>"
                    f"<div class='mini-metric-value'>${idea.startup_cost_min:,.0f} - "
                    f"${idea.startup_cost_max:,.0f}</div></div>",
                    unsafe_allow_html=True,
                )
            with m_col2:
                st.markdown(
                    f"<div class='mini-metric'>"
                    f"<div class='mini-metric-label'>9. Monthly Income Range</div>"
                    f"<div class='mini-metric-value'>${idea.monthly_income_min:,.0f} - "
                    f"${idea.monthly_income_max:,.0f}</div></div>",
                    unsafe_allow_html=True,
                )
            with m_col3:
                st.markdown(
                    f"<div class='mini-metric'>"
                    f"<div class='mini-metric-label'>8. Difficulty Level</div>"
                    f"<div class='mini-metric-value'>{idea.difficulty}</div></div>",
                    unsafe_allow_html=True,
                )

            st.write("")

            # 4. Target customers
            st.markdown("**4. Target Customers**")
            st.write(idea.target_customers)

            # 5. Revenue model
            st.markdown("**5. Revenue Model**")
            st.write(idea.revenue_model)

            # 6. & 7. Advantages and risks side by side
            adv_col, risk_col = st.columns(2)
            with adv_col:
                st.markdown("**6. ✅ Advantages**")
                for adv in idea.advantages:
                    st.markdown(f"- {adv}")
            with risk_col:
                st.markdown("**7. ⚠️ Risks**")
                for risk in idea.risks:
                    st.markdown(f"- {risk}")

            # 10. First 5 steps
            st.markdown("**10. 🪜 First 5 Steps to Start**")
            for i, step in enumerate(idea.first_steps, start=1):
                st.markdown(f"{i}. {step}")

    # ---- PDF Download Section ---------------------------------------------
    st.markdown('<div class="section-header">📄 Download Your Report</div>', unsafe_allow_html=True)
    st.write(
        "Download a complete PDF report with all 5 business ideas, ready to "
        "save, print, or share."
    )

    pdf_bytes = generate_pdf_report(
        ideas=ideas,
        budget=inputs["budget"],
        location=inputs["location"],
        category=inputs["category"],
        experience=inputs["experience"],
        weekly_hours=inputs["weekly_hours"],
    )

    st.download_button(
        label="⬇️ Download PDF Report",
        data=pdf_bytes,
        file_name="business_idea_report.pdf",
        mime="application/pdf",
        use_container_width=True,
        type="primary",
    )


# ==========================================================================
# 8. FOOTER
# ==========================================================================
st.markdown(
    "<div class='app-footer'>Built with Streamlit • AI Business Idea Generator "
    "• Estimates are for planning purposes only</div>",
    unsafe_allow_html=True,
)
