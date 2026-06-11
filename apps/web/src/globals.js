// window.* global köprüsü — ES module hoisting nedeniyle entry.jsx gövdesinde
// atama yapılamaz (import'lar önce çalışır); bu modül diğer her şeyden önce
// import edilir ve legacy dosyaların beklediği React/ReactDOM globallerini kurar.
import React from 'react';
import ReactDOM from 'react-dom/client';

window.React = React;
window.ReactDOM = ReactDOM;
