import asyncio
import json

import aiofiles
import aiofiles.os
from pathlib import Path
from typing import Dict, Any, Union

from loguru import logger


async def delete_file(data_file):
    await asyncio.sleep(5)
    try:
        data = json.loads(data_file)
        file_path = data.get("file_path")

        if not file_path:
            logger.info("Не указан путь к файлу")
            return {"success": False, "error": "Не указан путь к файлу"}

        if not isinstance(file_path, str):
            logger.info("Путь к файлу должен быть строкой")
            return {"success": False, "error": "Путь к файлу должен быть строкой"}

        path = Path(file_path)

        exists = await aiofiles.os.path.exists(str(path))
        if not exists:
            logger.info(f"Файл не существует: {path}")
            return {"success": False, "error": f"Файл не существует: {path}"}

        is_file = await aiofiles.os.path.isfile(str(path))
        if not is_file:
            logger.info(f"Указанный путь ведет к директории: {path}")
            return {"success": False, "error": f"Указанный путь ведет к директории: {path}"}

        await aiofiles.os.remove(str(path))

        logger.info(f"Файл успешно удален: {path}")
        return {"success": True, "message": f"Файл успешно удален: {path}"}

    except PermissionError:
        raise
    except Exception as e:
        raise
