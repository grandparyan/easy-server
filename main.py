# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

# 实例化 FastAPI 应用
app = FastAPI()

# 设置模板目录：指向名为 "templates" 的文件夹
templates = Jinja2Templates(directory="templates")

# ----------------------------------------------------
# 1. GET 路由：显示计算器首页 (index.html)
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def get_calculator(request: Request):
    """
    处理对根路径的 GET 请求。
    渲染 index.html，初始化时没有结果和错误信息。
    """
    # 渲染 index.html，并传递一个空的 'result' 和 'error' 变量
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "result": None, "error": None}
    )

# ----------------------------------------------------
# 2. POST 路由：处理计算请求 (从表单接收数据)
# ----------------------------------------------------
@app.post("/", response_class=HTMLResponse)
async def calculate(
    request: Request, 
    # 使用 Form(...) 从 HTML 表单中获取数据
    num1: float = Form(...), 
    num2: float = Form(...), 
    operation: str = Form(...)
):
    """
    处理对根路径的 POST 请求。
    根据 operation 执行计算，并将结果传回给 index.html。
    """
    result = None
    error_message = None

    try:
        # 核心计算逻辑
        if operation == 'add':
            result = num1 + num2
        elif operation == 'subtract':
            result = num1 - num2
        elif operation == 'multiply':
            result = num1 * num2
        elif operation == 'divide':
            if num2 == 0:
                error_message = "错误：除数不能为零！"
            else:
                result = num1 / num2
        else:
            error_message = "错误：无效的操作！"

    except Exception as e:
        # 捕获任何意外的计算错误
        error_message = f"计算发生错误：{e}"

    # 重新渲染 index.html
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            # 格式化结果显示
            "result": f"结果: {num1} {operation} {num2} = {result:.2f}" if result is not None else None,
            "error": error_message,
            # 保持用户输入以便重新渲染时显示
            "num1_val": num1,
            "num2_val": num2,
            "op_val": operation
        }
    )

# 运行说明：
# 在命令行中运行：uvicorn main:app --reload
# 然后访问：http://127.0.0.1:8000/
