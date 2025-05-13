# JJY Wave

## 概要

電波時計用の信号を生成するためのスクリプトです。

## 動作環境

基本的には，Python が動作する環境であれば動作します。
下記の環境での動作を確認しています。

- Linux (Ubuntu 24.04)
- Kubernetes

## 設定

同封されている `config.example.yaml` を `config.yaml` に名前変更して，お手元の環境に合わせて書き換えてください。

## 準備

```bash:bash
sudo apt install docker
```

## 実行 (Docker 使用)

```bash:bash
docker compose run --build --rm jjy-wave
```

## 実行 (Docker 未使用)

[Rye](https://rye.astral.sh/) がインストールされた環境であれば，
下記のようにして Docker を使わずに実行できます．

## Kubernetes で動かす場合

Kubernetes で実行するため設定ファイルが `kubernetes/jjy-wave.yaml` に入っていますので，
適宜カスタマイズして使っていただければと思います。

```bash:bash
rye sync
rye run python src/app.py
```

# ライセンス

Apache License Version 2.0 を適用します。
