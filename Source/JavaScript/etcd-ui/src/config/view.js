import React from 'react'

import { ConfigItem } from './item'


export class ConfigView extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            host: process.env.REACT_APP_ETCD_HOST,
            port: "2379",
            username: "root",
            password: ""
        }
    }

    render() {
      return (
        <div className="ConfigView">
            <ConfigItem name="Host" value={this.state.host} />
            <ConfigItem name="Port" value={this.state.port} />
            <ConfigItem name="Username" value={this.state.username} />
            <ConfigItem name="Password" type="password" value={this.state.password} />
        </div>
      );
    }
}
