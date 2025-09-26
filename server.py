import asyncio
import json
from typing import cast

import websockets

from main import GameProcess

gp = GameProcess()


async def main():
    host: str = '127.0.0.1'
    port: int = 1999

    print(f'[Server] 监听 ws://{host}:{port}')
    async with websockets.serve(process, host, port):
        await asyncio.Future()


async def process(websocket):
    addr = websocket.remote_address
    print(f'[Server] {addr} 已连接')

    try:
        while True:
            message = await websocket.recv()
            print(f'[Server] 收到消息: {message}')

            response = await run_cmd(message)

            await websocket.send(response)
    except websockets.exceptions.ConnectionClosed:
        print(f'[Server] {addr} 断开连接')
    except Exception as e:
        print(f'[Server] 错误: {e}')


async def run_cmd(data_json: str) -> str:
    try:
        data = json.loads(data_json)
        if not isinstance(data, dict):
            raise ValueError('异常数据类型')

        if 'cmd' not in data or 'data' not in data:
            raise ValueError('数据键异常')

        cmd = cast(str, data['cmd'])
        cmd_data = data['data']

        print('[Server] 接受命令', cmd)
        print('[Server] 接受数据', cmd_data)

        if cmd in [
            'get_allowed_skills',
            'get_need_selections',
            'run_container',
            'get_dict',
            'clear',
            'process',
            'ready'
        ]:
            if cmd_data is not None:
                res = getattr(gp, cmd)(**cmd_data)
            else:
                res = getattr(gp, cmd)()
        else:
            raise ValueError('未知命令')

        response = {
            'cmd': cmd,
            'data': res
        }
        return json.dumps(response)

    except Exception as e:
        error_response = {
            'cmd': 'error',
            'data': str(e)
        }
        return json.dumps(error_response)


if __name__ == "__main__":
    asyncio.run(main())
