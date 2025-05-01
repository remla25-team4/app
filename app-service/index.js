const express = require('express')
const cors = require('cors')
const app = express()

let reviews = [
    {
        "id": 1,
        "text": "What a lovely restaurant!",
        "sentiment": ""
    }
]

app.use(cors())
app.use(express.json())

app.get('/api/reviews', (request, response) => {
    response.json(reviews)
})

app.delete('/api/reviews/:id', (request, response) => {
    const id = request.params.id
    reviews = reviews.filter(p => p.id !== id)

    response.status(204).end()
})

const generateId = () => {
    return Math.floor(Math.random() * 5000) + 1
}

app.post('/api/reviews', (request, response) => {
    const body = request.body

    const newReview = {
        id: generateId(),
        text: body.text
    }

    reviews = reviews.concat(newReview)
    response.json(newReview)
})

const PORT = 3001
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})