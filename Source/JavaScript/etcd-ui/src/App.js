import React from 'react';

import './App.css';

import { ConfigView } from './config/view.js'
import { DataView } from './data/view.js'


class App extends React.Component {
    render() {
      return (
        <div className="App">
            <ConfigView />
            <DataView />
        </div>
      );
    }
}

export default App;
