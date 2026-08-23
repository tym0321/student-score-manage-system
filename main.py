from fastapi import FastAPI, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from jinja2 import Environment, FileSystemLoader
from ai_analysis import score_analysis

app = FastAPI()

env = Environment(loader=FileSystemLoader("templates"), cache_size=0)
templates = Jinja2Templates(env=env)

students = [
    {"id": "2025001", "name": "张三", "gender": "男", "cls": "计科1班", "phone": "13800138000"},
    {"id": "2025002", "name": "李四", "gender": "女", "cls": "计科2班", "phone": "13900139000"},
    {"id": "2025003", "name": "王五", "gender": "男", "cls": "计科1班", "phone": "13700137000"},
]

scores = [
    {"name": "张三", "course": "Python编程", "score": 95},
    {"name": "李四", "course": "Python编程", "score": 88},
    {"name": "王五", "course": "Python编程", "score": 92},
]

@app.get("/", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(request, "login.html")

@app.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(), password: str = Form()):
    if username == "admin" and password == "admin":
        return RedirectResponse("/index", 302)
    return templates.TemplateResponse(request, "login.html", {"error": "用户名或密码错误"})

@app.get("/index", response_class=HTMLResponse)
def index(request: Request):
    student_count = len(students)
    score_count = len(scores)
    avg_score = round(sum(s["score"] for s in scores) / len(scores), 1) if scores else 0
    pass_rate = round(len([s for s in scores if s["score"] >= 60]) / len(scores) * 100, 1) if scores else 0
    return templates.TemplateResponse(request, "index.html", {
        "student_count": student_count,
        "score_count": score_count,
        "avg_score": avg_score,
        "pass_rate": pass_rate,
    })

@app.get("/student", response_class=HTMLResponse)
def student_list(request: Request):
    return templates.TemplateResponse(request, "student.html", {"students": students})

@app.post("/student/add")
def add_stu_post(id: str = Form(), name: str = Form(), gender: str = Form(), cls: str = Form(), phone: str = Form()):
    students.append({"id": id, "name": name, "gender": gender, "cls": cls, "phone": phone})
    return RedirectResponse("/student", 302)

@app.post("/student/edit")
def edit_stu_post(id: str = Query(), name: str = Form(), gender: str = Form(), cls: str = Form(), phone: str = Form()):
    for s in students:
        if s["id"] == id:
            s["name"] = name
            s["gender"] = gender
            s["cls"] = cls
            s["phone"] = phone
    return RedirectResponse("/student", 302)

@app.get("/student/del")
def del_stu(id: str = Query()):
    global students
    students = [s for s in students if s["id"] != id]
    return RedirectResponse("/student", 302)

@app.get("/score", response_class=HTMLResponse)
def score_list(request: Request):
    return templates.TemplateResponse(request, "score.html", {"scores": scores})

@app.get("/score/search", response_class=HTMLResponse)
def search_score(request: Request, name: str = Query()):
    filtered = [s for s in scores if name in s["name"]]
    return templates.TemplateResponse(request, "score.html", {"scores": filtered, "search_name": name})

@app.post("/score/add")
def add_score_post(name: str = Form(), course: str = Form(), score: str = Form()):
    scores.append({"name": name, "course": course, "score": int(score)})
    return RedirectResponse("/score", 302)

@app.post("/score/edit")
def edit_score_post(
    name: str = Query(), course: str = Query(),
    new_course: str = Form(), score: str = Form(),
    orig_name: str = Form(), orig_course: str = Form(),
):
    for s in scores:
        if s["name"] == orig_name and s["course"] == orig_course:
            s["course"] = new_course
            s["score"] = int(score)
    return RedirectResponse("/score", 302)

@app.get("/score/del")
def del_score(name: str = Query(), course: str = Query()):
    global scores
    scores = [s for s in scores if not (s["name"] == name and s["course"] == course)]
    return RedirectResponse("/score", 302)

@app.get("/ai", response_class=HTMLResponse)
def ai(request: Request):
    result = score_analysis(scores)
    if "平均分" in result:
        stats = {
            "平均分": result["平均分"],
            "及格率": result["及格率(%)"],
            "最高分": max(s["score"] for s in scores),
            "最低分": min(s["score"] for s in scores),
        }
        distribution = {
            "优秀": len([s for s in scores if s["score"] >= 90]),
            "良好": len([s for s in scores if 80 <= s["score"] < 90]),
            "中等": len([s for s in scores if 70 <= s["score"] < 80]),
            "及格": len([s for s in scores if 60 <= s["score"] < 70]),
            "不及格": len([s for s in scores if s["score"] < 60]),
        }
        return templates.TemplateResponse(request, "ai_analysis.html", {
            "stats": stats,
            "distribution": distribution,
            "rankings": result["成绩排名"],
            "failing": result["挂科学生"],
        })
    return templates.TemplateResponse(request, "ai_analysis.html", {"stats": None})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)