import hashlib
import os

import uvicorn
from functools import lru_cache

from fastapi import FastAPI, Depends
from fastapi.responses import FileResponse, StreamingResponse, Response
from pydantic import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Awesome API"
    admin_email: str
    top_folder: str

    class Config:
        # 设置需要识别的 .env 文件
        env_file = ".env"
        # 设置字符编码
        env_file_encoding = 'utf-8'


app = FastAPI()


@lru_cache()
def get_settings():
    return Settings()


@app.get("/info")
async def info(settings: Settings = Depends(get_settings)):
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
    }


# 用于同步文件
file_hash_dict = {}
# 用于下载
hash_file_dict = {}

# 需要创建的文件
empty_folders = []


@app.on_event('startup')
def init_data():
    """初始化文件数据"""
    print('start')
    print(get_settings().top_folder)
    get_path_files(r'D:\BaiduNetdiskDownload\02【高级】打造千万级流量秒杀系统_29讲带笔记')


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/file_data")
async def get_file_data():
    return {'file_hash_dict': file_hash_dict, 'empty_folders': empty_folders}


@app.get("/files/{hash_value}")
async def file_download(hash_value: str, response: Response):
    print(hash_value)
    print(hash_file_dict)
    file_path: str = hash_file_dict.get(hash_value)
    file_name = file_path.rsplit(os.sep, maxsplit=1)[-1]
    if not file_path or not os.path.exists(file_path):
        response.status_code = 400
        return {"message", "file not found"}
    return FileResponse(path=file_path, filename=file_name, media_type='application/zip')


def calculate_sha256(filepath):
    with open(filepath, 'rb') as f:
        sha1_obj = hashlib.sha1()
        sha1_obj.update(f.read())
        hash_value = sha1_obj.hexdigest()
        return hash_value


@lru_cache()
def get_path_files(top_folder):
    """
    获得文件夹下所有文件的路径与空文件列表
    :param top_folder:
    :return:
    """

    folder_data = os.walk(top_folder)
    folder_len = len(top_folder)
    for dir_name, dir_folders, dir_files in folder_data:
        if dir_name == top_folder:
            relative_dir_name = ''
        else:
            relative_dir_name = dir_name[folder_len:]
        if not any([dir_folders, dir_files]):
            empty_folders.append(relative_dir_name)
        if dir_files:
            for file_name in dir_files:
                key_name = f'{relative_dir_name}{os.sep}{file_name}'
                file_full_name = f'{dir_name}{os.sep}{file_name}'
                file_hash = calculate_sha256(file_full_name)
                file_hash_dict.update({key_name: file_hash})
                hash_file_dict.update({file_hash: file_full_name})


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=5555)
