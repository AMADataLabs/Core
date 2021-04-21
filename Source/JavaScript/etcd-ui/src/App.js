import React from 'react';
import './App.css';


class App extends React.Component {
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
        <div className="App">
            {
                this.state.environment_variables.map(variable => (
                    <h1>{variable[0]}: {variable[1]}</h1>
                ))
            }
        </div>
      );
    }
}

export default App;
