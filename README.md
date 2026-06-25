# 💡 AI Business Idea Generator

A modern, professional **Streamlit** web application that generates 5
personalized, ranked business ideas based on a user's budget, location,
area of interest, experience level, and available time per week.

Each idea includes a business name, description, estimated startup cost,
target customers, revenue model, advantages, risks, difficulty level,
expected monthly income range, and the first 5 steps to get started —
plus a 1–100 viability score, interactive charts, and a downloadable PDF
report.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- 🎯 **Personalized input form** in a clean sidebar (budget, location,
  category, experience level, weekly hours).
- 🤖 **Smart idea generation engine** — a rule-based recommendation system
  that scales startup costs and income estimates to the user's actual
  budget and context (no external API key required, 100% free to run).
- 🏆 **1–100 viability score** for every idea, automatically ranked from
  best to worst fit.
- 📂 **Expandable idea cards** showing all 10 required details per idea.
- 📊 **Interactive charts** (Plotly) comparing startup cost, potential
  monthly income, and viability score across all ideas.
- 📄 **One-click PDF export** of the full personalized report.
- 🎨 **Modern, responsive UI** with custom styling, works well on desktop
  and mobile browsers.
- 🚀 **Zero-configuration deployment** — ready to push to GitHub and
  deploy on Streamlit Community Cloud with no secrets or API keys needed.

---

## 📁 Project Structure

```
ai-business-idea-generator/
├── app.py                  # Main Streamlit application (UI + page logic)
├── idea_generator.py       # Core idea-generation engine & scoring logic
├── charts.py               # Plotly chart builders (cost, income, score)
├── pdf_export.py           # PDF report generation (ReportLab)
├── requirements.txt        # Python dependencies
├── .streamlit/
│   └── config.toml         # Streamlit theme & server configuration
├── .gitignore
└── README.md                # You are here
```

---

## 🧠 How It Works

The app does **not** require an external AI/LLM API key. Instead,
`idea_generator.py` contains a curated knowledge base of realistic business
templates grouped by category (Technology, Agriculture, Education, Food,
E-commerce, Health, Other). When a user submits their profile:

1. Five relevant templates are selected for the chosen category.
2. Each template's startup cost is **scaled to the user's actual budget**.
3. Monthly income is estimated using a heuristic model that factors in
   difficulty, experience level, and weekly time commitment.
4. A **viability score (1–100)** is computed based on affordability,
   experience/difficulty match, and time availability.
5. Ideas are sorted from highest to lowest score (best to worst fit).

> 💡 Want to use a real LLM (OpenAI, Anthropic, etc.) instead? You can
> replace the body of `generate_ideas()` in `idea_generator.py` with an
> API call — as long as you return the same `BusinessIdea` data structure,
> the rest of the app (UI, charts, PDF) will keep working without changes.

---

## 🖥️ Local Installation

### Prerequisites
- Python 3.9 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/ai-business-idea-generator.git
   cd ai-business-idea-generator
   ```

2. **(Recommended) Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate      # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```bash
   streamlit run app.py
   ```

5. Open your browser at the URL shown in the terminal
   (usually `http://localhost:8501`).

---

## ☁️ Deploying to Streamlit Community Cloud

This project is **ready to deploy as-is** — no modifications, secrets, or
API keys required.

1. **Push the project to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit: AI Business Idea Generator"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/ai-business-idea-generator.git
   git push -u origin main
   ```

2. **Go to Streamlit Community Cloud**
   - Visit [share.streamlit.io](https://share.streamlit.io)
   - Sign in with your GitHub account.

3. **Create a new app**
   - Click **"New app"**.
   - Select your repository: `YOUR_USERNAME/ai-business-idea-generator`.
   - Set the branch to `main`.
   - Set the main file path to `app.py`.

4. **Deploy**
   - Click **"Deploy"**.
   - Streamlit Cloud will automatically install everything listed in
     `requirements.txt` and launch your app.
   - Your app will be live at a URL like:
     `https://your-app-name.streamlit.app`

That's it — no environment variables, secrets, or external services need
to be configured.

---

## 🛠️ Tech Stack

| Component        | Technology      |
|-------------------|-----------------|
| Web framework     | [Streamlit](https://streamlit.io)      |
| Charts            | [Plotly](https://plotly.com/python/)   |
| PDF generation    | [ReportLab](https://www.reportlab.com/) |
| Data handling     | [Pandas](https://pandas.pydata.org/)   |
| Language          | Python 3.9+     |

---

## 📌 Notes & Disclaimers

- All financial figures (startup costs, monthly income estimates, and
  viability scores) are **heuristic estimates for planning purposes only**.
  They are not financial advice and do not guarantee real-world outcomes.
- Always validate any business idea with real market research before
  investing time or money.

---

## 📄 License

This project is provided under the MIT License. Feel free to use, modify,
and distribute it for personal or commercial projects.

---

## 🙌 Acknowledgements

Built with ❤️ using Streamlit, Plotly, and ReportLab.
