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
            break;
         case 1:
            extension = '.md';
            break;
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
