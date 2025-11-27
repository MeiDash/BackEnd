import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';
const Login = () => {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const handleSubmit = (e) => {
        e.preventDefault();
        // TODO: Implementar lógica de login
        console.log('Login:', { email, password });
    };
    return (_jsx("div", { className: "auth-container", children: _jsxs("div", { className: "auth-card", children: [_jsx("h2", { className: "auth-title", children: "Entrar no Sistema MEI" }), _jsxs("form", { onSubmit: handleSubmit, className: "auth-form", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "email", children: "E-mail" }), _jsx("input", { type: "email", id: "email", value: email, onChange: (e) => setEmail(e.target.value), required: true, placeholder: "Digite seu e-mail" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "password", children: "Senha" }), _jsx("input", { type: "password", id: "password", value: password, onChange: (e) => setPassword(e.target.value), required: true, placeholder: "Digite sua senha" })] }), _jsx("button", { type: "submit", className: "btn btn-primary btn-full", children: "Entrar" })] }), _jsxs("div", { className: "auth-links", children: [_jsxs("p", { children: ["N\u00E3o tem uma conta?", ' ', _jsx(Link, { to: "/cadastro", className: "auth-link", children: "Cadastre-se" })] }), _jsx("p", { children: _jsx(Link, { to: "/", className: "auth-link", children: "Voltar ao in\u00EDcio" }) })] })] }) }));
};
export default Login;
