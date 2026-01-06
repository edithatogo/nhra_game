"""Captures content from ChatGPT for origin verification using Playwright."""

from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    """Launch browser to capture ChatGPT context."""
    with sync_playwright() as p:
        # Launch headful browser so the user can interact
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("Opening ChatGPT...")
        page.goto("https://chatgpt.com/auth/login")

        print("\n*** ACTION REQUIRED ***")
        print("Please log in and navigate to the relevant conversation in the browser window.")
        print("Once the conversation is fully loaded and you are ready to capture,")
        input("press ENTER in this terminal to capture the content...")

        # Simple capture of the main chat area
        # ChatGPT uses different selectors, we'll try to get the text from the main thread
        print("Capturing content...")

        # This is a naive capture of all text in the main element
        # It may need refinement based on exact ChatGPT DOM structure
        content = page.evaluate("() => document.body.innerText")

        output_path = Path("context/origin_chatgpt_context.md")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("# ChatGPT Origin Context Capture\n\n")
            f.write(f"Captured on: {Path().absolute()}\n\n")
            f.write(content)

        print(f"Captured content saved to {output_path}")
        print("Closing browser...")
        browser.close()


if __name__ == "__main__":
    main()
