import { useState, useEffect } from 'react'
import InputReview from './Components/InputReview'
import Reviews from './Components/Reviews'
import reviewService from './Services/reviews'
import Versions from './Components/Versions'
import Feedback from './Components/Feedback'
import './app.css'

function App() {
  const [reviewText, setReviewText] = useState('')
  const [reviews, setReviews] = useState([])
  const [showFeedback, setShowFeedback] = useState(false)
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
    setShowFeedback(false);

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
          setShowFeedback(true);
        });
      }
    } catch (err){
      console.error("Error sending post request to backend:", err);
    }
  }

  const handleFeedback = () => {
    const review = reviews[reviews.length - 1];
    reviewService
      .sendFeedback(review)
      .then(response => {
        console.log(response)
      });
  }

  return (
    <>
      <div className="app-container">
      <h1>Leave a Review</h1>
      <InputReview
      onSubmit={addReview}
      reviewText={reviewText} 
      changeReviewText={handleReviewText}/>

      <Reviews reviews={reviews}/>
    </div>
      <Feedback onSubmit={handleFeedback} showFeedback={showFeedback}/>
    </>
  )
}

export default App
