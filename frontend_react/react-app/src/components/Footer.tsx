function Footer(){
    return(
        <footer className= "footer">

            {/* {new Date().getFullYear()} runs real js inside the jsx to always 
            show the current year, instead of a hardcoded number   */}
            <p>&copy; {new Date().getFullYear()} MyApp. All rights reserved.</p>

        </footer>

    )
}

export default Footer