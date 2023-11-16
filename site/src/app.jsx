import React from "react"

const URL = "http://127.0.0.1:8000"

function App() {
	return(
	<form id="uploadForm" action="http://127.0.0.1:8000/assets/upload/?owner=sam&title=test1" method="post" enctype="multipart/form-data">
   	<input type="file" name="file" data-cloudinary-field="image_id"></input>
		<button type="submit">Submit</button>
	</form>)
}

function Profile() {
	return(<div></div>)
}

export { App }
