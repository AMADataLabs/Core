import React from 'react';

import './App.css';

import { ConfigView } from './config/view.js'
import { DataView } from './data/view.js'


class App extends React.Component {
    constructor() {
        super();

        this.state = {
            protocol: this.props.protocol,
            host: this.props.host,
            port: this.props.port,
            username: this.props.username,
            password: this.props.password,
        }
    }

    set_config() {
    }

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
