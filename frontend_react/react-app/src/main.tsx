import { StrictMode } from 'react'
//  strictMode is a helper that doesnt render anything visible by itself

import { createRoot } from 'react-dom/client'
// createRoot is how react 18/19 attaches your app to the actual HTML page

import { BrowserRouter , Routes, Route } from 'react-router-dom'
// BrowserRouter enables client-side routing (changing pages without a
// full browser reload). Routes + Route define which component shows
// for which URL path.

import './index.css'
// Global styles that apply to the whole app(fonts, body margin, etc)

import App from './App.tsx'
// App is now a shared layout (Navbar + Footer) that wraps every page

import Home from './pages/Home.tsx'
import About from './pages/About.tsx'


createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
     <Routes>
      {/* <Route path="..." element={...}> means:
            "when the URL matches this path, render this component" */}

            {/* App wraps its children (nested routes) with the Navbar/Footer layout.
            The <Route index> below fills in App's <Outlet /> with Home
            when the path is exactly "/" */}

            <Route path = "/" element = {<App/>}>
              <Route index element = {<Home/>}/>
              <Route path = "about" element = {<About/>}/>
            </Route>
     </Routes>
    
    
    </BrowserRouter>
   
  </StrictMode>,
)
