from ..config import settings
from langchain.vectorstores import Chroma


_embeddings = None
_store = None




def _build_embeddings():
    if settings.use_ollama:
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(base_url=settings.ollama_host, model=settings.ollama_embed_model)
    else:
        from langchain_openai import OpenAIEmbeddings
        return OpenAIEmbeddings(model="text-embedding-3-small")




def get_embeddings():
    global _embeddings
    if _embeddings is None:
        _embeddings = _build_embeddings()
    return _embeddings




def get_store():
    global _store
    if _store is None:
        _store = Chroma(
        collection_name=settings.chroma_collection,
        persist_directory=settings.chroma_dir,
        embedding_function=get_embeddings(),
        )
    return _store




def add_docs(texts: list[str], metadatas: list[dict] | None = None):
    store = get_store()
    store.add_texts(texts, metadatas=metadatas)
    store.persist()




def query(q: str, k: int = 4):
    return get_store().similarity_search(q, k=k)