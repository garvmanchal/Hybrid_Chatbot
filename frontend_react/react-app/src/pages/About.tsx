function About(){
    return(
        <div className = "card">
            <h1>About Page</h1>
            <p>
                This is the second page, reachable at <code>/about</code>, wired up with React Router.
                Notice the page changed without a full browser reload 
                -thats the client side routing in action

            </p>
        </div>
    )
}


export default About