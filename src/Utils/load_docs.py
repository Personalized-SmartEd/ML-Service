import os
from concurrent.futures import ThreadPoolExecutor
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
import chromadb
from tqdm import tqdm

docs_dir = '../../docs'
persist_directory = '../../data'

def load_pdf(pdf_path):
    """Load a single PDF with error handling"""
    try:
        loader = PyPDFLoader(pdf_path)
        docs = loader.load()
        return docs
    except Exception as e:
        print(f"\n Error loading {pdf_path}: {str(e)}")
        return []

def process_subject(class_name, subject, chroma_client):
    """Process all PDFs in a subject folder"""
    subject_path = os.path.join(docs_dir, class_name, subject)
    
    # Get all PDF files
    pdf_files = [
        os.path.join(subject_path, f) 
        for f in os.listdir(subject_path) 
        if f.endswith(".pdf")
    ]
    
    if not pdf_files:
        return 0

    with ThreadPoolExecutor() as executor:
        results = list(tqdm(
            executor.map(load_pdf, pdf_files),
            total=len(pdf_files),
            desc=f"📥 Loading {subject} PDFs",
            unit="pdf"
        ))
    
    documents = []
    for docs in results:
        for doc in docs:
            doc.metadata.update({
                "class": class_name,
                "subject": subject
            })
        documents.extend(docs)

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Increased chunk size
        chunk_overlap=200,
        length_function=len
    )
    
    texts = text_splitter.split_documents(documents)
    
    # Create collection
    collection_name = f"{class_name}_{subject}".replace(" ", "_")
    collection = chroma_client.get_or_create_collection(name=collection_name)
    
    # Batch upsert with progress
    batch_size = 100
    with tqdm(total=len(texts), desc=f"📤 Storing {subject} chunks") as pbar:
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i+batch_size]
            collection.upsert(
                ids=[f"doc_{i+j}" for j in range(len(batch))],
                documents=[doc.page_content for doc in batch],
                metadatas=[{
                    "source": doc.metadata.get("source", ""),
                    "page": doc.metadata.get("page", 0),
                    "class": class_name,
                    "subject": subject
                } for doc in batch]
            )
            pbar.update(len(batch))
    
    return len(texts)


def main():
    os.makedirs(persist_directory, exist_ok=True)
    chroma_client = chromadb.PersistentClient(path=persist_directory)

    # Process all classes and subjects
    total_chunks = 0
    for class_name in os.listdir(docs_dir):
        class_path = os.path.join(docs_dir, class_name)
        print(class_path)
        if not os.path.isdir(class_path):
            continue

        print(f"\n🏫 Processing Class: {class_name}")
        
        subjects = [d for d in os.listdir(class_path) 
                   if os.path.isdir(os.path.join(class_path, d))]
        print('Subject  = ',subjects)
        for subject in subjects:
            print(f"\n📚 Subject: {subject}")
            chunk_count = process_subject(class_name, subject, chroma_client)
            total_chunks += chunk_count
            print(f"✅ Added {chunk_count} chunks for {subject}")

    print(f"\n🎉 Total chunks ingested: {total_chunks}")

if __name__ == "__main__":
    main()