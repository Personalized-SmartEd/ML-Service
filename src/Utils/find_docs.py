import chromadb
from fastapi import HTTPException

CHROMA_DB_PATH = './tmp/data'
chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)


def find_pdf(student_class:int, subject:str, chapter: str, query: str):
    if student_class  < 6 or 8 < student_class:
        raise HTTPException(status_code=303, detail='Can only handle class between 6 to 8')
    book_name = 'Class-'+str(student_class) + '_'+subject
    book = chroma_client.get_collection(name=book_name)
    docs = book.query(query_texts=[query, chapter], n_results=3)

    return docs