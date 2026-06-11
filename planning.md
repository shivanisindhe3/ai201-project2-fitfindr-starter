# FitFindr — planning.md

> Complete this document before writing any implementation code.

---

## Tools

### Tool 1: search_listings

**What it does:**
Searches the mock secondhand listings dataset for items that match the user's requested description, size, and maximum price. It filters against listing fields like title, description, category, style tags, size, condition, price, colors, brand, and platform.

**Input parameters:**

* `description` (str): The clothing item or style the user is searching for, such as `"vintage graphic tee"`.
* `size` (str): The requested size, such as `"M"`, `"S"`, or `"L"`. This can be `None` if the user does not specify a size.
* `max_price` (float): The highest price the user wants to pay.

**What it returns:**
Returns a list of matching listing dictionaries. Each listing contains fields such as `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

**What happens if it fails or returns nothing:**
If no listings match, the tool returns an empty list. The agent stores an error message in the session and stops instead of calling `suggest_outfit`.

---

### Tool 2: suggest_outfit

**What it does:**
Suggests how to style the selected secondhand item with the user's existing wardrobe. It uses the selected listing and wardrobe items to create a complete outfit suggestion.

**Input parameters:**

* `new_item` (dict): The selected listing returned by `search_listings`.
* `wardrobe` (dict): The user's wardrobe data, including available clothing items and style preferences.

**What it returns:**
Returns a string containing one or more outfit suggestions. The suggestion explains what to pair with the new item and why the pieces work together.

**What happens if it fails or returns nothing:**
If the wardrobe is empty or minimal, the tool still returns general styling advice using the selected item. If no useful outfit can be created, the agent shows a clear message explaining that the wardrobe data was limited.

---

### Tool 3: create_fit_card

**What it does:**
Creates a short, shareable outfit caption based on the selected item and outfit suggestion. The caption should sound like something a user could post on Instagram or TikTok.

**Input parameters:**

* `outfit` (str): The outfit suggestion returned by `suggest_outfit`.
* `new_item` (dict): The selected listing returned by `search_listings`.

**What it returns:**
Returns a short string fit card or social caption. It includes the vibe of the outfit, the thrifted item, and a casual shareable tone.

**What happens if it fails or returns nothing:**
If the outfit input is missing or empty, the tool returns a descriptive error message instead of crashing. The agent displays that message to the user.

---

### Additional Tools

No additional tools will be implemented for the required version. If time allows, I may add a price comparison tool as a stretch feature.

---

## Planning Loop

The agent starts with the user's natural language query. It extracts the item description, size if available, and max price if available. Then it calls `search_listings(description, size, max_price)`.

After `search_listings` runs, the agent checks the returned results:

* If `results` is empty, the agent stores an error message in `session["error"]`, leaves `selected_item`, `outfit_suggestion`, and `fit_card` as `None`, and returns early.
* If results are found, the agent selects the top result and stores it in `session["selected_item"]`.

Next, the agent calls `suggest_outfit(selected_item, wardrobe)`. The outfit suggestion is stored in `session["outfit_suggestion"]`.

Then the agent checks whether the outfit suggestion is usable:

* If it is empty or invalid, the agent stores an error message and stops.
* If it is valid, the agent calls `create_fit_card(outfit_suggestion, selected_item)`.

Finally, the generated fit card is stored in `session["fit_card"]`, and the session is returned to the app.

The agent is done when it has either produced a fit card or reached an error state.

---

## State Management

The agent uses a session dictionary to pass information between tools during one interaction.

The session stores:

* `query`: the original user request
* `search_results`: the list returned by `search_listings`
* `selected_item`: the top listing selected from search results
* `wardrobe`: the user's wardrobe data
* `outfit_suggestion`: the string returned by `suggest_outfit`
* `fit_card`: the final caption returned by `create_fit_card`
* `error`: any error message if a step fails

The selected item from `search_listings` is passed directly into `suggest_outfit`. The outfit returned from `suggest_outfit` is passed directly into `create_fit_card`. The user does not need to re-enter this information.

---

## Error Handling

| Tool            | Failure mode                          | Agent response                                                                                                                                                                                                                       |
| --------------- | ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| search_listings | No results match the query            | The agent says: “I couldn't find any listings that match your description, size, and price. Try increasing your budget, removing the size filter, or using a broader description.” The agent stops and does not call the next tools. |
| suggest_outfit  | Wardrobe is empty                     | The agent gives general styling advice for the selected item instead of crashing. It explains that the suggestion is based on the item because the wardrobe has limited data.                                                        |
| create_fit_card | Outfit input is missing or incomplete | The agent returns: “I couldn't create a fit card because the outfit suggestion was missing. Try generating an outfit first.”                                                                                                         |

---

## Architecture

```text
User query
    |
    v
Planning Loop
    |
    |-- Extract description, size, max_price
    |
    v
search_listings(description, size, max_price)
    |
    |-- results = []
    |       |
    |       v
    |   session["error"] = "No listings found..."
    |       |
    |       v
    |   Return session early
    |
    |-- results = [item1, item2, ...]
            |
            v
    session["search_results"] = results
    session["selected_item"] = results[0]
            |
            v
suggest_outfit(selected_item, wardrobe)
            |
            v
    session["outfit_suggestion"] = outfit
            |
            |-- outfit missing
            |       |
            |       v
            |   session["error"] = "Could not create outfit..."
            |       |
            |       v
            |   Return session early
            |
            v
create_fit_card(outfit_suggestion, selected_item)
            |
            v
    session["fit_card"] = fit_card
            |
            v
Return completed session to app.py
```

---

## AI Tool Plan

**Milestone 3 — Individual tool implementations:**

I will use ChatGPT or Cursor AI to help implement each required tool one at a time. For `search_listings`, I will give the AI the Tool 1 specification and ask it to implement filtering using `load_listings()` from `utils/data_loader.py`. I will verify that the code filters by description, size, and max price, and that it returns an empty list instead of crashing when no results are found.

For `suggest_outfit`, I will give the AI the Tool 2 specification and ask it to use Groq with `llama-3.3-70b-versatile`. I will verify that it accepts `new_item` and `wardrobe`, handles an empty wardrobe, and returns a useful string.

For `create_fit_card`, I will give the AI the Tool 3 specification and ask it to generate a short social caption using Groq. I will verify that it handles an empty outfit string and produces varied outputs.

**Milestone 4 — Planning loop and state management:**

I will give the AI my Planning Loop, State Management section, and Architecture diagram. I will ask it to implement `run_agent()` in `agent.py` using the session dictionary. I will verify that the agent does not call all tools unconditionally. Specifically, I will test that when `search_listings` returns an empty list, the agent stores an error and stops before calling `suggest_outfit` or `create_fit_card`.

---

## A Complete Interaction (Step by Step)

**Example user query:**
"I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
The agent extracts:

* `description = "vintage graphic tee"`
* `size = None`
* `max_price = 30.0`

Then it calls:

`search_listings("vintage graphic tee", size=None, max_price=30.0)`

The tool searches the listings dataset and returns matching items.

**Step 2:**
The agent checks the search results. If results exist, it selects the first listing and stores it:

`session["selected_item"] = results[0]`

Example selected item:

`"Faded Band Tee" - $22 - Depop - Good condition`

Then the agent calls:

`suggest_outfit(selected_item, wardrobe)`

The outfit tool uses the selected tee and the user's wardrobe to suggest a complete look.

**Step 3:**
The agent stores the outfit suggestion:

`session["outfit_suggestion"] = "Pair this faded band tee with baggy jeans and chunky sneakers for a relaxed 90s-inspired streetwear look."`

Then it calls:

`create_fit_card(outfit_suggestion, selected_item)`

The fit card tool creates a short caption.

**Final output to user:**
The user sees:

* the selected listing
* the outfit suggestion
* the final fit card caption

Example final fit card:

"thrifted this faded band tee for $22 and styled it with baggy denim + chunky sneakers for the easiest 90s off-duty look 🖤"
