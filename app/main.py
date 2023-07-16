from fastapi import Cookie, FastAPI, Form, Request, Response, templating
from fastapi.responses import RedirectResponse

from .flowers_repository import Flower, FlowersRepository
from .purchases_repository import Purchase, PurchasesRepository
from .users_repository import User, UsersRepository
from jose import jwt

app = FastAPI()
templates = templating.Jinja2Templates("templates")


flowers_repository = FlowersRepository()
purchases_repository = PurchasesRepository()
users_repository = UsersRepository()


@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/signup")
def signup(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
def post_signup(request: Request, email: str=Form(), name: str=Form(), password: str=Form()):
    user = User(email=email, full_name=name, password=password)
    users_repository.save(user)
    return RedirectResponse("/login", status_code=303)

@app.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

def create_jwt(user_id: int) -> str:
    body = {"user_id", user_id}
    token = jwt.encode(body, "qwe", "HS256")
    return token

def decode_jwt(token: str) -> int:
    data = jwt.decode(token, "qwe", "HS256")
    return data["user_id"]

@app.post("/login")
def post_login(request: Request, 
    response: Response,
    email: str=Form(), 
    name: str=Form(), 
    password: str=Form(),
):
    user = users_repository.get_by_email(email)
    if user.password == password:
        response = Response(
            "Logged in",
        )
        token = create_jwt(user.id)
        response.set_cookie("token", token)
        return response
    return Response("permission denied")

@app.get("/profile")
def get_profile(
    request: Request,
    token: str = Cookie(),
):
    user_id = decode_jwt(token)
    user = users_repository.get_by_id(user_id)
    return templates.TemplateResponse(
        "profile.html", 
        {
            "request": request,
            "user": user,

        },
    )
