# Executive Summary  
Personal finance chatbots (PFM bots) aim to make financial data actionable through friendly, context-aware dialogue. Modern systems (e.g. Cleo) ingest users’ banking data, summarize it in easy-to-understand cards or charts, and generate conversational responses that guide budgeting, saving, and spending decisions. Key techniques include selecting high-impact data points (large transactions, upcoming bills, budget overruns), summarizing them via charts and text cards, and structuring replies with a supportive, concise tone. Advanced PFM bots build user models and memory of goals to personalize advice (e.g. reminding a user of a savings goal or past overspending patterns). Ranking and relevance techniques (rules or ML) help prioritize which insights to present first. Natural Language Generation ranges from safe templates to neural models with controlled style. Multimodal outputs (images, graphs, interactive cards) complement text. Good UX employs progressive disclosure (small bite-sized info), suggestion chips, and microcopy that match the brand personality. Key evaluation metrics include user satisfaction, task completion, retention, as well as fairness and privacy compliance. Under the hood, an architecture will pull data from bank APIs into a data pipeline and analytics engine, using caching and ML for responsiveness. The report details each dimension (data selection, summarization, personalization, etc.), compares techniques, offers concrete design guidelines with example messages, a system architecture diagram, an evaluation plan, and a reading list of primary sources.

## Data Selection (What Data to Show)  
Effective PFM bots choose the **most relevant financial data** from a user’s accounts. This typically means highlighting recent large or unusual transactions (e.g. an oversized restaurant bill), budget categories approaching limits, upcoming bills or subscriptions, and progress toward savings goals. Many systems use **heuristics** or thresholds (e.g. “spent 80% of grocery budget”) to flag items. More advanced bots apply **anomaly detection or clustering** on transaction history to surface spending spikes. For example, Cleo highlights things like “£200 at Restaurant” if it exceeds typical dining expenses, or reminds you of a recurring bill. Data selection should also consider user query context: if the user asks about “groceries,” the bot fetches grocery-category spending from the last 30 days. Overall, the goal is not to dump raw statements, but to pick what matters – balances, trends, goals, and actionable alerts (low balance, overspend, unexpected charges). Privacy considerations mean only pulling data the user has explicitly connected (e.g. via secure APIs like Plaid or open banking) and only storing sensitive details as needed for personalization.

## Data Summarization and Visualization (Text, Cards, Charts, Tables)  
Once data is selected, it must be **summarized in user-friendly formats**. PFM bots commonly use a mix of **text summaries** and **visual widgets**:  
- **Cards and Chat Bubbles:** Summarize an insight in one or two sentences, possibly with emojis or icons. E.g. “🎉 Nice job! You’re £50 under budget for dining out this month.” These cards often include a title, a short message, and a CTA (e.g. “View details”).  
- **Charts:** Pie charts for category breakdown (e.g. spending by category), line charts for trends (e.g. daily balance over a month), and bar charts for comparisons (e.g. this month vs last month). These are embedded as images or interactive UI components. For example, a monthly spending report might include a bar chart of weekly spending.  
- **Tables:** When detailed data is needed (e.g. list of recent transactions, or a budget table), tables are used. These often appear on demand (e.g. user taps “See transactions”).  
- **Progress Indicators:** Progress bars or gauges for goals (e.g. 70% of savings goal achieved).  
Summaries should use **plain language**, avoiding jargon. Visuals add clarity (e.g. a pie chart is easier to interpret than a text list of percentages). However, overuse of visuals can clutter a chat, so bots often default to brief text and only show a chart when requested. All visuals should be accessible (with text captions) and concise. 

## Response Structuring (Tone, Brevity, Scaffolding, Progressive Disclosure)  
PFM bot messages are **concise, supportive, and structured**. Best practices include:  
- **Friendly, Empathetic Tone:** Many PFM chatbots adopt a casual, playful tone to engage users (Cleo famously uses humor and emojis). Tone should match brand (Cleo is sassy and witty, while a traditional bank bot might be more formal). However, all maintain empathy (e.g. saying *“Don’t worry”* if budgets are tight) to avoid shaming the user.  
- **Brevity:** Keep messages to 1–2 sentences or bullet points. Long paragraphs can overwhelm in chat. Use line breaks or bullet emojis for lists.  
- **Progressive Disclosure:** Reveal information in steps. For example, first say “You spent £400 on groceries this month (up 10% from last month). Need a breakdown?” and then, if the user says “Yes” or taps a button, show the breakdown by category or week. This prevents overload.  
- **Scaffolding & Guidance:** If giving advice, break it into steps. E.g., “Step 1: Review your budget for groceries. Step 2: Consider cutting dining out by £50.”  
- **Clear Prompts and Quick Replies:** Use suggestion chips like “Yes, show details” or “No thanks” to guide the conversation.  
- **Personalized References:** Refer to the user’s data (“You,” or their nickname) and goals (“That rain boot fund is at 60%!”). This makes chats feel tailor-made.  
- **Transparency:** If the bot can’t do something (e.g. doesn’t have permission to pay bills), it should say so clearly. Safety messages or disclaimers (“I’m not a financial advisor”) can be included as needed to prevent over-trust.  

## Personalization (User Model, Context, Preferences, Privacy)  
Personalization is critical for engagement. Techniques include:  
- **User Profile & Goals:** Bots build a profile (age, income, financial goals). For example, if a user has a goal “save for vacation,” the bot will occasionally reference it (“You’ve saved £300 toward your holiday!”). This data is usually gathered via user input or onboarding surveys.  
- **Conversation Memory/Context:** Advanced bots remember past chats. If a user mentioned “help me save for rent,” the bot can later remind them of that goal. This requires storing conversation context securely. For example, Cleo 3.0’s memory system tracks “key details from previous chats, like budgeting goals and financial stressors” to personalize ongoing advice.  
- **Behavioral Signals:** The bot adapts based on how the user interacts. If a user frequently asks about investments, the bot will proactively send investing tips. Or if the user skips certain categories, it might change wording.  
- **Timing and Frequency:** Personalization extends to when and how often the bot messages. Some PFM bots send daily or weekly summaries; others wait for user prompts. Users may set preferences (“Send me alerts only above £100”).  
- **Tone Personalization:** Matching user style (formality, emoticon use) can be enabled by small preferences. E.g. user can choose between “Professional” vs “Casual” mode.  
- **Privacy Considerations:** All personal data use must comply with privacy laws (GDPR, etc.). Users should know what data is stored (financial, conversation history) and how it’s protected. For example, the bot might store only aggregated spending stats rather than raw transactions, or anonymize logs. Securing bank connections with encryption and requiring re-authentication (e.g. OAuth tokens expire) are standard practices.  

## Ranking and Relevance Algorithms (Heuristics, ML Models, Retrieval, Reranking)  
To decide what to say first, PFM bots use ranking:  
- **Heuristic Rules:** Simple rules like “always show current balance and last transaction” or “if spending in a category >75% of budget, alert the user”. These ensure consistent key info.  
- **Machine Learning Models:** More sophisticated bots may train models on past chats to predict what users care about. For example, a classification model might predict whether to mention credit score vs spending summary based on user profile. ML ranking (like learning-to-rank) can score various possible responses or insights and pick the top ones.  
- **Retrieval-Based Responses:** Some bots retrieve answers from a knowledge base or past chats. They might index FAQs and use a search to answer user queries (e.g. “How do I save more money?”). Retrieved answers are then re-ranked by relevance.  
- **Contextual Ranking:** The bot considers conversation context. If the user just asked about “savings”, the bot will prioritize a savings goal update over spending info.  
- **Feedback Loops:** A/B testing or reinforcement signals (like user rating of answers) can tune ranking. Bots can ask for thumbs-up/down on advice and adjust future suggestions.  
Trade-offs: Rule-based ranking is predictable and cheap but misses nuance; ML models can adapt but need training data (which in PFM means annotated chats or user feedback). Reranking using both rule and model (hybrid) is common: e.g. retrieve a few candidate messages then use ML to pick the best.  

## NLG Techniques (Templates, Neural Generation, Controlled Style, Safety)  
PFM bots use various NLG methods:  
- **Template-Based Generation:** Predefined sentence templates with variables. E.g. “You spent £{amount} on {category} this {period}.” This guarantees grammatical output and is easy to control for compliance (no hallucinations). Many finance bots primarily use templates for factual answers.  
- **Neural Generation (LLMs):** Some modern PFM bots incorporate LLMs (like fine-tuned GPT models) for more natural, varied speech. These can write paragraphs or creative analogies (“That dinner cost more than a cinema ticket—yikes!”). However, LLMs risk generating incorrect facts, so in finance often they are combined with data retrieval or guided by templates (constrained generation).  
- **Controlled Generation:** Techniques such as using a style prompt or classifier ensure the bot stays on-brand (e.g. always cheerful). A model might be fine-tuned on a dataset of “friendly financial advice” to control tone.  
- **Safety and Compliance:** NLG must avoid giving explicit financial advice (which may require licenses). Bots often include safe fallbacks (“I’m not a licensed advisor, but...”). They also avoid privacy leaks. If using an LLM, filtering sensitive content (like full account numbers) is crucial.  
- **Multi-turn Coherence:** For longer interactions, the NLG component may use the entire dialog history (or memory) so that responses are coherent with past context.  
Practically, many systems use a **hybrid**: templates for most data-driven responses, and neural generation for chit-chat or summarization. This balances natural language fluency with factual accuracy.

## Multimodal Outputs (Images, Charts, Interactive Cards)  
Beyond plain text, modern PFM chatbots use rich media:  
- **Embedded Images/Charts:** The bot can send a generated chart (e.g. spending pie chart) as an image in chat. This is useful in smartphone or web UIs that support images. For voice assistants, charts are less useful.  
- **Interactive Cards:** Instead of text only, bots may send structured "cards" with buttons and fields. For example, an “Account Summary” card showing balance, and buttons like “View Transactions” or “Transfer Money.” Platforms like Facebook Messenger or Slack have built-in card formats.  
- **Collapsible Tables or Accordions:** Some chat platforms allow expandable sections (e.g. transaction details hidden under a click).  
- **Notifications & Emails:** A bot might send an email or push notification as a follow-up with richer content. E.g. “Here’s your monthly report as a PDF.”  
- **Voice and Audio:** For voice-first interfaces, the bot might speak results and optionally send a link to a chart. Textual multimodal output is often translated to a succinct speech summary.  
- **Real-time Visualizations:** In advanced apps, the chat UI might include interactive graphs the user can zoom or filter. This goes beyond static images.  
Multimodality improves understanding (a picture of spending is intuitive) and engagement, but also adds complexity (must generate and host media) and accessibility concerns (alt-text needed).

## UI/UX Patterns (Conversational UI Components, Microcopy, Affordances)  
Designing the chat interface is as important as the AI. Common patterns:  
- **Avatar and Persona:** Bots often have a friendly avatar and use first-person voice (“I”/”we”) to personify them.  
- **Greeting and Introduction:** Clear onboarding message (“I’m Cleo, your AI budget buddy!”) with short tutorial of commands.  
- **Quick Reply Buttons:** After giving info, bots propose next steps. E.g. after showing spending, buttons like “Adjust Budget” or “Explain More.”  
- **Typing Indicator:** Show a “bot is typing” animation for realism and to indicate thinking time (so users know the bot is working on a response).  
- **Microcopy:** Short helper texts that guide use. For example, placeholder text in the input field (“Ask me about your spending…”) or tooltips explaining buttons.  
- **Error Handling:** Friendly error messages and suggestions if the bot misunderstands (“Sorry, I didn’t catch that. Try “show budget” or “fun fact about money”).  
- **Visual Affordances:** Use of color and icons (e.g. green up-arrow for savings, red down-arrow for overspending) to quickly signal good/bad.  
- **Multi-turn Navigation:** Some bots allow a “back” or “refresh” command to revisit previous steps. Others use a thread-like interface (every question is persistent).  
- **Privacy UX:** Clearly marked actions for connecting accounts, and easily accessible privacy settings or data deletion commands.  
Overall, the UX should feel fluid: the user shouldn’t have to type too much if buttons can do it, and the flow should feel like talking to a helpful assistant, not a rigid form.

## Evaluation Metrics (UX, Accuracy, Engagement, Fairness)  
Measuring a PFM chatbot’s success involves both quantitative and qualitative metrics:  
- **User Satisfaction (UX):** Surveys (e.g. Chatbot Usability Questionnaire scores) or net promotor score. Often measured after a session (“How helpful was Cleo today?”). Also track completion rate of tasks (did the user follow a budget suggestion?).  
- **Accuracy and Relevance:** Automatic metrics (like BLEU) are not great for chat. Instead, manual evaluation or semantic metrics measure if the answers are factually correct and relevant to the question. For example, if the user asks “What’s my balance?”, correctness is obvious, but for open advice questions, human judges may rate helpfulness.  
- **Engagement:** Frequency of use (daily/weekly active users), messages per session, retention rate over weeks. A lively bot that users return to is a good sign. For instance, high repeat usage of Cleo (millions of users reported) suggests engagement.  
- **Efficiency:** Average response time (latency); shorter is better. Also how quickly the user gets an answer (conversation turns to resolution).  
- **Error Rate:** Frequency of misunderstandings (e.g. “I didn’t understand”) or fallback to “I can’t answer that”. Lowering this over time is a goal.  
- **Behavioral Impact:** Downstream metrics like percentage of users who increase savings or stick to budgets after using the bot. These require long-term tracking.  
- **Fairness & Bias:** Ensure recommendations don’t disadvantage certain groups. For example, check that credit-related advice isn’t biased by demographic data. Standard fairness audits and anonymized logs reviews are needed.  
- **Privacy/Compliance:** This isn’t exactly a user metric, but audits should confirm user data is handled per policy (e.g. encryption in transit/storage). Lack of data breaches and user trust ratings (do users trust the bot with data?) matter.  

Evaluation typically involves A/B testing new features (e.g. more emoji vs fewer) and monitoring KPI’s. Log analysis (like dropped conversations or frequent queries) helps iteratively improve the bot.

## Implementation Architecture (Data Pipelines, Latency, Caching, APIs)  
A robust PFM chatbot uses a modular architecture:  

```mermaid
flowchart LR
    subgraph User_Device
        U(User) -->|Chat interface (app/web)| UI[Chat UI]
    end
    UI -->|User query| Backend[Chatbot Backend]
    Backend -->|NLP/Intent| NLU[NLP & Intent Engine]
    Backend -->|Data fetch| DataAPI[Bank APIs & Financial Data Sources]
    DataAPI --> FinDB[Financial Data Store]
    Backend -->|User context| ProfileDB[User Profile & Memory Store]
    NLU -->|Intent/Entities| Logic[Business Logic & Ranking]
    Logic -->|Select insight| DataSummarizer
    DataSummarizer -->|Summaries| Renderer[NLG & Response Generator]
    Renderer -->|Message| UI
    ProfileDB ---|store/retrieve| Logic
    Cache[(Cache & Session Store)] --> Backend
    subgraph Shared_Services
        Auth[(Auth & Security)]
        Analytics[(Logging & Analytics)]
    end
    Backend --> Auth
    Backend --> Analytics
```

**Flow Description:** When a user sends a message, the chat UI forwards it to the backend. The backend uses an NLP engine (often a library or cloud service) to parse intent and entities (e.g. “show me grocery spending”). It then uses business logic: it retrieves relevant data from a financial database (which may be populated by nightly ingestion from connected bank APIs), and from the user profile store (goals, preferences). A summarization/analytics module computes things like totals or trends. The NLG component (template or model) formats the response text. The response returns to the UI, possibly along with charts or cards.  

**Key Points:**  
- *Data Pipelines:* Financial data from banks is pulled via secure APIs (Plaid, open banking) and stored in a database. ETL jobs may run daily for analytics (like categorizing spending).  
- *Latency/Caching:* Caching recent data ensures snappy replies. Common queries (balance, budgets) are cached so the bot can respond quickly.  
- *APIs:* Use REST/GraphQL for internal modules, and ensure rate limits for bank APIs.  
- *Scalability:* The system may be hosted on cloud services (e.g. AWS, as Cleo has noted), with autoscaling for high traffic.  
- *Security:* All channels use TLS encryption. Tokens for bank connections are stored encrypted.  
- *Analytics:* Every interaction is logged (with PII removed) to analyze usage patterns and for ML training (e.g. to improve NLU intents).  

This modular design lets teams improve parts (e.g. swapping in a better ML ranker or a newer NLG model) without breaking the whole system.

## Case Studies: Cleo and Other PFM Chatbots  
- **Cleo (UK, AI Money Coach):** Cleo uses a **chat-first interface** on mobile. It shows spending summaries in chat (e.g. “You spent £X on takeout”) often with quick-reply cards (“Good job” or “Why so high?”). Cleo’s tone is irreverent (it jokes or uses GIFs) to build rapport. Under the hood it combines bank data (via Plaid) with ML to detect spending patterns and uses memory to recall user goals. Cleo 3.0 added voice and more proactive insights.  
- **Erica (Bank of America):** A mainstream bank assistant, Erica is more formal and helpful. It responds to direct questions (balance, pay bill) and proactively issues alerts (e.g. low balance). Erica’s UI uses cards in the BofA app (like “You got paid $X”). Its responses are template-based and compliance-focused. It doesn’t use humor but is heavily personalized to the user’s account data.  
- **Albert (US finance app):** Albert’s chatbot helps with budgeting and saving automatically. It sends plain-language tips (“Pay yourself first!”) and breakdowns of spending. Albert uses simple text explanations and leverages notifications. It uses rules and basic ML to advise on savings boosts or negotiating bills, and ensures disclaimers are included.  
- **Trim (US, now part of Coinbase):** Trim started as a text/SMS bot that analyzed transactions and suggested savings/cancellation of services. It would message users about unusual charges (“Should we cancel this $9.99 trial?”). Trim had a friendly but straightforward tone. The UI was chat-like via text, with links to web interfaces. It mainly used rule-based detection of subscriptions.  
These examples illustrate trade-offs: retail banking bots prioritize accuracy and brand voice, while fintech startups (Cleo/Trim) lean on engagement and personality. All focus on summarizing spending and nudging users towards financial goals, but differ in style and underlying tech.

## Comparison of Techniques and Trade-offs  

| **Technique**                  | **Use-Case**                              | **Pros**                                                         | **Cons**                                                     | **Complexity**              | **Data/Privacy Implications**                    |
|--------------------------------|-------------------------------------------|------------------------------------------------------------------|--------------------------------------------------------------|-----------------------------|--------------------------------------------------|
| **Template-Based NLG**         | Routine responses (balances, budgets)     | Predictable, low error rate; easy to ensure compliance.          | Can sound robotic and repetitive. Limited expressiveness.    | Low (just code templates).  | Low risk; templates control output.              |
| **Neural NLG (LLM)**           | Casual chat, creative responses           | Natural-sounding; handles open-ended queries flexibly.           | Risk of hallucinations, harder to control brand voice.       | High (model training/inference). | Needs filtering of personal data.               |
| **Rule-Based Ranking**         | Simple prioritization (alerts, FAQs)      | Transparent logic; easy to implement & debug.                    | Static; cannot learn new patterns automatically.            | Low-Med (rules design).      | Only uses pre-approved criteria (safe).          |
| **ML-Based Ranking**           | Complex personalization & relevance       | Adapts to user preferences; can optimize for engagement.         | Requires training data; may produce unexpected bias.         | High (data + models).        | Needs user data storage for training (privacy concerns). |
| **Charts/Pie Graphs**         | Visualizing spending by category          | Intuitive insight; quick to grasp proportions.                   | May be unclear if too many categories; not suitable for all UIs (e.g. voice). | Med (drawing code or libraries). | Mostly aggregate data; low privacy risk.         |
| **Text Summary**               | All-purpose (low-bandwidth mediums)       | Universally accessible; no images needed.                        | Can be verbose; harder to see trends at a glance.           | Low (just string formatting). | Contains raw values (like balances); moderate privacy since text can contain details. |
| **Interactive Cards/Buttons**  | Guided user choices (e.g. “Check Budget”) | Reduces user effort; steers conversation flow.                   | Limits user to predefined options; not flexible to all inputs. | Med (designing flows & UI).   | No extra data; improves UX.                      |
| **One-off Query (API)**        | Ad-hoc user questions (e.g. “What is $10 in INR?”) | Quick facts; leverages existing services (currency API, etc).    | No personalization; limited to API’s domain.                | Low (just API call).         | May log query; ensure no sensitive info sent.    |
| **Conversational Memory**      | Long-term personalization                 | Enables continuity; can reference past goals.                    | Requires secure storage; can be difficult to keep relevant.  | Med-High (database & logic).  | Stores personal goals & chat history (high privacy need). |

## Design Guidelines and Example Message Templates  

- **Be Empathetic and Encouraging:** Use a warm, motivating tone. e.g. *“Hey [Name], great news! You’ve saved £50 this week 😊”*. Template: 
  > **Bot:** “🎉 *Amazing work!* You’re *£50 under your dining budget* this month. Want to transfer that to savings?”  
- **Keep It Short and Scannable:** Present one idea per message. Use bullet-like formatting with emojis. e.g.  
  > **Bot:** “*Budget Summary:* You spent **£400** on Groceries (🍏), which is **80%** of your £500 limit.  
  > **Bot:** `Is that okay, or should I help adjust next month?`”  
- **Offer Quick Actions:** Always provide reply buttons or suggested actions to streamline flow. e.g. *“Got it”, “Set a reminder”, “Show tips”*.  
  **Bot:** “You’ll run out of budget in 5 days. 💡 *Tip:* Try cooking more at home. [Set Reminder] [View Recipes]”  
- **Use Progressive Disclosure:** Don’t overload data. Provide summary and ask if they want details.  
  > **Bot:** “You spent **£200 on transport** this week. ✈️ Would you like to see the breakdown (bus vs taxi)?”  
- **Personalize with Context:** Refer to names/goals.  
  **Bot:** “*Alex*, your holiday fund is at **65%**. Keep it up! 🏖️ Want to see your progress?”  
- **Maintain Safety and Compliance:** If unsure, disclaim.  
  **Bot:** “I’m not a financial advisor, but I notice you have some credit card debt. *Would you like some tips on paying it down faster?*”  

Each guideline above can be tailored. For instance, a message template for reminding about bills could be:  
> *“Just a heads-up, [Name] – your electricity bill (£40) is due in 3 days. ⚡ Any quick fixes needed?”*  

## Architecture Diagram (Data Flow)  

Below is a simplified **Mermaid** flowchart of the system architecture and data flow:

```mermaid
flowchart LR
    U[User] -->|Chat UI| UI[User Interface (App/Web)]
    UI -->|Query| Backend[Chatbot Backend]
    Backend --> NLU[NLP & Intent/Entity Recognition]
    Backend --> DataAPI[Bank APIs / Financial Data]
    DataAPI -->|Fetch Transactions| DataStore[(Transactions & Accounts DB)]
    Backend --> ProfileDB[(User Profile & Memory)]
    NLU -->|Intent, Entities| Logic[Business Logic & Ranking]
    Logic -->|Select Insights| AnalyticsEngine[Summarization & Insights Engine]
    AnalyticsEngine -->|Insights| Renderer[NLG & Response Generator]
    Renderer -->|Response| UI
    ProfileDB -->|Context| Logic
    Backend --> Cache[(Cache Store)]
    Backend --> Auth[Authentication & Security]
    Backend --> Analytics[(Logging & Analytics)]
```

## Evaluation Plan and Metrics  

To ensure the chatbot meets its goals, implement a multi-pronged evaluation:

- **A/B Testing & User Feedback:** Release changes (new tone, feature) to subsets of users. Compare engagement metrics (session length, click-through on suggestions) between variants. Collect user ratings (“Was this helpful?”).  
- **Success Rate:** Measure the percentage of user requests resolved successfully (vs. requiring escalation or human support).  
- **Task Completion Time:** Track how quickly users get answers. E.g. average time from question (“Show me food spending”) to final helpful reply.  
- **Qualitative Surveys:** Periodic questionnaires asking about satisfaction, trust, and perceived accuracy. Use standardized UX questionnaires adapted for chat (e.g. CSUQ).  
- **Behavioral Impact:** For a subset of users who opt-in, measure real financial outcomes (e.g. change in savings rate after 3 months of using the bot).  
- **Fairness Audits:** Regularly review suggestions to ensure no demographic bias. For example, check that budget recommendations are equitable across income levels.  
- **Technical Metrics:** Monitor NLU accuracy (intent recognition %), response latency, and system uptime. Also track user privacy compliance (audit logs for data access, encryption checks).  

Prioritize user-centric metrics (satisfaction, retention) first. Tie bot improvements to financial wellness if possible (e.g. X% of users achieve a savings goal). Continuously iterate based on data.

## Prioritized Reading List  

- *“Cleo: Meet Your AI Money Coach”* – Cleo official site (architecture and personalization overview)  
- *“Introducing Cleo 3.0”* – Cleo blog (memory and reasoning improvements)  
- *Shevat, A.* **Designing Bots** (O’Reilly, 2017) – Foundational conversational UI patterns and templates.  
- *DeAngelo, J. et al.* “HumAIne-Chatbot: Real-Time Personalized Conversational AI” (arXiv 2025) – Advanced personalization techniques.  
- *OpenAI Blog* **“A New Personal Finance Experience in ChatGPT”** – Example of integrating finance data with a chat UI (ChatGPT plugin).  
- *Microsoft* **“Conversational AI design guidelines”** – (Docs.microsoft.com) Practical tips on chat UX patterns.  
- *Nielsen Norman Group* **“10 UX Guidelines for AI Chatbots”** – Best practices for tone, interactions, and evaluation.  

(Links are indicative; search titles to locate official sources. The Cleo official site and blog contain detailed info on their AI approach, and industry posts or academic articles provide broader context.)

