import uuid
from abc import ABC, abstractmethod

import utils.config as config


class CollectionType(ABC):
    id: str      # type tag stored in payloads, e.g. "course_page"
    plural: str  # collection name suffix, e.g. "course_pages"

    @abstractmethod
    def extract_source(self, payload: dict) -> tuple[str, str, str]:
        """Returns (identifier, url, text)."""
        ...


class CoursePageCollection(CollectionType):
    id = "course_page"
    plural = "course_pages"

    def extract_source(self, payload: dict) -> tuple[str, str, str]:
        identifier = payload.get("identifier") or str(uuid.uuid4())
        source = f"{config.STATIC_FILES_URI_PATH}/{payload['source']}"
        anchor = payload.get("anchor") or ""
        url = f"{source}#{anchor}" if anchor else source
        text = payload.get("text") or ""
        return identifier, url, text


class VideoTranscriptCollection(CollectionType):
    id = "video_transcript"
    plural = "video_transcripts"

    def extract_source(self, payload: dict) -> tuple[str, str, str]:
        identifier = payload.get("chunk_id") or str(uuid.uuid4())
        source = f"{config.STATIC_VIDEOS_URI_PATH}/{payload['lecture_id']}.mp4"
        start = payload.get("start")
        url = f"{source}#t={start}" if start else source
        text = payload.get("text") or ""
        return identifier, url, text


COLLECTION_TYPES: list[CollectionType] = [
    CoursePageCollection(),
    VideoTranscriptCollection(),
]

COLLECTION_TYPE_MAP: dict[str, CollectionType] = {ct.id: ct for ct in COLLECTION_TYPES}
