# 💡 WeSTEM Club App

A web application for **WeSTEM Club** to manage events (lessons, workshops, activities) and student registrations.

## 🚀 Features
- 🔑 User authentication (roles: `student`, `teacher`, `admin`)
- 📅 Create, edit, and delete events
- ✅ Events automatically close after they finish
- 📋 Students can register for events
- 👤 Personal dashboard for students (view schedule and join events)
- 🛠 Admin panel for teachers/organizers (manage events)
- 📊 Data stored in **PostgreSQL (Supabase)**

## ⚙️ Tech Stack
- [Python 3.11+](https://www.python.org/)  
- [Streamlit](https://streamlit.io/) — web interface  
- [PostgreSQL (Supabase)](https://supabase.com/) — database  
- [Pandas](https://pandas.pydata.org/) — data handling  
- [psycopg2](https://www.psycopg.org/) — PostgreSQL connector  

## 📂 Project Structure
```
project/
│── main.py              # Main Streamlit application
│── .streamlit/          # Theme configuration
|──|── config.toml          # Theme configuration
│── requirements.txt     # Dependencies
│── README.md            # Documentation
```

## 🔑 Installation & Run
1. Clone the repository:
   ```bash
   git clone https://github.com/overthinkeeer/WeSTEM-Application.git
   cd westem-app
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run main.py
   ```

## 🗄️ Database Schema
Tables in **PostgreSQL (Supabase)**:

- **users** — user info (name, email, password hash, role)  
- **events** — event details (title, description, date, time, location, created_by, is_active)  
- **registrations** — links users and events (who registered for what)  

### Auto-deactivation of past events
Events automatically become inactive (`is_active = FALSE`) **one hour after the start time**:
```sql
UPDATE events
SET is_active = FALSE
WHERE event_date < CURRENT_DATE
   OR (event_date = CURRENT_DATE AND (event_time + INTERVAL '1 hour') < CURRENT_TIME);
```

## 🔄 Git Workflow
The project is version-controlled with **Git & GitHub**.  
Example workflow:
```bash
git init
git add .
git commit -m "Initial commit: Added main.py, config.toml, requirements.txt"
git push origin main
```

## ✨ Roadmap
- 📤 Sync event data with Google Sheets  
- 🏆 Generate certificates for active participants  
- 💬 Add AI-powered assistant in the personal dashboard  
- 🎨 Improve UI with animations and custom background patterns  

---

👨‍💻 Author: [Arsen Kenjakayev]  
📅 Created: 2025  
