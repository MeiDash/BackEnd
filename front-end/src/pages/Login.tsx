import React, { useState } from 'react'
import { Link } from 'react-router-dom'
import '../styles/Auth.css'

const Login: React.FC = () => {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    // TODO: Implementar lógica de login
    console.log('Login:', { email, password })
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h2 className="auth-title">Entrar no Sistema MEI</h2>

        <form onSubmit={handleSubmit} className="auth-form">
          <div className="form-group">
            <label htmlFor="email">E-mail</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Digite seu e-mail"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Senha</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Digite sua senha"
            />
          </div>

          <button type="submit" className="btn btn-primary btn-full">
            Entrar
          </button>
        </form>

        <div className="auth-links">
          <p>
            Não tem uma conta?{' '}
            <Link to="/cadastro" className="auth-link">
              Cadastre-se
            </Link>
          </p>
          <p>
            <Link to="/" className="auth-link">
              Voltar ao início
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login