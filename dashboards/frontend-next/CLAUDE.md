# DARKWIN Dashboard — AI Development Guide

## Project Context
This is the Next.js 16 frontend for DARKWIN-NGASR, an AI-driven security research platform. The dashboard provides real-time 3D attack surface visualization, live scan logging, and report management.

## Key Files
- `src/app/page.tsx` — Main dashboard page
- `src/app/layout.tsx` — Root layout with providers
- `src/components/AttackSurfaceGraph.tsx` — 3D neural map (Three.js/ForceGraph)
- `src/components/NewScanModal.tsx` — Scan creation dialog
- `src/lib/api.ts` — API client for Flask backend

## Conventions
- TypeScript strict mode
- Tailwind CSS 4 for styling
- Server components by default; 'use client' only when needed (interactivity, hooks)
- Socket.IO for real-time updates (not polling)
- API calls go through `src/lib/api.ts`

## Build Commands
```bash
npm run dev    # Development server
npm run build  # Production build
npm run lint   # ESLint check
```
