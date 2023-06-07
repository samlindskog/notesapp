import { createRoot } from 'react-dom/client';
import './app'

const domNode = document.getElementById('root');
const root = createRoot(domNode);

root.render(<App/>)
