const express = require('express')
const app = express()

let reviews = [
    {
        "id": 1,
        "text": "What a lovely restaurant!"
    }
]

app.get('/api/reviews', (request, response) => {
    response.json(reviews)
})

const PORT = 3001
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})