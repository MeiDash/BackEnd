import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Home, Login, Cadastro } from './pages';
function App() {
    return (_jsx(Router, { children: _jsx("div", { className: "App", children: _jsxs(Routes, { children: [_jsx(Route, { path: "/", element: _jsx(Home, {}) }), _jsx(Route, { path: "/login", element: _jsx(Login, {}) }), _jsx(Route, { path: "/cadastro", element: _jsx(Cadastro, {}) })] }) }) }));
}
export default App;
