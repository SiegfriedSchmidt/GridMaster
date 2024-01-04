from aiohttp import web

from libs.utils import check_errors_and_compile

routes = web.RouteTableDef()


@routes.post('/api/compile')
async def bytecode_compile(request: web.Request):
    content = await request.json()
    code = content.get('code', '')

    if not code:
        return web.json_response({'message': 'notext'}, status=250)

    error, source, bytecode_to_source, bytecode_lines = check_errors_and_compile(code)

    if error:
        return web.json_response({'message': error}, status=250)

    return web.json_response(
        {'source': source, 'bytecodeToSource': bytecode_to_source, 'bytecodeLines': bytecode_lines}
    )


def server():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='localhost', port=8081)
