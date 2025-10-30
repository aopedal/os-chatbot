# Inference config
LLM_BASE = "http://127.0.0.1:8000/v1"
MAX_TOKENS = 2048
TEMPERATURE = 0.2

# Vector db config
QDRANT_HOST = "localhost"
QDRANT_PORT = 6333
WEAVIATE_HOST = "localhost"
WEAVIATE_PORT = 6444
WEAVIATE_PORT_GRPC = 50051

# Embedding models
EMBEDDING_MODELS = [
    {"id": "ltg/norbert3-base", "name": "Norbert3 Base"},
    {"id": "NbAiLab/nb-sbert-base", "name": "NB-SBERT Base"},
    {"id": "intfloat/multilingual-e5-large", "name": "Multilingual E5 Large"},
    {"id": "BAAI/bge-m3", "name": "BGE-M3"},
    {"id": "Alibaba-NLP/gte-multilingual-base", "name": "GTE Multilingual Base"},
]

# Knowledge config
CHUNK_INPUT_FILE = "processed_chunks.jsonl"
STATIC_FILES_URI_PATH = "/ref/"

# System prompt
SYSTEM_PROMPT = (
    "Du er HårekBot, en hjelpsom assistent som gir nøyaktige svar om operativsystemer og Linux. "
    "Sammen med brukerens spørsmål får du systemkontekst i form av pensummateriale fra faget DATA2500 Operativsystemer. "
    "Du skal i størst mulig grad bruke systemkonteksten til å svare på brukerens spørsmål. "
    "Bruk rikelig med kildereferanser, slik at det tydelig hvilken kilde som er brukt i hvilken del av svaret. "
    "Kildereferanser skal oppgis med identifier i klammer. Eksempel: [node6_17_515]. Frontenden gjør dette om til linker. "
    "Hvis du tilføyer informasjon som ikke er nevnt i kildene, skal du tydelig oppgi ChatGPT som referanse. "
)