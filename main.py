from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import uvicorn

app = FastAPI()

computers_db = {}
global_active = True 

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

@app.get("/admin/stats")
def get_stats():
    return {
        "total_computers": len(computers_db),
        "global_status": "يعمل" if global_active else "متوقف للجميع",
        "computers": computers_db
    }

@app.get("/admin/stop_all")
def stop_all():
    global global_active
    global_active = False
    return {"message": "تم إيقاف البوت عن جميع الحواسيب بنجاح."}

@app.get("/admin/start_all")
def start_all():
    global global_active
    global_active = True
    return {"message": "تم السماح للبوت بالعمل مجدداً."}

@app.get("/admin/stop_pc/{hwid}")
def stop_pc(hwid: str):
    if hwid in computers_db:
        computers_db[hwid]["is_active"] = False
        return {"message": f"تم إيقاف الحاسوب {hwid} بنجاح."}
    return {"error": "هذا الحاسوب غير موجود."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
