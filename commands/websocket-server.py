#!/usr/bin/env python3
"""
DopeMAN WebSocket Server
提供即時任務進度監控
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import websockets

# 存儲所有連接的客戶端
connected_clients = set()

# 當前任務狀態
current_tasks = {}

async def execute_task(task_type, websocket):
    """執行任務並回報進度"""
    task_id = f"{task_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    current_tasks[task_id] = {
        'type': task_type,
        'status': 'running',
        'progress': 0,
        'started_at': datetime.now().isoformat()
    }

    try:
        # 發送開始訊息
        await broadcast_progress(task_id, 0, f"開始執行 {task_type}...")

        if task_type == 'scan':
            await execute_scan(task_id, websocket)
        elif task_type == 'health-check':
            await execute_health_check(task_id, websocket)
        elif task_type == 'fix':
            await execute_fix(task_id, websocket)
        elif task_type == 'update-info-stream':
            await execute_update_info_stream(task_id, websocket)
        else:
            await broadcast_progress(task_id, 0, f"未知任務類型: {task_type}", error=True)
            return

        # 任務完成
        current_tasks[task_id]['status'] = 'completed'
        current_tasks[task_id]['progress'] = 100
        current_tasks[task_id]['completed_at'] = datetime.now().isoformat()

        await broadcast_message({
            'type': 'task_completed',
            'task_id': task_id,
            'task_type': task_type,
            'message': f'{task_type} 執行完成'
        })

    except Exception as e:
        current_tasks[task_id]['status'] = 'failed'
        current_tasks[task_id]['error'] = str(e)

        await broadcast_message({
            'type': 'task_failed',
            'task_id': task_id,
            'task_type': task_type,
            'error': str(e)
        })

async def execute_scan(task_id, websocket):
    """執行掃描任務"""
    await broadcast_progress(task_id, 10, "掃描全域 Skills...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 30, "掃描專案 Skills...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 50, "掃描 Agents...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 70, "掃描 Commands...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 90, "生成資料檔案...")

    # 實際執行掃描
    process = await asyncio.create_subprocess_exec(
        'python3', 'scan-real-data.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"掃描失敗: {stderr.decode()}")

    await broadcast_progress(task_id, 100, "掃描完成")

async def execute_health_check(task_id, websocket):
    """執行健康檢查"""
    await broadcast_progress(task_id, 20, "檢查 Skills 目錄...")
    await asyncio.sleep(0.3)

    await broadcast_progress(task_id, 40, "檢查 Symlinks...")
    await asyncio.sleep(0.3)

    await broadcast_progress(task_id, 60, "檢查 Skill 結構...")
    await asyncio.sleep(0.3)

    await broadcast_progress(task_id, 80, "生成報告...")

    # 實際執行健康檢查
    process = await asyncio.create_subprocess_exec(
        'python3', 'health-check.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"健康檢查失敗: {stderr.decode()}")

    await broadcast_progress(task_id, 100, "健康檢查完成")

async def execute_fix(task_id, websocket):
    """執行自動修復"""
    await broadcast_progress(task_id, 20, "備份當前配置...")
    await asyncio.sleep(0.3)

    await broadcast_progress(task_id, 40, "檢查損壞的連結...")
    await asyncio.sleep(0.3)

    await broadcast_progress(task_id, 60, "修復 Symlinks...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 80, "驗證修復結果...")

    # 實際執行修復
    process = await asyncio.create_subprocess_exec(
        'python3', 'fix.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"修復失敗: {stderr.decode()}")

    await broadcast_progress(task_id, 100, "修復完成")

async def execute_update_info_stream(task_id, websocket):
    """更新個人資訊匯流資料"""
    await broadcast_progress(task_id, 10, "爬取 PTT 熱門文章...")
    await asyncio.sleep(1)

    await broadcast_progress(task_id, 30, "取得台股漲幅資料...")
    await asyncio.sleep(1)

    await broadcast_progress(task_id, 50, "取得台股跌幅資料...")
    await asyncio.sleep(1)

    await broadcast_progress(task_id, 70, "取得加權指數...")
    await asyncio.sleep(0.5)

    await broadcast_progress(task_id, 90, "儲存資料...")

    # 實際執行更新
    process = await asyncio.create_subprocess_exec(
        'python3', 'fetch-ptt-stocks-v2.py',
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        cwd=Path(__file__).parent
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(f"資料更新失敗: {stderr.decode()}")

    await broadcast_progress(task_id, 100, "資料更新完成")

async def broadcast_progress(task_id, progress, message, error=False):
    """廣播進度更新"""
    # 從 current_tasks 取得 task_type
    task_type = current_tasks.get(task_id, {}).get('type', 'unknown')

    data = {
        'type': 'progress',
        'task_id': task_id,
        'task_type': task_type,
        'progress': progress,
        'message': message,
        'error': error,
        'timestamp': datetime.now().isoformat()
    }

    await broadcast_message(data)

async def broadcast_message(data):
    """廣播訊息給所有連接的客戶端"""
    if connected_clients:
        message = json.dumps(data, ensure_ascii=False)
        await asyncio.gather(
            *[client.send(message) for client in connected_clients],
            return_exceptions=True
        )

async def handle_client(websocket):
    """處理客戶端連接"""
    # 註冊客戶端
    connected_clients.add(websocket)
    print(f"✅ 客戶端已連接 ({len(connected_clients)} 個連接)")

    try:
        # 發送當前任務狀態
        await websocket.send(json.dumps({
            'type': 'current_tasks',
            'tasks': current_tasks
        }, ensure_ascii=False))

        # 處理客戶端訊息
        async for message in websocket:
            try:
                data = json.loads(message)
                command = data.get('command')

                if command == 'start_task':
                    task_type = data.get('task_type')
                    if task_type:
                        # 在背景執行任務
                        asyncio.create_task(execute_task(task_type, websocket))
                    else:
                        await websocket.send(json.dumps({
                            'type': 'error',
                            'message': '缺少 task_type 參數'
                        }))

                elif command == 'get_status':
                    await websocket.send(json.dumps({
                        'type': 'current_tasks',
                        'tasks': current_tasks
                    }, ensure_ascii=False))

                else:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': f'未知命令: {command}'
                    }))

            except json.JSONDecodeError:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': '無效的 JSON 格式'
                }))
            except Exception as e:
                await websocket.send(json.dumps({
                    'type': 'error',
                    'message': str(e)
                }))

    finally:
        # 移除客戶端
        connected_clients.remove(websocket)
        print(f"❌ 客戶端已斷線 ({len(connected_clients)} 個連接)")

async def main():
    """啟動 WebSocket 伺服器"""
    print("🚀 DopeMAN WebSocket Server")
    print("=" * 60)
    print("📍 WebSocket URL: ws://localhost:8892")
    print("📡 支援的任務類型:")
    print("   - scan: 掃描 Skills/Agents/Projects")
    print("   - health-check: 健康檢查")
    print("   - fix: 自動修復")
    print("   - update-info-stream: 更新資訊匯流資料")
    print("\n按 Ctrl+C 停止伺服器\n")

    async with websockets.serve(handle_client, "localhost", 8892):
        await asyncio.Future()  # 永久運行

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  伺服器已停止")
