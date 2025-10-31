# main.py
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# 引入 eval 函数，但要小心使用，这里我们通过 ast 模块来做一定程度的安全限制
import ast
import operator

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 定义允许的运算操作符及其对应的函数
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def evaluate_expression(node):
    """
    安全地评估表达式。
    它只允许数字、加减乘除运算，禁止其他Python代码执行。
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        # 递归调用来计算左侧和右侧的值
        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)
        
        # 查找操作符对应的函数
        op_func = _OPERATORS.get(type(node.op))
        if op_func is None:
            raise TypeError(f"不支持的操作符: {type(node.op).__name__}")
            
        # 执行运算
        if type(node.op) is ast.Div and right == 0:
             raise ZeroDivisionError("除数不能为零")
             
        return op_func(left, right)
    elif isinstance(node, ast.Expression):
        return evaluate_expression(node.body)
    else:
        raise TypeError(f"表达式中发现不支持的结构: {type(node).__name__}")


# ----------------------------------------------------
# 1. GET 路由：显示计算器首页
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "expression": "", "result": None, "error": None}
    )

# ----------------------------------------------------
# 2. POST 路由：处理计算请求 (接收表达式字符串)
# ----------------------------------------------------
@app.post("/", response_class=HTMLResponse)
async def calculate_keypad(
    request: Request, 
    # 从 HTML 表单中接收一个名为 'expression' 的字符串
    expression: str = Form(...) 
):
    result = None
    error_message = None
    
    # 清除表达式中的空格
    safe_expression = expression.replace(' ', '')
    
    if not safe_expression:
        return templates.TemplateResponse("index.html", {"request": request, "expression": "", "result": None, "error": "请输入表达式"})

    try:
        # 使用 ast.parse 将表达式字符串解析为抽象语法树 (AST)
        tree = ast.parse(safe_expression, mode='eval')
        
        # 通过我们自定义的安全函数计算结果
        calculated_result = evaluate_expression(tree)
        
        # 格式化结果
        result = f"{calculated_result:.4f}".rstrip('0').rstrip('.')

    except ZeroDivisionError:
        error_message = "错误：除数不能为零！"
    except TypeError as e:
        error_message = f"表达式错误：{e}"
    except Exception:
        # 捕获其他解析错误，如操作符不规范等
        error_message = "表达式格式不正确，请检查！"

    # 重新渲染 index.html，并将原始表达式和结果/错误信息传回
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "expression": expression,
            "result": result,
            "error": error_message
        }
    )

# 运行说明：
# 在命令行中运行：py -m uvicorn main:app --reload
# 浏览器访问：http://127.0.0.1:8000/
