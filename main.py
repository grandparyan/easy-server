from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
# 引入 eval 函數，但要小心使用，這裡我們透過 ast 模組來做一定程度的安全限制
import ast
import operator

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# 定義允許的運算操作符及其對應的函數
_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}

def evaluate_expression(node):
    """
    安全地評估運算式。
    它只允許數字、加減乘除運算，禁止其他Python程式碼執行。
    """
    if isinstance(node, ast.Num):  # <number>
        return node.n
    elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
        # 遞迴呼叫來計算左側和右側的值
        left = evaluate_expression(node.left)
        right = evaluate_expression(node.right)
        
        # 查找操作符對應的函數
        op_func = _OPERATORS.get(type(node.op))
        if op_func is None:
            raise TypeError(f"不支援的操作符: {type(node.op).__name__}")
            
        # 執行運算
        if type(node.op) is ast.Div and right == 0:
             raise ZeroDivisionError("除數不能為零")
             
        return op_func(left, right)
    elif isinstance(node, ast.Expression):
        return evaluate_expression(node.body)
    else:
        raise TypeError(f"運算式中發現不支援的結構: {type(node).__name__}")


# ----------------------------------------------------
# 1. GET 路由：顯示計算器首頁
# ----------------------------------------------------
@app.get("/", response_class=HTMLResponse)
async def get_calculator(request: Request):
    return templates.TemplateResponse(
        "index.html", 
        {"request": request, "expression": "", "result": None, "error": None}
    )

# ----------------------------------------------------
# 2. POST 路由：處理計算請求 (接收運算式字串)
# ----------------------------------------------------
# main.py 中 @app.post("/") 路由的 try...except 區塊
# main.py (確保縮排和層級是正確的)
# main.py (部分程式碼)
@app.post("/", response_class=HTMLResponse)
async def calculate_keypad(
    request: Request, 
    expression: str = Form(...) 
):
    result = None
    error_message = None
    
    safe_expression = expression.replace(' ', '')
    
    if not safe_expression:
        return templates.TemplateResponse("index.html", {"request": request, "expression": "", "result": None, "error": "請輸入運算式"})

    try:
        # 你可以暫時用簡單的 eval() 來替換這裡的 ast.parse 和 evaluate_expression，直到它不報錯為止
        calculated_result = eval(safe_expression)
        result = f"{calculated_result:.4f}".rstrip('0').rstrip('.')

    except ZeroDivisionError:
        error_message = "錯誤：除數不能為零！"
    except Exception as e:
        # 你的錯誤很可能是在這個 except 區塊之後，
        # 比如你在檔案末尾留下了額外的縮排或者不完整的程式碼。
        print(f"DEBUG ERROR: {type(e).__name__}: {e}")
        error_message = "運算式格式不正確，請檢查！(偵錯中)"
        
    # 確保返回語句位於函數的最外層縮排
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "expression": expression,
            "result": result,
            "error": error_message
        }
    )
    # ⚠️ 確保第 86 行（或附近）沒有多餘的程式碼或不正確的縮排！
# 執行說明：
# 在命令列中執行：py -m uvicorn main:app --reload
# 瀏覽器造訪：http://127.0.0.1:8000/
