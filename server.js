const express = require('express');
const app = express();

app.use(express.json());

// ==========================================
// 🔒 نظام التحكم وإيقاف السكربت (Kill Switch)
// ==========================================
app.post('/check-license', (req, res) => {
    // 🔴 للتحكم في السكربت: 
    // اجعل هذه القيمة true ليعمل السكربت.
    // اجعلها false إذا سُرق السكربت وأردت إيقافه عند الجميع فوراً.
    const isScriptActive = true; 
    
    // إضافة حماية إضافية للتحقق من الدومين
    const allowedDomain = "morocco.blsinternational.com";
    const requestDomain = req.body.domain;

    if (isScriptActive && requestDomain === allowedDomain) {
        res.json({ status: "active" });
    } else {
        res.json({ status: "blocked" });
    }
});

// مسار افتراضي للتأكد من أن السيرفر يعمل
app.get('/', (req, res) => {
    res.send('Server is running and secure.');
});

// تشغيل السيرفر على المنفذ الذي تحدده منصة Railway
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
