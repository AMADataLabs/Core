import React from 'react'


export class DataView extends React.Component {
    constructor() {
        super();

        this.state = {
            environment_variables: []
        }
    }

    componentDidMount() {
        console.log(process.env);
        this.setState({environment_variables: Object.entries(process.env)});
    }

    render() {
      return (
        <div className="DataView">
            {/*
                this.state.environment_variables.map(variable => (
                    <h1>{variable[0]}: {variable[1]}</h1>
                ))
            */}
        </div>
      );
    }
}
