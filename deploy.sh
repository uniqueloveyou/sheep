#!/usr/bin/env bash
set -Eeuo pipefail

# 拉取最新代码，并使用项目虚拟环境重启 Django 开发服务器。

PROJECT_DIR="${PROJECT_DIR:-/home/youzi/sheep_project}"
BACKEND_DIR="${BACKEND_DIR:-$PROJECT_DIR/Django_backend}"
VENV_PY="${VENV_PY:-$BACKEND_DIR/sheep/bin/python}"
HOST="${HOST:-0.0.0.0}"
PORT="${PORT:-8000}"
PID_FILE="${PID_FILE:-$BACKEND_DIR/runserver.pid}"
LOG_DIR="${LOG_DIR:-$BACKEND_DIR/logs}"
LOG_FILE="${LOG_FILE:-$LOG_DIR/runserver.log}"

echo "==> 项目目录：$PROJECT_DIR"
echo "==> 后端目录：$BACKEND_DIR"
echo "==> Python：  $VENV_PY"

if [[ ! -d "$PROJECT_DIR/.git" ]]; then
  echo "错误：$PROJECT_DIR 不是一个 git 仓库。" >&2
  exit 1
fi

if [[ ! -f "$BACKEND_DIR/manage.py" ]]; then
  echo "错误：在 $BACKEND_DIR 中没有找到 manage.py。" >&2
  exit 1
fi

if [[ ! -x "$VENV_PY" ]]; then
  echo "错误：虚拟环境 Python 不存在或不可执行：$VENV_PY" >&2
  exit 1
fi

echo "==> 正在拉取最新代码..."
cd "$PROJECT_DIR"
git pull

echo "==> 正在准备日志目录..."
mkdir -p "$LOG_DIR"

echo "==> 正在停止旧的 Django runserver 进程..."
if [[ -f "$PID_FILE" ]]; then
  OLD_PID="$(cat "$PID_FILE" || true)"
  if [[ -n "${OLD_PID:-}" ]] && kill -0 "$OLD_PID" 2>/dev/null; then
    echo "    正在停止进程 PID：$OLD_PID"
    kill "$OLD_PID"
    for _ in {1..10}; do
      if ! kill -0 "$OLD_PID" 2>/dev/null; then
        break
      fi
      sleep 1
    done
    if kill -0 "$OLD_PID" 2>/dev/null; then
      echo "    进程 PID $OLD_PID 未正常退出，执行强制停止"
      kill -9 "$OLD_PID"
    fi
  fi
  rm -f "$PID_FILE"
fi

# 兜底：停止不是由本脚本启动、但命令一致的 runserver 进程。
OLD_PIDS="$(pgrep -f "$VENV_PY manage.py runserver $HOST:$PORT" || true)"
if [[ -n "$OLD_PIDS" ]]; then
  echo "    发现同端口旧进程，正在停止：$OLD_PIDS"
  kill $OLD_PIDS || true
  sleep 1
fi

echo "==> 正在启动 Django 服务..."
cd "$BACKEND_DIR"
nohup "$VENV_PY" manage.py runserver "$HOST:$PORT" >> "$LOG_FILE" 2>&1 &
NEW_PID="$!"
echo "$NEW_PID" > "$PID_FILE"

sleep 2
if kill -0 "$NEW_PID" 2>/dev/null; then
  echo "==> 启动成功。"
  echo "    进程 PID：$NEW_PID"
  echo "    访问地址：http://$HOST:$PORT"
  echo "    日志文件：$LOG_FILE"
else
  echo "错误：服务启动失败。最近日志如下：" >&2
  tail -n 80 "$LOG_FILE" >&2 || true
  exit 1
fi
