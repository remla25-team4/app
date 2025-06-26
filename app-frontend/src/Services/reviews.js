import axios from 'axios'
const baseUrl = 'http://localhost:3001/api/reviews'

const getAll = () => {
    const request = axios.get(baseUrl)
    return request.then(response => response.data)
}

const create = (newObject) => {
    const request = axios.post(baseUrl, newObject)
    return request.then(response => response.data)
}

const createElapsedTime = (newObject) => {
    const request = axios.post('/api/time-to-click', newObject)
    return request.then(response => response.data)
}

const getVersions = () => {
    const request = axios.get('/api/versions')
    return request.then(response => response.data)
}

const sendFeedback = (review) => {
    const request = axios.post('/api/feedback', review)
    return request.then(response => response.data)
}

const update = (id, updatedObject) =>{
    const request = axios.put(`${baseUrl}/${id}`, updatedObject)
    return request.then(response => response.data)
}

const remove = (id) =>{
    const request = axios.delete(`${baseUrl}/${id}`)
    return request.then(response => response.data)
}

export default {getAll, getVersions, create, createElapsedTime, sendFeedback, update, remove}