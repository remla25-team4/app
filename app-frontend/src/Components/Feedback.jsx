import { useState} from 'react'
const Feedback = (props) => {
    const [feedback, setFeedback] = useState(null)

    const handleFeedbackYes = () =>{
        setFeedback('yes')
    }

    const handleFeedbackNo = () =>{
        setFeedback('no')
        props.onSubmit()
    }

    return(
        <>
        {props.showFeedback ? 
            (
                <div class="app-container">
                <h3>Would you say the sentiment reflects your review?</h3>
                {feedback === null ? 
                    (
                        <div class="feedback-buttons">
                            <button class="yes-button" onClick={()=>handleFeedbackYes()}>Yes 👍</button>
                            <button type="submit" class="no-button" onClick={()=>handleFeedbackNo('no')}>No 👎</button>
                        </div>
                    )
                    :
                    (
                        <>
                            {feedback === 'yes' ? 
                            (<div class="feedback-message"><div class='emoji'>😁</div><p>Great!, thanks for the review</p></div>)
                            :
                            (<div class="feedback-message"><div class='emoji'>😔</div><p>Sorry to hear that! We will take your feedback into consideration.</p></div>)}
                        </>
                    ) }
            </div>
            ) 
            :
            (<></>)
        }
        </>
    )   
}

export default Feedback