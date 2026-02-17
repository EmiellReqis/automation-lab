from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health():
   return {"status": "ok"}

@app.get("/sum")
def sum_numbers(a: int, b: int):
   return {"a": a, "b": b, "sum": a+b}
