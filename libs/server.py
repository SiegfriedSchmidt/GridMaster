from aiohttp import web
from libs.database import Database
from libs.utils import check_errors_and_compile

db = Database('gridmaster.db')
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


@routes.get('/api/database/get_all')
async def get_all(request: web.Request):
    res = db.get_all()
    return web.json_response({'all': res})


@routes.post('/api/database/load')
async def load(request: web.Request):
    content = await request.json()
    index = content.get('index', '')
    if not index:
        return web.json_response({'message': 'noindex'}, status=250)

    res = db.load_code(index)
    return web.json_response({'code': res})


@routes.post('/api/database/save')
async def save(request: web.Request):
    content = await request.json()
    code = content.get('code', '')
    if not code:
        return web.json_response({'message': 'notext'}, status=250)

    res = db.save_code(code)
    return web.json_response({'index': res})


def server():
    app = web.Application()
    app.add_routes(routes)
    web.run_app(app, host='localhost', port=8081)
