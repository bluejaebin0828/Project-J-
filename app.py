

from flask import Flask, request, redirect, session, render_template_string
import sqlite3

app = Flask(__name__)
app.secret_key = "project_j_secret_key"

USERS = {
    "Joseph": "p4nets123!",
    "Katherine": "p4nets234!",
    "Paul": "p4nets345!",
    "Jaime": "p4nets456",
    }

def get_db():
    return sqlite3.connect("payments.db")

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    working_period TEXT,
    working_week INTEGER,
    location TEXT,
    department TEXT,
    invoice TEXT,
    invoice_issue_date TEXT,
    amount REAL,
    due_date TEXT,
    receiving_date TEXT,
    status TEXT,
    net_amount REAL,
    net_taxable REAL,
    sales_tax REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()


LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
<title>P4N Payments Login</title>
<style>
body{
font-family:Arial;
background:#f5f5f5;
padding:50px;
text-align:center;
}

.box{
background:white;
width:350px;
margin:auto;
padding:30px;
border-radius:10px;
box-shadow:0 0 10px rgba(0,0,0,.1);
}

input{
width:90%;
padding:10px;
margin:5px;
}

button{
padding:10px 20px;
cursor:pointer;
}
</style>
</head>
<body>

<div class="box">
<h1>P4N Payments</h1>

<form method="POST">

<input name="username" placeholder="Username">

<input
type="password"
name="password"
placeholder="Password">

<br><br>

<button type="submit">
Login
</button>

</form>

</div>

</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        print("Username entered:", repr(username))
        print("Password entered:", repr(password))
        print("Expected password:", repr(USERS.get(username)))

        if USERS.get(username) == password:
            session["user"] = username
            return redirect("/dashboard")

    return LOGIN_PAGE


@app.route("/dashboard")
def dashboard():

    if "user" not in session:
        return redirect("/")
    
    conn = get_db()
    cur = conn.cursor()

    search = request.args.get("search", "")

    if search:

        cur.execute("""
            SELECT * FROM payments
            WHERE invoice LIKE ?
        """, (f"%{search}%",))

    else:
        cur.execute("SELECT * FROM payments ORDER BY id DESC")

    payments = cur.fetchall()
    conn.close()

    rows = ""

    for p in payments:
        rows += f"""
        <tr>
            <td>{p[1]}</td>
            <td>{p[3]}</td>
            <td>{p[4]}</td>
            <td>{p[5]}</td>
            <td>{p[6]}</td>
            <td>{p[7]}</td>
            <td>{p[8]}</td>
            <td>{p[9]}</td>
            <td>{p[10]}</td>
            <td>{p[11]}</td>
            <td>{p[12]}</td>
            <td>{p[13]}</td>
                
            <td style="display:flex; gap:6px; justify-content:center;">

            <!-- EDIT BUTTON -->
            <a href="/edit/{p[0]}">
                <button type="button"
                        style="background:#007bff;color:white;border:none;padding:6px 10px;cursor:pointer;">
                    Edit
                </button>
            </a>

            <!-- DELETE BUTTON -->
            <form action="/delete/{p[0]}" method="POST" style="display:inline;">
                <button type="submit"
                        onclick="return confirm('Delete this payment?')"
                        style="background:#dc3545;color:white;border:none;padding:6px 10px;cursor:pointer;">
                    Delete
                </button>
            </form>

         </td>    
    </tr>
    """

    return f"""

<!DOCTYPE html>
<html>
<head>

<title>P4N Payments</title>

<style>

body {{
font-family:Arial;
padding:20px;
}}

h1 {{
text-align:center;
}}

table {{
width:100%;
border-collapse:collapse;
margin-top:20px;
}}

th, td {{
border:1px solid #ccc;
padding:8px;
text-align:center;
}}

th {{
background:#efefef;
}}

input, select {{
padding:8px;
margin:4px;
}}

button {{
padding:8px 16px;
}}

.top {{
display:flex;
justify-content:space-between;
align-items:center;
}}

</style>

</head>

<body>

<div class="top">

<div>
Logged in as:
<b>{session["user"]}</b>
</div>

<div>
<a href="/logout">Logout</a>
</div>

</div>

<h1>P4N Payments</h1>

<h2>Payment Registration</h2>

<form action="/register" method="POST">

<input name="working_period" placeholder="Working Period">

<input name="location" placeholder="Location">

<input name="department" placeholder="Department">

<input name="invoice" placeholder="Invoice">

<input name="invoice_issue_date" placeholder="Invoice Issue Date">

<input name="amount" placeholder="Amount">

<input name="due_date" placeholder="Due Date">

<input name="receiving_date" placeholder="Receiving Date">

<select name="status">
<option>Open</option>
<option>Closed</option>
</select>

<input name="net_amount" placeholder="Net Amount">

<input name="net_taxable" placeholder="Net Taxable">

<input name="sales_tax" placeholder="Sales Tax">

<br><br>

<div style="display:flex; gap:10px; align-items:center;">

    <button type="submit">
        Register Payment
    </button>

    <a href="/history" style="
    padding:8px 16px;
    background:#6c757d;
    color:white;
    text-decoration:none;
    border-radius:5px;
    display:inline-block;
">
    History
</a>

</div>

</form>

<hr>

<div style="display:flex; justify-content:space-between; align-items:center;">

    <div style="display:flex; align-items:center; gap:10px;">

        <form method="GET" action="/dashboard">
            <input name="search" 
            value="{search}"
            placeholder="Search Invoice">
            
            <button type="submit">Search</button>
        </form>

    </div>

    <div id="clock" style="font-weight:bold; font-size:16px;"></div>

</div>

<table>

<tr>
<th>Working Period</th>
<th>Location</th>
<th>Department</th>
<th>Invoice</th>
<th>Invoice Issue Date</th>
<th>Amount</th>
<th>Due Date</th>
<th>Receiving Date</th>
<th>Status</th>
<th>Net Amount</th>
<th>Net Taxable</th>
<th>Sales Tax</th>
<th>Actions</th>
</tr>

{rows}

</table>

<script>
function updateClock() {{
    const now = new Date();
    document.getElementById("clock").innerHTML = now.toLocaleString();
}}

updateClock();
setInterval(updateClock, 1000);
</script>

</body>
</html>
"""


@app.route("/register", methods=["POST"])
def register():

    conn = get_db()
    cur = conn.cursor()

    working_period = request.form.get("working_period", "").strip()

    if not working_period.startswith("WK"):
        return "Working Period must be in the format WK1, WK2, WK3, etc."

    try:
        working_week = int(working_period.replace("WK", ""))
    except ValueError:
        return "Invalid Working Period."

    cur.execute("""
    INSERT INTO payments(
    working_period,
    working_week,
    location,
    department,
    invoice,
    invoice_issue_date,
    amount,
    due_date,
    receiving_date,
    status,
    net_amount,
    net_taxable,
    sales_tax
    )
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, (

    working_period,
    working_week,
    request.form.get("location"),
    request.form.get("department"),
    request.form.get("invoice"),
    request.form.get("invoice_issue_date"), 
    float(request.form.get("amount") or 0),
    request.form.get("due_date"),
    request.form.get("receiving_date"),
    request.form.get("status"),
    float(request.form.get("net_amount") or 0),
    float(request.form.get("net_taxable") or 0),
    float(request.form.get("sales_tax") or 0),

    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/edit/<int:payment_id>", methods=["GET"])
def edit(payment_id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM payments WHERE id=?", (payment_id,))
    payment = cur.fetchone()
    conn.close()

    if payment is None:
        return "Payment not found"

    return render_template_string("""
    <h2>Edit Payment</h2>

    <form method="POST" action="/update/{{p[0]}}">
        <input name="working_period" value="{{p[1]}}">
        <input name="location" value="{{p[3]}}">
        <input name="department" value="{{p[4]}}">
        <input name="invoice" value="{{p[5]}}">
        <input name="invoice_issue_date" value="{{p[6]}}">
        <input name="amount" value="{{p[7]}}">
        <input name="due_date" value="{{p[8]}}">
        <input name="receiving_date" value="{{p[9]}}">
        
        <select name="status">
            <option {{'selected' if p[10]=='Open' else ''}}>Open</option>
            <option {{'selected' if p[10]=='Closed' else ''}}>Closed</option>
        </select>

        <input name="net_amount" value="{{p[11]}}">
        <input name="net_taxable" value="{{p[12]}}">
        <input name="sales_tax" value="{{p[13]}}">

        <button type="submit">Update</button>
    </form>
    """, p=payment)

@app.route("/update/<int:id>", methods=["POST"])
def update(id):

    conn = get_db()
    cur = conn.cursor()
    
    if "user" not in session:
        return redirect("/")

    working_period = request.form.get("working_period", "").strip()

    if not working_period.startswith("WK"):
        return "Working Period must be in the format WK1, WK2, WK10, etc."

    try:
        working_week = int(working_period.replace("WK", ""))
    except ValueError:
        return "Invalid Working Period."

    cur.execute("""
        UPDATE payments SET
            working_period = ?,
            working_week = ?, 
            location = ?,
            department = ?,
            invoice = ?,
            invoice_issue_date = ?,
            amount = ?,
            due_date = ?,
            receiving_date = ?,
            status = ?,
            net_amount = ?,
            net_taxable = ?,
            sales_tax = ?
        WHERE id = ?
    """, (
        working_period,
        working_week,
        request.form.get("location"),
        request.form.get("department"),
        request.form.get("invoice"),
        request.form.get("invoice_issue_date"),
        request.form.get("amount"),
        request.form.get("due_date"),
        request.form.get("receiving_date"),
        request.form.get("status"),
        request.form.get("net_amount"),
        request.form.get("net_taxable"),
        request.form.get("sales_tax"),
        id
    ))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("DELETE FROM payments WHERE id = ?", (id,))

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/history")
def history():

    from datetime import datetime
    import pytz

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()
    
    week_sort = session.get("week_sort", "latest_week")
    date_sort = session.get("date_sort", "newest")

    week_order = "DESC" if week_sort == "latest_week" else "ASC"
    date_order = "DESC" if date_sort == "newest" else "ASC"

    selected_locations = session.get("selected_locations", [])
    selected_departments = session.get("selected_departments", [])

    selected_status = session.get("selected_status",["Open", "Closed"])
    
    status_placeholders = ",".join(["?"] * len(session.get("selected_status", ["Open", "Closed"])))


    if selected_locations and selected_departments:

        location_placeholders = ",".join(["?"] * len(selected_locations))
        department_placeholders = ",".join(["?"] * len(selected_departments))

        cur.execute(f"""
            SELECT *
            FROM payments
            WHERE location IN ({location_placeholders})
            AND department IN ({department_placeholders})
            AND status IN ({status_placeholders})
            ORDER BY
                working_week {week_order},
                created_at {date_order}
        """, selected_locations + selected_departments + selected_status)

    elif selected_locations:

        location_placeholders = ",".join(["?"] * len(selected_locations))

        cur.execute(f"""
            SELECT *
            FROM payments
            WHERE location IN ({location_placeholders})
            AND status IN ({status_placeholders})
            ORDER BY
                working_week {week_order},
                created_at {date_order}
        """, selected_locations + selected_status)

    elif selected_departments:

        department_placeholders = ",".join(["?"] * len(selected_departments))

        cur.execute(f"""
            SELECT *
            FROM payments
            WHERE department IN ({department_placeholders})
            AND status IN ({status_placeholders})
            ORDER BY
                working_week {week_order},
                created_at {date_order}
        """, selected_departments + selected_status)

    else:

        cur.execute(f"""
            SELECT *
            FROM payments
            WHERE status IN ({status_placeholders})
            ORDER BY
                working_week {week_order},
                created_at {date_order}
        """, selected_status)

    payments = cur.fetchall()
    conn.close()

    rows = ""

    central = pytz.timezone("America/Chicago")

    for p in payments:

        raw_time = p[14] if len(p) > 14 else None

        if raw_time:
            utc_time = datetime.strptime(raw_time, "%Y-%m-%d %H:%M:%S")
            utc_time = pytz.utc.localize(utc_time)

            central_time = utc_time.astimezone(central)
            formatted_time = central_time.strftime("%m/%d/%Y %I:%M %p")
        else:
            formatted_time = ""

        rows += f"""
        <tr>
            <td>{p[1]}</td>
            <td>{p[3]}</td>
            <td>{p[4]}</td>
            <td>{p[5]}</td>
            <td>{p[10]}</td>
            <td>{formatted_time}</td>
        </tr>
        """
    return f"""

    <!DOCTYPE html>
    <html>
    <head>
        <title>Payment History</title>
    </head>
    <body>

    <h1>Payment History</h1>

    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">

        <a href="/dashboard">
            <button>Back to Dashboard</button>
        </a>

        <a href="/history_settings">
        <button>History Settings</button>
        </a>
    
    </div>

    <br><br>

    <table border="1" cellpadding="8">

        <tr>
            <th>Working Period</th>
            <th>Location</th>
            <th>Department</th>
            <th>Invoice</th>
            <th>Status</th>
            <th>Posted Date & Time</th>
        </tr>

        {rows}

    </table>

    </body>
    </html>
    """



@app.route("/history_settings")
def history_settings():

    if "user" not in session:
        return redirect("/")

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        SELECT DISTINCT location
        FROM payments
        WHERE location IS NOT NULL
            AND location <> ''
        ORDER BY location
    """)

    locations = cur.fetchall()

    cur.execute("""
        SELECT DISTINCT department
        FROM payments
        WHERE department IS NOT NULL
            AND department <> ''
        ORDER BY department
    """)

    departments = cur.fetchall()

    conn.close()

    location_options = '<option value="">All Locations</option>'

    for loc in locations:

        selected = ""

        if loc[0] in session.get("selected_locations", []):
            selected = "selected"

        location_options += f"""
        <option value="{loc[0]}" {selected}>
            {loc[0]}
        </option>
        """

    department_options = '<option value="">All Departments</option>'

    for dept in departments:

        selected = ""

        if dept[0] in session.get("selected_departments", []):
            selected = "selected"

        department_options += f"""
        <option value="{dept[0]}" {selected}>
            {dept[0]}
        </option>
        """

    return f"""
    <!DOCTYPE html>
    <html>

    <head>

    <title>History Settings</title>

    <style>

    body{{
        font-family:Arial;
    padding:30px;
    }}

    h1{{
        text-align:center;
    }}

    .section{{
        margin-top:40px;
    }}

    button{{
        padding:10px 18px;
        cursor:pointer;
        margin-top:10px;
    }}

    .option{{
        margin-left:30px;
        margin-top:10px;
    }}

    </style>

    </head>

    <body>

    <h1>History Settings</h1>

    <a href="/history">
    <button type="button">Back to History</button>
    </a>

    <div class="section">
    
    <button type="button" onclick="toggleOrganization()">
        History Organization
    </button>

    <button type="button" onclick="toggleFilters()">
        Filters
    </button>

    <div id="organization" style="display:none;">

    <form method="POST" action="/save_history_settings">

    <h3>Week Organization</h3>

    <div class="option">
        <input type="radio" 
        name="week_sort" 
        value="latest_week"
        {"checked" if session.get("week_sort","latest_week")=="latest_week" else ""}>
        Latest Week → Recent Week
    </div>

    <div class="option">
        <input type="radio" 
        name="week_sort" 
        value="recent_week" 
        {"checked" if session.get("week_sort")=="recent_week" else ""}>
        Recent Week → Latest Week
    </div>


    <h3>Date & Time Organization</h3>

    <div class="option">
        <input type="radio" 
        name="date_sort" 
        value="newest"
        {"checked" if session.get("date_sort","newest")=="newest" else ""}>
        Latest Date &amp; 
        Time → Recent Date &amp; 
        Time
    </div>

    <div class="option">
        <input type="radio" 
        name="date_sort" 
        value="oldest"
        {"checked" if session.get("date_sort")=="oldest" else ""}>
        Recent Date &amp; 
        Time → Latest Date &amp; 
        Time
    </div>

    <br>

    <button type="submit">
    Save
    </button>

    </form>

    </div>

    <div id="filtersPanel" style="display:none; margin-top:20px;">

    <!-- This section is for filters -->

    <h2>Filters</h2>

    <form method="POST" action="/save_filters">

        <div class="option" style="display:flex; flex-direction:column; gap:10px; margin-left:30px;">

            <div style="margin-left:30px; margin-top:10px;">

        <label>Select Location</label>

        <br>

        <select name="selected_locations" multiple size="6">

    {location_options}

    </select>

    </div>

        <label>
            <input type="checkbox" 
                name="filter_department"
                {"checked" if session.get("filter_department") else ""}>
            Department
        </label>

        <div style="margin-left:30px; margin-top:10px;">

        <label>Select Department</label>

        <br>

        <select name="selected_departments" multiple size="6">

        {department_options}

        </select>

        </div>

    <h3>Status</h3>

    <label>
        <input type="checkbox"
            name="selected_status"
            value="Open"
            {"checked" if "Open" in session.get("selected_status", ["Open","Closed"]) else ""}>
        Open
    </label>

    <br>

    <label>
        <input type="checkbox"
            name="selected_status"
            value="Closed"
            {"checked" if "Closed" in session.get("selected_status", ["Open","Closed"]) else ""}>
        Closed
    </label>
        
        <button type="submit">
            Save Filters
        </button>

        </div>    

    </form>

    </div>

    <script>

    function toggleOrganization(){{

        let menu=document.getElementById("organization");

        if(menu.style.display=="none"){{
            menu.style.display="block";
        }}
        else{{
            menu.style.display="none";
        }}
    }}

    function toggleFilters(){{
        let panel=document.getElementById("filtersPanel");

        panel.style.display = (panel.style.display=="none") ? "block" : "none";
    }}

    </script>

    </body>

    </html>
    """

@app.route("/save_history_settings", methods=["POST"])
def save_history_settings():

    if "user" not in session:
        return redirect("/")

    session["week_sort"] = request.form.get(
        "week_sort",
        "latest_week"
    )

    session["date_sort"] = request.form.get(
        "date_sort",
        "newest"
    )

    return redirect("/history")

@app.route("/save_filters", methods=["POST"])
def save_filters():

    if "user" not in session:
        return redirect("/")

    location = request.form.get("filter_location")
    department = request.form.get("filter_department")
    status = request.form.get("filter_status")

    session["filter_location"] = location
    session["filter_department"] = department
    session["filter_status"] = status
    
    locations = [
    loc.strip()
    for loc in request.form.getlist("selected_locations")
    if loc.strip()
    ]

    session["selected_locations"] = locations

    departments = [
    dept.strip()
    for dept in request.form.getlist("selected_departments")
    if dept.strip()
    ]

    session["selected_departments"] = departments

    statuses = [
        status.strip()
        for status in request.form.getlist("selected_status")
        if status.strip()
    ]

    if not statuses:
        statuses = ["Open", "Closed"]

    session["selected_status"] = statuses

    return redirect("/history")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

import os

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False
    )