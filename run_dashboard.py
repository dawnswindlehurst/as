#!/usr/bin/env python3
"""
Runner do Dashboard.

Uso:
    python run_dashboard.py
    
Acesse: http://localhost:8000
"""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "dashboard.app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
