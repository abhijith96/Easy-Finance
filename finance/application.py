
from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
import mysql.connector
  


from helpers import *


def get_password():
    path = "password.txt"
    file1 = open(path, 'r')
    count = 0
    line = file1.readline()
    return line

# configure application
app = Flask(__name__)

def GetDBConnection():
    db_handle = mysql.connector.connect(host='localhost',
                        database='EasyFinance',
                        user='root',
                        password=get_password())
    return db_handle;

  


# ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# custom filter
app.jinja_env.filters["usd"] = usd

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# configure CS50 Library to use SQLite database


@app.route("/")
@login_required
def index():
    s=session["user_id"]
    return render_template("index.html")
  

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock."""
    if request.method == "GET":
        return  render_template("buy.html")

    elif request.method=="POST":
        # bs=request.form.get("bsymbol")
        # bs=bs.upper()
        # bsh=int(request.form.get("bshares"))
        # ba=lookup(bs)
        # if ba!= None and int(bsh)>0:
        #     ncash=float(bsh)*ba['price']
        #     c=session["user_id"]
        #     brow= mysql.execute("SELECT * FROM users WHERE id = :id", id=c)
        #     if brow:
        #         if ncash<=brow[0]["cash"]:
        #             mysql.execute("INSERT INTO history(id,symbol,name,shares,price,total) VALUES(:id,:symbol,:name,:shares,:price,:total)", id=c, symbol=bs,
        #             name=bs, shares=bsh, price=ba['price'],total=ncash)
        #             brow2=mysql.execute("SELECT sum(shares) from history where id=:id and ticker=:symbol", id=c, symbol=bs)
        #             zz=brow2[0]["sum(shares)"]
        #             total2=float(zz)*ba['price']
        #             mysql.execute("INSERT OR REPLACE INTO portfolio(id,ticker,name,shares,price,total) values(:id,:symbol,:name,:shares,:price,:total)",
        #             id=c, symbol=bs, name=bs, shares=zz,price=ba['price'],total=total2)

        #             nncash=brow[0]["cash"]-ncash
        #             nrcash=usd(round(nncash,2))
        #             mysql.execute("UPDATE users set cash=:cash where id=:id", cash=nncash, id=c)
        #             return redirect(url_for("index"))
        #         else:
        #             return apology("Not enough Funds")
        #     else:
        #         return apology("Log in again")


        # else:
        #     return apology("Invalid stock symbol or shares
        return apology("Buy not implemented")


@app.route("/history")
@login_required
def history():
    """Show history of transactions."""
    c=session["user_id"]
    # rows=mysql.execute("SELECT * FROM history where id=:id", id=c)
    # return render_template("history.html", rows=rows)
    return apology("History not implemented")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        db_handle = GetDBConnection()
        cursor = db_handle.cursor()
        rows = cursor.execute("SELECT * FROM users WHERE username = %s", (request.form.get("username"),))
        result_tuple = cursor.fetchone()
        print(result_tuple)
        print(rows)


        # ensure username exists and password is correct
        if not result_tuple:
            return apology("invalid username and/or password")
        elif not pwd_context.verify(request.form.get("password"), result_tuple[2]):
            return apology("invalid username or/and password")

        # remember which user has logged in
        session["user_id"] = result_tuple[0]


        # redirect user to home page
        return redirect(url_for("index"))

    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()

    # redirect user to login form
    return redirect(url_for("login"))

@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method=="POST":
        a=request.form.get("symbol")
        b=lookup(a)
        if(a==""):
            return apology("INVAID SYMBOL")

        if b:
            c=a
            d=usd(b['price'])
            return render_template("quoted.html", quote=c, price=d)
        else:
            return apology("INVAID SYMBOL",a)


    else:
        return render_template("quote.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user."""
    session.clear()
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
        elif not request.form.get("confirm"):
            return apology("must confirm password")
        
        password=request.form.get("password")
        username=request.form.get("username")
        password_confirmation=request.form.get("confirm")
    
        if password != password_confirmation:
            return apology("Passwords do not match")
        
        db_handle = GetDBConnection()
        cursor = db_handle.cursor()
        row_count = cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        queryed_row = cursor.fetchone()

    
        if queryed_row:
            return apology("Username exists")
        else:
            pwd_hash = pwd_context.hash(password)
            print( "hash lne", len(pwd_hash))
            cursor.execute("INSERT INTO users(username,hash) VALUES(%s, %s)", (request.form.get("username"), pwd_hash))
            g=cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            h = cursor.fetchone()
            print(h)
            if h:
                session["user_id"]=h[0]
                db_handle.commit()
                db_handle.close()
            return redirect(url_for("index"))
    else:
        return render_template("register.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock."""
    if request.method == "GET":
        return render_template("sell.html")
    elif request.method=="POST":
        return apology("Sell not Implemented")
        # sa=request.form.get("ssymbol")
        # sb=int(request.form.get("sshares"))
        # sc=session["user_id"]
        # srows=mysql.execute("SELECT * from portfolio where id=:id and ticker=:symbol", id=sc, symbol=sa)
        # srows2=mysql.execute("SELECT cash from users where id=:id ", id=sc)
        # oldcash=srows2[0]['cash']

        # if srows:
        #     sd=srows[0]['shares']


        #     if sb <=sd:

        #         se=lookup(sa)
        #         sf=se['price']
        #         sg=sf*sb
        #         sh=sd-sb
        #         si=sh*sf
        #         newcash=oldcash+sg
        #         mysql.execute("INSERT INTO history(id,symbol,name,shares,price,total) VALUES(:id,:symbol,:name,:shares,:price,:total)", id=sc, symbol=sa,
        #                 name=sa, shares=-sb, price=sf,total=sg)
        #         mysql.execute("update users set cash=:cash where id=:id ",cash=newcash, id=sc)
        #         if sb!=sd:
        #             mysql.execute("update portfolio set price=:price where id=:id and symbol=:symbol",price=sf, id=sc, symbol=sa)
        #             mysql.execute("update portfolio set shares=:shares where id=:id and symbol=:symbol",shares=sh, id=sc, symbol=sa)
        #             mysql.execute("update portfolio set total=:total where id=:id and symbol=:symbol",total=si, id=sc, symbol=sa)


        #             return redirect(url_for("index"))
        #         else:
        #             mysql.execute("delete from portfolio where id=:id and symbol=:symbol", id=sc, symbol=sa)
        #             return redirect(url_for("index"))

        #     else:
        #         return apology("You dont have enough stocks")
        # else:
        #     return apology("You dont own any stocks of current company")


@app.route("/addmoney", methods=["GET", "POST"])
@login_required
def addmoney():
    if request.method=="POST":
        a=int(request.form.get("money"))
        # if a>0:
        #     c=session["user_id"]
        #     row=mysql.execute("SELECT cash from users where id=:id", id=c)
        #     oldcash=row[0]['cash']
        #     newcash=oldcash+a
        #     mysql.execute("UPDATE users SET cash=:cash where id=:id", cash=newcash, id=c)
        #     return render_template("addmoney2.html", am=usd(a), total=usd(newcash))
        # else:
        #     return apology("Enter valid money")
        return apology("Add Money not Implemented")
    else:
        return render_template("addmoney.html")
