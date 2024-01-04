from aiohttp import web
from libs.database import Database
from libs.utils import check_errors_and_compile
from pathlib import Path

static_dir_path = Path('./webui/build')
database_path = Path('./gridmaster.db')

db = Database(database_path)
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


@routes.get('/')
async def index(request: web.Request):
    return web.FileResponse(static_dir_path / 'index.html')


def server():
    app = web.Application()
    app.add_routes(routes)
    app.add_routes([web.static('/', static_dir_path)])
    web.run_app(app, host='0.0.0.0', port=8081)
