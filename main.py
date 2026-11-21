from dotenv import load_dotenv

from utils.audio_processor import process_input
from core.transcriber import transcribe_all
from core.summarize import summarize, generate_title
from core.extractor import (
    extract_action_items,
    extract_key_decisions,
    extract_questions
)
from core.rag_engine import build_rag_chain, ask_question

load_dotenv()


def run_pipeline(source: str, language: str = "english") -> dict:
    print("Starting AI Video Assistant...")

    # 1. Audio processing
    chunks = process_input(source)

    # 2. Transcription
    translate = language.lower() != "english"
    transcript = transcribe_all(chunks, translate=translate)

    print(f"Raw transcription (first 300 chars): {transcript[:300]}")

    # 3. Meeting intelligence
    title = generate_title(transcript)
    summary = summarize(transcript)

    # action_items = extract_action_items(transcript)
    # decisions = extract_key_decisions(transcript)
    # questions = extract_questions(transcript)

    # 4. RAG
    rag_chain = build_rag_chain(transcript)

    return {
        "title": title,
        "transcript": transcript,
        "summary": summary,
        "action_items": action_items,
        "key_decisions": decisions,
        "open_questions": questions,
        "rag_chain": rag_chain,
    }


if __name__ == "__main__":

    source = input(
        "Enter YouTube URL or local file path: "
    ).strip()

    language = input(
        "Language: "
    ).strip() or "english"

    result = run_pipeline(source, language)

    print(f"\nTitle: {result['title']}")
    print(f"\nSummary:\n{result['summary']}")

    print("\nAction Items:")
    print(result["action_items"])

    print("\nKey Decisions:")
    print(result["key_decisions"])

    print("\nOpen Questions:")
    print(result["open_questions"])

    print("\nChat with your meeting (type 'exit' to quit)")

    rag_chain = result["rag_chain"]

    while True:
        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            print("Goodbye!")
            break

        answer = ask_question(rag_chain, question)

        print(f"\nAssistant: {answer}")