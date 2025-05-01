const Reviews = (props) => {
    return(
        <div>
            <table>
                <thead>
                    <tr>
                        <th>Review</th>
                        <th>Sentiment</th>
                    </tr>
                </thead>
                <tbody>
                    {props.reviews.map(review =>
                        <tr key={review.id}>
                            <td>{review.text}</td>
                            <td></td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    )
}

export default Reviews