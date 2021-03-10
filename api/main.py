import logging
from aiohttp import web
import aiohttp_jinja2
import jinja2

from gui.home_view import home_view, get_sync_data, get_sync_long_data, send_rmq_direct, update_task_status_api


logger = logging.getLogger(__name__)


if __name__ == '__main__':
    app = web.Application()

    app.add_routes([
        web.get('/', home_view, name='home'),
        web.get('/get_sync_data/', get_sync_data, name='get_sync_data'),
        web.get('/get_sync_long_data/', get_sync_long_data, name='get_sync_long_data'),
        web.post('/send_rmq_direct/', send_rmq_direct, name='send_rmq_direct'),
        web.post('/update_task_status_api/', update_task_status_api, name='update_task_status_api'),
    ])

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('./api/templates'))

    web.run_app(app, host='0.0.0.0')

