import { useState, useEffect } from 'react';

const Feedback = (props) => {
    const [feedback, setFeedback] = useState(null);

    useEffect(() => {
        if (props.showFeedback) {
            setFeedback(null);
        }
    }, [props.showFeedback]);

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
                            <button type="submit" class="no-button" onClick={()=>handleFeedbackNo()}>No 👎</button>
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