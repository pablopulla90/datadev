from __future__ import annotations

from sqlmodel import Session

from app.models.entities import CrawlRun, ProcessedDocument, RawDocument, Source
from app.services.nlp_utils import clean_text, detect_language, sentiment, topic_from_text


def run_scraping(session: Session, source: Source, project_id: int) -> CrawlRun:
    run = CrawlRun(project_id=project_id, source_id=source.id, status="running")
    session.add(run)
    session.commit()
    session.refresh(run)

    try:
        import httpx
        from bs4 import BeautifulSoup

        response = httpx.get(source.url, timeout=10.0)
        response.raise_for_status()
        html = response.text

        raw = RawDocument(run_id=run.id, url=source.url, html=html)
        session.add(raw)

        soup = BeautifulSoup(html, "html.parser")
        for tag in soup(["script", "style", "noscript"]):
            tag.extract()

        selected = soup.select(source.selector_rule or "body")
        text = " ".join([item.get_text(" ", strip=True) for item in selected])
        normalized = clean_text(text)
        language = detect_language(normalized)
        label, score, confidence = sentiment(normalized)
        topic = topic_from_text(normalized)

        processed = ProcessedDocument(
            run_id=run.id,
            url=source.url,
            text=normalized,
            language=language,
            sentiment_label=label,
            sentiment_score=score,
            confidence=confidence,
            topic=topic,
        )
        session.add(processed)

        run.status = "completed"
        session.add(run)
        session.commit()
    except Exception as exc:
        run.status = "failed"
        run.error = str(exc)
        session.add(run)
        session.commit()

    session.refresh(run)
    return run
