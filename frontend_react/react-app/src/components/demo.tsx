// import { useState } from "react"
type DemoProps = {
    name : string
    role : string
}



function Demo({ name , role} : DemoProps)
{
  return (
    <div className = "card">
        <h2>{name}</h2>
        <p>{role}</p>
    </div>
  )
}

export default Demo