from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import openai
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from starlette.middleware.cors import CORSMiddleware
from typing import Optional
import random
import string

# OpenAI APIキーの設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# SQLAlchemy設定
SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:~1000koji+1ki@127.0.0.1:3306/ttsqlpjt?charset=utf8mb4"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# モデルの定義
class SQLInfo(Base):
    __tablename__ = "sqlinfo"
    user_id = Column(String(3), primary_key=True, index=True)
    sqlformat = Column(Text, index=True)

# データベース初期化
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

class SQLRequest(BaseModel):
    sqlformat: Optional[str] = None
    sqlcontent: str
    user_id: Optional[str] = None

@app.post("/hoge")
async def generate_sql(request: SQLRequest):
    try:
        db = SessionLocal()
        new_user_id = False

        if request.user_id:
            # フロントエンドからuser_idを受け取った場合の処理
            db_sqlinfo = db.query(SQLInfo).filter(SQLInfo.user_id == request.user_id).first()
            if not db_sqlinfo:
                # レコードが存在しない場合の処理で404エラーを返す。
                raise HTTPException(status_code=404, detail="User ID not found")
            sqlformat = db_sqlinfo.sqlformat
            user_id = request.user_id
        else:
            # フロントエンドからuser_idを受け取らなかった場合の処理
            new_user_id = True
            new_user_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=3))
            sqlformat = request.sqlformat or ""  # sqlformatがNoneの場合は空文字列を使用
            db_sqlinfo = SQLInfo(user_id=new_user_id, sqlformat=sqlformat)
            db.add(db_sqlinfo)
            db.commit()

        # OpenAI APIをコール
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"In a database with a schema named '{sqlformat}', to extract data with the content '{request.sqlcontent}', what SQL query should be written? Please output the SQL statement.",
            max_tokens=1000
        )
        sql_query = response.choices[0].text.strip()

        # 新しいuser_idが生成された場合は、sql_queryとuser_idを返す
        if new_user_id:
            return {"sql_query": sql_query, "user_id": new_user_id}
        # 既存のuser_idが使用された場合は、sql_queryのみを返す
        else:
            return {"sql_query": sql_query, "user_id": user_id}
    except Exception as e:
        # エラーハンドリング
        error_message = f"予期せぬエラーが発生しました: {type(e).__name__} - {e}"
        print(error_message)
        return JSONResponse(status_code=500, content={"detail": error_message})
    finally:
        db.close()

