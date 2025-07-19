import asyncio
import aiohttp
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import db
import t
import utils
import requests

load_dotenv()
headers = {
  'authority': 'api.minimax.com',
  'Authorization': f'Bearer {os.getenv("MINIMAX_API_KEY")}',
  'Content-Type': 'application/json',
}
# sample_text = '江山如此多娇，引无数英雄竞折腰。惜秦皇汉武，略输文采；唐宗宋祖，稍逊风骚。一代天骄，成吉思汗，只识弯弓射大雕。俱往矣，数风流人物，还看今朝。'
sample_text = '想来西北的朋友，一定要先联系我们。小恐龙国旅推出的青甘环线纯玩王牌线路，7天6晚畅游青海湖、茶卡盐湖、U型公路、水上雅丹、翡翠湖、黑独山、莫高窟、鸣沙山、七彩丹霞、祁连草原、门源花海，体验独属于大西北的五彩斑斓。吃的是羊肉串、辣条子拌面，手抓羊肉，炕锅羊排，牦牛肉火锅，我们全程安排入住星级舒适酒店，现在点击左下角推荐链接，还能升级一晚摩洛哥星空帐篷，置身沙漠中，抬头仰望漫天星辰...现在人均2000出头就足够了，没有隐形购物环节和强制消费，小恐龙国际旅行社承诺，不满意免费重游，现在暑期青甘2-8人纯玩小团名额不多了，赶紧点击左下角链接咨询详情吧'

@asynccontextmanager
async def lifespan(app: FastAPI):
    db.create_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.post('/voices')
async def generate_voice(template_file: UploadFile, name: str = Form()):
   async with aiohttp.ClientSession() as s:
      upload_file_payload = aiohttp.FormData()
      upload_file_payload.add_field('file', template_file.file, filename=template_file.filename, content_type=template_file.content_type)
      upload_file_payload.add_field('purpose', 'voice_clone')
      upload_resp, _ = await utils.fetch(
         s,
         url=build_minimaxi_api_url('/files/upload'),
         method='POST',
         # 移除Content-Type，让aiohttp自动设置
         headers=dict(filter(lambda p: p[0].lower() != 'content-type', headers.items())),
         data=upload_file_payload,
      )
      upload_resp_error_message = utils.validate_minimaxi_response(upload_resp, '上传文件')
      if upload_resp_error_message: return utils.error(code=400, message=upload_resp_error_message)
      file_id = upload_resp['file']['file_id']
      # voice_id 是自定义生成的，作用是标识一个音色，后续调用音频生成相关api时可以使用
      voice_id = f'V{utils.generate_uuid(31)}'
      voice_clone_payload = { 'file_id': file_id, 'voice_id': voice_id, 'text': sample_text, 'model': 'speech-02-hd' }
      voice_clone_resp, _ = await utils.fetch(
         s,
         url=build_minimaxi_api_url('/voice_clone'),
         method='POST',
         headers=headers,
         json=voice_clone_payload,
      )
      voice_clone_error_message = utils.validate_minimaxi_response(voice_clone_resp, '生成音色')
      if voice_clone_error_message: return utils.error(code=400, message=voice_clone_error_message)
      if voice_clone_resp['input_sensitive']: return utils.error(message='音色命中了风控，生成失败')
      voice = db.create_voice(voice_id, file_id, name, voice_clone_resp['demo_audio'])
      return utils.ok(data=voice)

@app.get('/voices')
async def get_all_voices():
  """获取所有音色"""
  result = db.get_all_voices()
  return utils.ok(data=list(map(lambda v: { 'id': v[0], 'voice_id': v[1], 'file_id': v[2], 'name': v[3] ,'demo_audio': v[4]}, result)))

@app.post('/audio/generate')
async def generate_audio_by_text(payload: t.GenerateAudioPayload):
   json_str = payload.model_dump_json(exclude_none=True)
   print('generate_audio_by_text payload:')
   print(json_str)
   async with aiohttp.ClientSession() as s:
      resp, _ = await utils.fetch(
         s,
         url=build_minimaxi_api_url('/t2a_v2'),
         method='POST',
         headers=headers,
         data=json_str,
      )
      error_message = utils.validate_minimaxi_response(resp, '生成音频')
      if error_message: return utils.error(code=400, message=error_message)
      return utils.ok(data={ 'extra_info': resp['extra_info'], 'audio_url': resp['data']['audio'] })

def build_minimaxi_api_url(path: str):
   return f'https://api.minimaxi.com/v1{path}?GroupId={os.getenv("MINIMAX_GROUP_ID")}'

def main():
   url = f'https://api.minimaxi.com/v1/files/upload?GroupId={os.getenv("MINIMAX_GROUP_ID")}'
   headers = {
      'authority': 'api.minimax.com',
      'Authorization': f'Bearer {os.getenv("MINIMAX_API_KEY")}',
   }
   data = { 'purpose': 'voice_clone' }
   files = { 'file': open('video.mp3', 'rb') }
   resp = requests.post(url, headers=headers, data=data, files=files)
   print(resp.request.headers)
   print(resp.text)
   
# if __name__ == '__main__':
#    main()