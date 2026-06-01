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

sudo ufw allow 5173
uvicorn main:app --reload --host 0.0.0.0 --port 8000

Recommended Technology StackGame Engines: Phaser (2D) or Babylon.js (3D) are industry standards for building web games that work everywhere.Frontend Frameworks: React or Vue.js for structuring the website's menus, user accounts, and UI elements.UI Toolkits: Tailwind CSS helps you build a fluid layout that scales perfectly from a smartphone to a laptop screen.

cd /home/vijay/casino/frontend
rm -rf node_modules package-lock.json
npm install
npm install lucide-react
npm run dev

cd /home/vijay/casino/frontend
rm -rf node_modules package-lock.json
npm install vite@5.4.11 @vitejs/plugin-react@4.3.4 --save-dev
npm install
npm install lucide-react phaser
npm run dev