const express = require("express");
const cors = require("cors");
const mongoose = require("mongoose");
require("dotenv").config({ path: "../.env" });

const app = express();

app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

mongoose.connect(process.env.MONGODB_URI)
    .then(() => {
        console.log("MongoDB connected successfully");
    })
    .catch((error) => {
        console.error("MongoDB connection failed:", error.message);
    });

app.get("/", (req, res) => {
    res.json({
        message: "AdvSystem backend is running!"
    });
});

app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});