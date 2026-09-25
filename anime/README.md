# 147年、ふぐ一筋。— 山西水産 四代の物語

和紙・墨・切り絵のアニメーション動画（縦型 1080×1920・48秒・音声付き）。

- 完成動画：`yamanishi_suisan_4dai_9x16.mp4`
- ブラウザで再生：`index.html`（「音つきで再生」ボタン）

## 中身

| ファイル | 内容 |
|---|---|
| `index.html` | アニメ本体。全フレームを時間から描画する（Canvas） |
| `track.mp3` | BGM・効果音（琴・太鼓・笛・波などをコードで合成） |
| `img/` | 使用した写真とロゴ（`photos/` と商品LPから縮小コピー） |
| `tools/render.mjs` | フレームと効果音のタイミング（cues.json）を書き出す |
| `tools/synth.py` | cues.json から BGM と効果音を合成する |

## 作り直すとき

```bash
cd anime
node tools/render.mjs /tmp/frames 24            # フレーム + cues.json を書き出す
python3 tools/synth.py /tmp/frames/cues.json /tmp/track.wav
ffmpeg -framerate 24 -i /tmp/frames/f%05d.jpg -i /tmp/track.wav \
  -c:v libx264 -crf 23 -pix_fmt yuv420p -c:a aac -shortest yamanishi_suisan_4dai_9x16.mp4
```

## 内容の出典

会社サイト（このリポジトリの `index.html`）と商品LP（yamanishi-suisan-lp）に掲載の事実と、4代目 山西伸典の言葉のみを使用。
