const express = require('express');
const app = express();

// Middleware to parse incoming request bodies (application/x-www-form-urlencoded)
app.use(express.urlencoded({ extended: true }));
// Middleware to parse incoming request bodies as JSON (application/json)
app.use(express.json());

// Route to handle POST requests
app.post('/post_location', (req, res) => {
    // Log the request body to see what is being sent
    console.log(req.body);

    // Send back a response with the received data
    res.send(`Received: ${JSON.stringify(req.body)}`);
});

// Start the server
const port = 5000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});