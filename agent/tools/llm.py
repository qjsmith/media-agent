from langchain_core.messages import HumanMessage, SystemMessage


def llm_resolve(parsed: dict, candidates: list, llm) -> dict | None:
    """Use LLM to resolve ambiguous or uncertain matches."""
    candidate_text = "\n".join([f"- {c['title']} ({c['year']}) — popularity: {c['popularity']}" for c in candidates])

    context = f"""
Filename: {parsed["filename"]}
Parent folder: {parsed["context"]["parent_folder"]}
Grandparent folder: {parsed["context"]["grandparent_folder"]}
Extracted title: {parsed["cleaned_title"]}
Season: {parsed["season"]}
Episode: {parsed["episode"]}
Year: {parsed["year"]}
"""

    prompt = f"""You are helping identify a media file for a Plex server.

Here is what we know about the file:
{context}

Here are the top TMDB candidates:
{candidate_text}

Which candidate is the most likely match? Reply with ONLY the title and year 
in this exact format: TITLE (YEAR)
If you genuinely cannot determine the match, reply with: UNKNOWN
"""

    response = llm.invoke(
        [
            SystemMessage(content="You are a media identification assistant."),
            HumanMessage(content=prompt),
        ]
    )

    answer = response.content.strip()
    print(f"  [LLM] {answer}")

    if answer == "UNKNOWN":
        return None

    for c in sorted(candidates, key=lambda x: len(x["title"]), reverse=True):
        if c["title"].lower() in answer.lower():
            return c

    return None
