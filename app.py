from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
import pymysql
import os
from werkzeug.utils import secure_filename
from functools import wraps

app = Flask(__name__)
app.secret_key = "panvel_realty_secret_key"
app.config['SESSION_PERMANENT'] = False

import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

# ===== ADMIN AUTHENTICATION DECORATOR =====
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

# ===== FILE UPLOADS CONFIGURATION =====
UPLOAD_FOLDER = os.path.join('static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ===== PURE PYTHON MYSQL CONNECTION =====
def get_db_connection():
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_user = os.environ.get('DB_USER', 'root')
    db_password = os.environ.get('DB_PASSWORD', '')
    db_name = os.environ.get('DB_NAME', 'panvel_realty')
    db_port = int(os.environ.get('DB_PORT', 3306))
    
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith('mysql://'):
        try:
            from urllib.parse import urlparse
            url = urlparse(db_url)
            db_host = url.hostname or db_host
            db_user = url.username or db_user
            db_password = url.password or db_password
            db_name = url.path.lstrip('/') or db_name
            db_port = url.port or db_port
        except Exception as e:
            print("Error parsing DATABASE_URL:", e)

    return pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name,
        port=db_port,
        charset='utf8mb4'
    )

def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. Enquiries Table Schema Setup
        cur.execute("""
            CREATE TABLE IF NOT EXISTS enquiries (
                id INT AUTO_INCREMENT PRIMARY KEY,
                client_name VARCHAR(100) NOT NULL,
                client_phone VARCHAR(20) NOT NULL,
                client_email VARCHAR(100),
                looking_for VARCHAR(50),
                property_type VARCHAR(50),
                budget_range VARCHAR(50),
                message TEXT,
                status VARCHAR(20) DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        
        # Verify status column
        try:
            cur.execute("SHOW COLUMNS FROM enquiries LIKE 'status'")
            result = cur.fetchone()
            if not result:
                cur.execute("ALTER TABLE enquiries ADD COLUMN status VARCHAR(20) DEFAULT 'Pending'")
                conn.commit()
                print("Status column added successfully.")
        except Exception as col_err:
            print("Status column verification error:", col_err)
            
        # 2. Properties Table Schema Setup
        cur.execute("""
            CREATE TABLE IF NOT EXISTS properties (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL,
                loc VARCHAR(150) NOT NULL,
                price VARCHAR(50) NOT NULL,
                priceV FLOAT NOT NULL,
                type VARCHAR(50) NOT NULL,
                purpose VARCHAR(50) NOT NULL,
                area VARCHAR(50) NOT NULL,
                beds VARCHAR(50) NOT NULL,
                bath VARCHAR(50) NOT NULL,
                parking VARCHAR(50) NOT NULL,
                img VARCHAR(255) NOT NULL,
                badge VARCHAR(50) NOT NULL
            )
        """)
        conn.commit()
        
        # 2b. Property Images Table Setup
        cur.execute("""
            CREATE TABLE IF NOT EXISTS property_images (
                id INT AUTO_INCREMENT PRIMARY KEY,
                property_id INT NOT NULL,
                img_path VARCHAR(255) NOT NULL,
                FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
            )
        """)
        conn.commit()
        
        # 3. Seeding properties if table is empty
        cur.execute("SELECT COUNT(*) FROM properties")
        count = cur.fetchone()[0]
        if count == 0:
            seed_data = [
                ('2BHK Ready-to-Move Flat', 'Sector 7, Kamothe', '₹45 Lakh', 45.0, 'flat', 'buy', '820 sq.ft', '2 BHK', '2', '1', 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&q=80', 'For Sale'),
                ('1BHK Furnished Flat on Rent', 'Sector 12, Kamothe', '₹12,000/mo', 0.12, 'flat', 'rent', '550 sq.ft', '1 BHK', '1', '1', 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?w=600&q=80', 'For Rent'),
                ('Commercial Shop — Ground Floor', 'Sector 20, Kamothe', '₹28 Lakh', 28.0, 'shop', 'buy', '320 sq.ft', 'Commercial', '1', '1', 'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=600&q=80', 'For Sale'),
                ('500 Sq.Yd Residential Plot', 'Kharghar, Navi Mumbai', '₹85 Lakh', 85.0, 'plot', 'buy', '500 sq.yd', '—', '—', '—', 'https://images.unsplash.com/photo-1500382017468-9049fed747ef?w=600&q=80', 'For Sale'),
                ('3BHK Spacious Apartment', 'Sector 3, Kamothe', '₹78 Lakh', 78.0, 'flat', 'buy', '1200 sq.ft', '3 BHK', '2', '1', 'https://images.unsplash.com/photo-1484154218962-a197022b5858?w=600&q=80', 'For Sale'),
                ('Shop on Rent — High Footfall', 'Sector 15, Kamothe', '₹18,000/mo', 0.18, 'shop', 'rent', '450 sq.ft', 'Commercial', '1', '2', 'https://images.unsplash.com/photo-1563013544-824ae1d704d3?w=600&q=80', 'For Rent'),
                ('G+4 Residential Building', 'Panvel, Navi Mumbai', '₹3.2 Crore', 320.0, 'building', 'buy', '4500 sq.ft', '12 Units', '12', '8', 'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=600&q=80', 'For Sale'),
                ('Office Space — IT Park Area', 'Kharghar, Navi Mumbai', '₹55 Lakh', 55.0, 'office', 'buy', '900 sq.ft', 'Office', '2', '2', 'https://images.unsplash.com/photo-1497366216548-37526070297c?w=600&q=80', 'For Sale'),
                ('2BHK Semi-Furnished Flat', 'Sector 22, Kamothe', '₹14,500/mo', 0.145, 'flat', 'rent', '780 sq.ft', '2 BHK', '2', '1', 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600&q=80', 'For Rent'),
                ('250 Sq.Yd Corner Plot', 'Ulwe, Navi Mumbai', '₹42 Lakh', 42.0, 'plot', 'buy', '250 sq.yd', '—', '—', '—', 'https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?w=600&q=80', 'For Sale'),
                ('1BHK New Construction Flat', 'Sector 9, Kamothe', '₹32 Lakh', 32.0, 'flat', 'buy', '610 sq.ft', '1 BHK', '1', '1', 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600&q=80', 'For Sale'),
                ('Showroom — Main Road', 'Sector 1, Kamothe', '₹25,000/mo', 0.25, 'shop', 'rent', '700 sq.ft', 'Commercial', '1', '3', 'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=600&q=80', 'For Rent')
            ]
            cur.executemany("""
                INSERT INTO properties (name, loc, price, priceV, type, purpose, area, beds, bath, parking, img, badge)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, seed_data)
            conn.commit()
            print("Default properties seeded successfully.")
            
        # 4. Setup admin_users table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS admin_users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                role VARCHAR(50) DEFAULT 'admin',
                security_question VARCHAR(255) NOT NULL,
                security_answer VARCHAR(255) NOT NULL
            )
        """)
        conn.commit()

        # Seed default admin user if table is empty
        cur.execute("SELECT COUNT(*) FROM admin_users")
        admin_count = cur.fetchone()[0]
        if admin_count == 0:
            h_password = hash_password("admin123")
            h_answer = hash_password("panvelrealty")
            cur.execute("""
                INSERT INTO admin_users (username, password, role, security_question, security_answer)
                VALUES (%s, %s, %s, %s, %s)
            """, ("admin", h_password, "main_admin", "What is your default recovery key?", h_answer))
            conn.commit()
            print("Default admin user seeded successfully.")
        else:
            cur.execute("UPDATE admin_users SET role = 'main_admin' WHERE username = 'admin'")
            conn.commit()

        cur.close()
        conn.close()
    except Exception as e:
        print("Database init error:", e)

# ===== PAGES ROUTING =====
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/properties')
def properties():
    return render_template('properties.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

# ===== ADMIN AUTHENTICATION ROUTES =====
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    error = None
    success_message = None
    if request.args.get('reset_success'):
        success_message = "Password reset successful! Please sign in with your new password."
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        try:
            conn = get_db_connection()
            cur = conn.cursor(pymysql.cursors.DictCursor)
            cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            
            if user and check_password(password, user['password']):
                session['admin_logged_in'] = True
                session.permanent = False
                session['admin_username'] = user['username']
                session['admin_user_id'] = user['id']
                return redirect(url_for('admin_dashboard', login_event='true'))
            else:
                error = "Invalid Username or Password!"
        except Exception as e:
            error = f"Database Error: {str(e)}"
            
    return render_template('login.html', error=error, success_message=success_message)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    session.pop('admin_user_id', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
        
    error = None
    step = 1
    username = None
    security_question = None
    
    if request.method == 'POST':
        action = request.form.get('action')
        username = request.form.get('username')
        
        if action == 'search_username':
            try:
                conn = get_db_connection()
                cur = conn.cursor(pymysql.cursors.DictCursor)
                cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
                user = cur.fetchone()
                cur.close()
                conn.close()
                
                if user:
                    step = 2
                    security_question = user['security_question']
                else:
                    error = "Username not found!"
            except Exception as e:
                error = f"Database Error: {str(e)}"
                
        elif action == 'reset_password':
            security_answer = request.form.get('security_answer')
            new_password = request.form.get('new_password')
            
            if not security_answer or not new_password:
                error = "All fields are required!"
                step = 2
            else:
                try:
                    conn = get_db_connection()
                    cur = conn.cursor(pymysql.cursors.DictCursor)
                    cur.execute("SELECT * FROM admin_users WHERE username = %s", (username,))
                    user = cur.fetchone()
                    
                    if user:
                        if check_password(security_answer.strip().lower(), user['security_answer']):
                            h_password = hash_password(new_password)
                            cur.execute("UPDATE admin_users SET password = %s WHERE id = %s", (h_password, user['id']))
                            conn.commit()
                            cur.close()
                            conn.close()
                            return redirect(url_for('admin_login', reset_success=True))
                        else:
                            error = "Incorrect answer to security question!"
                            step = 2
                            security_question = user['security_question']
                    else:
                        error = "Username no longer exists!"
                        step = 1
                    
                    cur.close()
                    conn.close()
                except Exception as e:
                    error = f"Database Error: {str(e)}"
                    step = 2
                    
    return render_template('forgot_password.html', error=error, step=step, username=username, security_question=security_question)

# ===== SUBMIT ENQUIRY LOGIC =====
@app.route('/submit-enquiry', methods=['POST'])
def submit_enquiry():
    if request.method == 'POST':
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        looking_for = request.form.get('looking_for')
        prop_type = request.form.get('prop_type')
        budget = request.form.get('budget')
        message = request.form.get('message')
        
        if not name or not phone:
            return "Error: Name and Phone are required!", 400
            
        try:
            # Connection open kiya
            conn = get_db_connection()
            cur = conn.cursor()
            
            query = """INSERT INTO enquiries (client_name, client_phone, client_email, looking_for, property_type, budget_range, message) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cur.execute(query, (name, phone, email, looking_for, prop_type, budget, message))
            
            conn.commit() # Data save kiya
            cur.close()   # Cursor band kiya
            conn.close()  # Connection band kiya
            
            return redirect(url_for('contact', success=True))
        except Exception as e:
            return f"Database Error: {str(e)}", 500
# ===== ADMIN DASHBOARD PORTAL =====
@app.route('/admin')
@admin_required
def admin_dashboard():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        
        # 1. Fetch saari enquiries (ordered by id DESC so new ones appear first)
        cur.execute("SELECT * FROM enquiries ORDER BY id DESC")
        all_enquiries = cur.fetchall()
        
        # 2. Fetch saari properties
        cur.execute("SELECT * FROM properties ORDER BY id DESC")
        all_properties = cur.fetchall()
        
        # 3. Fetch all admins for user management
        cur.execute("SELECT id, username, role, security_question FROM admin_users ORDER BY id ASC")
        all_admins = cur.fetchall()
        
        # 4. Fetch details of the currently logged-in user
        logged_in_id = session.get('admin_user_id')
        cur.execute("SELECT * FROM admin_users WHERE id = %s", (logged_in_id,))
        current_admin = cur.fetchone()
        
        is_main_admin = (current_admin['role'] == 'main_admin') if current_admin else False
        
        cur.close()
        conn.close()
        
        return render_template('admin.html', 
                               enquiries=all_enquiries, 
                               properties=all_properties, 
                               admins=all_admins,
                               current_admin=current_admin,
                               is_main_admin=is_main_admin)
    except Exception as e:
        return f"Database Error: {str(e)}", 500

@app.route('/admin/users/add', methods=['POST'])
@admin_required
def add_admin():
    try:
        current_user_id = session.get('admin_user_id')
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify role
        cur.execute("SELECT role FROM admin_users WHERE id = %s", (current_user_id,))
        role_res = cur.fetchone()
        if not role_res or role_res[0] != 'main_admin':
            cur.close()
            conn.close()
            return redirect(url_for('admin_dashboard', tab='users', add_error="Permission denied: Only the main administrator can create new accounts."))

        username = request.form.get('username')
        password = request.form.get('password')
        security_question = request.form.get('security_question')
        security_answer = request.form.get('security_answer')
        
        if not username or not password or not security_question or not security_answer:
            cur.close()
            conn.close()
            return redirect(url_for('admin_dashboard', tab='users', add_error="All fields are required!"))
            
        # Check if username is taken
        cur.execute("SELECT id FROM admin_users WHERE username = %s", (username,))
        existing_user = cur.fetchone()
        if existing_user:
            cur.close()
            conn.close()
            return redirect(url_for('admin_dashboard', tab='users', add_error="Username already exists!"))
            
        h_password = hash_password(password)
        h_answer = hash_password(security_answer.strip().lower())
        
        cur.execute("""
            INSERT INTO admin_users (username, password, role, security_question, security_answer)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, h_password, 'admin', security_question, h_answer))
        
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for('admin_dashboard', tab='users', add_success=True))
    except Exception as e:
        return f"Database Error: {str(e)}", 500



@app.route('/admin/users/delete/<int:id>', methods=['POST'])
@admin_required
def delete_admin(id):
    try:
        current_user_id = session.get('admin_user_id')
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Verify role
        cur.execute("SELECT role FROM admin_users WHERE id = %s", (current_user_id,))
        role_res = cur.fetchone()
        if not role_res or role_res[0] != 'main_admin':
            cur.close()
            conn.close()
            return {"error": "Permission denied: Only the main administrator can delete accounts."}, 403

        if id == current_user_id:
            cur.close()
            conn.close()
            return {"error": "You cannot delete yourself!"}, 400
            
        # Check if this is the last admin
        cur.execute("SELECT COUNT(*) FROM admin_users")
        count = cur.fetchone()[0]
        if count <= 1:
            cur.close()
            conn.close()
            return {"error": "Cannot delete the only remaining administrator!"}, 400
            
        cur.execute("DELETE FROM admin_users WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/admin/update-status', methods=['POST'])
@admin_required
def update_status():
    try:
        data = request.get_json()
        enq_id = data.get('id')
        status = data.get('status')
        
        if not enq_id or not status:
            return {"error": "Missing parameters"}, 400
            
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("UPDATE enquiries SET status = %s WHERE id = %s", (status, enq_id))
        conn.commit()
        cur.close()
        conn.close()
        
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}, 500

# ===== PROPERTIES API =====
@app.route('/api/properties')
def api_properties():
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM properties ORDER BY id DESC")
        props = cur.fetchall()
        cur.execute("SELECT * FROM property_images")
        images = cur.fetchall()
        cur.close()
        conn.close()
        
        from collections import defaultdict
        prop_imgs = defaultdict(list)
        for img in images:
            prop_imgs[img['property_id']].append(img['img_path'])
            
        for p in props:
            p['images'] = [p['img']] + prop_imgs[p['id']]
            
        return jsonify(props)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/properties/<int:id>')
def api_property(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor(pymysql.cursors.DictCursor)
        cur.execute("SELECT * FROM properties WHERE id = %s", (id,))
        prop = cur.fetchone()
        if prop:
            cur.execute("SELECT id, img_path FROM property_images WHERE property_id = %s", (id,))
            add_imgs = cur.fetchall()
            prop['additional_images'] = add_imgs
            prop['images'] = [prop['img']] + [img['img_path'] for img in add_imgs]
        cur.close()
        conn.close()
        if prop:
            return jsonify(prop)
        return jsonify({"error": "Property not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== PROPERTY CRUD OPERATONS =====
@app.route('/admin/properties/add', methods=['POST'])
@admin_required
def add_property():
    try:
        name = request.form.get('name')
        loc = request.form.get('loc')
        price = request.form.get('price')
        priceV_raw = request.form.get('priceV')
        type_ = request.form.get('type')
        purpose = request.form.get('purpose')
        area = request.form.get('area', '—')
        beds = request.form.get('beds', '—')
        bath = request.form.get('bath', '—')
        parking = request.form.get('parking', '—')
        badge = request.form.get('badge')
        
        try:
            priceV = float(priceV_raw) if priceV_raw else 0.0
        except ValueError:
            priceV = 0.0
            
        img = ""
        # Handle file upload
        if 'img_file' in request.files and request.files['img_file'].filename != '':
            file = request.files['img_file']
            filename = secure_filename(file.filename)
            import time
            unique_filename = f"{int(time.time())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            img = f"/static/uploads/{unique_filename}"
        else:
            # Fallback to external URL
            img = request.form.get('img_url', 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=600&q=80')
            
        conn = get_db_connection()
        cur = conn.cursor()
        query = """
            INSERT INTO properties (name, loc, price, priceV, type, purpose, area, beds, bath, parking, img, badge)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cur.execute(query, (name, loc, price, priceV, type_, purpose, area, beds, bath, parking, img, badge))
        prop_id = cur.lastrowid
        
        # Handle multiple additional files upload
        if 'property_images' in request.files:
            files = request.files.getlist('property_images')
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    import time
                    import random
                    unique_filename = f"{int(time.time())}_{random.randint(1000, 9999)}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    img_path = f"/static/uploads/{unique_filename}"
                    cur.execute("INSERT INTO property_images (property_id, img_path) VALUES (%s, %s)", (prop_id, img_path))
                    
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard', tab='properties', prop_success=True))
    except Exception as e:
        return f"Database Error: {str(e)}", 500

@app.route('/admin/properties/edit', methods=['POST'])
@admin_required
def edit_property():
    try:
        prop_id = request.form.get('id')
        name = request.form.get('name')
        loc = request.form.get('loc')
        price = request.form.get('price')
        priceV_raw = request.form.get('priceV')
        type_ = request.form.get('type')
        purpose = request.form.get('purpose')
        area = request.form.get('area', '—')
        beds = request.form.get('beds', '—')
        bath = request.form.get('bath', '—')
        parking = request.form.get('parking', '—')
        badge = request.form.get('badge')
        
        try:
            priceV = float(priceV_raw) if priceV_raw else 0.0
        except ValueError:
            priceV = 0.0
            
        conn = get_db_connection()
        cur = conn.cursor()
        
        img = ""
        # Handle file upload
        if 'img_file' in request.files and request.files['img_file'].filename != '':
            file = request.files['img_file']
            filename = secure_filename(file.filename)
            import time
            unique_filename = f"{int(time.time())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(filepath)
            img = f"/static/uploads/{unique_filename}"
            
            # Optional: delete old image if it was local
            cur.execute("SELECT img FROM properties WHERE id = %s", (prop_id,))
            res = cur.fetchone()
            if res and res[0].startswith('/static/uploads/'):
                old_filename = res[0].replace('/static/uploads/', '')
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], old_filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print("Failed to remove old file:", e)
        else:
            # Check if external URL is provided
            img_url = request.form.get('img_url')
            if img_url:
                img = img_url
            else:
                # Keep old image
                cur.execute("SELECT img FROM properties WHERE id = %s", (prop_id,))
                res = cur.fetchone()
                img = res[0] if res else ""
                
        query = """
            UPDATE properties 
            SET name=%s, loc=%s, price=%s, priceV=%s, type=%s, purpose=%s, area=%s, beds=%s, bath=%s, parking=%s, img=%s, badge=%s
            WHERE id=%s
        """
        cur.execute(query, (name, loc, price, priceV, type_, purpose, area, beds, bath, parking, img, badge, prop_id))
        
        # Handle multiple additional files upload during edit
        if 'property_images' in request.files:
            files = request.files.getlist('property_images')
            for file in files:
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    import time
                    import random
                    unique_filename = f"{int(time.time())}_{random.randint(1000, 9999)}_{filename}"
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                    file.save(filepath)
                    img_path = f"/static/uploads/{unique_filename}"
                    cur.execute("INSERT INTO property_images (property_id, img_path) VALUES (%s, %s)", (prop_id, img_path))
                    
        conn.commit()
        cur.close()
        conn.close()
        
        return redirect(url_for('admin_dashboard', tab='properties', prop_edit_success=True))
    except Exception as e:
        return f"Database Error: {str(e)}", 500

@app.route('/admin/properties/delete-image/<int:image_id>', methods=['POST'])
@admin_required
def delete_property_image(image_id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT img_path FROM property_images WHERE id = %s", (image_id,))
        res = cur.fetchone()
        if res:
            img_path = res[0]
            if img_path.startswith('/static/uploads/'):
                filename = img_path.replace('/static/uploads/', '')
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print("Failed to delete local file:", e)
            cur.execute("DELETE FROM property_images WHERE id = %s", (image_id,))
            conn.commit()
            cur.close()
            conn.close()
            return {"success": True}
        cur.close()
        conn.close()
        return {"error": "Image not found"}, 404
    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/admin/properties/delete/<int:id>', methods=['POST'])
@admin_required
def delete_property(id):
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check and delete main image from local disk if it was uploaded
        cur.execute("SELECT img FROM properties WHERE id = %s", (id,))
        res = cur.fetchone()
        if res:
            img_path = res[0]
            if img_path.startswith('/static/uploads/'):
                filename = img_path.replace('/static/uploads/', '')
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print("Failed to delete local file:", e)
                        
        # Check and delete additional images from local disk if they were uploaded
        cur.execute("SELECT img_path FROM property_images WHERE property_id = %s", (id,))
        add_imgs = cur.fetchall()
        for row in add_imgs:
            img_path = row[0]
            if img_path.startswith('/static/uploads/'):
                filename = img_path.replace('/static/uploads/', '')
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                if os.path.exists(full_path):
                    try:
                        os.remove(full_path)
                    except Exception as e:
                        print("Failed to delete local additional file:", e)
                        
        cur.execute("DELETE FROM properties WHERE id = %s", (id,))
        conn.commit()
        cur.close()
        conn.close()
        return {"success": True}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    init_db()
    app.run(debug=True)