const express = require("express");
const crypto = require("crypto");
const Razorpay = require("razorpay");
const router = express.Router();

const razorpay = new Razorpay({
  key_id: process.env.RAZORPAY_KEY_ID,
  key_secret: process.env.RAZORPAY_KEY_SECRET,
});

// POST /api/payment/order   body: { amount: 1499 }  (rupees)
router.post("/order", async (req, res) => {
  try {
    const { amount } = req.body;
    if (!amount) return res.status(400).json({ message: "amount required" });

    const order = await razorpay.orders.create({
      amount: Math.round(amount * 100), // razorpay uses paise
      currency: "INR",
      receipt: "rcpt_" + Date.now(),
    });
    res.json(order);
  } catch (err) {
    res.status(500).json({ message: "Could not create order" });
  }
});

// POST /api/payment/verify
router.post("/verify", (req, res) => {
  const { razorpay_order_id, razorpay_payment_id, razorpay_signature } = req.body;

  const expected = crypto
    .createHmac("sha256", process.env.RAZORPAY_KEY_SECRET)
    .update(razorpay_order_id + "|" + razorpay_payment_id)
    .digest("hex");

  if (expected === razorpay_signature) {
    return res.json({ success: true });
  }
  res.status(400).json({ success: false, message: "Invalid signature" });
});

module.exports = router;
