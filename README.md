# GreenHash ♻️

> An educational cryptocurrency that rewards recycling — built with a **security-first** approach for the Secure Software Engineering course (Cybersecurity & AI degree).

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-000000?logo=flask&logoColor=white)
![MariaDB](https://img.shields.io/badge/MariaDB-11.3-003545?logo=mariadb&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-pytest-0A9EDC?logo=pytest&logoColor=white)

Users earn **GreenHash coins** for recycling at authorized collection points and redeem them
for sustainable products. Every reward is a verifiable transaction: signed, auditable and
protected against double spending.

## Security-first design

This project was built for a secure software engineering course, so security is not a
feature — it is the architecture:

| Control | Implementation |
|---|---|
| Transaction authenticity | Digital signatures (`cryptography`) — every transaction is signed and verified |
| Double-spend prevention | Transaction validation rules in `core/transactions.py` |
| Value conservation | TRANSFER / SPLIT / MERGE operations cannot create or destroy value |
| Wallet limits | Hard cap of 100 coins per wallet enforced by the protocol |
| Password storage | `bcrypt` hashing — no plaintext credentials |
| Design by contract | `icontract` pre/postconditions on critical operations |
| Access control | Security decorators + session-based auth (`app/security`, `app/auth`) |
| Auditability | Dedicated audit module (`core/audit.py`) for traceable reward history |

## Architecture

```
App/
├── Backend/            # Flask application
│   ├── app/
│   │   ├── core/       # Domain: crypto, transactions, wallet, rewards, audit, contracts
│   │   ├── security/   # Security decorators
│   │   ├── auth/       # Session management
│   │   └── web/        # Routes / views
│   ├── db/             # MariaDB schema
│   └── tests/          # pytest suite (crypto, security, transactions, wallet, rewards, audit)
├── Frontend/           # React (JSX) UI served by Flask
└── Infra/              # Docker Compose (app + MariaDB with healthchecks)
```

## Run it

```bash
cd App/Infra
docker compose up --build
# App available at http://localhost:5000
```

## Run the tests

```bash
cd App/Backend
pip install -r requirements.txt -r requirements-dev.txt
pytest
```

## Documentation

- [Original project proposal](./Documentacion/propuesta-original.md) (Spanish) — problem, threat analysis and state of the art
- [`Documentacion/`](./Documentacion) — course documentation
- [`Modelado/`](./Modelado) — system modeling
- [`Presentacion/`](./Presentacion) — project presentation

## Team

[@yuliu18](https://github.com/yuliu18) · [@sgwb1re19](https://github.com/sgwb1re19) · [@sgwb2fe34](https://github.com/sgwb2fe34) · [@sgwb2kk30](https://github.com/sgwb2kk30) · [@sgwb1yy10](https://github.com/sgwb1yy10) · [@sgwi2](https://github.com/sgwi2) · [@alexjandro9834](https://github.com/alexjandro9834)

## License

See [LICENSE](./LICENSE).
