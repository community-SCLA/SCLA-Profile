#!/bin/bash
cd ~/Documents/SCLA/SCLA-Profile
git pull origin main
git add -A
git diff --cached --quiet || git commit -m "local sync $(date '+%Y-%m-%d %H:%M')"
git push origin main
