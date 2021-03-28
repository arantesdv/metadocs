#!/usr/bin/env python
# coding: utf-8

import bcrypt
import os
from pydantic import (BaseModel, validator)
from fastapi import (Depends, FastAPI, Form, Request)
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from deta import Deta
from typing import (List, Union, Dict, Any)
from dotenv import (load_dotenv, find_dotenv)

templates = Jinja2Templates(directory='./templates')

load_dotenv(find_dotenv('.env'))


PROJECT_KEY: str = os.getenv('PROJECT_KEY')
PROJECT_ID: str = os.getenv('PROJECT_ID')
API: str = 'essencia.users'
MODEL: str = 'User'


async def get_user_table() -> Deta.Base:
    return Deta(project_id=PROJECT_ID, project_key=PROJECT_KEY).Base(MODEL)


async def get_user(key: str) -> Union[Dict[str, Any], None]:
    table = await get_user_table()
    exist = table.get(key=key)
    return exist if exist is not None else None


async def get_users(table: Deta.Base = Depends(get_user_table)):
    return next(table.fetch({}))


async def hash_password(userin: 'UserIn'):
    if userin.password1 == userin.password2:
        salt = bcrypt.gensalt()
        secret = bcrypt.hashpw(bytes(userin.password1.encode()), salt)
        return secret
    raise ValueError('passwords are not equal')


async def check_hash(username: str, password: str):
    user = await get_user(key=username)
    if bcrypt.checkpw(password.encode(), user['secret'].encode()):
        print("match")
        return True
    else:
        print("does not match")
        return False


class Message(dict):
    '''Message error class '''
    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        for k, v in kwargs.items():
           setattr(self, k, v)


class UserBase(BaseModel):
    username: str 
        
        
class UserIn(UserBase):
    password1: str
    password2: str

    @validator('password1', allow_reuse=True)
    def pass1(cls, v: str):
        if len(v) > 7:
            return v
        raise ValueError('a senha deve ser maior que 7 caracteres')

    @validator('password2', allow_reuse=True)
    def pass2(cls, v: str, values):
        if 'password1' in values:
            if values['password1'] == v:
                return v
        raise ValueError('as senhas não conferem')
        
        
class UserOut(UserBase):
    pass


class User(UserBase):
    key: str


class UserData(User):
    secret: str


app = FastAPI(title=API)


@app.get('/{username}', response_model=UserOut)
async def read(username: str):
    return await get_user(key=username)


@app.post('/', response_model=Union[User, dict])
async def create(username: str = Form(...),
              password1: str = Form(...),
              password2: str = Form(...),
              table: Deta.Base = Depends(get_user_table)) -> Union[User, dict]:

    exist = await get_user(key=username)
    if exist:
        return dict(error='este usuário ja existe')
    userin = UserIn(username=username, password1=password1, password2=password2)
    try:
        secret = await hash_password(userin=userin)
        userdata = UserData(key=userin.username, secret=secret.decode(), username=userin.username)
        created = table.put(userdata.dict())
        if created:
            return User(**created)
    except:
        return dict(error='o usuário não pode ser criado')


@app.get('/api/', response_model=List[UserOut])
async def list(users = Depends(get_users)):
    return users

@app.get('/', response_model=List[UserOut], response_class=HTMLResponse)
async def list(users = Depends(get_users), request: Request = Request):
    context = dict(request=request, users=users)
    return templates.TemplateResponse('users.html', context=context)


@app.post('/api/login', response_model=bool)
async def check(username: str, password: str):
    result = await check_hash(username, password)
    return result


@app.get('/login', response_class=HTMLResponse)
async def start(request: Request = Request):
    return templates.TemplateResponse('login.html', context=dict(request=request))


@app.post('/send/', response_model=List[UserOut], response_class=HTMLResponse)
async def check(username: str, password: str, request: Request = Request):
    result = await check_hash(username, password)
    return templates.TemplateResponse('login.html',
                                      context=dict(request=request, result='logado com sucesso' if result else 'login não realizado'))


if __name__ == '__main__':
    gen = (x for x in range(7777,8888))
    import uvicorn
    try:
        uvicorn.run('main:app', host='127.0.0.1', reload=True, port=next(gen))
    except:
        try:
            uvicorn.run('main:app', host='127.0.0.1', reload=True, port=next(gen))
        except:
            try:
                uvicorn.run('main:app', host='127.0.0.1', reload=True, port=next(gen))
            except:
                try:
                    uvicorn.run('main:app', host='127.0.0.1', reload=True, port=next(gen))
                except:
                    pass