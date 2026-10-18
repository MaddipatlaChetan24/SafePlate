# LinkedIn post

Attach `docs/screenshots/linkedin-banner.png` as the main image. Optionally add
`overview-light.png`, `discover-light.png`, `recipe-detail.png` and `meal-planner.png` as a carousel.
Put the GitHub link in the first comment; LinkedIn tends to show posts with links in the body to fewer people.

---

🍛 What happens when an AI recipe app suggests Paneer Butter Masala (made with cashews) to someone with a nut allergy?

Most AI recipe generators make one LLM call and trust the answer. I wanted to build one that doesn't.

So I built **SafePlate**, an AI kitchen copilot for Indian home cooking that treats the LLM's output as a draft, not the final answer:

1️⃣ You add what's in your fridge (paneer, dal, palak…), plus allergies, diet and a time limit
2️⃣ The LLM drafts recipes as typed, structured output
3️⃣ Deterministic safety rules check every ingredient against your constraints
4️⃣ If anything fails, the exact violations go back to the model to fix
5️⃣ Anything still unsafe after the retries is dropped, never shown

You can watch each step live in the app's "agent trace" bar.

On top of that:
🗓 Meal planner that reuses ingredients across the week to cut waste
🛒 Smart shopping list that merges quantities and skips what's already in your pantry
📖 Cookbook with ratings. Regions you rate highly (Punjabi, Kerala, South Indian…) are favoured in future suggestions
⚖️ Serving scaler, Markdown export, dark mode, mobile layout
🔌 Offline demo mode, so anyone can try it without an API key

🛠 Stack: Python · FastAPI · LangChain · Pydantic · SQLite · vanilla JS · pytest (40 tests)

The most interesting problem was the allergen matching. "Coconut milk" isn't dairy and "eggplant" isn't egg, but "almond milk" is still a nut, "rava" is wheat, and "pav bhaji masala" is just spices. Plain substring matching gets these wrong.

My main takeaway: LLMs are great at drafting and bad at guaranteeing anything. Put deterministic checks around them and let the model fix its own mistakes.

Code in the comments 👇 Feedback welcome!

#AI #LLM #AIAgents #Python #FastAPI #LangChain #BuildInPublic #SideProject

---

**First comment:**
GitHub: https://github.com/MaddipatlaChetan24/SafePlate
