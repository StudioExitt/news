#!/bin/bash

set -e

# 현재 브랜치 확인
BRANCH=$(git branch --show-current)

# 변경 사항 확인
if [[ -z $(git status --porcelain) ]]; then
    echo "변경 사항이 없습니다."
    exit 0
fi

# 변경 파일 목록 추출 (최대 5개)
CHANGED_FILES=$(git diff --name-only HEAD 2>/dev/null | head -5 | tr '\n' ',' | sed 's/,$//')

# 신규 파일 포함
if [ -z "$CHANGED_FILES" ]; then
    CHANGED_FILES=$(git status --porcelain | awk '{print $2}' | head -5 | tr '\n' ',' | sed 's/,$//')
fi

# 날짜 생성
DATE_STR=$(date '+%Y-%m-%d %H:%M')

# 커밋 메시지 생성
COMMIT_MSG="${DATE_STR} - update: ${CHANGED_FILES}"

echo "Commit Message:"
echo "$COMMIT_MSG"

# Add
git add .

# Commit
git commit -m "$COMMIT_MSG"

# Pull
git pull origin "$BRANCH" --rebase

# Push
git push origin "$BRANCH"

echo "완료: $BRANCH 브랜치에 push 되었습니다."
