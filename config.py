import os
from dotenv import load_dotenv


# 加载环境变量
load_dotenv()

# 应用配置
APP_TITLE = os.getenv("APP_TITLE")
APP_ICON = os.getenv("APP_ICON")