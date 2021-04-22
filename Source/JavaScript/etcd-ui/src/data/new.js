import React from 'react'


export class NewButton extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            file: this.props.file,
            view: this.props.view,
            key: "",
            value: ""
        }

        this.set_key = this.set_key.bind(this)
        this.set_value = this.set_value.bind(this)
    }

    set_key(key) {
        console.log("Key: ", key)
        if (key !== this.state.key) {
            this.setState({key: key})
        }
    }

    set_value(value) {
        console.log("Value: ", value)
        if (value !== this.state.value) {
            this.setState({value: value})
        }
    }

    render() {
      return (
        <div className="ConfigView">
            <label>
                Key
                <input onChange={(event) => {
                    this.set_key(event.target.value)
                }} />
            </label>
            <label>
                Value
                <input onChange={(event) => {
                    this.set_value(event.target.value)
                }} />
            </label>

            <button onClick={() => {
                console.log("State: ", this.state)
                var pairs = this.state.view.state.key_value_pairs;
                pairs[this.state.key] = this.state.value;

                this.state.view.set_key_value_pairs(pairs);
            }} > New </button>
        </div>
      );
    }
}
