from urllib.parse import urljoin, urlparse

from django.conf import settings
from django.core.files.storage import default_storage


def is_absolute_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return bool(parsed.scheme and parsed.netloc)


def normalize_media_url(value: str | None, request=None) -> str | None:
    if not value:
        return None

    if is_absolute_url(value):
        return value

    if value.startswith("/"):
        relative_url = value
    else:
        relative_url = _storage_url(value)

    public_base_url = getattr(settings, "MEDIA_PUBLIC_BASE_URL", "").strip()
    if public_base_url:
        return urljoin(f"{public_base_url.rstrip('/')}/", relative_url.lstrip("/"))

    if request is not None:
        return request.build_absolute_uri(relative_url)

    return relative_url


def normalize_media_urls(values, request=None) -> list[str]:
    return [url for url in (normalize_media_url(value, request) for value in values) if url]


def _storage_url(value: str) -> str:
    try:
        return default_storage.url(value)
    except Exception:
        return urljoin(settings.MEDIA_URL, value)
