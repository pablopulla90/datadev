from collections import Counter

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from app.database import get_session, init_db
from app.models.entities import CrawlRun, ProcessedDocument, Project, Source, User
from app.services.auth import authenticate, register_user
from app.services.scraping import run_scraping

app = FastAPI(title="Plataforma de Web Scraping y Analítica")
templates = Jinja2Templates(directory="app/templates")
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, session: Session = Depends(get_session)):
    docs = session.exec(select(ProcessedDocument)).all()
    by_sentiment = Counter([d.sentiment_label for d in docs])
    by_topic = Counter([d.topic for d in docs])
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "total_docs": len(docs),
            "sentiments": dict(by_sentiment),
            "topics": dict(by_topic),
            "recent": docs[-10:],
        },
    )


@app.get("/projects", response_class=HTMLResponse)
def projects_page(request: Request, session: Session = Depends(get_session)):
    projects = session.exec(select(Project)).all()
    users = session.exec(select(User)).all()
    return templates.TemplateResponse(
        "projects.html", {"request": request, "projects": projects, "users": users}
    )


@app.post("/users/register")
def register(
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("analista"),
    session: Session = Depends(get_session),
):
    register_user(session, username, password, role)
    return RedirectResponse("/projects", status_code=303)


@app.post("/auth/login")
def login(
    username: str = Form(...),
    password: str = Form(...),
    session: Session = Depends(get_session),
):
    user = authenticate(session, username, password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    return {"message": "Autenticado", "user": {"id": user.id, "role": user.role}}


@app.post("/projects")
def create_project(
    name: str = Form(...),
    description: str = Form(""),
    owner_id: int = Form(...),
    policy: str = Form("Solo fuentes públicas/autorizadas"),
    session: Session = Depends(get_session),
):
    project = Project(name=name, description=description, owner_id=owner_id, policy=policy)
    session.add(project)
    session.commit()
    return RedirectResponse("/projects", status_code=303)


@app.post("/sources")
def create_source(
    project_id: int = Form(...),
    url: str = Form(...),
    selector_rule: str = Form("body"),
    crawl_depth: int = Form(1),
    allowed_domains: str = Form(""),
    excluded_domains: str = Form(""),
    session: Session = Depends(get_session),
):
    source = Source(
        project_id=project_id,
        url=url,
        selector_rule=selector_rule,
        crawl_depth=crawl_depth,
        allowed_domains=allowed_domains,
        excluded_domains=excluded_domains,
    )
    session.add(source)
    session.commit()
    return RedirectResponse(f"/projects/{project_id}", status_code=303)


@app.get("/projects/{project_id}", response_class=HTMLResponse)
def project_detail(project_id: int, request: Request, session: Session = Depends(get_session)):
    project = session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    sources = session.exec(select(Source).where(Source.project_id == project_id)).all()
    runs = session.exec(select(CrawlRun).where(CrawlRun.project_id == project_id)).all()
    return templates.TemplateResponse(
        "project_detail.html",
        {"request": request, "project": project, "sources": sources, "runs": runs},
    )


@app.post("/scrape/{source_id}")
def scrape_source(source_id: int, session: Session = Depends(get_session)):
    source = session.get(Source, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Fuente no encontrada")
    run_scraping(session, source, source.project_id)
    return RedirectResponse(f"/projects/{source.project_id}", status_code=303)


@app.get("/report/csv")
def export_csv(session: Session = Depends(get_session)):
    docs = session.exec(select(ProcessedDocument)).all()
    header = "url,language,sentiment,score,confidence,topic\n"
    lines = [
        f'{d.url},{d.language},{d.sentiment_label},{d.sentiment_score:.3f},{d.confidence:.3f},{d.topic}'
        for d in docs
    ]
    return HTMLResponse(header + "\n".join(lines), media_type="text/csv")
