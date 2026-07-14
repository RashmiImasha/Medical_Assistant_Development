from app.services.llm import get_structured_output
from app.models.schemas import FinancialMetrics
from types import SimpleNamespace

class Retriever:

    def __init__(self, index, embeddings, namespace=None):
        self.index = index
        self.embeddings = embeddings
        self.namespace = namespace

    def invoke(
        self,
        query,
        company=None,
        year=None,
        top_k=20
    ):

        vector = self.embeddings.embed_query(query)

        filter_dict = None

        if company and year:
            filter_dict = {
                "company": company,
                "year": year
            }

        results = self.index.query(
            vector=vector,
            top_k=top_k,
            namespace=self.namespace,
            filter=filter_dict,
            include_metadata=True
        )

        documents = []

        for match in results.matches:

            documents.append(
                SimpleNamespace(
                    page_content=match.metadata.get("text", ""),
                    metadata=match.metadata
                )
            )

        return documents
    
def retrieve_context(
    retriever: Retriever,
    company: str,
    year: int
) -> str:
    """
    Retrieve broad financial context from the vector store.
    """
    query = f"""
    Annual report financial statements,
    income statement,
    balance sheet,
    cash flow statement,
    risks,
    growth drivers,
    financial performance
    for {company} fiscal year {year}
    """

    documents = retriever.invoke(
        query=query,
        company=company,
        year=year,
        top_k=20
    )
    # print(documents)
    return "\n\n".join(
        doc.page_content
        for doc in documents
    )

def build_extraction_prompt(
    company: str,
    year: int,
    context: str
) -> str:
    """
    Build KPI extraction prompt.
    """
    return f"""
You are an expert financial analyst.

Company: {company}
Year: {year}

Context:
{context}

Extract the following information:

1. Revenue
2. Net Income
3. Operating Income
4. Cash Flow from Operating Activities
5. Total Assets
6. Total Liabilities
7. Top Risk Factors
8. Top Growth Drivers

Instructions:

- Use only the provided context.
- Return null if unavailable.
- Financial values must match the report exactly.
- Risk factors should be concise.
- Growth drivers should be concise.
- Return valid JSON only.
"""

def extract_financial_metrics(
    retriever: Retriever,
    company: str,
    year: int
) -> dict:
    """
    Extract KPIs using RAG.
    """
    context = retrieve_context(
        retriever=retriever,
        company=company,
        year=year
    )

    prompt = build_extraction_prompt(
        company=company,
        year=year,
        context=context
    )

    metrics = get_structured_output(
        prompt=prompt,
        response_model=FinancialMetrics
    )

    return metrics

