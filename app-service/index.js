require('dotenv').config();
const express = require('express')
const axios = require('axios')
const cors = require('cors')
const path = require('path');
const app = express()

const MODEL_SERVICE_URL = process.env.MODEL_SERVICE_URL

let reviews = [
    {
        "id": 1,
        "text": "What a lovely restaurant!",
        "sentiment": "positive"
    }
]

app.use(cors())
app.use(express.json())
app.use(express.static('../app-frontend/build'));


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

app.post('/api/reviews', async (request, response) => {
    try{
        const body = request.body
        
        const modelResponse = await axios.post(`${MODEL_SERVICE_URL}/predict`, {
            text: body.text
        })
        
        const newReview = {
            id: generateId(),
            text: body.text,
            sentiment: modelResponse.data.prediction
        }
        
        reviews = reviews.concat(newReview)
        response.json(newReview)
    }
    catch (error) {
        console.error('Error connecting to model service:', error.message)
    }
})

app.get('*', (req, res) => {
  res.sendFile(path.resolve(__dirname, '../app-frontend/build', 'index.html'));
});

const PORT = 3001
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`)
})