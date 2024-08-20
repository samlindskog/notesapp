import React from 'react';
import { createRoot } from 'react-dom/client';
import { AssetList, PdfViewer } from './app.jsx';
import CssBaseline from '@mui/material/CssBaseline';
import '@fontsource/roboto/300.css';
import '@fontsource/roboto/400.css';
import '@fontsource/roboto/500.css';
import '@fontsource/roboto/700.css';
import { createBrowserRouter, RouterProvider, Outlet } from 'react-router-dom';

export const config = {
   endpoint: 'http://72.14.178.40',
};

const r = createBrowserRouter([
   {
      path: '/',
      element: <AssetList></AssetList>,
	},
]);

const domRoot = document.getElementById('root');
const root = createRoot(domRoot);
root.render(
   <>
      <CssBaseline />
      <RouterProvider router={r}>
         <Outlet></Outlet>
      </RouterProvider>
   </>
);
