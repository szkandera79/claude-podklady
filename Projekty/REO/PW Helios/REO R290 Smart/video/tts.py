import sys,json,base64,urllib.request,wave,os
k=sys.argv[1]; S=sys.argv[2]; voice=sys.argv[3] if len(sys.argv)>3 else "Charon"
lines=json.load(open(f"{S}/build/vo.json"))
for i,(a,b,t) in enumerate(lines):
    out=f"{S}/tts/{i:02d}.wav"
    if os.path.exists(out): continue
    body={"contents":[{"parts":[{"text":f"Přečti česky, klidným, sebevědomým hlasem profesionálního komentátora produktového videa, plynule a spíše svižně: {t}"}]}],
          "generationConfig":{"responseModalities":["AUDIO"],"speechConfig":{"voiceConfig":{"prebuiltVoiceConfig":{"voiceName":voice}}}}}
    for m in ["gemini-2.5-pro-preview-tts","gemini-3.8-flash-tts"]:
        try:
            r=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",json.dumps(body).encode(),{"Content-Type":"application/json","x-goog-api-key":k})
            d=json.load(urllib.request.urlopen(r,timeout=300))
            pcm=base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]); break
        except Exception as e: print(m,'ERR',e, getattr(e,'read',lambda:b'')()[:200])
    w=wave.open(out,'wb'); w.setnchannels(1); w.setsampwidth(2); w.setframerate(24000); w.writeframes(pcm); w.close()
    print(i, f"slot {b-a:.1f}s  tts {len(pcm)/48000:.1f}s", t[:40], flush=True)
