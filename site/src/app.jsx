import React from "react"

const URL = "http://127.0.0.1:8000"

function App() {
	return(
	<form id="uploadForm">
   	<input type="file" name="file" data-cloudinary-field="image_id"></input>
   	<progress id="progressBar" value="0" max="100"></progress>
	</form>)
}

function Profile() {
	return(<div></div>)
}

export { App }
