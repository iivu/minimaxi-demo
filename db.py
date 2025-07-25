import sqlite3
import os
import time

def create_db():
  if not os.path.exists('app.db'):
    conn = sqlite3.connect('app.db')
    # voices表
    # 字段：id, voice_id, file_id, name, demo_audio, is_deleted, created_at, updated_at
    conn.execute("CREATE TABLE IF NOT EXISTS voices (id INTEGER PRIMARY KEY AUTOINCREMENT, voice_id TEXT, file_id TEXT, name TEXT, demo_audio TEXT, is_deleted INTEGER DEFAULT 0, created_at INTEGER, updated_at INTEGER)")
    conn.close()

def create_voice(voice_id: str, file_id: str, name: str, demo_audio: str):
  conn = sqlite3.connect('app.db')
  now = int(time.time())
  conn.execute("INSERT INTO voices (voice_id, file_id, name, demo_audio, is_deleted, create_at, update_at) VALUES (?, ?, ?, ?, ?, ?, ?)", (voice_id, file_id, name, demo_audio, 0, now, now))
  conn.commit()
  conn.close()
  return { 'voice_id': voice_id, 'file_id': file_id, 'name': name, 'demo_audio': demo_audio }

def get_all_voices():
  conn = sqlite3.connect('app.db')
  cursor = conn.execute("SELECT * FROM voices")
  voices = cursor.fetchall()
  conn.close()
  return voices

def get_voice_by_voice_id(voice_id: str):
  conn = sqlite3.connect('app.db')
  cursor = conn.execute("SELECT * FROM voices WHERE voice_id = ?", (voice_id,))
  voice = cursor.fetchone()
  conn.close()
  return voice
