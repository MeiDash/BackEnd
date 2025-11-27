import React from 'react'
import { Link } from 'react-router-dom'
import '../styles/Home.css'

const Home: React.FC = () => {
  return (
    <div className="home-container">
      <header className="home-header">
        <h1 className="home-title">Sistema MEI</h1>
        <p className="home-subtitle">Gerencie seu Microempreendedor Individual e CNPJ de forma simples e eficiente</p>
      </header>

      <main className="home-main">
        <div className="home-content">
          <div className="home-description">
            <h2>Simplifique sua gestão empresarial</h2>
            <p>
              Nossa plataforma oferece todas as ferramentas necessárias para que você,
              Microempreendedor Individual (MEI), possa gerenciar seu negócio com facilidade.
              Controle financeiro, emissão de notas fiscais, obrigações fiscais e muito mais.
            </p>
            <ul className="home-features">
              <li>✓ Controle financeiro completo</li>
              <li>✓ Emissão de notas fiscais</li>
              <li>✓ Gestão de obrigações fiscais</li>
              <li>✓ Relatórios detalhados</li>
              <li>✓ Suporte especializado</li>
            </ul>
          </div>

          <div className="home-actions">
            <Link to="/login" className="btn btn-primary">
              Entrar
            </Link>
            <Link to="/cadastro" className="btn btn-secondary">
              Cadastrar-se
            </Link>
          </div>
        </div>
      </main>

      <footer className="home-footer">
        <p>&copy; 2025 Sistema MEI. Todos os direitos reservados.</p>
      </footer>
    </div>
  )
}

export default Home