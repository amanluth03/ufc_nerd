import React from 'react';
import ReactDOM from 'react-dom/client';

class App extends React.Component {
  state = { champions: [] };

  componentDidMount() {
    fetch('/api/champions/records')
      .then(res => res.json())
      .then(data => this.setState({ champions: data }));
  }

  render() {
    return (
      <div>
        <h1>Former UFC Champions Records After Losing Belt</h1>
        <ul>
          {this.state.champions.map((c, idx) => (
            <li key={idx}>{c.name}: {c.record_after_belt}</li>
          ))}
        </ul>
      </div>
    );
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
