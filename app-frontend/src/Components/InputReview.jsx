import React, { useEffect, useState } from 'react';

const InputReview = (props) => {
    const [pageLoadTime, setPageLoadTime] = useState(null);

    useEffect(() => {
        setPageLoadTime(Date.now());
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Measure elapsed time
        if (pageLoadTime) {
            const elapsedTime = (Date.now() - pageLoadTime) / 1000;

            // Send elapsed time to back end once a submit happened
            try {
                await fetch('/api/time-to-click', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ elapsedTime })
                });
            } catch (err) {
                console.error("Error sending time to backend:", err);
            }
        }

        // Call parent submit handler
        props.onSubmit(e);
    };

    return(
        <div class="form-container">
            <form onSubmit={props.onSubmit}>
                    <div class="input-container">
                        <input 
                            class="review-input" 
                            value={props.reviewText} 
                            onChange={props.changeReviewText}
                            placeholder="Leave a review..."/>
                    </div>
                    <div class="button-container">
                        <button type="submit" class="submit-button">Submit</button>
                    </div>
            </form>
        </div>
    )
}

export default InputReview