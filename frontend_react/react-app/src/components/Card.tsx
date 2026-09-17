type CardProps = {
    title : string
    description : string
}


function Card({title, description} : CardProps){
    return (
        <div className = "card-box">
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    )

}

export default Card 

