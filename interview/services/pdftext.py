from langchain_community.document_loaders import PyPDFLoader


def extract_text(path: str) -> str:
    pages = PyPDFLoader(path).load()
    return "\n\n".join(page.page_content for page in pages).strip()
