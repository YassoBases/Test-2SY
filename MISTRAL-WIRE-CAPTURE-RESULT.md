# MISTRAL-WIRE-CAPTURE-RESULT

Captured from the **real FastAPI worker** Mistral OCR HTTP exchange during teacher PDF upload (lesson **99**).

## 1. Exact outgoing request

| Field | Value |
|-------|-------|
| Timestamp (UTC) | `2026-07-01T23:40:18.471564+00:00` |
| Worker PID | `30408` |
| Request URL | `https://api.mistral.ai/v1/ocr` |
| HTTP Method | `POST` |
| Model sent | `mistral-ocr-latest` |

### Authorization fingerprint (not full key)

| Field | Value |
|-------|-------|
| First 6 chars | `g8vGm6` |
| Last 6 chars | `0t8eTm` |
| SHA-256 | `e4a1e2959bb774ad75fee4997cd7bbf616e23aedd307e901254e7f8a96eac32e` |

### Request JSON (sanitized)

| Field | Value |
|-------|-------|
| `model` | `mistral-ocr-latest` |
| `document.type` | `document_url` |
| `document` field length (chars) | `3706344` |
| PDF size (bytes) | `2779736` |
| MIME type | `application/pdf` |

## 2. Exact incoming response

| Field | Value |
|-------|-------|
| HTTP status | `200` |
| Elapsed time (ms) | `2503.7` |

### Response headers (exact)

- `access-control-allow-origin`: `*`
- `alt-svc`: `h3=":443"; ma=86400`
- `cf-cache-status`: `DYNAMIC`
- `cf-ray`: `a1494138e95cceb6-KUL`
- `connection`: `keep-alive`
- `content-encoding`: `gzip`
- `content-type`: `application/json`
- `date`: `Wed, 01 Jul 2026 23:40:18 GMT`
- `mistral-correlation-id`: `019f200e-0019-7261-b333-8afaa3e14eee`
- `server`: `cloudflare`
- `set-cookie`: `__cf_bm=8wXJ0ZiHBbuYWd.P6p1K1qOyIgiIknloYWcAiVrurrM-1782949216.14289-1.0.1.1-iMKlK5BdBc2uWjQdXtUc3zHw3ob6PJQLNJc0pxOZeZCiwkRhlJJSAUTKj5OlhkNzEEi5c1QbUjp8ugH_XdAFZE65Qlcqv.0bk2hNAbCGAmODSvXDiEDP.4gi0aVkmNoB; HttpOnly; SameSite=None; Secure; Path=/; Domain=mistral.ai; Expires=Thu, 02 Jul 2026 00:10:18 GMT`
- `strict-transport-security`: `max-age=15552000; includeSubDomains; preload`
- `transfer-encoding`: `chunked`
- `x-content-type-options`: `nosniff`
- `x-envoy-upstream-service-time`: `338`
- `x-kong-proxy-latency`: `17`
- `x-kong-request-id`: `019f200e-0019-7261-b333-8afaa3e14eee`
- `x-kong-upstream-latency`: `1740`
- `x-ratelimit-limit-ocr-pages-minute`: `625`
- `x-ratelimit-ocr-pages-query-cost`: `25`
- `x-ratelimit-remaining-ocr-pages-minute`: `600`

### Highlighted headers

| Header | Value |
|--------|-------|
| `mistral-correlation-id` | `019f200e-0019-7261-b333-8afaa3e14eee` |
| `x-kong-request-id` | `019f200e-0019-7261-b333-8afaa3e14eee` |
| `cf-ray` | `a1494138e95cceb6-KUL` |

### `x-ratelimit-*` headers

- `x-ratelimit-limit-ocr-pages-minute`: `625`
- `x-ratelimit-ocr-pages-query-cost`: `25`
- `x-ratelimit-remaining-ocr-pages-minute`: `600`

### Response JSON (selected fields; `pages` array omitted)

```json
{
  "model": "mistral-ocr-latest",
  "usage_info": {
    "pages_processed": 25,
    "doc_size_bytes": 2779736
  },
  "pages_processed": 25,
  "doc_size_bytes": 2779736,
  "billing_related_top_level_fields": {
    "pages": "<omitted array length 25>",
    "usage_info": {
      "pages_processed": 25,
      "doc_size_bytes": 2779736
    }
  }
}
```

## 3. API key fingerprint

- Prefix: `g8vGm6`
- Suffix: `0t8eTm`
- SHA-256: `e4a1e2959bb774ad75fee4997cd7bbf616e23aedd307e901254e7f8a96eac32e`

## 4. Correlation IDs

- `mistral-correlation-id`: `019f200e-0019-7261-b333-8afaa3e14eee`
- `x-kong-request-id`: `019f200e-0019-7261-b333-8afaa3e14eee`
- `cf-ray`: `a1494138e95cceb6-KUL`

## 5. Usage info

```json
{
  "pages_processed": 25,
  "doc_size_bytes": 2779736
}
```

- `pages_processed`: `25`
- `doc_size_bytes`: `2779736`

## 6. Model actually returned by Mistral

- Response top-level `model`: **`mistral-ocr-latest`**
- Request `model` sent: **`mistral-ocr-latest`**

## 7. After OCR (FastAPI pipeline)

### At wire capture (immediately after Mistral HTTP 200)

| Field | Value |
|-------|-------|
| Extracted pages (response `pages` array) | `25` |
| Extracted text length (chars) | `56920` |
| Lesson ID (upload that triggered this OCR call) | `99` |

### DB state when report was written (downstream pipeline still running)

| Field | Value |
|-------|-------|
| Generated chunks | `0` |
| Lesson status | `processing` |
| Lesson `page_count` | `None` |

OCR completed in **2503.7 ms**; chunking/quiz steps had not finished yet when this report was generated.

## 8. Mistral Usage dashboard expectation (runtime evidence only)

- Mistral response `usage_info.pages_processed` = **25**.
- Response header `x-ratelimit-ocr-pages-query-cost` = **25**.

**Conclusion:** Runtime API response records billable OCR usage (25 pages processed; query-cost header 25) for correlation ID `019f200e-0019-7261-b333-8afaa3e14eee`. This request should be attributable to API key fingerprint in section 3 under that key's Mistral workspace usage.
