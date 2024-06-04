import React from "react"

function App() {
	return(
		<>
		<Thumbnail></Thumbnail>
		</>
	)
}

function Thumbnail() {
	return(<object data="https://research.google.com/pubs/archive/44678.pdf"
   width="800" height="600"></object>)
}

export { App }
