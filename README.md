# 🏢 Panvel Realty - Real Estate Management System

A premium, modern, and fully featured Real Estate web application built with **Flask** and **MySQL**. It features an elegant client-facing interface for viewing properties and submitting inquiries, alongside a powerful administrative dashboard for managing properties, inquiries, and admin users.

---

## 🌟 Key Features

### 👤 Client-Facing Application
- **Interactive Property Search:** Filter properties dynamically by type (Flat, Shop, Office, Plot, etc.), purpose (Buy/Rent), budget/price range, and location.
- **Detailed Property Views:** View multiple images, badges (e.g., "For Sale", "For Rent"), specifications (beds, baths, parking, area), and location details.
- **Inquiry Submission System:** Integrated client inquiry form that instantly saves queries to the database and alerts admins.
- **Fully Responsive Design:** Crafted with custom modern CSS, smooth hover states, responsive layouts, and seamless mobile support.

### 🛡️ Admin Dashboard Portal (`/admin`)
- **Tabbed Administration Panel:** Unified UI to manage **Inquiries**, **Properties**, and **Admin Users** seamlessly.
- **Inquiry Status Management:** View client inquiry details and update statuses (e.g., *Pending*, *In Progress*, *Resolved*) dynamically via AJAX API calls.
- **Property CRUD Panel:**
  - Add/Edit properties with fields for name, location, price, type, purpose, dimensions, beds, baths, and parking.
  - Support for main cover image uploads and **multiple additional images** per property.
- **Admin User Management:**
  - Create new admin sub-accounts (exclusively allowed for `main_admin`).
  - Delete admin accounts safely (with checks to prevent self-deletion or removing the final admin).
  - High-security password hashing with `bcrypt`.
  - **Self-Service Password Reset:** Integrated security question and answer mechanism to recover forgotten admin passwords.

---

## 🛠️ Tech Stack & Architecture

- **Backend:** Flask (Python 3)
- **Database:** MySQL / MariaDB (via PyMySQL)
- **Security:** Bcrypt (Password Hashing)
- **Frontend:** HTML5, Modern Vanilla CSS (no framework wrappers), JavaScript (Vanilla ES6)
- **Deployment-Ready:** Configured to parse `DATABASE_URL` (ideal for Render, Heroku, etc.) with SSL support and fallback parameters.

---

## 📂 Project Structure

```text
📂 Real Estate/
├── 📂 static/
│   ├── 📂 CSS/
│   │   └── style.css            # Custom premium styling, animations, and layouts
│   ├── 📂 JS/
│   │   └── main.js             # Client-side dynamic interaction & AJAX requests
│   └── 📂 uploads/            # Location for uploaded property images
├── 📂 templates/
│   ├── index.html              # Main homepage with featured listings
│   ├── properties.html         # Detailed property listing page with search filters
│   ├── contact.html            # Inquiry form & contact page
│   ├── login.html              # Secure Admin login page
│   ├── admin.html              # Main administrative dashboard portal
│   └── forgot_password.html    # Admin security question password reset
├── app.py                      # Main Flask application, routing, and DB logic
├── requirements.txt            # Python dependencies
└── README.md                   # Project documentation
```

---

## 🚀 Setup & Installation

Follow these steps to run Panvel Realty on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/Jay280704/Panvel-Reality.git
cd Panvel-Reality
```

### 2. Set Up a Virtual Environment
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (macOS/Linux)
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Setup
1. Create a MySQL database named `panvel_realty`:
   ```sql
   CREATE DATABASE panvel_realty;
   ```
2. Configure your connection environment variables (or let the app default to `localhost` with user `root` and no password).
3. The database tables (and default properties + admin user) will be **automatically created and seeded** on the first run of the application.

### 5. Run the Application
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000/`.

---

## 🔐 Credentials (Default Seeding)

On the initial setup, a default main administrator is created:
- **Username:** `admin`
- **Password:** `admin123`
- **Security Recovery Answer:** `panvelrealty` *(Used to reset password via security question)*

> [!WARNING]
> Please change the default admin credentials and recovery details immediately after logging into the admin panel for security reasons.

---

## ☁️ Production Deployment

The project is fully optimized for cloud deployment services like **Render** or **Heroku**:
1. It automatically supports the `DATABASE_URL` environment variable for cloud-hosted MySQL instances (e.g., Aiven, Clever Cloud).
2. It includes SSL configuration handling so database connections remain encrypted over cloud networks.
3. Uses `gunicorn` as the WSGI HTTP Server. Run it on production using:
   ```bash
   gunicorn app:app
   ```

---

## 📜 License

This project is licensed under the MIT License. Feel free to use and modify it for personal or commercial projects.
