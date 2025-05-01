const InputReview = (props) => {
    return(
       <form onSubmit={props.onSubmit}>
            <div>
                <input value={props.reviewText} onChange={props.changeReviewText}/>
            </div>
            <div>
                <button type="submit">Submit</button>
            </div>
       </form>
    )
}

export default InputReview