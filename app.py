import os, sqlite3
from datetime import datetime
from functools import wraps
from flask import Flask, g, jsonify, request, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.secret_key=os.environ.get("SECRET_KEY","change-this-secret-before-deployment")
DB=os.environ.get("DATABASE_PATH","smart_hall.db")
HALLS=[
("Main Auditorium","Large venue for seminars, conferences and cultural programmes",600,"Nu 5000","auditorium","https://images.unsplash.com/photo-1506157786151-b8491531f063?w=1000"),
("Conference Hall","Professional space with projector and conference seating",120,"Nu 2500","meeting","https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=1000"),
("Multi-purpose Hall","Flexible indoor venue for workshops and exhibitions",300,"Nu 3500","event","https://images.unsplash.com/photo-1519167758481-83f550bb49b3?w=1000"),
("Seminar Room A","Compact room for lectures and group discussions",60,"Nu 1000","classroom","https://images.unsplash.com/photo-1497366811353-6870744d04b2?w=1000"),
("Sports Hall","Indoor sports and activity venue",400,"Nu 3000","sports","https://images.unsplash.com/photo-1546519638-68e109498ffc?w=1000"),
("Open Ground","Outdoor venue for fairs and celebrations",1000,"Nu 2000","outdoor","https://images.unsplash.com/photo-1470229722913-7c0e2dbbaf67?w=1000")]

def db():
    if "db" not in g:
        g.db=sqlite3.connect(DB);g.db.row_factory=sqlite3.Row
    return g.db
@app.teardown_appcontext
def close_db(_):
    conn=g.pop("db",None)
    if conn: conn.close()
def init_db():
    c=sqlite3.connect(DB)
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT NOT NULL,email TEXT UNIQUE NOT NULL,password TEXT NOT NULL,role TEXT DEFAULT 'student',created_at TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS halls(id INTEGER PRIMARY KEY,name TEXT NOT NULL,description TEXT,capacity INTEGER,price TEXT,category TEXT,image TEXT,available INTEGER DEFAULT 1);
    CREATE TABLE IF NOT EXISTS bookings(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,hall_id INTEGER NOT NULL,event_name TEXT NOT NULL,event_date TEXT NOT NULL,start_time TEXT NOT NULL,end_time TEXT NOT NULL,attendees INTEGER NOT NULL,purpose TEXT,status TEXT DEFAULT 'Pending',created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id),FOREIGN KEY(hall_id) REFERENCES halls(id));
    CREATE TABLE IF NOT EXISTS feedback(id INTEGER PRIMARY KEY,user_id INTEGER NOT NULL,rating INTEGER NOT NULL,comment TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY(user_id) REFERENCES users(id));
    """)
    if c.execute("SELECT COUNT(*) FROM halls").fetchone()[0]==0:
        c.executemany("INSERT INTO halls(name,description,capacity,price,category,image) VALUES(?,?,?,?,?,?)",HALLS)
    if not c.execute("SELECT id FROM users WHERE email='admin@college.edu'").fetchone():
        c.execute("INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",("System Admin","admin@college.edu",generate_password_hash("Admin123!"),"admin"))
    c.commit();c.close()
def user():
    if not session.get("user_id"): return None
    return db().execute("SELECT id,name,email,role FROM users WHERE id=?",(session["user_id"],)).fetchone()
def required(fn):
    @wraps(fn)
    def w(*a,**k):
        if not user(): return jsonify(error="Please sign in first"),401
        return fn(*a,**k)
    return w
def admin(fn):
    @wraps(fn)
    def w(*a,**k):
        u=user()
        if not u:return jsonify(error="Please sign in first"),401
        if u["role"]!="admin":return jsonify(error="Administrator access required"),403
        return fn(*a,**k)
    return w

HTML = r"""
<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Smart Hall Booking | JNEC</title><link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Manrope:wght@600;700;800&display=swap" rel="stylesheet"><style>
:root{--navy:#20105f;--purple:#3510a0;--violet:#6429dc;--yellow:#ffc928;--ink:#201b36;--muted:#77738a;--bg:#f6f5fb;--line:#e9e6f2}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:'DM Sans',sans-serif}.top{height:72px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 5vw;position:sticky;top:0;z-index:3}.brand{font:800 19px Manrope;display:flex;align-items:center;gap:10px}.logo{width:38px;height:38px;border-radius:12px;background:var(--yellow);color:var(--navy);display:grid;place-items:center;font-weight:900}.top nav{display:flex;gap:22px;align-items:center}.top a{color:#eee;text-decoration:none;font-size:13px;cursor:pointer}.top a:hover{color:var(--yellow)}.wrap{max-width:1180px;margin:auto;padding:34px 24px}.hero{background:linear-gradient(115deg,#241067,#5420c1);border-radius:22px;color:white;padding:38px 42px;display:flex;justify-content:space-between;align-items:center;gap:20px}.hero h1{font:800 clamp(27px,4vw,42px) Manrope;margin:8px 0}.hero p{color:#ded6ff;max-width:570px;line-height:1.6}.eyebrow{color:var(--yellow);font-size:12px;font-weight:800;letter-spacing:1.7px}.btn{border:0;border-radius:9px;padding:11px 17px;background:var(--violet);color:white;font-weight:700;cursor:pointer}.yellow{background:var(--yellow);color:#241067}.red{background:#e84b62}.head{display:flex;justify-content:space-between;align-items:center;margin:34px 0 17px}.head h2{font:800 23px Manrope;margin:0}.muted{color:var(--muted);font-size:13px}.grid{display:grid;grid-template-columns:repeat(3,1fr);gap:19px}.hall{background:white;border:1px solid var(--line);border-radius:16px;overflow:hidden}.hall img{width:100%;height:165px;object-fit:cover;background:#ddd}.hallbody{padding:17px}.hall h3{margin:0 0 8px;font:700 17px Manrope}.hall p{font-size:13px;color:var(--muted);line-height:1.5;min-height:40px}.meta{display:flex;justify-content:space-between;font-size:12px;margin:12px 0 15px}.price{font-weight:800;color:var(--purple)}.panel,.stat{background:white;border:1px solid var(--line);border-radius:14px;padding:20px;margin-top:20px}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.stat strong{display:block;font:800 27px Manrope;color:var(--purple)}.stat span{font-size:12px;color:var(--muted)}.tablewrap{overflow:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{text-align:left;padding:13px;border-bottom:1px solid var(--line);white-space:nowrap}th{color:var(--muted);font-size:11px;text-transform:uppercase}.pill{border-radius:30px;padding:5px 10px;background:#fff4d5;color:#946700;font-size:11px;font-weight:700}.pill.Approved{background:#e0f8ed;color:#16814d}.pill.Rejected,.pill.Cancelled{background:#ffe5e9;color:#b72c48}.modal{position:fixed;inset:0;background:#130b36a6;display:none;align-items:center;justify-content:center;padding:20px;z-index:5}.modal.show{display:flex}.dialog{background:white;border-radius:18px;padding:25px;width:min(560px,100%);max-height:90vh;overflow:auto}.dialoghead{display:flex;justify-content:space-between;align-items:center;margin-bottom:18px}.dialoghead h2{margin:0;font:800 22px Manrope}.close{border:0;border-radius:50%;width:32px;height:32px;cursor:pointer}.tabs{display:flex;gap:8px}.tab{border:1px solid var(--line);background:white;border-radius:8px;padding:9px 13px;cursor:pointer}.tab.active{background:var(--navy);color:white}.field{margin:12px 0}label{display:block;font-size:12px;font-weight:700;margin-bottom:6px}input,select,textarea{width:100%;padding:11px 12px;border:1px solid #ded9ec;border-radius:8px;font:14px 'DM Sans'}textarea{min-height:85px}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.hidden{display:none!important}.empty{text-align:center;padding:28px;color:var(--muted)}footer{text-align:center;color:#9994aa;padding:28px;font-size:12px}@media(max-width:800px){.grid{grid-template-columns:repeat(2,1fr)}.stats{grid-template-columns:repeat(2,1fr)}}@media(max-width:560px){.grid,.formgrid{grid-template-columns:1fr}.top{padding:0 14px}.top nav{gap:9px}.top nav a{font-size:11px}.wrap{padding:20px 14px}.hero{padding:26px 22px}}
</style></head><body><header class="top"><div class="brand"><div class="logo">J</div> SMART HALL BOOKING</div><nav><a onclick="view('home')">Home</a><a onclick="view('bookings')">My Bookings</a><a id="adminLink" class="hidden" onclick="view('admin')">Admin</a><a onclick="modal('feedbackModal')">Feedback</a><a id="authLink" onclick="modal('authModal')">Login / Register</a><span id="userLabel"></span><a id="logoutLink" class="hidden" onclick="logout()">Logout</a></nav></header><main class="wrap">
<section id="homeView"><div class="hero"><div><div class="eyebrow">JIGME NAMGYEL ENGINEERING COLLEGE</div><h1>Find the perfect space<br>for your next event.</h1><p>Explore campus venues, check availability and reserve your hall in a few simple steps.</p><button class="btn yellow" onclick="document.getElementById('halls').scrollIntoView({behavior:'smooth'})">Explore Halls ↓</button></div><div style="font-size:90px;opacity:.2">⌂</div></div><div class="head"><div><h2>Available Halls</h2><span class="muted">Choose a venue that fits your event</span></div><select id="filter" style="width:170px" onchange="loadHalls()"><option value="">All categories</option><option>auditorium</option><option>meeting</option><option>event</option><option>classroom</option><option>sports</option><option>outdoor</option></select></div><div class="grid" id="halls"></div></section>
<section id="bookingsView" class="hidden"><div class="head"><h2>My Bookings</h2><button class="btn" onclick="view('home')">+ New Booking</button></div><div class="panel tablewrap"><table><thead><tr><th>Event</th><th>Hall</th><th>Date</th><th>Time</th><th>Attendees</th><th>Status</th><th>Action</th></tr></thead><tbody id="myBookings"></tbody></table><div id="bookingEmpty" class="empty hidden">No bookings yet.</div></div></section>
<section id="adminView" class="hidden"><div class="head"><h2>Administrator Dashboard</h2></div><div class="stats"><div class="stat"><strong id="statBookings">0</strong><span>Total bookings</span></div><div class="stat"><strong id="statPending">0</strong><span>Pending requests</span></div><div class="stat"><strong id="statUsers">0</strong><span>Registered users</span></div><div class="stat"><strong id="statHalls">0</strong><span>Active halls</span></div></div><div class="panel tablewrap"><h3>Booking requests</h3><table><thead><tr><th>Student</th><th>Event</th><th>Hall</th><th>Date</th><th>Time</th><th>Status</th><th>Decision</th></tr></thead><tbody id="adminBookings"></tbody></table></div></section></main><footer>Smart Hall Booking System · JNEC · Tashi · 05250198</footer>
<div class="modal" id="authModal"><div class="dialog"><div class="dialoghead"><h2 id="authTitle">Welcome back</h2><button class="close" onclick="hide('authModal')">×</button></div><div class="tabs"><button class="tab active" id="loginTab" onclick="authMode('login')">Login</button><button class="tab" id="registerTab" onclick="authMode('register')">Create account</button></div><form id="authForm"><div class="field hidden" id="nameField"><label>Full name</label><input name="name"></div><div class="field"><label>Email</label><input name="email" type="email" required></div><div class="field"><label>Password</label><input name="password" type="password" minlength="6" required></div><button class="btn">Continue</button></form><p id="authMsg" class="muted"></p></div></div>
<div class="modal" id="bookingModal"><div class="dialog"><div class="dialoghead"><h2>Book a Hall</h2><button class="close" onclick="hide('bookingModal')">×</button></div><p id="bookingHall" class="muted"></p><form id="bookingForm"><input type="hidden" name="hall_id"><div class="field"><label>Event name</label><input name="event_name" required></div><div class="field"><label>Purpose</label><textarea name="purpose"></textarea></div><div class="formgrid"><div class="field"><label>Event date</label><input name="event_date" type="date" required></div><div class="field"><label>Attendees</label><input name="attendees" type="number" min="1" required></div><div class="field"><label>Start time</label><input name="start_time" type="time" required></div><div class="field"><label>End time</label><input name="end_time" type="time" required></div></div><button class="btn">Submit booking request</button></form></div></div>
<div class="modal" id="feedbackModal"><div class="dialog"><div class="dialoghead"><h2>Share feedback</h2><button class="close" onclick="hide('feedbackModal')">×</button></div><form id="feedbackForm"><div class="field"><label>Rating</label><select name="rating"><option value="5">★★★★★ Excellent</option><option value="4">★★★★ Very good</option><option value="3">★★★ Good</option><option value="2">★★ Fair</option><option value="1">★ Poor</option></select></div><div class="field"><label>Comments</label><textarea name="comment"></textarea></div><button class="btn">Send feedback</button></form></div></div>
<script>
let me=null,hallCache=[],mode='login';const $=s=>document.querySelector(s);
async function api(url,opts={}){let r=await fetch(url,{headers:{'Content-Type':'application/json'},...opts}),d=await r.json();if(!r.ok)throw Error(d.error||'Request failed');return d}
function modal(id){if(id==='bookingModal'&&!me){modal('authModal');return}$('#'+id).classList.add('show')}function hide(id){$('#'+id).classList.remove('show')}
function view(v){['home','bookings','admin'].forEach(x=>$('#'+x+'View').classList.toggle('hidden',x!==v));if(v==='bookings')loadBookings();if(v==='admin')loadAdmin()}
function authMode(m){mode=m;$('#authTitle').textContent=m==='login'?'Welcome back':'Create account';$('#nameField').classList.toggle('hidden',m==='login');$('#loginTab').classList.toggle('active',m==='login');$('#registerTab').classList.toggle('active',m==='register')}
async function loadMe(){try{me=(await api('/api/me')).user}catch(e){me=null}$('#authLink').classList.toggle('hidden',!!me);$('#logoutLink').classList.toggle('hidden',!me);$('#userLabel').textContent=me?'Hi, '+me.name:'';$('#adminLink').classList.toggle('hidden',!me||me.role!=='admin')}
$('#authForm').onsubmit=async e=>{e.preventDefault();try{await api('/api/'+mode,{method:'POST',body:JSON.stringify(Object.fromEntries(new FormData(e.target)))});hide('authModal');await loadMe();alert('Signed in successfully')}catch(x){$('#authMsg').textContent=x.message}};
async function logout(){await api('/api/logout',{method:'POST'});await loadMe();view('home')}
async function loadHalls(){try{hallCache=(await api('/api/halls')).halls;let cat=$('#filter').value,items=hallCache.filter(h=>!cat||h.category===cat);$('#halls').innerHTML=items.map(h=>'<article class="hall"><img src="'+h.image+'" alt="'+h.name+'"><div class="hallbody"><h3>'+h.name+'</h3><p>'+h.description+'</p><div class="meta"><span>Capacity: '+h.capacity+'</span><span class="price">'+h.price+'</span></div><button class="btn" onclick="book('+h.id+')">Book this hall →</button></div></article>').join('')||'<div class="empty">No halls found.</div>'}catch(e){alert(e.message)}}
function book(id){let h=hallCache.find(x=>x.id===id);$('#bookingHall').textContent=h.name+' · Capacity '+h.capacity;$('#bookingForm').reset();$('#bookingForm').elements.hall_id.value=id;$('#bookingForm').elements.attendees.max=h.capacity;modal('bookingModal')}
$('#bookingForm').onsubmit=async e=>{e.preventDefault();let f=Object.fromEntries(new FormData(e.target));f.hall_id=Number(f.hall_id);f.attendees=Number(f.attendees);try{await api('/api/bookings',{method:'POST',body:JSON.stringify(f)});hide('bookingModal');alert('Booking request submitted');view('bookings')}catch(x){alert(x.message)}};
async function loadBookings(){try{let b=(await api('/api/bookings')).bookings;$('#bookingEmpty').classList.toggle('hidden',b.length>0);$('#myBookings').innerHTML=b.map(x=>'<tr><td>'+x.event_name+'</td><td>'+x.hall+'</td><td>'+x.event_date+'</td><td>'+x.start_time+'–'+x.end_time+'</td><td>'+x.attendees+'</td><td><span class="pill '+x.status+'">'+x.status+'</span></td><td>'+(['Pending','Approved'].includes(x.status)?'<button class="btn red" onclick="cancelBooking('+x.id+')">Cancel</button>':'—')+'</td></tr>').join('')}catch(e){alert(e.message)}}
async function cancelBooking(id){if(!confirm('Cancel this booking?'))return;try{await api('/api/bookings/'+id+'/cancel',{method:'POST'});loadBookings()}catch(e){alert(e.message)}}
async function loadAdmin(){try{let d=await api('/api/admin/dashboard');$('#statBookings').textContent=d.stats.bookings;$('#statPending').textContent=d.stats.pending;$('#statUsers').textContent=d.stats.users;$('#statHalls').textContent=d.stats.halls;$('#adminBookings').innerHTML=d.bookings.map(x=>'<tr><td>'+x.student+'</td><td>'+x.event_name+'</td><td>'+x.hall+'</td><td>'+x.event_date+'</td><td>'+x.start_time+'–'+x.end_time+'</td><td>'+x.status+'</td><td>'+(x.status==='Pending'?'<button class="btn" onclick="decide('+x.id+',\'Approved\')">Approve</button> <button class="btn red" onclick="decide('+x.id+',\'Rejected\')">Reject</button>':'—')+'</td></tr>').join('')}catch(e){alert(e.message);view('home')}}
async function decide(id,status){try{await api('/api/admin/bookings/'+id,{method:'PATCH',body:JSON.stringify({status})});loadAdmin()}catch(e){alert(e.message)}}
$('#feedbackForm').onsubmit=async e=>{e.preventDefault();try{await api('/api/feedback',{method:'POST',body:JSON.stringify(Object.fromEntries(new FormData(e.target)))});hide('feedbackModal');alert('Thank you for your feedback')}catch(x){alert(x.message)}};
loadMe();loadHalls();
</script></body></html>
"""

@app.get("/")
def home(): return render_template_string(HTML)
@app.get("/api/health")
def health(): return jsonify(status="ok",service="Smart Hall Booking API")
@app.post("/api/register")
def register():
    d=request.get_json() or {};name=d.get("name","").strip();email=d.get("email","").strip().lower();pw=d.get("password","")
    if not name or not email or len(pw)<6:return jsonify(error="Name, valid email and password of at least 6 characters are required"),400
    try:
        cur=db().execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",(name,email,generate_password_hash(pw)));db().commit();session["user_id"]=cur.lastrowid
        return jsonify(user={"id":cur.lastrowid,"name":name,"email":email,"role":"student"}),201
    except sqlite3.IntegrityError:return jsonify(error="Email already registered"),409
@app.post("/api/login")
def login():
    d=request.get_json() or {};u=db().execute("SELECT * FROM users WHERE email=?",(d.get("email","").lower(),)).fetchone()
    if not u or not check_password_hash(u["password"],d.get("password","")):return jsonify(error="Invalid email or password"),401
    session["user_id"]=u["id"];return jsonify(user={"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"]})
@app.post("/api/logout")
def logout():session.clear();return jsonify(message="Logged out")
@app.get("/api/me")
def me():
    u=user()
    return jsonify(user=dict(u)) if u else (jsonify(error="Not logged in"),401)
@app.get("/api/halls")
def halls():return jsonify(halls=[dict(x) for x in db().execute("SELECT * FROM halls WHERE available=1 ORDER BY id")])
@app.get("/api/bookings")
@required
def bookings():
    rows=db().execute("SELECT b.*,h.name hall FROM bookings b JOIN halls h ON h.id=b.hall_id WHERE b.user_id=? ORDER BY b.event_date DESC",(session["user_id"],))
    return jsonify(bookings=[dict(x) for x in rows])
@app.post("/api/bookings")
@required
def create_booking():
    d=request.get_json() or {}
    try:
        date=datetime.strptime(d["event_date"],"%Y-%m-%d").date();start=datetime.strptime(d["start_time"],"%H:%M");end=datetime.strptime(d["end_time"],"%H:%M");n=int(d["attendees"]);h=db().execute("SELECT * FROM halls WHERE id=? AND available=1",(int(d["hall_id"]),)).fetchone()
    except (KeyError,ValueError,TypeError):return jsonify(error="Complete all booking fields with valid values"),400
    if not d.get("event_name","").strip():return jsonify(error="Event name is required"),400
    if date<datetime.now().date():return jsonify(error="Choose today or a future date"),400
    if end<=start:return jsonify(error="End time must be after start time"),400
    if not h or n<1 or n>h["capacity"]:return jsonify(error="Hall not found or attendee count exceeds capacity"),400
    clash=db().execute("SELECT id FROM bookings WHERE hall_id=? AND event_date=? AND status IN ('Pending','Approved') AND start_time<? AND end_time>?",(h["id"],d["event_date"],d["end_time"],d["start_time"])).fetchone()
    if clash:return jsonify(error="This hall already has a booking during that time"),409
    cur=db().execute("INSERT INTO bookings(user_id,hall_id,event_name,event_date,start_time,end_time,attendees,purpose) VALUES(?,?,?,?,?,?,?,?)",(session["user_id"],h["id"],d["event_name"].strip(),d["event_date"],d["start_time"],d["end_time"],n,d.get("purpose","")));db().commit()
    return jsonify(booking_id=cur.lastrowid,message="Booking submitted"),201
@app.post("/api/bookings/<int:bid>/cancel")
@required
def cancel_booking(bid):
    cur=db().execute("UPDATE bookings SET status='Cancelled' WHERE id=? AND user_id=? AND status IN ('Pending','Approved')",(bid,session["user_id"]));db().commit()
    return (jsonify(message="Cancelled") if cur.rowcount else (jsonify(error="Booking not found or cannot be cancelled"),404))
@app.post("/api/feedback")
@required
def feedback():
    d=request.get_json() or {}
    try:r=int(d.get("rating",5))
    except ValueError:return jsonify(error="Invalid rating"),400
    if r<1 or r>5:return jsonify(error="Rating must be between 1 and 5"),400
    db().execute("INSERT INTO feedback(user_id,rating,comment) VALUES(?,?,?)",(session["user_id"],r,d.get("comment","")));db().commit();return jsonify(message="Feedback saved"),201
@app.get("/api/admin/dashboard")
@admin
def dashboard():
    c=db();stats={"bookings":c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0],"pending":c.execute("SELECT COUNT(*) FROM bookings WHERE status='Pending'").fetchone()[0],"users":c.execute("SELECT COUNT(*) FROM users").fetchone()[0],"halls":c.execute("SELECT COUNT(*) FROM halls WHERE available=1").fetchone()[0]}
    rows=c.execute("SELECT b.*,h.name hall,u.name student FROM bookings b JOIN halls h ON h.id=b.hall_id JOIN users u ON u.id=b.user_id ORDER BY b.created_at DESC")
    return jsonify(stats=stats,bookings=[dict(x) for x in rows])
@app.patch("/api/admin/bookings/<int:bid>")
@admin
def decide_booking(bid):
    status=(request.get_json() or {}).get("status")
    if status not in ("Approved","Rejected"):return jsonify(error="Choose Approved or Rejected"),400
    b=db().execute("SELECT * FROM bookings WHERE id=?",(bid,)).fetchone()
    if not b:return jsonify(error="Booking not found"),404
    if status=="Approved":
        clash=db().execute("SELECT id FROM bookings WHERE hall_id=? AND event_date=? AND id<>? AND status='Approved' AND start_time<? AND end_time>?",(b["hall_id"],b["event_date"],bid,b["end_time"],b["start_time"])).fetchone()
        if clash:return jsonify(error="Another approved booking conflicts with this request"),409
    db().execute("UPDATE bookings SET status=? WHERE id=?",(status,bid));db().commit();return jsonify(message="Booking "+status.lower())
if __name__=="__main__":
    init_db();app.run(host="0.0.0.0",port=int(os.environ.get("PORT",5000)),debug=os.environ.get("FLASK_DEBUG")=="1")
