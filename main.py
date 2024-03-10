import sys, os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# ________________ HANDLE THE PATH THING ________________ #
# get the absolute path of the script's directory
script_path = os.path.dirname(os.path.abspath(__file__))
# get the parent directory of the script's directory
parent_path = os.path.dirname(script_path)
sys.path.append(parent_path)


from endpoints.todotoday_backend import router as todotoday_router
from endpoints.aichatbot_web_backend import router as aichatbot_web_router
from endpoints.englishtutor_backend import router as englishtutor_router
from endpoints.talkativeagent_backend import router as talkativeagent_router
from endpoints.thehappycave_auth_backend import router as thehappycave_auth_router


app = FastAPI()


# CORS configuration
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:4173",
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "https://aichatbot-e.netlify.app",
    "https://todotoday0.netlify.app",
]

# Configure CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


app.include_router(todotoday_router, prefix="/todotoday")
app.include_router(aichatbot_web_router, prefix="/aichatbot_web")
app.include_router(englishtutor_router, prefix="/english_tutor")
app.include_router(talkativeagent_router, prefix="/talkative_agent")
app.include_router(thehappycave_auth_router, prefix="/thehappycave_auth")


if __name__ == "__main__":
    import uvicorn

    port = int(
        os.environ.get("PORT", 8000)  # 8000 for local
    )  # define port so we can map container port to localhost

    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)  # True for test
