import aiohttp
from typing import Any
from fastapi.responses import JSONResponse
from nanoid import generate

ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'

def generate_uuid(len = 32):
  return generate(ALPHABET, len)

async def fetch(s: aiohttp.ClientSession, **kwargs):
  method = kwargs.pop('method', 'GET')
  url = kwargs.pop('url', '')
  async with s.request(method, url, **kwargs) as r:
    return (None, r.status) if r.status != 200 else (await r.json(), r.status)

def ok(*, code = 200, data = None):
 return JSONResponse(content={'code': code, 'data': data, 'message': 'ok'}, status_code=200)

def error(*, code = 500, data = None, message = 'Internal Server Error'):
  return JSONResponse(content={'code': code, 'data': data, 'message': message}, status_code=code)

def validate_minimaxi_response(resp: dict, action: str):
  if not resp: return f'{action}失败#1'
  if not resp['base_resp']: return f'{action}失败#2'
  if resp['base_resp']['status_code'] != 0: return f"{action} - {resp['base_resp']['status_code']}/{resp['base_resp']['status_msg']}"
  return None