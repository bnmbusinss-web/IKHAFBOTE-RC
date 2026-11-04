const express = require('express');
const app = express();

app.use(express.json());

// ==========================================
// 🔒 نظام التحكم وإيقاف السكربت (Kill Switch)
// ==========================================
app.post('/check-license', (req, res) => {
    // 🔴 يمكنك التحكم بحالة السكربت عن طريق تغيير هذه المتغيرات:
    
    const isScriptActive = true;     // اجعلها false لإيقاف السكربت برسالة "تم إيقاف السكربت من الإدارة"
    const isSubscriptionExpired = false; // اجعلها true لإيقاف السكربت برسالة "انتهى الاشتراك"
    
    // حماية لتأكيد الدومين
    const allowedDomain = "morocco.blsinternational.com";
    const requestDomain = req.body.domain;

    if (requestDomain !== allowedDomain) {
        return res.json({ status: "blocked" });
    }

    if (isSubscriptionExpired) {
        return res.json({ status: "expired" });
    }

    if (isScriptActive) {
        return res.json({ status: "active" });
    } else {
        return res.json({ status: "blocked" });
    }
});

// مسار افتراضي 
app.get('/', (req, res) => {
    res.send('BLS License Server is running.');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
