from aiohttp import web

from libs.utils import check_errors_and_compile

routes = web.RouteTableDef()


@routes.get('/api/compile')
async def bytecode_compile(request: web.Request):
    content = await request.json()
    code = content.get('code', '')

    if not code:
        return web.json_response({'message': 'notext'}, status=250)

    error, code_lines, bytecode_lines = check_errors_and_compile(code)

    if error:
        return web.json_response({'message': error}, status=250)

    return web.json_response({'bytecode': bytecode_lines})


def start_server():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, port=8080)
