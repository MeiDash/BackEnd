import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';
const Cadastro = () => {
    const [formData, setFormData] = useState({
        nome: '',
        email: '',
        senha: '',
        confirmarSenha: '',
        cpf: '',
        telefone: ''
    });
    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };
    const handleSubmit = (e) => {
        e.preventDefault();
        // TODO: Implementar lógica de cadastro
        console.log('Cadastro:', formData);
    };
    return (_jsx("div", { className: "auth-container", children: _jsxs("div", { className: "auth-card", children: [_jsx("h2", { className: "auth-title", children: "Cadastrar no Sistema MEI" }), _jsxs("form", { onSubmit: handleSubmit, className: "auth-form", children: [_jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "nome", children: "Nome Completo" }), _jsx("input", { type: "text", id: "nome", name: "nome", value: formData.nome, onChange: handleChange, required: true, placeholder: "Digite seu nome completo" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "email", children: "E-mail" }), _jsx("input", { type: "email", id: "email", name: "email", value: formData.email, onChange: handleChange, required: true, placeholder: "Digite seu e-mail" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "cpf", children: "CPF" }), _jsx("input", { type: "text", id: "cpf", name: "cpf", value: formData.cpf, onChange: handleChange, required: true, placeholder: "Digite seu CPF" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "telefone", children: "Telefone" }), _jsx("input", { type: "tel", id: "telefone", name: "telefone", value: formData.telefone, onChange: handleChange, required: true, placeholder: "Digite seu telefone" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "senha", children: "Senha" }), _jsx("input", { type: "password", id: "senha", name: "senha", value: formData.senha, onChange: handleChange, required: true, placeholder: "Digite sua senha" })] }), _jsxs("div", { className: "form-group", children: [_jsx("label", { htmlFor: "confirmarSenha", children: "Confirmar Senha" }), _jsx("input", { type: "password", id: "confirmarSenha", name: "confirmarSenha", value: formData.confirmarSenha, onChange: handleChange, required: true, placeholder: "Confirme sua senha" })] }), _jsx("button", { type: "submit", className: "btn btn-primary btn-full", children: "Cadastrar" })] }), _jsxs("div", { className: "auth-links", children: [_jsxs("p", { children: ["J\u00E1 tem uma conta?", ' ', _jsx(Link, { to: "/login", className: "auth-link", children: "Fa\u00E7a login" })] }), _jsx("p", { children: _jsx(Link, { to: "/", className: "auth-link", children: "Voltar ao in\u00EDcio" }) })] })] }) }));
};
export default Cadastro;
