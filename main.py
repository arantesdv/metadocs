from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory='./templates')

app = FastAPI(title='metadocs')

ORIGINS = [
    'http://localhost:8080',
    "https://v0pqn4.deta.dev",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS,
    allow_credentials=True,

)

@app.get('/', response_class=HTMLResponse)
async def home(request: Request = Request):
    data = [
        {'id':1, 'name': 'Daniel'},
        {'id': 2, 'name': 'Lélia'}

    ]
    context=dict(request=request, data=data)
    return templates.TemplateResponse('index.html', context=context)



if __name__ == '__main__':
    import uvicorn
    uvicorn.run('main:app', reload=True)