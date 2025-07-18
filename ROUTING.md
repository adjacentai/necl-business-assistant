# How Our Bot Works: From Message to Response

This document explains in simple terms how our AI assistant understands the user and conducts a dialogue. The magic is built on three pillars: the **NLU Model**, the **Finite State Machine (FSM)**, and **AI Generation**.

---

### Step 1: The User Writes Something

It all starts with a message from the user. Let's say they write:

> "Hi! Can you recommend a bouquet for a birthday?"

---

### Step 2: NLU - Understanding What They Want

We don't just read the text; we try to understand its **essence**. To do this, the message is sent to the first AI model (GPT) with a special system prompt, `NLU_SYSTEM_PROMPT`.

**This model's task:** To turn text into structured data. It identifies the **intent** and extracts **entities**.

```text
Message: "Can you recommend a bouquet for a birthday?"
     |
     V
[NLU Model (GPT)]
     |
     V
JSON Response: {"intent": "ask_for_recommendation", "entities": {"occasion": "birthday"}}
```

Now we know the user wants a **recommendation** and the occasion is a **"birthday"**.

---

### Step 3: The Router (FSM) - Deciding What to Do Next

This is the brain of our bot, the `route_message` function in `src/bot/handlers.py`. It acts like a station dispatcher: it looks at the `intent` and decides which "track" (scenario) to send the user on.

1.  **Intent Check:** The dispatcher sees `intent: "ask_for_recommendation"`. It knows that this intent should trigger the flower ordering scenario.

2.  **Entity Check (the smart move!):** The dispatcher checks if we've already extracted any useful information. Yes! We have `entities: {"occasion": "birthday"}`.

3.  **Start Scenario & Skip Step:** Instead of blindly asking "What's the occasion for the bouquet?", the bot:
    *   Immediately saves "birthday" to its temporary memory (FSM).
    *   **Skips the first step** and goes directly to the second.
    *   Asks the next question: "Great, we're looking for a bouquet... What is your budget?"

If the user had just written "I want a bouquet," the NLU would have returned `{"intent": "order_flowers", "entities": {}}`. The dispatcher would have seen this and asked the very first question: "What's the occasion?"

---

### Step 4: The Scenario (FSM) - Guiding the Client Through the Funnel

The user is now "inside" the `OrderFlowers` scenario. Each of their subsequent answers will be handled by a separate function designed for that step:

*   `process_occasion` (if asked about the occasion)
*   `process_budget` (when asked about the budget)
*   `process_preferences` (when asked about preferences)

At each step, the bot saves the answers to the FSM memory.

---

### Step 5: AI Generation - Creating a Personalized Offer

When all the information is collected (occasion, budget, preferences), the climax arrives.

1.  **Gather All Data:** We take all the information from the FSM memory.
2.  **Form a Detailed Prompt:** We create a new, very detailed request for the second AI model (the main one, with the "sales consultant" persona).
    ```
    "Generate a bouquet suggestion for a client with the following details:
    - Occasion: birthday
    - Budget: 3000 rubles
    - Preferences: something delicate, in pink tones.
    Propose one specific, beautiful option..."
    ```
3.  **Get a Creative Response:** The AI salesperson generates a unique sales proposition, for example:
    > "For such a delicate occasion, I would recommend our signature 'Morning Dew' bouquet. It consists of cream peonies, pink ranunculus, and eucalyptus sprigs, which fits perfectly within your budget. How do you like this option?"

---

### Step 6: Completion

The user either agrees or disagrees. The bot responds to this and **clears its state** (`state.clear()`), ending the scenario. Now it is ready to receive new commands and direct them through the router again.

### Overall Diagram

```mermaid
graph TD
    A[Client sends a message] --> B{1. NLU Model (GPT)};
    B --> C{2. Router in handlers.py};
    C -- "Intent NOT determined" --> D[General response from AI];
    C -- "Intent 'Order Flowers' + Entities EXIST" --> F[Step 2: Ask for budget];
    C -- "Intent 'Order Flowers' + NO Entities" --> E[Step 1: Ask for occasion];
    E --> F;
    F --> G[Step 3: Ask for preferences];
    G --> H{4. Gather all data &<br/>form a detailed prompt};
    H --> I[5. AI Generation of<br/>a personalized offer];
    I --> J{6. Confirmation from client};
    J --> K[End of scenario / Clear state];
``` 