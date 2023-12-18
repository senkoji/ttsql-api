from fastapi import FastAPI
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

class SqlResponse(BaseModel):
    sqlformat: str
    sqlcontent: str

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,   # 追記により追加
    allow_methods=["*"],      # 追記により追加
    allow_headers=["*"]       # 追記により追加
)

@app.get("/")
def index():
    return {"message": "Hello World"}

@app.post("/hoge")
def console_result(data: SqlResponse):
    input_data = data.sqlformat + data.sqlcontent
    return {'あなたの入力値の結合！': input_data}
