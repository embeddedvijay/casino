# Gold365 Style Demo Game

Demo/testing project only. Frontend ko future result ya hidden server logic nahi bheja jaata.

## Run

First time:

```bash
npm install
npm run dev
```

Open:

- Frontend: http://localhost:5173
- Backend: http://localhost:8000

## Notes

- Node 18 compatible Vite version is pinned.
- Backend and frontend both start from root using `npm run dev`.
- Game result/crash point is generated on backend only.


casino/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── websocket.py
│   │   └── security.py
│   │
│   ├── common/
│   │   ├── wallet.py
│   │   ├── bets.py
│   │   ├── rounds.py
│   │   ├── history.py
│   │   └── users.py
│   │
│   ├── games/
│   │   ├── aviator/
│   │   │   ├── router.py
│   │   │   ├── engine.py
│   │   │   ├── schemas.py
│   │   │   └── manager.py
│   │   │
│   │   ├── dragon_tiger/
│   │   │   ├── router.py
│   │   │   ├── engine.py
│   │   │   ├── schemas.py
│   │   │   └── manager.py
│   │   │
│   │   ├── game_three/
│   │   │   ├── router.py
│   │   │   ├── engine.py
│   │   │   ├── schemas.py
│   │   │   └── manager.py
│   │   │
│   │   └── game_four/
│   │       ├── router.py
│   │       ├── engine.py
│   │       ├── schemas.py
│   │       └── manager.py
│   │
│   └── admin/
│       ├── router.py
│       ├── game_control.py
│       ├── reports.py
│       └── settings.py
│
└── frontend/
    ├── package.json
    └── src/
        ├── main.jsx
        ├── App.jsx
        │
        ├── api/
        │   ├── client.js
        │   ├── socket.js
        │   └── gameApi.js
        │
        ├── layouts/
        │   ├── CasinoLayout.jsx
        │   └── AdminLayout.jsx
        │
        ├── pages/
        │   ├── GameLobby.jsx
        │   ├── AdminDashboard.jsx
        │   └── WalletPage.jsx
        │
        ├── games/
        │   ├── aviator/
        │   │   ├── Aviator.jsx
        │   │   ├── aviator.css
        │   │   └── components/
        │   │
        │   ├── dragon-tiger/
        │   │   ├── DragonTiger.jsx
        │   │   ├── dragonTiger.css
        │   │   └── components/
        │   │
        │   ├── game-three/
        │   │   ├── GameThree.jsx
        │   │   └── gameThree.css
        │   │
        │   └── game-four/
        │       ├── GameFour.jsx
        │       └── gameFour.css
        │
        └── shared/
            ├── Header.jsx
            ├── BetPanel.jsx
            ├── Chips.jsx
            ├── HistoryBar.jsx
            └── Loader.jsx

uvicorn main:app --reload --host 0.0.0.0 --port 8000