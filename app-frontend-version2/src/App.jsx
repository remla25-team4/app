import { useState, useEffect } from 'react'
import InputReview from './Components/InputReview'
import Reviews from './Components/Reviews'
import reviewService from './Services/reviews'
import './app.css'

function App() {
  const [reviewText, setReviewText] = useState('')
  const [reviews, setReviews] = useState([])
  const [pageLoadTime, setPageLoadTime] = useState(null);
  
  useEffect(()=>{
    reviewService
    .getAll()
    .then(allReviews =>{
      setReviews(allReviews)
    })

    setPageLoadTime(Date.now());
  },[])

  const handleReviewText = (event) => {
    setReviewText(event.target.value)
    console.log(reviewText)
  }

  const addReview = (event) => {
    event.preventDefault();

    try{
      if (pageLoadTime) {
        const elapsedTime = {
          time: (Date.now() - pageLoadTime) / 1000,
          version: "canary"
        };
        
        reviewService
        .createElapsedTime(elapsedTime)
        .then(elapsedTimeResponse => {
          console.log(elapsedTimeResponse)
        })

        setPageLoadTime(null)
      }
      
      
      if (reviewText !== '') {
        const newReview = {
          text: reviewText,
          sentiment: ""
        };
        
        reviewService
        .create(newReview)
        .then(createdReview => {
          setReviews(reviews.concat(createdReview));
          setReviewText('');
        });
      }
    } catch (err){
      console.error("Error sending post request to backend:", err);
    }
  }

  return (
    <div class="app-container">
      <h1>Leave a Review</h1>
      <InputReview
      onSubmit={addReview}
      reviewText={reviewText} 
      changeReviewText={handleReviewText}/>

      <Reviews reviews={reviews}/>
    </div>
  )
}

export default App
