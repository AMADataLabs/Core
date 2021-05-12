import React from 'react';

import './App.css';

import { ConfigView } from './config/view.js'
import { DataView } from './data/view.js'


class App extends React.Component {
    constructor() {
        super();

        this.state = {
            config: {
                protocol: "http",
                host: "localhost",
                port: "2379",
                username: "",
                password: "",
                prefix: this.props.prefix,
            }
        }
    }
    //
    // componentDidUpdate(old_props) {
    //     var new_state = {}
    //
    //     for (var [key, value] of Object.entries(this.props)) {
    //         if (value !== old_props[key]) {
    //             new_state[key] = value
    //         }
    //     }
    //
    //     if (new_state.size > 0) {
    //         this.setState({key_value_pairs: new_state});
    //     }
    // }

    set_config(config) {
        var changed = false

        for (var [key, value] of Object.entries(config)) {
            if (value !== this.state.config[key]) {
                changed = true;
                break;
            }
        }

        if (changed) {
            this.setState({config: config});
        }
    }

    render() {
      return (
        <div className="App">
            <ConfigView parent={this} />
            <DataView config={this.state} />
        </div>
      );
    }
}

export default App;
