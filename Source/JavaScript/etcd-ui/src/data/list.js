import React from 'react'

import { Item } from '../item'


export class KeyValuePairList extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            key_value_pairs: this.props.key_value_pairs
        }
    }

    componentDidUpdate(old_props) {
        if (this.props.key_value_pairs.size !== old_props.key_value_pairs.size) {
            this.setState({key_value_pairs: this.props.key_value_pairs});
        } else {
            for (var [key, value] of Object.entries(this.props.key_value_pairs)) {
                if (value !== old_props.key_value_pairs[key]) {
                    this.setState({key_value_pairs: this.props.key_value_pairs});

                    return;
                }
            }
        }
    }

    render() {
      return (
        <div className="KeyValuePairList">
            {
                Object.entries(this.state.key_value_pairs).map((key_value_pair, index) => (
                    <Item name={key_value_pair[0]} value={key_value_pair[1]} key={index} />
                ))
            }
        </div>
      );
    }
}
