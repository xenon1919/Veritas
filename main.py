import sys

from agent_core.agent import research


def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = input("Research question: ").strip()

    if not question:
        print("No question provided.")
        return

    print(f"\nResearching: {question}\n")
    result = research(question, on_progress=print)
    print("\n=== Report ===\n")
    print(result["report"])


if __name__ == "__main__":
    main()
