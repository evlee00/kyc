from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from db import get_conn

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def home(request: Request, category: str = "", search: str = "", sort: str = "subs"):
    conn = get_conn()
    cur = conn.cursor()

    query = """
        SELECT title, category, subscriber_count, view_count, video_count
        FROM youtube_channels
        WHERE 1=1
    """
    params = []

    if category:
        query += " AND category = %s"
        params.append(category)
    if search:
        query += " AND LOWER(title) LIKE %s"
        params.append(f"%{search.lower()}%")

    if sort == "views":
        query += " ORDER BY view_count DESC"
    elif sort == "videos":
        query += " ORDER BY video_count DESC"
    else:
        query += " ORDER BY subscriber_count DESC"

    cur.execute(query, params)
    rows = cur.fetchall()
    cur.close()
    conn.close()

    data = [
        {"rank": i + 1, "title": r[0], "category": r[1], "subs": r[2], "views": r[3], "videos": r[4]}
        for i, r in enumerate(rows)
    ]

    # 그래프용 데이터 (상위 10개)
    top10 = data[:10]
    labels = [d["title"] for d in top10]
    subs = [d["subs"] for d in top10]
    views = [d["views"] for d in top10]

    return templates.TemplateResponse("index.html", {
        "request": request,
        "channels": data,
        "category": category,
        "search": search,
        "sort": sort,
        "labels": labels,
        "subs": subs,
        "views": views
    })
