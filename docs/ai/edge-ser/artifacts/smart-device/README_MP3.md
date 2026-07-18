# MP3 to emotion (C++)

`ser_mp3.cpp` separates the pipeline into two commands: extract the 45 model-ready
features to JSON, then use that JSON with the exported Random Forest in `classifier.h`.

```powershell
cd AIoT-Server/docs/ai/edge-ser/artifacts/smart-device
g++ -std=c++17 -O2 ser_mp3.cpp -o ser_mp3.exe
.\ser_mp3.exe extract "C:\path\to\speech.mp3" ".\speech.features.json"
.\ser_mp3.exe classify ".\speech.features.json"
```

The program prints JSON such as:

```json
{"schema_version":1,"feature_count":45,"features":[0,0,1211,...]}

{"emotion_label":"Happy","confidence":0.420}
```

`ffmpeg` must be available on `PATH`. The bundled classifier is a prototype;
validate it against representative spoken-audio recordings before product use.
