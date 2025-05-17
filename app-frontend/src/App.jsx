import { useState, useEffect } from 'react'
import InputReview from './Components/InputReview'
import Reviews from './Components/Reviews'
import Versions from './Components/Versions'
import reviewService from './Services/reviews'
import './app.css'

function App() {
  const [reviewText, setReviewText] = useState('')
  const [reviews, setReviews] = useState([])
  const [versions, setVersions] = useState({})
  
  useEffect(()=>{
    reviewService
    .getAll()
    .then(allReviews =>{
      setReviews(allReviews)
    })

    reviewService
    .getVersions()
    .then(allVersions => {
      setVersions(allVersions)
    })
  },[])

  const handleReviewText = (event) => {
    setReviewText(event.target.value)
  }

  const addReview = (event) => {
    event.preventDefault()

    if(reviewText != ''){
      const newReview = {
        text: reviewText,
        sentiment: ""
      }

      reviewService
      .create(newReview)
      .then(createdReview => {
        setReviews(reviews.concat(createdReview))
        setReviewText('')
      })
    }
  }

  return (
    <>
    {console.log(versions)}
      <Versions
      modelVersion={versions.modelVersion}
      appVersion={versions.appVersion}
      libVersion={versions.libVersion}/>
      <div class="app-container">
        <h1>Leave a Review!</h1>
        <InputReview
        onSubmit={addReview}
        reviewText={reviewText} 
        changeReviewText={handleReviewText}/>

        <Reviews reviews={reviews}/>
      </div>
    </>
  )
}

export default App
