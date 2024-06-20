import React, {useState} from "react"
import { useEffect } from "react"

export function App() {
	return(
		<ThumbnailContainer></ThumbnailContainer>
	)
}


function ThumbnailContainer({children}) {
	assetsList = fetch("http://72.14.178.40/assets/list", 
		{method: "GET", headers: {"Content-Type": "application/json"}}).then(res => {return res.json()})
	.catch(err => {console.log(err); return []})

	console.log(assetsList)

 	const [notes, setNotes] = useState([])

	return(
		<div>
			{children}
		</div>
	)
}

