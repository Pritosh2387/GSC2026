# SportGuard AI — Telegram Piracy Detection System

SportGuard AI is an AI-powered system that monitors Telegram channels in real time and detects unauthorized sharing of protected media using perceptual fingerprinting and similarity matching.

This project helps content creators, broadcasters, and organizations detect piracy automatically and respond quickly.

---

# Key Features

- Real-time Telegram media monitoring  
- Image fingerprinting using perceptual hashing  
- Duplicate detection using SHA-256 hashing  
- Similarity-based piracy detection  
- Automatic alert logging  
- Reference media fingerprint database  
- Fast and lightweight processing  
- Modular and extensible architecture  

---

# How It Works

The system follows this detection pipeline:
1. **Reference Content Registration**: Content owners register their media, which is then fingerprinted and stored in a database.
2. **Real-time Monitoring**: The Telegram monitor scans subscribed channels for new media.
3. **Similarity Matching**: Detected media is compared against the reference database using perceptual hashing.
4. **Alert Generation**: If a match is found above the threshold, an alert is logged and visible on the dashboard.
5. **ARES Analysis**: The ARES (Automated Revenue Enforcement & Shield) engine analyzes the match for commercial intent and severity.

---

# Getting Started

Follow these instructions to get the project up and running on your local machine.

## Prerequisites

- **Python**: 3.10 or higher
- **Node.js**: 18.x or higher
- **npm**: 9.x or higher
- **MongoDB**: A running MongoDB instance (Atlas or Local)

## Backend Setup

1. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

2. **Set up Environment Variables**:
   Ensure you have a `.env` file in the root directory (one level above `backend`). It should contain:
   ```env
   TELEGRAM_API_ID=your_api_id
   TELEGRAM_API_HASH=your_api_hash
   MONGODB_URI=your_mongodb_uri
   MONGODB_DB_NAME=sportguard
   JWT_SECRET_KEY=your_secret_key
   ```

3. **Install Dependencies**:
   It is recommended to use a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   pip install -r ../requirements.txt
   ```

4. **Run the API Server**:
   ```bash
   python api.py
   ```
   The backend will be available at `http://127.0.0.1:8000`.

5. **Run Simulations (Optional)**:
   To run a pipeline simulation without real Telegram data:
   ```bash
   python main.py
   ```

## Frontend Setup

1. **Navigate to the frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install Dependencies**:
   ```bash
   npm install
   ```

3. **Run the Development Server**:
   ```bash
   npm run dev
   ```
   The dashboard will be available at `http://localhost:3000`.

---

# Project Structure

- `backend/`: FastAPI server, database logic, and Telegram monitor.
- `frontend/`: Next.js dashboard for monitoring alerts and matches.
- `ml/`: Machine learning models for deepfake detection and analysis.
- `sportguard/`: Core logic for fingerprinting and similarity matching.
