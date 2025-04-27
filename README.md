# 🎵 SoundCloud Backend – Django REST Framework

This is the backend API for **MyMusic**, a modern music streaming platform. Built with Django and DRF, it supports full CRUD operations for Songs, Albums, Artists, Playlists, and User Authentication.

---

## 🚀 Features

- 🔑 JWT Authentication & User Management.
- 🎶 Upload, edit, delete songs with metadata (genre, track no, release date).
- 📀 Album & Artist management.
- 🎨 Cloudinary integration for media files (audio, images).
- 🔍 Unified Search across all models (songs, albums, artists, playlists).
- 📝 API endpoints with permission-based access.
- 🛠 Song metadata extraction (BPM, duration, etc.)

---

## 📦 Tech Stack

- **Django** (4.x)
- **Django REST Framework**
- **Cloudinary**
- **SQLite**
- **Librosa** & **pydub** (Audio metadata extraction)

---

## 🔧 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/sound_cloud_backend.git
cd sound_cloud_backend
```

## 2. Create & Activate Virtual Environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

## 3. Install Dependencies
`pip install -r requirements.txt`

## 4. Configure Environment Variables
Create a .env file:

```bash
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://user:pass@localhost:5432/mymusic
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

## 5. Run Migrations & Server

```bash
python manage.py migrate
python manage.py runserver
```

## 🌐 API Endpoints

### Method | Endpoint | Description
#### GET | /api/songs/ | List all songs
#### POST | /api/songs/ | Upload new song
#### PATCH | /api/songs/<id>/ | Update song details
#### DELETE | /api/songs/<id>/ | Delete song
#### GET | /api/albums/ | List all albums
#### GET | /api/artists/ | List all artists
#### GET | /api/playlists/ | List all playlists
#### GET | /api/search/?q=query | Unified search across all models

## 🧑‍💻 Development

###### Clone the frontend
###### Use Django Admin for quick management.
###### Extend API endpoints with DRF's ViewSets or APIView.

## 🤝 Contributing
Pull requests are welcome. Please open issues first for major changes.

## 📜 License
MIT


---
