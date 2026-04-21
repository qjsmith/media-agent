from langchain_groq import ChatGroq
from langchain.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from config import GROQ_API_KEY
from agent.tools.scanner import scan_missing_subtitles
from agent.tools.metadata import search_tmdb
from agent.tools.subtitles import download_subtitle
from agent.tools.logger import log_decision


def run_agent(task: str):
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.3-70b-versatile"
    )

    system_prompt = open("agent/prompts.py").read()

    # Step 1 - scan
    print("[Agent] Scanning library...")
    missing = scan_missing_subtitles()
    print(f"[Agent] Found {len(missing)} files missing subtitles")

    if not missing:
        print("[Agent] Nothing to do.")
        return

    # Step 2 - for each file, ask LLM what to do
    for item in missing[:5]:
        filename = item['filename']
        print(f"\n[Agent] Processing: {filename}")

        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=f"""
I found a media file missing subtitles: {filename}

Should I attempt to download subtitles for this file? 
Reply with YES or NO and a brief reason.
""")
        ]

        response = llm.invoke(messages)
        reasoning = response.content
        print(f"[Agent] LLM says: {reasoning}")

        if "YES" in reasoning.upper():
            result = download_subtitle(item['path'])
            log_decision(
                filename=filename,
                action="subtitle_download",
                reasoning=reasoning,
                success=result['success'],
                details=result
            )
            print(f"[Agent] Result: {result}")
        else:
            log_decision(
                filename=filename,
                action="skipped",
                reasoning=reasoning,
                success=False
            )


if __name__ == "__main__":
    run_agent("Find and fix missing subtitles")