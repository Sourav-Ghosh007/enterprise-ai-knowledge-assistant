from fastapi import FastAPI
app = FastAPI(title = "Enterprise AI Knowledge Assistant")

@app.get("/") 
def home(): return {"message": "Enterprise AI Knowledge Assistant is running"}       