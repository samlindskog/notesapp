import React, { useState, useEffect, useRef, useContext } from 'react';
import { useNavigate, useLoaderData } from 'react-router-dom';
import Moment from 'moment';
import Container from '@mui/material/Container';
import { Grid, Typography } from '@mui/material';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CardHeader from '@mui/material/CardHeader';
import CardActionArea from '@mui/material/CardActionArea';
import { useTheme, ThemeProvider, createTheme } from '@mui/material/styles';

import { config } from './main';

export function AssetList() {
   return (
      <Container>
         <Grid container spacing={4}>
            <Thumbnails />
         </Grid>
      </Container>
   );
}

function Thumbnails({ children }) {
   const [assets, setAssets] = useState([]);
   const navigate = useNavigate();

   useEffect(() => {
      fetch(`${config.endpoint}/assets/list`, {
         method: 'GET',
         headers: { 'Content-Type': 'application/json' },
      })
         .then((res) => {
            return res.json();
         })
         .then((data) => {
            setAssets(data);
         })
         .catch((err) => {
            console.log(err);
         });
   }, []);

   const images = assets.map((asset) => {
      readable_time = Moment.parseZone(asset.dt).format('MMM D, YYYY h:mma');
      switch (asset.typ) {
         case 0:
            extension = '.pdf';
         case 1:
            extension = '.md';
         default:
            extension = '';
      }
      return (
         <Grid item xs={3} key={asset.id}>
            <CardActionArea
               disableRipple={true}
               onClick={() =>
                  window.open(
                     `${config.endpoint}/assets/view/${asset.id}${extension}`,
                     '_blank'
                  )
               }
            >
               <Card>
                  <CardHeader
                     title={asset.title}
                     subheader={`Edited: ${readable_time}`}
                  ></CardHeader>
                  <CardMedia
                     component="img"
                     image={`${config.endpoint}/assets/${asset.id}.jpg`}
                  ></CardMedia>
               </Card>
            </CardActionArea>
         </Grid>
      );
   });

   return images;
}

export function PdfViewer() {
   const [dataUri, setDataUri] = useState();
   const [dimensions, setDimensions] = useState({
      width: document.body.clientWidth,
      height: document.body.clientHeight,
   });
   const windowRef = useRef(window);
   const params = useLoaderData();

   useEffect(() => {
      // dynamic sizing for object element
      document.body.style.height = '100vh';
      document.body.style.width = '100vw';
      document.documentElement.style.overflow = 'hidden';
      // hacky initial run to update clientHeight
      setDimensions({
         width: document.body.clientWidth,
         height: document.body.clientHeight,
      });
      windowRef.current.addEventListener('resize', () => {
         setDimensions({
            width: document.body.clientWidth,
            height: document.body.clientHeight,
         });
         console.log('ran');
         console.log(getWidth());
      });

      fetch(`${config.endpoint}/assets/${params.assetname}`, {
         method: 'GET',
         headers: { 'Content-Type': 'application/json' },
      })
         .then((response) => response.arrayBuffer())
         .then((pdfBytes) => {
            const blob = new Blob([pdfBytes], { type: 'application/pdf' });
            setDataUri(URL.createObjectURL(blob));
         });
   }, []);

   return (
      <object
         id={params.assetname}
         data={dataUri}
         width={dimensions.width}
         height={dimensions.height}
      ></object>
   );
}
