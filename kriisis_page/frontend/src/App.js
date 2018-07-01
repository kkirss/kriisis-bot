import React, { Component } from 'react';
import { connect } from 'react-redux';
import PropTypes from 'prop-types';
import logo from './logo.svg';
import './App.css';
import { fetchCategories } from './ducks/categories';
import { fetchShops } from './ducks/shops';

class App extends Component {
  componentDidMount() {
    document.title = this.props.title;
    this.props.fetchCategories();
    this.props.fetchShops();
  }

  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
      </div>
    );
  }
}

App.propTypes = {
  title: PropTypes.string.isRequired,
  fetchCategories: PropTypes.func.isRequired,
  fetchShops: PropTypes.func.isRequired,
};

const mapStateToProps = state => ({
  state,
  title: state.title,
});

const mapDispatchToProps = dispatch => ({
  fetchCategories: () => dispatch(fetchCategories),
  fetchShops: () => dispatch(fetchShops),
});

export default connect(mapStateToProps, mapDispatchToProps)(App);
