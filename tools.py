"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.
"""

import os

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    listings = load_listings()

    keywords = set(description.lower().replace("-", " ").split())
    scored_results = []

    for item in listings:
        if max_price is not None and float(item.get("price", 0)) > max_price:
            continue

        if size:
            item_size = str(item.get("size", "")).lower()
            if size.lower() not in item_size:
                continue

        searchable_text = " ".join([
            str(item.get("title", "")),
            str(item.get("description", "")),
            str(item.get("category", "")),
            " ".join(item.get("style_tags", [])),
            " ".join(item.get("colors", [])),
            str(item.get("brand", "")),
            str(item.get("platform", "")),
        ]).lower()

        score = sum(1 for word in keywords if word in searchable_text)

        if score > 0:
            scored_results.append((score, item))

    scored_results.sort(key=lambda x: x[0], reverse=True)

    return [item for score, item in scored_results]


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    client = _get_groq_client()

    wardrobe_items = wardrobe.get("items", [])

    item_details = f"""
Item:
Title: {new_item.get("title")}
Description: {new_item.get("description")}
Category: {new_item.get("category")}
Style tags: {new_item.get("style_tags")}
Colors: {new_item.get("colors")}
Price: ${new_item.get("price")}
Platform: {new_item.get("platform")}
"""

    if not wardrobe_items:
        prompt = f"""
You are FitFindr, a helpful thrift styling assistant.

The user is considering this secondhand item:

{item_details}

The user's wardrobe is empty or unavailable.

Suggest 1-2 complete outfits using general wardrobe pieces someone might own.
Be specific, casual, and practical. Mention that the advice is based on general styling because wardrobe data is limited.
"""
    else:
        wardrobe_text = "\n".join(
            [
                f"- {item.get('name', item.get('title', 'Unknown item'))}: "
                f"{item.get('category', '')}, {item.get('colors', '')}, "
                f"{item.get('style_tags', '')}"
                for item in wardrobe_items
            ]
        )

        prompt = f"""
You are FitFindr, a helpful thrift styling assistant.

The user is considering this secondhand item:

{item_details}

Here is the user's wardrobe:

{wardrobe_text}

Suggest 1-2 complete outfit combinations using the new item and specific pieces from the wardrobe.
Explain why the outfit works. Keep it friendly and concise.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a concise fashion styling assistant.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=300,
    )

    return response.choices[0].message.content.strip()


def create_fit_card(outfit: str, new_item: dict) -> str:
    if not outfit or not outfit.strip():
        return (
            "I couldn't create a fit card because the outfit suggestion was missing. "
            "Try generating an outfit first."
        )

    client = _get_groq_client()

    prompt = f"""
Create a short, shareable outfit caption for an Instagram or TikTok post.

Thrifted item:
Title: {new_item.get("title")}
Price: ${new_item.get("price")}
Platform: {new_item.get("platform")}
Condition: {new_item.get("condition")}
Colors: {new_item.get("colors")}
Style tags: {new_item.get("style_tags")}

Outfit suggestion:
{outfit}

Rules:
- 2 to 4 sentences max
- casual and authentic
- mention the item name, price, and platform naturally once
- make it sound like a real outfit caption, not a product description
- include the outfit vibe
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You write short, stylish social media outfit captions.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=1.0,
        max_tokens=180,
    )

    return response.choices[0].message.content.strip()