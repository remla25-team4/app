const InputReview = (props) => {
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