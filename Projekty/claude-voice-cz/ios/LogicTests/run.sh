#!/bin/bash
# Zkompiluje a spustí testy logiky aplikace na Macu (bez iPhonu).
set -euo pipefail
cd "$(dirname "$0")/.."
OUT="$(mktemp -d)/logictests"
swiftc -O -o "$OUT" \
  ClaudeVoiceCZ/SentenceSplitter.swift \
  ClaudeVoiceCZ/SSEParser.swift \
  ClaudeVoiceCZ/ConversationStore.swift \
  LogicTests/main.swift
"$OUT"
