import { Link } from 'react-router-dom'

function Navbar(){
    return(
        <nav className = "navbar">
            <span className = "navbar-logo">MyApp</span>
            <ul className = "navbar-links">
                <li><Link to = "/">Home</Link></li>
                <li><Link to = "/about">About</Link></li>
            </ul>
        </nav>
    )

}

export default Navbar


