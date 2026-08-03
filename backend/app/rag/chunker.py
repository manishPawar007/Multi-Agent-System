import re
from typing import List
from backend.app.utils.logger import logger

class TextChunker:
    @staticmethod
    def chunk_text(
        text: str,
        chunk_size: int = 400,
        chunk_overlap: int = 50
    ) -> List[str]:
        if not text or not text.strip():
            return []

        text = text.strip()
        if len(text) <= chunk_size:
            return [text]

        # Try recursive splitting on natural delimiters
        delimiters = ["\n\n", "\n", ". ", "! ", "? ", "; ", " ", ""]
        chunks = []
        
        # Simple sliding character window fallback with boundary awareness
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            if end >= text_length:
                chunks.append(text[start:].strip())
                break

            # Find best split boundary within overlap region
            split_at = -1
            boundary_search_start = max(start + chunk_size - chunk_overlap, start)
            sub_text = text[boundary_search_start:end]

            for delim in ["\n\n", "\n", ". ", "! ", "? ", " "]:
                pos = sub_text.rfind(delim)
                if pos != -1:
                    split_at = boundary_search_start + pos + len(delim)
                    break

            if split_at == -1 or split_at <= start:
                split_at = end

            chunk_str = text[start:split_at].strip()
            if chunk_str:
                chunks.append(chunk_str)

            # Slide window back by overlap amount
            start = split_at - chunk_overlap if (split_at - chunk_overlap) > start else split_at

        return chunks
