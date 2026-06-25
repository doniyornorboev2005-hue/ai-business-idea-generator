"""
idea_generator.py
------------------
Core "AI" logic for the AI Business Idea Generator app.

This module contains a rule-based / template-driven generation engine that
produces realistic, budget-aware, and context-aware business ideas based on
user inputs (budget, location, interest area, experience level, and weekly
time commitment).

NOTE ON "AI":
This generator does not call an external LLM API (no API key required),
which keeps the app 100% free to deploy on Streamlit Cloud without any
secrets/configuration. Instead, it uses a curated knowledge base of business
templates per category, combined with deterministic scoring and budget-aware
financial estimation logic. This mimics what an AI assistant would suggest,
while keeping the app fast, free, and dependency-light.

If desired, this module can easily be swapped to call OpenAI/Anthropic APIs
by replacing the `generate_ideas()` function body with an API call -- the
rest of the app (UI, PDF export, charts) does not need to change as long as
the same data structure is returned.
"""

import random
from dataclasses import dataclass, field
from typing import List


# --------------------------------------------------------------------------
# Data model
# --------------------------------------------------------------------------

@dataclass
class BusinessIdea:
    """Structured representation of a single generated business idea."""
    rank: int
    name: str
    description: str
    startup_cost_min: float
    startup_cost_max: float
    target_customers: str
    revenue_model: str
    advantages: List[str]
    risks: List[str]
    difficulty: str          # Easy / Medium / Hard
    monthly_income_min: float
    monthly_income_max: float
    first_steps: List[str] = field(default_factory=list)
    score: int = 0           # 1-100 viability score


# --------------------------------------------------------------------------
# Knowledge base: business templates grouped by category
# --------------------------------------------------------------------------
# Each template defines a "shape" of business. Concrete numbers are scaled
# at generation time based on the user's actual budget, so a $200 budget and
# a $20,000 budget produce sensibly different versions of the same idea.

CATEGORY_TEMPLATES = {
    "Technology": [
        {
            "name": "Freelance Web & App Development Studio",
            "description": "A lean studio offering websites, landing pages, and simple "
                            "mobile apps to small businesses that need an online presence "
                            "but cannot afford large agencies.",
            "cost_ratio": (0.05, 0.25),
            "target_customers": "Local small businesses, startups, and solo entrepreneurs "
                                 "needing an affordable web/app presence.",
            "revenue_model": "Fixed-price project fees plus optional monthly maintenance "
                              "retainers (hosting, updates, support).",
            "advantages": ["Very low overhead", "Can be run remotely",
                           "Skills are highly transferable and scalable"],
            "risks": ["Income can be irregular between projects",
                      "Requires continuous learning to stay competitive"],
            "difficulty": "Medium",
        },
        {
            "name": "No-Code Automation Agency",
            "description": "Helping local businesses automate repetitive tasks "
                            "(invoicing, lead follow-up, scheduling) using no-code "
                            "tools, reducing the need for custom-coded software.",
            "cost_ratio": (0.03, 0.15),
            "target_customers": "SMEs that want efficiency gains without hiring developers.",
            "revenue_model": "Setup fees plus monthly subscription for maintaining "
                              "automations.",
            "advantages": ["Minimal technical barrier to start",
                           "Recurring revenue from maintenance contracts"],
            "risks": ["Clients may attempt to self-serve once it's set up",
                      "Tool subscription costs can erode margins"],
            "difficulty": "Easy",
        },
        {
            "name": "IT Support & Tech Repair Service",
            "description": "On-demand computer, phone, and small-office network "
                            "support for individuals and small businesses.",
            "cost_ratio": (0.1, 0.4),
            "target_customers": "Households and small offices without in-house IT staff.",
            "revenue_model": "Per-visit service fees and monthly support contracts.",
            "advantages": ["Strong local demand", "Low marketing cost via word of mouth"],
            "risks": ["Physically time-bound (limits scaling)",
                      "Requires reliable transportation"],
            "difficulty": "Easy",
        },
    ],
    "Agriculture": [
        {
            "name": "Urban Micro-Greens Farm",
            "description": "Growing high-value microgreens and herbs in a small "
                            "indoor or greenhouse space for sale to restaurants "
                            "and local consumers.",
            "cost_ratio": (0.2, 0.6),
            "target_customers": "Restaurants, juice bars, health-food stores, and "
                                 "direct consumers at farmers' markets.",
            "revenue_model": "Direct sales to restaurants and recurring weekly "
                              "subscription boxes for consumers.",
            "advantages": ["Fast crop cycle (7-14 days)", "High margin per square meter"],
            "risks": ["Requires consistent climate control",
                      "Perishable product needs fast distribution"],
            "difficulty": "Medium",
        },
        {
            "name": "Organic Fertilizer & Compost Production",
            "description": "Producing organic compost/fertilizer from agricultural "
                            "or food waste and selling to local farmers and gardeners.",
            "cost_ratio": (0.15, 0.5),
            "target_customers": "Small farmers, nurseries, and home gardeners "
                                 "seeking organic inputs.",
            "revenue_model": "Bulk and retail sales of packaged compost/fertilizer.",
            "advantages": ["Low raw material cost (often free waste)",
                          "Growing demand for organic farming inputs"],
            "risks": ["Production takes time (weeks to months)",
                      "Requires storage and basic processing space"],
            "difficulty": "Medium",
        },
        {
            "name": "Smallholder Poultry & Egg Business",
            "description": "Raising chickens for eggs and meat at small scale, "
                            "selling directly to local households and shops.",
            "cost_ratio": (0.3, 0.8),
            "target_customers": "Local households, restaurants, and small grocery shops.",
            "revenue_model": "Direct retail sales of eggs and poultry meat.",
            "advantages": ["Steady recurring demand", "Can start very small and scale up"],
            "risks": ["Disease risk to flock", "Feed costs can fluctuate"],
            "difficulty": "Easy",
        },
    ],
    "Education": [
        {
            "name": "Online Tutoring & Exam Prep Service",
            "description": "One-on-one or small-group online tutoring in academic "
                            "subjects, languages, or standardized test preparation.",
            "cost_ratio": (0.02, 0.1),
            "target_customers": "Students and parents seeking academic support "
                                 "or exam preparation.",
            "revenue_model": "Hourly tutoring fees and bundled course packages.",
            "advantages": ["Extremely low starting cost",
                          "Can operate fully online from anywhere"],
            "risks": ["Highly competitive market",
                      "Income depends on personal time availability"],
            "difficulty": "Easy",
        },
        {
            "name": "Skill-Based Workshop & Bootcamp Provider",
            "description": "Short, practical workshops teaching in-demand skills "
                            "(e.g. digital marketing, coding basics, design) to "
                            "career-switchers and students.",
            "cost_ratio": (0.1, 0.35),
            "target_customers": "Young professionals and students wanting practical, "
                                 "job-ready skills.",
            "revenue_model": "Workshop ticket sales and corporate training contracts.",
            "advantages": ["Can be delivered online or in person",
                          "Strong word-of-mouth growth potential"],
            "risks": ["Requires strong subject credibility/marketing",
                      "Curriculum needs continual updates"],
            "difficulty": "Medium",
        },
        {
            "name": "Educational Content & Online Course Platform",
            "description": "Creating and selling pre-recorded video courses on a "
                            "specific topic of expertise, distributed via an "
                            "online course platform.",
            "cost_ratio": (0.05, 0.2),
            "target_customers": "Self-learners worldwide interested in the course topic.",
            "revenue_model": "One-time course sales and tiered membership access.",
            "advantages": ["Scalable - sell to unlimited students once created",
                          "Passive income after initial production effort"],
            "risks": ["High upfront time investment with no guaranteed sales",
                      "Requires marketing to stand out among many courses"],
            "difficulty": "Medium",
        },
    ],
    "Food": [
        {
            "name": "Home-Based Specialty Food Business",
            "description": "Producing and selling a specialty food product "
                            "(baked goods, sauces, snacks) from a home kitchen "
                            "to local customers and shops.",
            "cost_ratio": (0.1, 0.4),
            "target_customers": "Local consumers, cafes, and small grocery stores.",
            "revenue_model": "Direct sales, local shop wholesale, and online orders.",
            "advantages": ["Low overhead with home-based production",
                          "Product can be tested and iterated quickly"],
            "risks": ["Local food safety regulations may apply",
                      "Limited production capacity without commercial kitchen"],
            "difficulty": "Easy",
        },
        {
            "name": "Cloud Kitchen / Delivery-Only Restaurant",
            "description": "A delivery-only food brand operating from a shared "
                            "or small rented kitchen, focused on a specific cuisine "
                            "niche, sold via delivery apps.",
            "cost_ratio": (0.3, 0.8),
            "target_customers": "Urban customers ordering food delivery via apps.",
            "revenue_model": "Per-order sales through delivery platforms and direct orders.",
            "advantages": ["No need for a dine-in storefront",
                          "Can test multiple food concepts cheaply"],
            "risks": ["Delivery platform commissions reduce margins",
                      "Highly competitive and trend-sensitive market"],
            "difficulty": "Medium",
        },
        {
            "name": "Mobile Food Cart / Street Food Stand",
            "description": "A mobile or stationary food cart serving a focused "
                            "menu of street food or beverages in high-foot-traffic areas.",
            "cost_ratio": (0.25, 0.7),
            "target_customers": "Foot traffic in busy urban areas, office workers, students.",
            "revenue_model": "Direct cash/card sales per transaction.",
            "advantages": ["Lower cost than a full restaurant",
                          "Flexible location based on demand"],
            "risks": ["Weather-dependent foot traffic",
                      "Permits may be required depending on location"],
            "difficulty": "Easy",
        },
    ],
    "E-commerce": [
        {
            "name": "Niche Dropshipping Store",
            "description": "An online store selling a curated range of products "
                            "in a specific niche, fulfilled directly by suppliers "
                            "without holding inventory.",
            "cost_ratio": (0.1, 0.35),
            "target_customers": "Online shoppers interested in the chosen product niche.",
            "revenue_model": "Retail markup between supplier cost and selling price.",
            "advantages": ["No inventory or warehousing required",
                          "Quick to launch and test multiple products"],
            "risks": ["Thin margins after advertising costs",
                      "Less control over shipping times and quality"],
            "difficulty": "Easy",
        },
        {
            "name": "Print-on-Demand Merchandise Brand",
            "description": "Designing custom apparel, mugs, and accessories that "
                            "are printed and shipped only after a sale is made.",
            "cost_ratio": (0.05, 0.2),
            "target_customers": "Fans of niche designs, communities, and gift buyers.",
            "revenue_model": "Markup on each printed item sold online.",
            "advantages": ["No upfront inventory cost",
                          "Easy to test many designs at low risk"],
            "risks": ["Lower per-unit margin than bulk manufacturing",
                      "Design needs to stand out in a saturated market"],
            "difficulty": "Easy",
        },
        {
            "name": "Curated Local Marketplace",
            "description": "An online marketplace or storefront aggregating "
                            "products from local artisans/producers and selling "
                            "them to a wider regional or national audience.",
            "cost_ratio": (0.15, 0.45),
            "target_customers": "Consumers seeking unique local/artisan products online.",
            "revenue_model": "Commission per sale or wholesale markup on listed products.",
            "advantages": ["Differentiated catalog vs. mass marketplaces",
                          "Supports and partners with local producers"],
            "risks": ["Requires coordinating multiple suppliers",
                      "Logistics complexity grows with catalog size"],
            "difficulty": "Medium",
        },
    ],
    "Health": [
        {
            "name": "Personal Fitness & Online Coaching",
            "description": "Providing personalized fitness training and coaching "
                            "programs, delivered in person and/or via video calls "
                            "and apps.",
            "cost_ratio": (0.05, 0.2),
            "target_customers": "Individuals seeking fitness guidance and accountability.",
            "revenue_model": "Monthly coaching subscriptions and session packages.",
            "advantages": ["Low equipment requirement to start",
                          "Recurring subscription revenue potential"],
            "risks": ["Income tied to personal time availability",
                      "Requires building trust/credibility to attract clients"],
            "difficulty": "Easy",
        },
        {
            "name": "Wellness & Mental Health Support Platform",
            "description": "A service connecting clients with wellness resources, "
                            "guided meditation, or licensed counseling referrals "
                            "through an online platform.",
            "cost_ratio": (0.1, 0.35),
            "target_customers": "Individuals seeking accessible mental wellness support.",
            "revenue_model": "Subscription fees and per-session booking commissions.",
            "advantages": ["Growing demand for accessible mental health services",
                          "Can operate with a distributed, remote team"],
            "risks": ["May require licensing/compliance depending on services offered",
                      "Trust and credibility take time to build"],
            "difficulty": "Hard",
        },
        {
            "name": "Healthy Meal Prep & Nutrition Service",
            "description": "Preparing and delivering healthy, portioned meals "
                            "based on customer dietary goals (weight loss, muscle "
                            "gain, allergies, etc.).",
            "cost_ratio": (0.2, 0.6),
            "target_customers": "Busy professionals and fitness-focused individuals.",
            "revenue_model": "Weekly/monthly meal plan subscriptions.",
            "advantages": ["Recurring subscription revenue",
                          "Differentiated by nutrition expertise"],
            "risks": ["Requires food-safe preparation and delivery logistics",
                      "Ingredient costs can fluctuate"],
            "difficulty": "Medium",
        },
    ],
    "Other": [
        {
            "name": "Personal Branding & Social Media Management Agency",
            "description": "Managing social media content, posting schedules, "
                            "and growth strategy for small businesses and personal "
                            "brands.",
            "cost_ratio": (0.03, 0.15),
            "target_customers": "Small businesses and individuals who lack time or "
                                 "skill to manage their own social media.",
            "revenue_model": "Monthly retainer fees per client managed.",
            "advantages": ["Very low startup cost", "Can be done fully remotely"],
            "risks": ["Highly competitive niche",
                      "Client results can be hard to guarantee"],
            "difficulty": "Easy",
        },
        {
            "name": "Event Planning & Coordination Service",
            "description": "Planning and coordinating small to mid-size events "
                            "such as birthdays, corporate gatherings, and weddings.",
            "cost_ratio": (0.1, 0.3),
            "target_customers": "Individuals and businesses hosting events who "
                                 "want professional coordination.",
            "revenue_model": "Flat planning fees plus a percentage of vendor bookings.",
            "advantages": ["Can start part-time with minimal equipment",
                          "Builds a strong referral network over time"],
            "risks": ["Seasonal demand fluctuations",
                      "Requires juggling multiple vendors and timelines"],
            "difficulty": "Medium",
        },
        {
            "name": "Mobile Car Detailing & Cleaning Service",
            "description": "Offering on-location car washing, detailing, and "
                            "interior cleaning services to customers at their "
                            "home or workplace.",
            "cost_ratio": (0.15, 0.5),
            "target_customers": "Car owners who value convenience over visiting a "
                                 "physical car wash.",
            "revenue_model": "Per-service fees with optional subscription packages.",
            "advantages": ["Low entry cost relative to a fixed-location shop",
                          "Mobility allows serving a wide service area"],
            "risks": ["Physically demanding work",
                      "Weather can disrupt scheduling"],
            "difficulty": "Easy",
        },
    ],
}


# --------------------------------------------------------------------------
# Helper functions
# --------------------------------------------------------------------------

def _scale_startup_cost(budget: float, cost_ratio: tuple) -> tuple:
    """Scale a template's cost ratio against the user's actual budget.

    Returns a (min, max) tuple of estimated startup cost in USD, always
    kept at or below the user's stated budget on the upper bound.
    """
    low_ratio, high_ratio = cost_ratio
    cost_min = round(budget * low_ratio, 2)
    cost_max = round(budget * high_ratio, 2)
    # Ensure minimum sensible floor of $20 so figures don't look like zero.
    cost_min = max(cost_min, 20)
    cost_max = max(cost_max, cost_min + 20)
    return cost_min, cost_max


def _estimate_monthly_income(cost_max: float, difficulty: str,
                              experience: str, weekly_hours: int) -> tuple:
    """Estimate a plausible monthly income range.

    The estimate blends startup investment size, difficulty level,
    experience level, and time commitment into a simple multiplier model.
    This is a heuristic, not a guaranteed forecast.
    """
    # Base multiplier: how many times the startup cost might be generated
    # in monthly revenue once the business is reasonably established.
    base_multiplier = {"Easy": 0.35, "Medium": 0.55, "Hard": 0.8}.get(difficulty, 0.5)

    # Experience adjusts execution efficiency.
    experience_factor = {"Beginner": 0.7, "Intermediate": 1.0, "Advanced": 1.4}.get(
        experience, 1.0
    )

    # Time commitment factor (capped, since more hours has diminishing returns).
    time_factor = min(weekly_hours / 20.0, 2.0)
    time_factor = max(time_factor, 0.3)

    income_min = cost_max * base_multiplier * experience_factor * time_factor * 0.5
    income_max = cost_max * base_multiplier * experience_factor * time_factor * 1.4

    # Sensible floors so very small budgets don't show $0 income.
    income_min = max(round(income_min, 2), 50)
    income_max = max(round(income_max, 2), income_min + 50)

    return income_min, income_max


def _compute_score(budget: float, cost_max: float, difficulty: str,
                    experience: str, weekly_hours: int) -> int:
    """Compute a 1-100 viability score for ranking ideas.

    The score rewards: affordability relative to budget, manageable
    difficulty for the user's experience level, and adequate time
    availability for the chosen difficulty.
    """
    score = 50  # baseline

    # Affordability: reward ideas that fit comfortably within budget.
    if budget > 0:
        cost_ratio_of_budget = cost_max / budget
        if cost_ratio_of_budget <= 0.5:
            score += 20
        elif cost_ratio_of_budget <= 0.8:
            score += 10
        elif cost_ratio_of_budget <= 1.0:
            score += 0
        else:
            score -= 15

    # Difficulty vs experience alignment.
    difficulty_rank = {"Easy": 1, "Medium": 2, "Hard": 3}.get(difficulty, 2)
    experience_rank = {"Beginner": 1, "Intermediate": 2, "Advanced": 3}.get(
        experience, 2
    )
    gap = experience_rank - difficulty_rank
    if gap >= 1:
        score += 15       # user is more experienced than required
    elif gap == 0:
        score += 8        # well matched
    else:
        score -= 10        # business harder than user's experience level

    # Time availability vs difficulty (harder businesses need more time).
    required_hours = {"Easy": 10, "Medium": 20, "Hard": 30}.get(difficulty, 20)
    if weekly_hours >= required_hours:
        score += 10
    elif weekly_hours >= required_hours * 0.6:
        score += 3
    else:
        score -= 12

    # Small random variation to avoid identical scores across runs,
    # while keeping the ranking primarily driven by the logic above.
    score += random.randint(-3, 3)

    # Clamp into [1, 100].
    return max(1, min(100, int(round(score))))


def _build_first_steps(category: str, country: str) -> List[str]:
    """Generate 5 generic-but-relevant first steps to start the business."""
    return [
        f"Validate demand by talking to at least 10-15 potential customers in "
        f"{country} to confirm they would pay for this {category.lower()} solution.",
        "Write a simple one-page business plan covering your offer, target "
        "customer, pricing, and how you will reach your first 10 customers.",
        "Set aside your starting budget and list out the minimum equipment, "
        "tools, or licenses required to legally and practically begin operating.",
        "Create a simple brand identity (name, logo, basic online presence) "
        "and launch a minimum viable version of your product or service.",
        "Acquire your first 3-5 paying customers, collect feedback, and refine "
        "your offer before investing further in growth or marketing.",
    ]


# --------------------------------------------------------------------------
# Main generation function
# --------------------------------------------------------------------------

def generate_ideas(budget: float, location: str, category: str,
                    experience: str, weekly_hours: int, num_ideas: int = 5
                    ) -> List[BusinessIdea]:
    """Generate a ranked list of business ideas based on user inputs.

    Parameters
    ----------
    budget : float
        Available budget in USD.
    location : str
        Country or city provided by the user (used for contextual text).
    category : str
        Area of interest, must match a key in CATEGORY_TEMPLATES
        (falls back to "Other" if not found).
    experience : str
        One of "Beginner", "Intermediate", "Advanced".
    weekly_hours : int
        Hours per week the user can dedicate to the business.
    num_ideas : int
        Number of ideas to generate (default 5).

    Returns
    -------
    List[BusinessIdea]
        Ideas sorted from best (highest score) to worst (lowest score).
    """
    templates = CATEGORY_TEMPLATES.get(category, CATEGORY_TEMPLATES["Other"])

    # If the category has fewer templates than requested, pull extra
    # templates from "Other" to always return the requested count.
    pool = list(templates)
    if len(pool) < num_ideas:
        extra_pool = [t for t in CATEGORY_TEMPLATES["Other"] if t not in pool]
        pool.extend(extra_pool)

    # Repeat/cycle templates if still not enough (keeps app robust for any
    # num_ideas value), then take exactly num_ideas templates.
    while len(pool) < num_ideas:
        pool.extend(templates)
    selected_templates = pool[:num_ideas]

    ideas: List[BusinessIdea] = []

    for template in selected_templates:
        cost_min, cost_max = _scale_startup_cost(budget, template["cost_ratio"])
        income_min, income_max = _estimate_monthly_income(
            cost_max, template["difficulty"], experience, weekly_hours
        )
        score = _compute_score(
            budget, cost_max, template["difficulty"], experience, weekly_hours
        )

        idea = BusinessIdea(
            rank=0,  # assigned after sorting
            name=template["name"],
            description=template["description"],
            startup_cost_min=cost_min,
            startup_cost_max=cost_max,
            target_customers=template["target_customers"],
            revenue_model=template["revenue_model"],
            advantages=template["advantages"],
            risks=template["risks"],
            difficulty=template["difficulty"],
            monthly_income_min=income_min,
            monthly_income_max=income_max,
            first_steps=_build_first_steps(category, location),
            score=score,
        )
        ideas.append(idea)

    # Sort from best (highest score) to worst (lowest score), then assign ranks.
    ideas.sort(key=lambda i: i.score, reverse=True)
    for position, idea in enumerate(ideas, start=1):
        idea.rank = position

    return ideas
