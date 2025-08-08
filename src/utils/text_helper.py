def truncate_text(text: str, max_length: int = 150) -> str:
    if len(text) > max_length:
        return text[:max_length] + "..."
    return text


def newline_to_br(text: str) -> str:
    return text.replace("\n", "<br>")
