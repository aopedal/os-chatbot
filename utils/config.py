import os

# Inference config
LLM_HOST = os.getenv("LLM_HOST", "localhost")
LLM_PORT = int(os.getenv("LLM_PORT", 8000))
LLM_BASE = f"http://{LLM_HOST}:{LLM_PORT}/v1"
MAX_TOKENS = 2048
TEMPERATURE = 0.2

# Vector db config
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))

WEAVIATE_HOST = os.getenv("WEAVIATE_HOST", "localhost")
WEAVIATE_PORT = int(os.getenv("WEAVIATE_PORT", 6444))
WEAVIATE_PORT_GRPC = int(os.getenv("WEAVIATE_PORT_GRPC", 50051))

# Retrieval server config
RETRIEVAL_HOST = os.getenv("RETRIEVAL_HOST", "localhost")
RETRIEVAL_PORT = int(os.getenv("RETRIEVAL_PORT", 8080))
RETRIEVAL_URL = f"http://{RETRIEVAL_HOST}:{RETRIEVAL_PORT}"
STATIC_FILES_HOST = os.getenv("STATIC_FILES_HOST", RETRIEVAL_URL)
STATIC_FILES_URI_PATH = os.getenv("STATIC_FILES_URI_PATH", "/ref/")

# Embedding models
EMBEDDING_MODELS = [
    {"id": "Alibaba-NLP/gte-multilingual-base", "name": "GTE Multilingual Base"},
    {"id": "intfloat/multilingual-e5-large", "name": "Multilingual E5 Large"},
    {"id": "BAAI/bge-m3", "name": "BGE-M3"},
    {"id": "ltg/norbert3-base", "name": "Norbert3 Base"},
    {"id": "NbAiLab/nb-sbert-base", "name": "NB-SBERT Base"},
]

# Knowledge config
CHUNK_INPUT_FILE = "processed_chunks.jsonl"

# System prompt
SYSTEM_PROMPT = (
    "Du er HårekBot, en hjelpsom og jovial assistent som gir nøyaktige svar om operativsystemer og Linux. "

    "Fra systemet får du et utvalg av pensummateriale fra faget DATA2500 Operativsystemer. "
    "Du skal i størst mulig grad bruke pensummaterialet til å svare på brukerens spørsmål. "

    "Bruk rikelig med kildereferanser, slik at det tydelig hvilken kilde som er brukt i hvilken del av svaret. "
    "Kildereferanser skal alltid oppgis med klammer, f.eks. [linux9.2] eller [os13.1]. "
    "Det er viktig at du bruker klammer, siden frontenden bruker dette formatet for å knytte linker til referansene. "
    "Hvis en kodeblokk trenger kildereferanse, skal denne legges under kodeblokken, ikke inni. "

    # Alternativt: Du skal kun bruke informasjon fra kildene. Hvis kildene ikke inneholder svar på spørsmålet, skal du si...
    "Hvis pensummaterialet ikke inneholder nok informasjon til å svare fullstendig, kan du supplere med generell AI-kunnskap. "
    "Oppgi alltid 'generell AI-kunnskap' som referanse for informasjon som ikke er hentet fra pensummaterialet. "

    "Hvis brukeren stiller spørsmål som fremstår helt urelatert til ditt tiltenkte formål, "
    "skal du oppgi at du ikke kan hjelpe med det, og oppfordre brukeren til å spørre om det du er ekspert på. "
    "Du kan svare på praktiske spørsmål om kurset hvis kildene inneholder relevant informasjon. "
)