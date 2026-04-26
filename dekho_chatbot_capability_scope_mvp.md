# Dekho — Chatbot Capability Scope (MVP)

## 1. Purpose
This document defines the first version of **Ask Dekho**, the chatbot for the Dekho personal finance companion. It is intended to guide Antigravity during implementation and to keep the chatbot aligned with the product vision, UX style, and future production integration.

## 2. Product Context
Ask Dekho is not a generic chat assistant. It is a finance companion inside Dekho that helps users:
- understand spending
- ask questions about their own finances
- build better budgeting and savings habits
- explore suitable next steps based on their financial stage

The chatbot must support Dekho’s habit-first, behavior-first philosophy and feel calm, clear, and emotionally safe.

## 3. MVP Goal
The MVP should demonstrate that a user can:
1. Ask finance-related questions in natural language.
2. Query their own dummy financial data.
3. Receive simple, useful, personalized answers.
4. Get plain-language explanations and next-step suggestions.
5. Access the chatbot on mobile and desktop through a clean React UI.

## 4. Core User Questions the Chatbot Must Handle
The chatbot should answer questions such as:
- Where did I spend the most?
- What are my top expense categories?
- How much did I spend this month?
- How much can I save this month?
- What patterns do I repeat?
- Am I spending too much on food, shopping, travel, or subscriptions?
- What changed compared to last month?
- What are my saving habits looking like?
- What budgeting goal should I set?
- What financial next step makes sense for me?

## 5. Data Sources for the MVP
The chatbot will work on two main sources of data.

### 5.1 Dummy User Financial Data
Use CSV or document-based sample data for prototype users. This can include:
- transaction history
- income entries
- recurring bills
- savings entries
- investment entries
- goal progress
- categorical tags such as food, travel, rent, shopping, bills, entertainment

### 5.2 Finance Knowledge Base
Use a separate knowledge base for general finance guidance. This should cover:
- budgeting basics
- savings concepts
- emergency fund planning
- debt repayment basics
- spending behavior
- Indian finance terminology
- asset and investment basics
- goal-setting and money habits

## 6. Chatbot Behavior Rules
The chatbot should follow these rules:
- Answer in simple, human language.
- Prefer short, direct, and useful responses.
- Explain calculations when needed.
- Mention assumptions when data is incomplete.
- Avoid sounding robotic, harsh, or overly technical.
- Never pretend to know real bank data when only dummy data exists.
- If the question is outside the available data, explain what is missing.

## 7. Conversational Style
The chatbot should feel:
- warm
- intelligent
- non-judgmental
- slightly playful when appropriate
- confidence-building
- private and trustworthy

### Tone references inspired by strong consumer finance assistants
Borrow these interaction ideas in a Dekho-appropriate way:
- conversational chat-first UI
- personalized responses based on user behavior
- clear spending insights instead of dense dashboards
- timely nudges and reminders
- a strong assistant personality that still feels helpful

For Dekho, the personality should be less harsh and more calm/editorial than aggressive roast-style finance apps.

## 8. What the Chatbot Must Not Do in MVP
The first version should not:
- make legal, tax, or regulated investment claims
- connect to live bank systems yet
- hallucinate financial records
- give unsafe or overly confident advice
- promise guaranteed returns
- act like a human financial advisor
- overload the user with charts or jargon

## 9. Response Types the Chatbot Should Support
The chatbot should generate these response formats:

### 9.1 Summary Response
A concise answer to a finance question.

### 9.2 Insight Response
A short explanation of behavior or spending patterns.

### 9.3 Suggestion Response
A next-step recommendation such as:
- set a budget
- reduce a category
- build a savings goal
- review a recurring expense

### 9.4 Comparison Response
Compare one time period with another, such as this month vs last month.

### 9.5 Clarification Response
Ask the user for more context when the question cannot be answered clearly.

## 10. MVP Capabilities
### 10.1 Transaction Questions
- total spend
- category-wise spend
- merchant-wise spend
- recurring spend detection
- month-over-month changes

### 10.2 Budgeting Support
- estimate a safe spending limit
- suggest a monthly savings target
- show progress toward a goal

### 10.3 Behavioral Insights
- identify spending habits
- detect possible impulse spending
- highlight repeated patterns
- summarize financial behavior in simple language

### 10.4 Savings and Goals
- show savings progress
- suggest achievable savings actions
- support goal-based planning

### 10.5 Finance Knowledge Answers
- explain terms
- explain budgeting concepts
- explain savings basics
- explain investment basics in simple terms

## 11. Cleo-Inspired UX Principles to Borrow
Cleo is a strong reference for conversational finance assistance, and a few interaction ideas can be adapted for Dekho:
- chat-first access to financial insights
- personalized money guidance
- nudges based on behavior
- friendly, memorable assistant personality
- simple language that reduces money anxiety
- a tone that makes finance feel less intimidating

## 12. Dekho-Specific Differentiation
Dekho should not copy a playful finance app directly. It should keep these unique traits:
- calm and editorial rather than noisy
- behavior-first, not product-push-first
- habit-building before optimization
- emotional safety before hard finance language
- suggestions that fit the user’s stage

## 13. Inputs the Chatbot Should Read
The chatbot should be able to read:
- CSV transaction tables
- dummy income and expense logs
- savings goal records
- investment placeholders
- finance knowledge documents
- user profile metadata such as financial stage and goals

## 14. Output Principles
Every answer should aim to be:
- correct
- short enough to read quickly
- grounded in the available data
- easy for a first-time finance user to understand
- actionable whenever possible

## 15. Acceptance Criteria for the MVP
The chatbot is acceptable for prototype integration when it can:
- answer common finance questions from dummy data
- use knowledge base content for general finance explanations
- run in the React UI
- work on multiple devices
- maintain a consistent assistant persona
- avoid errors when data is missing or incomplete

## 16. Handoff Note for Antigravity
Antigravity should use this document as the product behavior contract for Ask Dekho. Build the chatbot as a modular service so the dummy data layer can later be replaced with real user data sources without redesigning the whole system.

