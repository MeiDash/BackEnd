# FrontEnd

Um projeto React moderno desenvolvido com TypeScript, Vite e ferramentas de qualidade de código.

## 🚀 Tecnologias Utilizadas

- **React 18** - Biblioteca para construção de interfaces
- **TypeScript** - Superset do JavaScript com tipagem estática
- **Vite** - Build tool e servidor de desenvolvimento ultra-rápido
- **ESLint** - Linter para qualidade de código
- **Prettier** - Formatador de código
- **Path Aliases** - Importações limpas com aliases configurados

## 📁 Estrutura do Projeto

```
FrontEnd/
├── src/
│   ├── components/        # Componentes React reutilizáveis
│   ├── pages/            # Páginas/componentes de rotas
│   ├── styles/           # Arquivos CSS e estilos
│   │   ├── index.css     # Estilos globais da aplicação
│   │   └── App.css       # Estilos específicos do componente App
│   ├── types/            # Definições de tipos TypeScript
│   ├── utils/            # Funções utilitárias e helpers
│   ├── hooks/            # Custom hooks do React
│   ├── services/         # Serviços de API e lógica de negócio
│   ├── assets/           # Imagens, ícones, fontes e outros recursos
│   ├── main.tsx          # Ponto de entrada da aplicação
│   └── App.tsx           # Componente raiz da aplicação
├── public/               # Arquivos estáticos servidos diretamente
├── index.html           # Template HTML principal
├── package.json         # Dependências e scripts do projeto
├── tsconfig.json        # Configuração do TypeScript
├── vite.config.ts       # Configuração do Vite
├── .eslintrc.cjs        # Configuração do ESLint
├── .prettierrc          # Configuração do Prettier
└── .gitignore           # Arquivos ignorados pelo Git
```

## 🛠️ Instalação e Configuração

### Pré-requisitos

- **Node.js** (versão 16 ou superior)
- **npm** ou **yarn** (gerenciadores de pacotes)

### Instalação

1. Clone o repositório:
```bash
git clone https://github.com/MeiDash/FrontEnd.git
cd FrontEnd
```

2. Instale as dependências:
```bash
npm install
```

## 🚀 Como Rodar o Projeto

### Desenvolvimento

Para iniciar o servidor de desenvolvimento com hot-reload:

```bash
npm run dev
```

O servidor será iniciado em `http://localhost:5173/`

### Build para Produção

Para gerar os arquivos otimizados para produção:

```bash
npm run build
```

Os arquivos serão gerados na pasta `dist/`

### Preview do Build

Para visualizar o build de produção localmente:

```bash
npm run preview
```

### Linting

Para verificar e corrigir problemas de código:

```bash
npm run lint
```

### Formatação de Código

Para formatar automaticamente todos os arquivos:

```bash
npm run format
```

## 📝 Scripts Disponíveis

| Comando | Descrição |
|---------|-----------|
| `npm run dev` | Inicia o servidor de desenvolvimento |
| `npm run build` | Compila o projeto para produção |
| `npm run preview` | Visualiza o build de produção |
| `npm run lint` | Executa o linter (ESLint) |
| `npm run format` | Formata o código (Prettier) |

## 🔧 Configurações

### Path Aliases

O projeto utiliza aliases para importações mais limpas:

```typescript
// Em vez de:
import Component from '../../../components/Component'

// Use:
import Component from '@/components/Component'
import Component from '@components/Component'
```

**Aliases disponíveis:**
- `@/` - Raiz do diretório `src/`
- `@components/` - `src/components/`
- `@pages/` - `src/pages/`
- `@styles/` - `src/styles/`
- `@types/` - `src/types/`
- `@utils/` - `src/utils/`
- `@hooks/` - `src/hooks/`
- `@services/` - `src/services/`
- `@assets/` - `src/assets/`

### TypeScript

- **Strict mode** habilitado para maior segurança de tipos
- **JSX** configurado como `react-jsx` (React 17+)
- **Path mapping** configurado para os aliases

### ESLint

Configurado com regras para:
- TypeScript
- React Hooks
- Práticas recomendadas do React

### Prettier

Configurado com:
- Ponto e vírgula obrigatório
- Aspas simples
- Largura máxima de linha: 80 caracteres
- Tabulação com 2 espaços

## 🏗️ Desenvolvimento

### Criando Componentes

1. Crie o arquivo na pasta `src/components/`:
```typescript
// src/components/Button.tsx
import React from 'react'

interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: 'primary' | 'secondary'
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary'
}) => {
  return (
    <button
      className={`button button--${variant}`}
      onClick={onClick}
    >
      {children}
    </button>
  )
}
```

2. Exporte no arquivo `index.ts` da pasta components:
```typescript
// src/components/index.ts
export { Button } from './Button'
```

### Criando Páginas

1. Crie o arquivo na pasta `src/pages/`:
```typescript
// src/pages/Home.tsx
import React from 'react'

const Home: React.FC = () => {
  return (
    <div>
      <h1>Bem-vindo à Home</h1>
      <p>Esta é a página inicial da aplicação.</p>
    </div>
  )
}

export default Home
```

### Criando Hooks Customizados

```typescript
// src/hooks/useLocalStorage.ts
import { useState, useEffect } from 'react'

export function useLocalStorage<T>(
  key: string,
  initialValue: T
): [T, (value: T) => void] {
  const [storedValue, setStoredValue] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      return initialValue
    }
  })

  const setValue = (value: T) => {
    try {
      setStoredValue(value)
      window.localStorage.setItem(key, JSON.stringify(value))
    } catch (error) {
      console.error(error)
    }
  }

  return [storedValue, setValue]
}
```

### Criando Serviços

```typescript
// src/services/api.ts
const API_BASE_URL = 'https://api.example.com'

export const api = {
  async get(endpoint: string) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`)
    return response.json()
  },

  async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    })
    return response.json()
  },
}
```

### Adicionando Tipos

```typescript
// src/types/user.ts
export interface User {
  id: number
  name: string
  email: string
  avatar?: string
}

export interface UserProfile extends User {
  bio?: string
  location?: string
  website?: string
}
```

## 🎨 Estilização

### CSS Modules (Recomendado)

```typescript
// src/components/Button.module.css
.button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: background-color 0.2s;
}

.buttonPrimary {
  background-color: #007bff;
  color: white;
}

.buttonPrimary:hover {
  background-color: #0056b3;
}
```

```typescript
// src/components/Button.tsx
import React from 'react'
import styles from './Button.module.css'

interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  primary?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  primary = false
}) => {
  const className = primary
    ? `${styles.button} ${styles.buttonPrimary}`
    : styles.button

  return (
    <button className={className} onClick={onClick}>
      {children}
    </button>
  )
}
```

### CSS Global

Para estilos globais, utilize `src/styles/index.css`.

## 📦 Deploy

### Netlify

1. Faça o build do projeto:
```bash
npm run build
```

2. Faça o deploy da pasta `dist/` no Netlify

### Vercel

1. Instale a CLI do Vercel:
```bash
npm i -g vercel
```

2. Faça o deploy:
```bash
vercel
```

### GitHub Pages

1. Instale o `gh-pages`:
```bash
npm install --save-dev gh-pages
```

2. Adicione ao `package.json`:
```json
{
  "scripts": {
    "deploy": "gh-pages -d dist"
  }
}
```

3. Execute:
```bash
npm run build
npm run deploy
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 📞 Suporte

Para dúvidas ou sugestões, abra uma issue no GitHub ou entre em contato com a equipe de desenvolvimento.

---

**Happy coding! 🚀**