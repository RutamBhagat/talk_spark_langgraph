import re


def scrape_profile(markdown_content: str) -> str:
    """
    Clean markdown content by removing unnecessary elements while preserving core information.

    Args:
        markdown_content (str): Raw markdown content

    Returns:
        str: Cleaned content with unnecessary elements removed
    """
    # Remove HTML tags
    content = re.sub(r"<[^>]+>", "", markdown_content)

    # Remove markdown links but keep link text
    content = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", content)

    # Remove reference-style links
    content = re.sub(r"\[\^?\d+\](?:\[[^\]]*\]|\([^\)]*\))?", "", content)

    # Remove URLs
    content = re.sub(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        "",
        content,
    )

    # Remove markdown tables
    content = re.sub(r"\|[^\n]*\|", "", content)
    content = re.sub(r"[-|]+\s*\n", "", content)

    # Remove multiple newlines and whitespace
    content = re.sub(r"\n\s*\n\s*\n", "\n\n", content)

    # Remove footnotes
    content = re.sub(r"^\[\^[^\]]*\]:[^\n]*$", "", content, flags=re.MULTILINE)

    # Remove image markdown
    content = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", content)

    # Remove emphasis markers but keep the text
    content = re.sub(r"[*_]{1,2}([^*_]+)[*_]{1,2}", r"\1", content)

    # Remove code blocks
    content = re.sub(r"```[^`]*```", "", content)
    content = re.sub(r"`[^`]+`", "", content)

    # Remove heading markers
    content = re.sub(r"^#+\s*", "", content, flags=re.MULTILINE)

    # Clean up any remaining artifacts
    content = re.sub(r"\s+", " ", content)  # Collapse multiple spaces
    content = re.sub(r"\n\s*\n", "\n\n", content)  # Normalize line breaks
    content = re.sub(r"^\s+|\s+$", "", content, flags=re.MULTILINE)  # Trim lines

    # Final cleanup
    cleaned_paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    return "\n\n".join(cleaned_paragraphs)
