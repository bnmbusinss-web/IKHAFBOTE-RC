const express = require('express');
const app = express();

app.use(express.json());

// ==========================================
// 🔒 نظام التحكم وإيقاف السكربت (Kill Switch)
// ==========================================
app.post('/check-license', (req, res) => {
    // 🔴 تحكم فوري من هنا:
    const isScriptActive = true;         // اجعلها false لإيقاف السكربت فوراً
    const isSubscriptionExpired = false; // اجعلها true إذا انتهى اشتراك العميل

    // إذا انتهى الاشتراك
    if (isSubscriptionExpired) {
        return res.json({ status: "expired" });
    }

    // إذا كان السكربت مفَعّلاً
    if (isScriptActive) {
        return res.json({ status: "active" });
    } else {
        return res.json({ status: "blocked" });
    }
});

// مسار افتراضي للتأكد من أن السيرفر يعمل
app.get('/', (req, res) => {
    res.send('BLS License Server is running.');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
