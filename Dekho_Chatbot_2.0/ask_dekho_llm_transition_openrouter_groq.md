# Ask Dekho 2.0 — LLM Transition Plan

## Purpose
This document explains the transition from a single-provider Gemini-based setup to a multi-provider LLM layer using **OpenRouter as the primary provider** and **Groq as the fallback provider**.

The goal is to make the chatbot easier to operate during the pilot stage, reduce dependency on one API key, avoid unnecessary billing friction, and preserve the existing application architecture as much as possible.

This is not a product redesign. It is a **provider-layer migration**.

---

## Why this transition is happening

The current system was designed around a Gemini-first approach, but the pilot requirements now favor a more flexible setup:

- The product is being deployed as a **cloud-hosted PWA**.
- The pilot is expected to serve **50–100 users initially**, with the possibility of growth later.
- The team wants to reduce dependence on a single LLM provider.
- The team wants a solution that is easier to operate in early-stage deployment.
- The chatbot already has an architecture that supports **provider switching**, **streaming**, **prompt injection**, **session memory**, and **fallback handling**.

Because of that, the most practical move is to replace the single Gemini API dependency with a **multi-provider LLM abstraction layer**.

---

## What is changing

### Before
The backend uses one main provider path:

- User message enters the chatbot
- Backend builds context and prompt
- Backend sends request to **Gemini**
- Response is streamed back to frontend through SSE
- Conversation history and rate limiting are handled through Redis and PostgreSQL-based logic

### After
The backend will use a provider selection flow:

- User message enters the chatbot
- Backend builds context and prompt
- Backend sends request to **OpenRouter first**
- If OpenRouter is unavailable, rate-limited, or unsuitable for a specific request, the backend can fall back to **Groq**
- Response is streamed back to frontend through the same SSE path
- Conversation history, Redis cache, rate limiting, and response formatting remain intact

In simple words: **the chatbot interface does not change; only the model provider behind it changes**.

---

## What stays the same

The following components do not need to be redesigned:

### Frontend
- React 19 + Vite + Zustand UI layer
- Chat screen structure
- Message bubbles
- Streaming UI behavior
- Preset suggestions
- Charts and rich response components
- Input flow and loading indicators

### Backend
- FastAPI routes
- SSE streaming endpoint
- Prompt assembly logic
- Financial context injection
- Intent detection framework
- Redis-based memory and caching
- Rate limiting logic
- PostgreSQL persistence layer
- Response packaging format

### Product behavior
- User still gets conversational financial guidance
- User still sees streaming responses
- User still gets structured outputs where needed
- User still interacts through the same PWA flow

---

## Why OpenRouter is the primary choice

OpenRouter is a strong fit for this project because it behaves like a **model access layer** rather than a single-model vendor.

### Reasons OpenRouter fits Ask Dekho

#### 1. OpenAI-style compatibility
OpenRouter is designed to work in an OpenAI-compatible way, which makes integration easier when a backend already has a generic LLM wrapper or an OpenAI-like client structure.

That is useful here because the backend is already built around a unified `llm_client.py` concept and a provider toggle pattern.

#### 2. Free-model routing
OpenRouter provides access to free or low-cost model routes. For a pilot, this is useful because the product can be tested with real users without locking the team into a single paid provider from day one.

#### 3. Better flexibility
Instead of depending on one model family, OpenRouter allows the backend to route requests through whatever model is available and suitable.

That is helpful when the product has different kinds of chatbot requests:
- intent classification
- short financial answers
- explanatory responses
- structured outputs
- fallback handling

#### 4. Easier experimentation
The team can test different models without rewriting application logic every time.

That matters because Ask Dekho is still in its pilot stage and the team may want to tune:
- response quality
- latency
- token cost
- output consistency
- structured JSON reliability

#### 5. Good fit for a “provider abstraction” architecture
Ask Dekho already has the kind of architecture where the backend decides what kind of response to produce. OpenRouter fits this model well because it lets the backend focus on orchestration instead of hard-coding model-specific behavior.

---

## Why Groq is the fallback choice

Groq is a good fallback provider because it is typically valued for speed and compatibility.

### Reasons Groq fits Ask Dekho

#### 1. OpenAI-compatible API behavior
Groq’s API structure is close enough to OpenAI-style usage that it usually plugs in cleanly inside an existing LLM wrapper.

That means the backend can switch providers without major changes to request formation or response parsing.

#### 2. Fast response generation
For a chatbot, especially during a pilot, latency matters.

Groq is useful when the team wants:
- faster first-token response
- faster conversational feel
- quick fallback when the primary provider is limited

#### 3. Backup reliability
A backup provider is valuable even when the primary provider is working well.

If OpenRouter is rate-limited, unavailable, or not ideal for a specific request, Groq can serve as the alternate route.

#### 4. Simple failover design
Groq works well as a fallback because the backend can use a simple rule:

- try OpenRouter first
- if that fails, switch to Groq
- if that also fails, use a static fallback response

That gives the chatbot multiple layers of resilience.

---

## Why Ollama is being removed from this plan

Ollama is useful when a team wants to self-host a local model and eliminate external API billing. However, for this specific deployment plan, it adds complexity that is not necessary right now.

### Why it is not the right fit for this stage

#### 1. The product is cloud-hosted
The PWA itself is hosted on cloud infrastructure, and the backend already needs to run on the VPS. Adding a locally hosted LLM on the same VPS would increase load significantly.

#### 2. VPS resources are limited
The selected VPS is suitable for:
- frontend hosting
- FastAPI backend
- PostgreSQL
- Redis

But it is not ideal for serving a model alongside all of those services if the user base grows.

#### 3. The team does not need model hosting complexity yet
The current goal is to validate the product, not to become an infrastructure-heavy LLM host.

#### 4. The project already has a strong provider-based backend design
Since the app already supports provider switching, it is more efficient to use external APIs than to self-host a model.

### Practical conclusion
Ollama is not wrong in general; it is just not the best fit for this stage of Ask Dekho.

For the current pilot, **OpenRouter + Groq is simpler, lighter, and easier to maintain**.

---

## How the transition should work technically

### Existing model flow
The current system is effectively built around a single provider path.

A typical flow looks like this:

1. User sends a message
2. Backend performs intent detection
3. Backend builds user context
4. Backend assembles the system prompt
5. Backend calls the LLM provider
6. Backend streams response back to frontend

### New model flow
The updated system should look like this:

1. User sends a message
2. Backend performs intent detection
3. Backend builds user context
4. Backend assembles the system prompt
5. Backend tries **OpenRouter** first
6. If OpenRouter fails or is unavailable, backend falls back to **Groq**
7. If both fail, backend returns a static graceful fallback message
8. Response is streamed back to frontend using the same SSE mechanism

This means the app remains stable at the user-facing level while becoming more resilient at the provider level.

---

## Recommended provider strategy

### Primary provider
**OpenRouter**

Use this as the main route because it gives the backend flexibility and helps avoid depending on a single LLM vendor.

### Secondary provider
**Groq**

Use this as the fallback route when OpenRouter is unavailable or unsuitable for a particular request.

### Final fallback
A static, curated response template

This should be used only if both providers fail. It ensures the app does not break the user experience.

---

## Suggested priority logic

The backend can follow a simple decision order:

### Option A: Always prefer OpenRouter
This is the cleanest default strategy.

- Send request to OpenRouter
- If successful, return the response
- If error occurs, retry once if appropriate
- If it still fails, switch to Groq
- If Groq also fails, use fallback response

### Option B: Intent-based routing
If the team wants slightly more control, the backend can use OpenRouter for most requests and Groq for high-latency or specific intent categories.

For example:
- OpenRouter for general chat and structured responses
- Groq for speed-sensitive interactions

### Option C: Health-check based routing
The backend can periodically check provider health and temporarily prefer the provider with better availability or lower latency.

For the pilot stage, Option A is enough.

---

## Compatibility with the existing stack

This transition fits the current stack well because the backend already uses a layered design.

### Existing backend elements that support this change
- unified LLM client wrapper
- provider toggle through environment variables
- streaming response architecture
- response cache
- session memory
- intent detection
- structured prompt assembly
- error handling and fallback logic

That means no major frontend rewrite is needed.

The main updates are inside the backend provider layer and configuration layer.

---

## What must be updated in the backend

### 1. LLM client wrapper
The current single-provider assumption should be replaced with a provider abstraction.

The wrapper should support:
- OpenRouter calls
- Groq calls
- fallback selection
- streaming and non-streaming modes
- structured response handling

### 2. Environment variables
Instead of only storing a Gemini key, the backend should support multiple provider settings.

Example variables might include:
- `LLM_PROVIDER_PRIMARY=openrouter`
- `LLM_PROVIDER_SECONDARY=groq`
- `OPENROUTER_API_KEY=...`
- `GROQ_API_KEY=...`
- `OPENROUTER_MODEL=...`
- `GROQ_MODEL=...`

### 3. Prompt and response handling
The prompt logic should remain the same, but the response parsing logic should be tested for both providers to ensure compatibility.

### 4. Error handling
The backend should define what happens when:
- provider times out
- provider returns malformed output
- provider rate limits the request
- provider temporarily fails

### 5. Logging and observability
The app should log:
- provider used
- response latency
- fallback triggered or not
- error type if failure occurs

This will help the team understand which provider is actually performing better in real use.

---

## What must not change

The following should stay stable during transition:

- frontend screen structure
- backend route names
- chat request format
- streaming endpoint behavior
- conversation memory logic
- financial context builder
- user experience flow
- response schema expected by the UI

This is important because the team should avoid turning a provider migration into a product migration.

---

## Suggested migration sequence

### Phase 1: Introduce provider abstraction
Refactor the current LLM client so it no longer depends on Gemini-specific logic.

### Phase 2: Add OpenRouter support
Make OpenRouter the default provider.

### Phase 3: Add Groq fallback
Enable Groq as a secondary route.

### Phase 4: Test streaming behavior
Check that SSE output still works correctly with both providers.

### Phase 5: Test structured outputs
Verify that intent detection, JSON formatting, and other structured responses behave as expected.

### Phase 6: Pilot rollout
Roll out to a small group first, monitor logs, and then expand usage.

---

## Risks to watch

### 1. Rate limits
Free or low-cost provider routes may have limits.

### 2. Output variance
Different models can respond differently even to the same prompt.

### 3. Structured output inconsistency
If the chatbot depends on JSON responses or specific schema shapes, those outputs must be tested carefully.

### 4. Latency differences
The system should be prepared for provider latency variation.

### 5. Prompt sensitivity
A prompt that works well with Gemini may behave differently on OpenRouter or Groq.

That is normal and should be handled by testing.

---

## What Antigravity should understand from this change

The key message for Antigravity is:

- We are not changing the product.
- We are not changing the frontend UX.
- We are not removing the chatbot features.
- We are only replacing the underlying provider strategy.
- We are shifting from a single Gemini dependency to a more flexible OpenRouter + Groq architecture.

That gives the project more resilience, lower friction, and better suitability for a real pilot deployment.

---

## Final recommendation

For Ask Dekho’s pilot stage, the recommended provider setup is:

### Recommended order
1. **OpenRouter** as the primary LLM provider
2. **Groq** as the fallback provider
3. **Static fallback responses** if both providers fail

### Reason
This combination gives the best balance of:
- compatibility with the current FastAPI architecture
- minimal code changes
- cloud deployment simplicity
- good pilot-stage flexibility
- reduced dependence on one API key
- low operational overhead

This is the most practical choice for a cloud-hosted PWA chatbot that needs to serve early users without committing to a heavy infrastructure setup.

---

## Next implementation note
After this document, the next step should be a concise technical handoff note for Antigravity that lists:
- current state
- target state
- environment variables
- provider priority order
- fallback behavior
- testing checklist

That handoff can be much shorter than this document, but this document should remain the main explanation of the transition.

