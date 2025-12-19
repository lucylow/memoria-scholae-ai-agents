# Frontend Integration Guide

## Quick Setup

Backend is now compatible with frontend at: https://github.com/lucylow/dec-17-2025-end

## New Endpoints Added

1. **POST /api/v1/query** - Main research query endpoint
2. **GET /api/v1/memory/{id}** - Get memory by ID
3. **POST /api/v1/graph/query** - Execute Cypher queries
4. **GET /api/v1/agents/status** - Agent pipeline status

## Changes Made

- ✅ CORS configured for Vite (localhost:5173)
- ✅ Response formats match frontend TypeScript interfaces
- ✅ Query endpoint returns proper structure
- ✅ Added frontend-compatible router

## Usage

Start backend:
```bash
python main.py
```

Backend runs on: http://localhost:8000

Frontend expects: https://api.memoriaschola.ai/v1 (configure in frontend .env)

## Environment Variable for Frontend

In frontend `.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```
