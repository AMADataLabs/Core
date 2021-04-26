import React from 'react'

import { GetButton } from './get'
import { NewButton } from './new'
import { KeyValuePairList } from './list'


export class DataView extends React.Component {
    constructor() {
        super();

        this.state = {
            config: this.props.config,
            key_value_pairs: {}
        }

        this.set_key_value_pairs = this.set_key_value_pairs.bind(this)
    }

    set_key_value_pairs(key_value_pairs) {
        console.log("View: set_key_value_pairs() <- ", key_value_pairs)
        this.setState({key_value_pairs: key_value_pairs})
    }

    render() {
        console.log("View: render() <- ", this.state.key_value_pairs)

      return (
        <div className="DataView">
            <GetButton view={this}  />
            <NewButton view={this} />
            <KeyValuePairList key_value_pairs={this.state.key_value_pairs} />
        </div>
      );
    }
}
