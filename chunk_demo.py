def chunk_text(text,size,overlap):
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return chunks

if __name__ == "__main__":
    text = "가나다라마바사아자차카타파하" * 3
    for c in chunk_text(text, 10, 3):
        print(c)