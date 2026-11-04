from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

computers_db = {}
global_active = True 
ADMIN_PASSWORD = "zakaria2026" 

class BotInfo(BaseModel):
    hwid: str
    os_info: str
    pc_name: str

@app.post("/ping")
def ping(info: BotInfo):
    if not global_active:
        return {"status": "stop", "message": "تم إيقاف البوت من قبل الإدارة للإصلاح أو لانتهاء الصلاحية."}
    
    if info.hwid in computers_db and computers_db[info.hwid].get("is_active") == False:
        return {"status": "stop", "message": "انتهى اشتراكك، يرجى التواصل مع الإدارة."}

    if info.hwid not in computers_db:
        computers_db[info.hwid] = {
            "pc_name": info.pc_name,
            "os": info.os_info,
            "is_active": True,
            "first_seen": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    computers_db[info.hwid]["last_seen"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"status": "success", "total_computers": len(computers_db)}

def check_password(password: str):
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="كلمة السر خاطئة")

@app.get("/admin/stats")
def get_stats(password: str = ""):
    check_password(password)
    return {
        "total_computers": len(computers_db),
        "global_status": global_active,
        "computers": computers_db
    }

@app.get("/admin/stop_all")
def stop_all(password: str = ""):
    check_password(password)
    global global_active
    global_active = False
    return {"message": "تم إيقاف البوت عن الجميع"}

@app.get("/admin/start_all")
def start_all(password: str = ""):
    check_password(password)
    global global_active
    global_active = True
    return {"message": "تم تشغيل البوت للجميع"}

@app.get("/admin/stop_pc/{hwid}")
def stop_pc(hwid: str, password: str = ""):
    check_password(password)
    if hwid in computers_db:
        computers_db[hwid]["is_active"] = False
        return {"message": "تم الإيقاف"}
    return {"error": "غير موجود"}

@app.get("/admin/start_pc/{hwid}")
def start_pc(hwid: str, password: str = ""):
    check_password(password)
    if hwid in computers_db:
        computers_db[hwid]["is_active"] = True
        return {"message": "تم التشغيل"}
    return {"error": "غير موجود"}

# ========================================================
# 🎨 واجهة لوحة التحكم المرئية (HTML / CSS / JS)
# ========================================================
@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_content = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>لوحة تحكم البوت - BLS TURBO</title>
        <style>
            body { font-family: system-ui, -apple-system, sans-serif; background: #09090b; color: #fafafa; margin: 0; padding: 0; }
            .container { max-width: 1000px; margin: 0 auto; padding: 20px; }
            .header { text-align: center; margin-bottom: 30px; border-bottom: 1px solid #27272a; padding-bottom: 20px; }
            .header h1 { color: #22c55e; margin: 0; font-size: 28px; font-weight: 900; }
            
            /* شاشة تسجيل الدخول */
            #login-screen { display: flex; flex-direction: column; align-items: center; justify-content: center; height: 60vh; }
            input[type="password"] { background: #18181b; border: 1px solid #3f3f46; color: #fff; padding: 12px 20px; border-radius: 8px; font-size: 16px; margin-bottom: 15px; width: 250px; text-align: center; }
            .btn { border: none; padding: 10px 20px; border-radius: 8px; font-size: 14px; font-weight: bold; cursor: pointer; transition: 0.2s; }
            .btn-blue { background: #38bdf8; color: #000; }
            .btn-blue:hover { background: #0284c7; }
            
            /* لوحة التحكم */
            #dashboard-screen { display: none; }
            .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
            .stat-card { background: #18181b; border: 1px solid #27272a; border-radius: 12px; padding: 20px; text-align: center; }
            .stat-card h3 { margin: 0; color: #a1a1aa; font-size: 16px; }
            .stat-card .value { font-size: 32px; font-weight: 900; color: #38bdf8; margin: 10px 0; }
            
            .controls { display: flex; gap: 15px; justify-content: center; margin-bottom: 30px; }
            .btn-green { background: #22c55e; color: #000; font-size: 16px; padding: 12px 24px; }
            .btn-red { background: #ef4444; color: #fff; font-size: 16px; padding: 12px 24px; }
            
            table { width: 100%; border-collapse: collapse; background: #18181b; border-radius: 12px; overflow: hidden; }
            th, td { padding: 14px; text-align: right; border-bottom: 1px solid #27272a; font-size: 14px; }
            th { background: #27272a; color: #a1a1aa; }
            tr:hover { background: #27272a; }
            .status-on { color: #22c55e; font-weight: bold; }
            .status-off { color: #ef4444; font-weight: bold; }
            .action-btn { padding: 6px 12px; border-radius: 6px; font-size: 12px; margin-right: 5px; }
            
            .error-msg { color: #ef4444; margin-top: 10px; display: none; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>⚡ لوحة تحكم BLS TURBO</h1>
                <p style="color: #a1a1aa; margin-top: 5px;">الإدارة والتحكم في الأجهزة المتصلة</p>
            </div>

            <!-- شاشة الدخول -->
            <div id="login-screen">
                <h3 style="margin-bottom: 20px;">الرجاء إدخال كلمة المرور للوصول</h3>
                <input type="password" id="pass-input" placeholder="••••••••" onkeypress="if(event.key === 'Enter') login()">
                <button class="btn btn-blue" onclick="login()">تسجيل الدخول</button>
                <div id="login-error" class="error-msg">كلمة السر خاطئة!</div>
            </div>

            <!-- شاشة لوحة التحكم -->
            <div id="dashboard-screen">
                <div class="stats-grid">
                    <div class="stat-card">
                        <h3>عدد الحواسيب المتصلة</h3>
                        <div class="value" id="total-pcs">0</div>
                    </div>
                    <div class="stat-card">
                        <h3>حالة النظام العام</h3>
                        <div class="value" id="global-status">...</div>
                    </div>
                </div>

                <div class="controls">
                    <button class="btn btn-green" onclick="controlGlobal('start')">▶️ تشغيل البوت للجميع</button>
                    <button class="btn btn-red" onclick="controlGlobal('stop')">⏹️ إيقاف البوت عن الجميع</button>
                </div>

                <h3 style="margin-bottom: 15px; color: #eab308;">💻 قائمة الأجهزة المتصلة:</h3>
                <div style="overflow-x: auto;">
                    <table>
                        <thead>
                            <tr>
                                <th>اسم الحاسوب</th>
                                <th>نظام التشغيل</th>
                                <th>رقم الجهاز (HWID)</th>
                                <th>تاريخ التسجيل</th>
                                <th>الحالة</th>
                                <th>الإجراء</th>
                            </tr>
                        </thead>
                        <tbody id="table-body">
                            <!-- سيتم حقن البيانات هنا -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <script>
            let adminPass = "";
            const API_URL = window.location.origin;

            async function login() {
                const pass = document.getElementById("pass-input").value;
                if(!pass) return;
                
                try {
                    const res = await fetch(`${API_URL}/admin/stats?password=${pass}`);
                    if (res.status === 403) {
                        document.getElementById("login-error").style.display = "block";
                    } else if (res.ok) {
                        adminPass = pass;
                        document.getElementById("login-screen").style.display = "none";
                        document.getElementById("dashboard-screen").style.display = "block";
                        loadData();
                        setInterval(loadData, 5000); // تحديث تلقائي كل 5 ثواني
                    }
                } catch (e) {
                    alert("تعذر الاتصال بالسيرفر");
                }
            }

            async function loadData() {
                if(!adminPass) return;
                const res = await fetch(`${API_URL}/admin/stats?password=${adminPass}`);
                const data = await res.json();
                
                document.getElementById("total-pcs").innerText = data.total_computers;
                const statusEl = document.getElementById("global-status");
                if(data.global_status) {
                    statusEl.innerText = "يعمل ✅";
                    statusEl.style.color = "#22c55e";
                } else {
                    statusEl.innerText = "متوقف ❌";
                    statusEl.style.color = "#ef4444";
                }

                const tbody = document.getElementById("table-body");
                tbody.innerHTML = "";

                if(Object.keys(data.computers).length === 0) {
                    tbody.innerHTML = "<tr><td colspan='6' style='text-align:center;'>لا يوجد أي حاسوب متصل حتى الآن.</td></tr>";
                    return;
                }

                for (const hwid in data.computers) {
                    const pc = data.computers[hwid];
                    const isActive = pc.is_active;
                    const statusHtml = isActive ? `<span class="status-on">نشط</span>` : `<span class="status-off">موقوف</span>`;
                    
                    const actionBtn = isActive 
                        ? `<button class="btn action-btn btn-red" onclick="controlPC('${hwid}', 'stop')">إيقاف</button>`
                        : `<button class="btn action-btn btn-green" onclick="controlPC('${hwid}', 'start')">سماح</button>`;

                    tbody.innerHTML += `
                        <tr>
                            <td style="font-weight:bold; color:#38bdf8;">${pc.pc_name}</td>
                            <td>${pc.os}</td>
                            <td style="font-size:11px; font-family:monospace; color:#a1a1aa;">${hwid}</td>
                            <td style="direction:ltr;">${pc.first_seen}</td>
                            <td>${statusHtml}</td>
                            <td>${actionBtn}</td>
                        </tr>
                    `;
                }
            }

            async function controlGlobal(action) {
                const endpoint = action === 'start' ? 'start_all' : 'stop_all';
                await fetch(`${API_URL}/admin/${endpoint}?password=${adminPass}`);
                loadData();
            }

            async function controlPC(hwid, action) {
                const endpoint = action === 'start' ? 'start_pc' : 'stop_pc';
                await fetch(`${API_URL}/admin/${endpoint}/${hwid}?password=${adminPass}`);
                loadData();
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
