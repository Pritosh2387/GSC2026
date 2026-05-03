# SportGuard AI

SportGuard AI is a content-protection project with four main surfaces:

- A FastAPI backend for auth, alerts, Telegram monitoring, ARES analysis, content registration, and deepfake inference.
- A Next.js dashboard for operators.
- A deepfake detection pipeline backed by a local Keras model artifact.
- Supporting ML and simulation scripts for model validation and ARES testing.

## Prerequisites

- Python `3.10+`
- Node.js `18+`
- npm `9+`
- MongoDB

## Environment Variables

Create `.env` in the project root:

```env
TELEGRAM_API_ID=your_api_id
TELEGRAM_API_HASH=your_api_hash
MONGODB_URI=your_mongodb_uri
MONGODB_DB_NAME=sportguard
JWT_SECRET_KEY=your_secret_key
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
DEEPFAKE_MODEL_PATH=
DEEPFAKE_MODEL_FILE_ID=1o_jinpmPFLad1iGhAyapBbtpUT39d7Hy
```

Notes:

- `DEEPFAKE_MODEL_PATH` is optional. If set, the backend will try that file first.
- `DEEPFAKE_MODEL_FILE_ID` is optional. It defaults to the current Google Drive file id used by the deepfake model downloader.
- `NEXT_PUBLIC_API_URL` is optional for the frontend. If omitted, the frontend falls back to `http://localhost:8000`.

## Local Setup

### 1. Create the virtualenv

```bash
cd /Users/aadvikchaturvedi/Documents/googleSolution
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install backend dependencies

```bash
pip install -r requirements.txt
pip install gdown==6.0.0
```

Why `gdown` is separate:

- The backend deepfake auto-download helper uses `gdown`.
- The current `requirements.txt` does not pin `gdown`, so install it into `.venv` explicitly.

### 3. Install frontend dependencies

```bash
cd frontend
npm install
cd ..
```

## Scripts And Commands

### Backend commands

| Command | Purpose |
| --- | --- |
| `./.venv/bin/python backend/api.py` | Start the FastAPI backend on `127.0.0.1:8000` |
| `./.venv/bin/python backend/main.py` | Run the ARES simulation pipeline |
| `./.venv/bin/python ml/model.py` | Download and validate the deepfake model locally |
| `./.venv/bin/python -m py_compile backend/api.py` | Quick backend syntax check |

### Frontend scripts

These come from [frontend/package.json](/Users/aadvikchaturvedi/Documents/googleSolution/frontend/package.json:1):

| Script | Expands to | Purpose |
| --- | --- | --- |
| `npm run dev` | `next dev` | Start the frontend development server |
| `npm run build` | `next build` | Production build |
| `npm run start` | `next start` | Run the production build |
| `npm run lint` | `eslint` | Lint the frontend |

## Running The App

### Start the backend

```bash
cd /Users/aadvikchaturvedi/Documents/googleSolution
./.venv/bin/python backend/api.py
```

Backend URL:

- `http://127.0.0.1:8000`

### Start the frontend

```bash
cd /Users/aadvikchaturvedi/Documents/googleSolution/frontend
npm run dev
```

Frontend URL:

- `http://localhost:3000`

## Deepfake Model Notes

- Model artifact location:
  `ml/cnn_lstm_new_model.keras`
- Python runtime location:
  `.venv`
- The deepfake backend route is `/predict-video`.
- If the model file is missing, backend startup will try to download it with `gdown`.
- If the backend is started outside `.venv`, deepfake detection may fail even if the model file exists.

## Dependency Manifests

### Frontend dependencies

Runtime dependencies:

```txt
lucide-react ^1.11.0
next 16.2.4
react 19.2.4
react-dom 19.2.4
```

Development dependencies:

```txt
@tailwindcss/postcss ^4
@types/node ^20
@types/react ^19
@types/react-dom ^19
eslint ^9
eslint-config-next 16.2.4
tailwindcss ^4
typescript ^5
```

### Backend dependencies

Pinned backend dependencies come from `requirements.txt`.

Additional package installed into the project virtualenv for deepfake model auto-download:

```txt
gdown==6.0.0
```

<details>
<summary>Full backend dependency list from <code>requirements.txt</code></summary>

```txt
absl-py==2.3.1
annotated-doc==0.0.4
annotated-types==0.7.0
anyio==4.12.1
asttokens==3.0.1
astunparse==1.6.3
certifi==2025.11.12
charset-normalizer==3.4.4
click==8.3.1
colorama==0.4.6
comm==0.2.3
contourpy==1.3.2
cycler==0.12.1
debugpy==1.8.19
decorator==5.2.1
exceptiongroup==1.3.1
executing==2.2.1
fastapi==0.135.1
filelock==3.20.1
flatbuffers==25.12.19
fonttools==4.61.1
fsspec==2025.12.0
gast==0.7.0
git-filter-repo==2.47.0
google-pasta==0.2.0
grpcio==1.76.0
h11==0.16.0
h5py==3.15.1
httptools==0.7.1
idna==3.11
ipykernel==7.1.0
ipython==8.37.0
jedi==0.19.2
Jinja2==3.1.6
joblib==1.5.3
jupyter_client==8.7.0
jupyter_core==5.9.1
keras==3.12.0
kiwisolver==1.4.9
libclang==18.1.1
Markdown==3.10
markdown-it-py==4.0.0
MarkupSafe==3.0.3
matplotlib==3.10.8
matplotlib-inline==0.2.1
mdurl==0.1.2
ml_dtypes==0.5.4
mpmath==1.3.0
namex==0.1.0
nest-asyncio==1.6.0
networkx==3.4.2
numpy==2.2.6
opencv-python==4.12.0.88
opt_einsum==3.4.0
optree==0.18.0
packaging==25.0
pandas==2.3.3
parso==0.8.5
pillow==12.0.0
platformdirs==4.5.1
prompt_toolkit==3.0.52
protobuf==6.33.2
psutil==7.1.3
pure_eval==0.2.3
pyaes==1.6.1
pyasn1==0.6.3
pydantic==2.12.5
pydantic_core==2.41.5
Pygments==2.19.2
pyparsing==3.2.5
python-dateutil==2.9.0.post0
python-dotenv==1.2.2
pytz==2025.2
PyYAML==6.0.3
pyzmq==27.1.0
requests==2.32.5
rich==14.2.0
rsa==4.9.1
scikit-learn==1.7.2
scipy==1.15.3
six==1.17.0
stack-data==0.6.3
starlette==1.0.0
sympy==1.14.0
Telethon==1.43.2
tensorboard==2.20.0
tensorboard-data-server==0.7.2
tensorflow==2.20.0
termcolor==3.2.0
threadpoolctl==3.6.0
torch==2.9.1
torchaudio==2.9.1
torchvision==0.24.1
tornado==6.5.4
traitlets==5.14.3
typing-inspection==0.4.2
typing_extensions==4.15.0
tzdata==2025.3
urllib3==2.6.2
uvicorn==0.42.0
watchfiles==1.1.1
wcwidth==0.2.14
websockets==16.0
Werkzeug==3.1.4
wrapt==2.0.1
xgboost==3.1.3
```

</details>

## Project Structure

- `backend/`: FastAPI server, auth, alerts, Telegram monitor, ARES, content registration, deepfake route
- `frontend/`: Next.js dashboard
- `ml/`: Deepfake model helper and local model artifact
- `out/`: Static export/build artifacts

## Recommended Verification

After setup:

1. Start the backend with `.venv`.
2. Start the frontend with `npm run dev`.
3. Open `http://localhost:3000/dashboard/deepfake/`.
4. Upload a test video and confirm the page shows computed analysis instead of a missing-model error.
