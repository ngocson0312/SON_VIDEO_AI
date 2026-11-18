# -*- coding: utf-8 -*-
"""nghe.py <video> <work_dir> : tách tiếng + Whisper large-v3 (CPU) -> words.json + loi_doc.txt"""
import sys, os, json, subprocess, wave
import numpy as np
video, work = sys.argv[1], sys.argv[2]
os.makedirs(work, exist_ok=True)
wav = os.path.join(work, 'tieng16k.wav')
subprocess.run(['ffmpeg','-y','-v','error','-i',video,'-vn','-ac','1','-ar','16000','-af','highpass=f=80','-c:a','pcm_s16le',wav],check=True)
with wave.open(wav,'rb') as wf:
    pcm = np.frombuffer(wf.readframes(wf.getnframes()), np.int16).astype(np.float32)/32768.0
from faster_whisper import WhisperModel
m = WhisperModel('large-v3', device='cpu', compute_type='int8', cpu_threads=10)
segs,_ = m.transcribe(pcm, language='vi', word_timestamps=True, vad_filter=True,
    vad_parameters=dict(min_silence_duration_ms=500, speech_pad_ms=300),
    condition_on_previous_text=False, beam_size=5,
    initial_prompt='Huấn luyện viên thể hình giải thích về cột sống, xương chậu, cơ mông, cơ gập hông, bài tập.')
words=[]; lines=[]
for s in segs:
    lines.append('[%.2f-%.2f] %s'%(s.start,s.end,s.text.strip()))
    for w in s.words:
        t=w.word.strip()
        if t: words.append({'w':t,'s':round(w.start,3),'e':round(w.end,3),'p':round(w.probability,2)})
json.dump(words,open(os.path.join(work,'words.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
open(os.path.join(work,'loi_doc.txt'),'w',encoding='utf-8').write('\n'.join(lines))
print('XONG',len(words),'chu')
