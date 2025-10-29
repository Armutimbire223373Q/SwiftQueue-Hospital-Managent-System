#!/usr/bin/env python3
"""Lightweight mock of Ollama endpoints for local testing.

Provides:
- GET /api/tags
- POST /api/generate

Run with:
    python backend/scripts/mock_ollama.py

This is intended for local development and CI isolation only.
"""
import asyncio
from aiohttp import web
import json

async def tags(request):
    return web.json_response({
        "models": [
            {"name": "phi3:3.8b", "size": 1024 * 1024 * 1024},
            {"name": "mistral:latest", "size": 512 * 1024 * 1024}
        ]
    })

async def generate(request):
    try:
        body = await request.json()
    except Exception:
        body = {}

    model = body.get('model', 'phi3:3.8b')
    prompt = body.get('prompt', '')

    # Minimal heuristic: if prompt contains MEDICAL TRIAGE, return JSON inside string
    if 'MEDICAL TRIAGE ANALYSIS' in str(prompt):
        response_text = json.dumps({
            "emergency_level": "critical",
            "confidence": 0.95,
            "triage_category": "Emergency",
            "estimated_wait_time": 5,
            "department_recommendation": "Emergency",
            "recommended_actions": ["Call 911", "Administer oxygen"],
            "risk_factors": ["chest pain"],
            "ai_reasoning": "Symptoms indicate potential myocardial infarction"
        })
    else:
        # Generic short response
        if 'analyze' in str(prompt).lower():
            response_text = json.dumps({
                "emergency_level": "moderate",
                "confidence": 0.8,
                "triage_category": "Semi-urgent",
                "estimated_wait_time": 30,
                "department_recommendation": "General Medicine",
                "recommended_actions": ["Schedule appointment"],
                "risk_factors": [],
                "ai_reasoning": "Symptoms do not indicate immediate danger"
            })
        else:
            response_text = "OK"

    return web.json_response({"response": response_text})


async def health(request):
    return web.Response(text="ok")


def main():
    app = web.Application()
    app.router.add_get('/api/tags', tags)
    app.router.add_post('/api/generate', generate)
    app.router.add_get('/health', health)

    web.run_app(app, host='0.0.0.0', port=11434)

if __name__ == '__main__':
    main()
