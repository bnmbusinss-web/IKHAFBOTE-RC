const express = require('express');
const cors = require('cors'); // استدعاء مكتبة الـ CORS
const app = express();

app.use(cors()); // السماح لجميع الطلبات الخارجية بالمرور من أي موقع
app.use(express.json());

// مسار فحص الترخيص
app.post('/check-license', (req, res) => {
    const isScriptActive = true;         
    const isSubscriptionExpired = false; 

    if (isSubscriptionExpired) {
        return res.json({ status: "expired" });
    }

    if (isScriptActive) {
        return res.json({ status: "active" });
    } else {
        return res.json({ status: "blocked" });
    }
});

app.get('/', (req, res) => {
    res.send('BLS License Server is running.');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is listening on port ${PORT}`);
});
