# EmotiCare Testing Simulator

`AIoT-Testing-Simulator` is a Vite/React browser simulator for the interaction flow implemented by `AIoT-Hardware/Smart Device`. It does not replace firmware and does not modify hardware source code.

## Run

Start the API first:

```bash
uvicorn app.main:app --reload
```

Then start the simulator:

```bash
cd ../AIoT-Testing-Simulator
npm install
npm run dev
```

The simulator defaults to `http://localhost:8000` and works with Vite's default `http://localhost:5173` origin, included in Server CORS defaults.

## API coverage

| Simulator action | Server endpoint |
| --- | --- |
| Connection / Pair | `POST /api/devices/pair` |
| Heartbeat | `POST /api/devices/heartbeat` |
| Check-in | `POST /api/emotion-sessions/sync`, `GET /api/emotion-sessions` |
| Support | `POST /api/recommendations/request` |
| Discover | `POST /api/media/music/recommend`, `POST /api/media/podcast/recommend` |
| Companion Chat | `POST /api/conversations/respond` |
| Insights | `GET /api/statistics/day` |
| API Lab | authenticated arbitrary `GET` and `POST` request |

Use the seeded pairing code `DEMO-001` or the demo device token in the Server README. The browser saves a token and most recent session ID only in local storage.
