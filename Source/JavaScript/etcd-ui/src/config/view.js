import React from 'react'

import { Item } from '../item'


export class ConfigView extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            host: process.env.REACT_APP_ETCD_HOST,
            port: "2379",
            username: "root",
            password: "",
            file: ""
        }
    }

    render() {
      return (
        <div className="ConfigView">
            <Item name="Host" value={this.state.host} />
            <Item name="Port" value={this.state.port} />
            <Item name="Username" value={this.state.username} />
            <Item name="Password" type="password" value={this.state.password} />
        </div>
      );
    }
}
