# Tool Inventory

## Tool 1: search_listings(description: str, size: str | None, max_price: float | None) -> list[dict]

**Purpose:**
Searches the thrift listings dataset and returns items that match the user's description, size preference, and budget.

**Inputs:**

* `description (str)` – keywords describing the desired item
* `size (str | None)` – clothing size filter
* `max_price (float | None)` – maximum budget filter

**Output:**

* `list[dict]` containing matching thrift listings sorted by relevance

---

## Tool 2: suggest_outfit(new_item: dict, wardrobe: dict) -> str

**Purpose:**
Generates outfit recommendations using the selected thrift item and the user's wardrobe.

**Inputs:**

* `new_item (dict)` – selected listing from search results
* `wardrobe (dict)` – user's wardrobe data

**Output:**

* `str` containing one or more outfit suggestions

---

## Tool 3: create_fit_card(outfit: str, new_item: dict) -> str

**Purpose:**
Creates a short social-media-style caption describing the outfit.

**Inputs:**

* `outfit (str)` – outfit recommendation from suggest_outfit()
* `new_item (dict)` – selected thrift item

**Output:**

* `str` containing a fit card caption

# Planning Loop

The agent follows a sequential planning loop with conditional branching.

1. The user submits a natural language query.
2. The query is parsed to extract:

   * description
   * size
   * maximum price
3. The agent calls `search_listings()`.
4. If `search_listings()` returns an empty list:

   * the agent stores an error message in session state
   * execution stops immediately
   * no additional tools are called
5. If listings are found:

   * the highest-ranked listing is selected
   * the selected listing is stored in session state
6. The agent calls `suggest_outfit()` using the selected item and wardrobe.
7. The returned outfit recommendation is stored in session state.
8. The agent calls `create_fit_card()` using the outfit recommendation and selected item.
9. The completed response is returned to the user.

The planning loop uses tool outputs to determine the next action. For example, if no listings are found, the outfit and fit-card tools are skipped entirely.

# State Management

The agent maintains a session dictionary throughout execution.

Stored state includes:

* `query` – original user query
* `parsed` – extracted description, size, and max_price
* `search_results` – results returned by search_listings()
* `selected_item` – top-ranked listing chosen by the agent
* `wardrobe` – user's wardrobe data
* `outfit_suggestion` – output from suggest_outfit()
* `fit_card` – output from create_fit_card()
* `error` – error message if execution ends early

State is passed between tools as follows:

* `search_results` → `selected_item`
* `selected_item` → `suggest_outfit()`
* `outfit_suggestion` → `create_fit_card()`

This allows tools to build on previous results without repeating work.

# Error Handling Strategy

| Tool            | Failure Mode               | Agent Response                                                               |
| --------------- | -------------------------- | ---------------------------------------------------------------------------- |
| search_listings | No matching listings found | Return empty list and stop execution with a helpful error message            |
| suggest_outfit  | Wardrobe is empty          | Generate general styling advice instead of wardrobe-specific recommendations |
| create_fit_card | Outfit string is empty     | Return a descriptive error message instead of calling the LLM                |

### Concrete Testing Examples

**search_listings()**

Input:
`designer ballgown size XXS under $5`

Result:
`[]`

Agent response:
"I couldn't find any listings that match your description, size, and price."

**suggest_outfit()**

Tested using:
`get_empty_wardrobe()`

Result:
The tool generated general styling suggestions instead of failing.

**create_fit_card()**

Input:
`create_fit_card("", item)`

Result:
"I couldn't create a fit card because the outfit suggestion was missing."

# Spec Reflection

### How the spec helped

The planning document helped define tool responsibilities before implementation. By clearly specifying inputs, outputs, and failure cases, implementation became more organized and easier to debug.

### How implementation diverged from the spec

Originally, the search tool was planned as a simple keyword filter. During implementation, keyword-overlap scoring was added to rank results by relevance. This produced better search quality than a basic filter and improved the user experience.
# AI Usage

## Example 1

**Task given to AI:**
Generate an initial implementation of `search_listings()` based on the tool specification in `planning.md`.

**What AI produced:**
A basic keyword-based search function for matching user queries to thrift listings.

**What I revised:**
I added size filtering, price filtering, keyword-overlap scoring, and relevance-based sorting to better match the project requirements.

---

## Example 2

**Task given to AI:**
Generate the planning loop for `run_agent()` using the workflow described in `planning.md`.

**What AI produced:**
A simple sequential workflow connecting the tools.

**What I revised:**
I added query parsing, session state management, error handling for no-results scenarios, and early termination logic so the agent would stop when no listings were found instead of continuing with invalid data.
