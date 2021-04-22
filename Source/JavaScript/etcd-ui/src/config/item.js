import React from 'react'


export class ConfigItem extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            name: this.props.name,
            type: this.props.type,
            value: this.props.value
        }
    }

    render() {
      return (
        <div className="ConfigItem">
            <label>{this.state.name}</label>
            <input type={this.state.type} value={this.state.value} />
        </div>
      );
    }
}
