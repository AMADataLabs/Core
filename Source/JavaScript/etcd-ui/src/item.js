import React from 'react'


export class Item extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            key: this.props.key,
            name: this.props.name,
            type: this.props.type,
            value: this.props.value
        }
    }

    componentDidUpdate(old_props) {
        if (this.props.value !== old_props.value) {
            this.setState({value: this.props.value});
        }
    }

    render() {
      return (
        <div className="ConfigItem">
            <label>{this.state.name}</label>
            <input type={this.state.type} value={this.state.value} onChange={(event) => {
                this.setState({value: event.target.value})
            }} />
        </div>
      );
    }
}
