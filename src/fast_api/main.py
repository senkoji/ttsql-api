from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from starlette.middleware.cors import CORSMiddleware

# OpenAI APIキーの設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class SQLRequest(BaseModel):
    sqlformat: str
    sqlcontent: str

@app.post("/hoge")
async def generate_sql(request: SQLRequest):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # モデルの選択（最新のモデル名に更新してください）
            prompt=f"In a database with a schema named '{request.sqlformat}', to extract data with the content '{request.sqlcontent}', what SQL query should be written? Please output the SQL statement.",
            max_tokens=1000  # 応答の最大トークン数
        )
        return {"sql_query": response.choices[0].text.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))