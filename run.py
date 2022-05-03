import uvicorn

from api import app

if __name__ == "__main__":
    uvicorn.run(
        "run:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        ssl_keyfile="openssl/server.key",
        ssl_certfile="openssl/server.crt",
    )
