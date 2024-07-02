import React, { useState } from 'react';
import { useEffect } from 'react';

export function App() {
   return <ThumbnailContainer></ThumbnailContainer>;
}

function ThumbnailContainer({ children }) {
   const assetsList = fetch('http://72.14.178.40/assets/list', {
      method: 'GET',
      headers: { 'Content-Type': 'application/json' },
   })
      .then(res => {
         res.json();
      })
      .catch((err) => {
         console.log(err);
         return [];
      });

   console.log(assetsList);

   const [notes, setNotes] = useState([]);

   const jpg_urls = assetsList.map((item) => {
      'http://72.14.178.40/assets/' + item.id + '.jpg';
   });

   const images = jpg_urls.map((url) => {
      <image href={url}></image>;
   });

   return <div>{images}</div>;
}
