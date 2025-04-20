<!-- README.md for rainbow-six-API -->
# Rainbow Six API

API em **Python** (Flask) que fornece dados dos operadores do jogo **Rainbow Six**:

- **GET /operators** — lista completa de operadores  
- **GET /operators/<id>** — detalhes de um operador (armas, gadgets, habilidade)  

Os dados estão armazenados em um banco **SQLite** (`operators.db`).

---

## Instalação e Execução

1. **Clone este repositório**  
   ```bash
   git clone https://github.com/RpVitrine/rainbow-six-API.git
   
2. **Acesse a pasta do projeto**  
   ```bash
    cd rainbow-six-API

3. **(Opcional) Crie e ative um ambiente virtual**  
   ```bash
    python -m venv env
    source env/bin/activate    # Linux/Mac
    env\Scripts\activate       # Windows

4. **Instale as dependências**  
   ```bash
    pip install flask

5. **Execute a API**
   ```bash
    python main.py
