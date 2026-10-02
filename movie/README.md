# 山西水産 ブランドムービー

- `brand-movie.html` … 映像（Canvas 2D）と音（Web Audio）をコードで生成する約20秒のブランドムービー。`?format=vertical` で縦型（9:16）。
- `brand-movie-9x16.mp4` / `brand-movie-16x9.mp4` … 書き出し済みの完成版（音あり）。Instagramリール・YouTubeショートには縦型、YouTube・展示には横型。
- `brand-movie-web.mp4` / `brand-movie-poster.jpg` … LPに埋め込む軽量版（音なし・720×1280）とポスター画像。
- `src/` … 使用写真（すべてLP掲載の実写）。

## 構成（90BPM・7シーン）
1. 下関（金の渦潮）→ 2. 南風泊市場 → 3. 産地直結の鮮度／147年の職人技 → 4. ふぐ→ふく → 5. 四代（1879・1949・1972・2011）、147年 → 6. ふぐ刺し・てっちり・ふぐの唐揚げ → 本場の海から、あなたの食卓へ。→ 7. 変わり続けることが、続いてきた理由。／山西水産

言葉と数字はLPに掲載済みのものだけを使用。「147年」は書き出した2026年時点の表記なので、年が変わったら書き出し直してください。

## 書き出し
```
npm i -D playwright   # 未導入の場合
node movie/render.js              # 横型 16:9
node movie/render.js --vertical   # 縦型 9:16
node movie/render.js --frames 0,120,300   # 確認用の静止画
```
書き出し後、音量をそろえる場合：`ffmpeg -i in.mp4 -c:v copy -af loudnorm=I=-16:TP=-1.5:LRA=11 -c:a aac -b:a 160k out.mp4`
