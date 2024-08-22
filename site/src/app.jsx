import React, { useState, useEffect } from 'react';
import Moment from 'moment';
import Container from '@mui/material/Container';
import { Grid, Typography } from '@mui/material';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import CardMedia from '@mui/material/CardMedia';
import CardHeader from '@mui/material/CardHeader';
import CardActionArea from '@mui/material/CardActionArea';
import Divider from '@mui/material/Divider';
import { useTheme, ThemeProvider, createTheme } from '@mui/material/styles';

import { config } from './main';

export function Home() {
	return(
		<>
		<Typography variant="h3" sx={{padding: "1rem"}}>Sam's notes</Typography>
		<Divider></Divider>
		<AssetList></AssetList>
		</>
	)
}

export function AssetList() {
   return (
      <Container
         sx={{
            paddingTop: '2rem',
            paddingBottom: '2rem',
         }}
      >
         <Grid container spacing={4}>
            <Thumbnails />
         </Grid>
      </Container>
   );
}

function Thumbnails({ children }) {
   const [assets, setAssets] = useState([]);

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

   function Image({ uuid, typ }) {
      switch (typ) {
         case 0:
            return (
               <CardMedia
                  component="img"
                  image={`${config.endpoint}/assets/${uuid}.jpg`}
               ></CardMedia>
            );
         case 1:
            return null;
      }
   }

   const images = assets.map((asset) => {
      readable_time = Moment.parseZone(asset.dt).format('MMM D, YYYY h:mma');
      switch (asset.typ) {
         case 0:
            asset.ext = '.pdf';
            break;
         case 1:
            asset.ext = '.md';
            break;
         default:
            asset.ext = '';
      }
      return (
         <Grid item xs={3} key={asset.id}>
            <CardActionArea
               disableRipple={true}
               onClick={() =>
                  window.open(
                     `${config.endpoint}/assets/view/${asset.id}${asset.ext}`,
                     '_blank'
                  )
               }
            >
               <Card>
                  <CardHeader
                     title={asset.title}
                     subheader={`Edited: ${readable_time}`}
                  ></CardHeader>
                  <Image typ={asset.typ} uuid={asset.id}></Image>
               </Card>
            </CardActionArea>
         </Grid>
      );
   });

   return images;
}
