#!/usr/bin/env bash
# 빌드 + 커밋 + 푸시 한 방.  사용법: ./publish.sh "커밋 메시지"
set -e
python3 build.py
git add -A
git commit -m "${1:-update}"
git push
echo "published."
