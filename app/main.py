import multiprocessing
import os
import sys
import threading
# 获取当前工作目录的路径
current_path = os.getcwd()
print(current_path)
sys.path.append(current_path)
import uvicorn as uvicorn
from PIL import Image
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from uvicorn import Config

from app.utils.system import SystemUtils

# 禁用输出
if SystemUtils.is_frozen():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

from app.core.config import settings
from app.core.module import ModuleManager
from app.core.plugin import PluginManager
from app.db.init import init_db, update_db, init_super_user
from app.helper.thread import ThreadHelper
from app.helper.display import DisplayHelper
from app.helper.resource import ResourceHelper
from app.helper.sites import SitesHelper
from app.helper.message import MessageHelper
from app.scheduler import Scheduler
from app.command import Command, CommandChian
from app.schemas import Notification, NotificationType

# App
App = FastAPI(title=settings.PROJECT_NAME,
              openapi_url=f"{settings.API_V1_STR}/openapi.json")

# 跨域
App.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_HOSTS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# uvicorn服务
Server = uvicorn.Server(Config(App, host=settings.HOST, port=settings.PORT,
                               reload=settings.DEV, workers=multiprocessing.cpu_count()))


def init_routers():
    """
    初始化路由
    """
    from app.api.apiv1 import api_router
    from app.api.servarr import arr_router
    from app.api.servcookie import cookie_router
    # API路由
    App.include_router(api_router, prefix=settings.API_V1_STR)
    # Radarr、Sonarr路由
    App.include_router(arr_router, prefix="/api/v3")
    # CookieCloud路由
    App.include_router(cookie_router, prefix="/cookiecloud")


def start_frontend():
    """
    启动前端服务
    """
    # 仅Windows可执行文件支持内嵌nginx
    if not SystemUtils.is_frozen() \
            or not SystemUtils.is_windows():
        return
    # 临时Nginx目录
    nginx_path = settings.ROOT_PATH / 'nginx'
    if not nginx_path.exists():
        return
    # 配置目录下的Nginx目录
    run_nginx_dir = settings.CONFIG_PATH.with_name('nginx')
    if not run_nginx_dir.exists():
        # 移动到配置目录
        SystemUtils.move(nginx_path, run_nginx_dir)
    # 启动Nginx
    import subprocess
    subprocess.Popen("start nginx.exe",
                     cwd=run_nginx_dir,
                     shell=True)


def stop_frontend():
    """
    停止前端服务
    """
    if not SystemUtils.is_frozen() \
            or not SystemUtils.is_windows():
        return
    import subprocess
    subprocess.Popen(f"taskkill /f /im nginx.exe", shell=True)


def start_tray():
    """
    启动托盘图标
    """

    if not SystemUtils.is_frozen():
        return

    if not SystemUtils.is_windows():
        return

    def open_web():
        """
        调用浏览器打开前端页面
        """
        import webbrowser
        webbrowser.open(f"http://localhost:{settings.NGINX_PORT}")

    def quit_app():
        """
        退出程序
        """
        TrayIcon.stop()
        Server.should_exit = True

    import pystray

    # 托盘图标
    TrayIcon = pystray.Icon(
        settings.PROJECT_NAME,
        icon=Image.open(settings.ROOT_PATH / 'app.ico'),
        menu=pystray.Menu(
            pystray.MenuItem(
                '打开',
                open_web,
            ),
            pystray.MenuItem(
                '退出',
                quit_app,
            )
        )
    )
    # 启动托盘图标
    threading.Thread(target=TrayIcon.run, daemon=True).start()


def check_auth():
    """
    检查认证状态
    """
    if SitesHelper().auth_level < 2:
        err_msg = "用户认证失败，站点相关功能将无法使用！"
        MessageHelper().put(f"注意：{err_msg}")
        CommandChian().post_message(
            Notification(
                mtype=NotificationType.Manual,
                title="MoviePilot用户认证",
                text=err_msg
            )
        )


@App.on_event("shutdown")
def shutdown_server():
    """
    服务关闭
    """
    # 停止模块
    ModuleManager().stop()
    # 停止插件
    PluginManager().stop()
    # 停止事件消费
    Command().stop()
    # 停止虚拟显示
    DisplayHelper().stop()
    # 停止定时服务
    Scheduler().stop()
    # 停止线程池
    ThreadHelper().shutdown()
    # 停止前端服务
    stop_frontend()


@App.on_event("startup")
def start_module():
    """
    启动模块
    """
    auth_site = settings.AUTH_SITE
    if 'iyuu' in auth_site:
        os.environ['IYUU_SIGN'] = settings.IYUU_SIGN
    if 'hhclub' in auth_site:
        os.environ['HHCLUB_USERNAME'] = settings.HHCLUB_USERNAME
        os.environ['HHCLUB_PASSKEY'] = settings.HHCLUB_PASSKEY
    if 'audiences' in auth_site:
        os.environ['AUDIENCES_UID'] = settings.AUDIENCES_UID
        os.environ['AUDIENCES_PASSKEY'] = settings.AUDIENCES_PASSKEY
    if 'hddolby' in auth_site:
        os.environ['HDDOLBY_ID'] = settings.HDDOLBY_ID
        os.environ['HDDOLBY_PASSKEY'] = settings.HDDOLBY_PASSKEY
    if 'zmpt' in auth_site:
        os.environ['ZMPT_UID'] = settings.ZMPT_UID
        os.environ['ZMPT_PASSKEY'] = settings.ZMPT_PASSKEY
    if 'freefarm' in auth_site:
        os.environ['FREEFARM_UID'] = settings.FREEFARM_UID
        os.environ['FREEFARM_PASSKEY'] = settings.FREEFARM_PASSKEY
    if 'hdfans' in auth_site:
        os.environ['HDFANS_UID'] = settings.HDFANS_UID
        os.environ['HDFANS_PASSKEY'] = settings.HDFANS_PASSKEY
    if 'wintersakura' in auth_site:
        os.environ['WINTERSAKURA_UID'] = settings.WINTERSAKURA_UID
        os.environ['WINTERSAKURA_PASSKEY'] = settings.WINTERSAKURA_PASSKEY
    if 'leaves' in auth_site:
        os.environ['LEAVES_UID'] = settings.LEAVES_UID
        os.environ['LEAVES_PASSKEY'] = settings.LEAVES_PASSKEY
    if '1ptba' in auth_site:
        settings.AUTH_SITE = 'ptba'
        os.environ['PTBA_UID'] = settings.ONEPTBA_UID
        os.environ['PTBA_PASSKEY'] = settings.ONEPTBA_PASSKEY
    if 'ptba' in auth_site:
        os.environ['PTBA_UID'] = settings.PTBA_UID
        os.environ['PTBA_PASSKEY'] = settings.PTBA_PASSKEY
    if 'icc2022' in auth_site:
        os.environ['ICC2022_UID'] = settings.ICC2022_UID
        os.environ['ICC2022_PASSKEY'] = settings.ICC2022_PASSKEY
    if 'ptlsp' in auth_site:
        os.environ['PTLSP_UID'] = settings.PTLSP_UID
        os.environ['PTLSP_PASSKEY'] = settings.PTLSP_PASSKEY
    if 'xingtan' in auth_site:
        os.environ['XINGTAN_UID'] = settings.XINGTAN_UID
        os.environ['XINGTAN_PASSKEY'] = settings.XINGTAN_PASSKEY
    if 'agsvpt' in auth_site:
        os.environ['AGSVPT_UID'] = settings.AGSVPT_UID
        os.environ['AGSVPT_PASSKEY'] = settings.AGSVPT_PASSKEY
    if 'ptvicomo' in auth_site:
        os.environ['PTVICOMO_UID'] = settings.PTVICOMO_UID
        os.environ['PTVICOMO_PASSKEY'] = settings.PTVICOMO_PASSKEY
    if 'hdkyl' in auth_site:
        os.environ['HDKYL_UID'] = settings.HDKYL_UID
        os.environ['HDKYL_PASSKEY'] = settings.HDKYL_PASSKEY
    if 'qingwa' in auth_site:
        os.environ['QINGWA_UID'] = settings.QINGWA_UID
        os.environ['QINGWA_PASSKEY'] = settings.QINGWA_PASSKEY
    # 初始化超级管理员
    init_super_user()
    # 虚拟显示
    DisplayHelper()
    # 站点管理
    SitesHelper()
    # 资源包检测
    ResourceHelper()
    # 加载模块
    ModuleManager()
    # 安装在线插件
    PluginManager().install_online_plugin()
    # 加载插件
    PluginManager().start()
    # 启动定时服务
    Scheduler()
    # 启动事件消费
    Command()
    # 初始化路由
    init_routers()
    # 检查认证状态
    check_auth()


if __name__ == '__main__':
    # 初始化数据库
    init_db()
    # 更新数据库
    update_db()
    # 启动API服务
    Server.run()
