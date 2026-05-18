from fastapi import Request


async def get_services(request: Request):
    return request.app.state.services
