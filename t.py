from typing import Literal
from pydantic import BaseModel, Field

class VoiceSetting(BaseModel):
  # 生成声音的速度
  speed: float = 1.0
  # 生成声音的音量
  vol: float = 1.0
  # 生成声音的音调
  pitch: int = 0
  # 系统音色id
  voice_id: str
  emotion: Literal["happy", "sad", "angry", "fearful", "disgusted", "surprised", "neutral"] | None = None
  latex_read: bool | None = None
  english_normalization: bool | None = None

class AudioSetting(BaseModel):
  # 生成声音的采样率
  sample_rate: Literal[8000, 16000, 22050, 24000, 32000, 44100] = 32000
  # 生成声音的比特率
  bitrate: Literal[32000, 64000, 128000, 256000] = 128000
  # 生成声音的格式
  format: Literal['mp3', 'wav', 'pcm', 'flac'] = 'mp3'
  # 生成声音的声道数
  channel: Literal[1, 2] | None = None

class Pronunciation(BaseModel):
  tone: list[str] = []

class TimberWeights(BaseModel):
  voice_id: str
  weight: int = Field(100, ge=1, le=100)

class StreamOptions(BaseModel):
  exclude_aggregated_audio: bool = False

class GenerateAudioPayload(BaseModel):
  text: str
  model: str = 'speech-02-hd'
  voice_setting: VoiceSetting | None = None
  audio_setting: AudioSetting | None = None
  pronunciation_dict: Pronunciation | None = None
  timber_weights: list[TimberWeights] | None = None
  stream: bool | None = None
  stream_options: StreamOptions | None = None
  language_boost: str | None = None
  subtitle_enable: bool | None = None
  output_format: Literal['hex', 'url'] | None = 'url'
