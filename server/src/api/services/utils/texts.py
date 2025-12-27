import re

def chunk_text_by_words(text, max_tokens=100):
    sentences = split_sentences(text)
    chunks = []
    current_chunk = []
    current_count = 0

    for sentence in sentences:
        words = sentence.split()
        word_count = len(words)

        if current_count + word_count > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_count = word_count
        else:
            current_chunk.append(sentence)
            current_count += word_count

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def split_sentences(text):
    return re.split(r'(?<=[.!?])\s+', text)