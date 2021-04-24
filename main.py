from flask import Flask, render_template, url_for, redirect, make_response, request, abort
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from waitress import serve
import datetime as dt
from data import db_session
from data.user_s import User
from data.gen_s import Genre
from data.book_s import Book
from data.gen_s import genre_book
from data.buyer_s import Buyer
from data.cour_s import Courier
from data.region_s import Region
from data.region_s import region_courier
from data.ord_s import Order
from data.shed_ord_s import Shedule_order
from data.shed_s import Shedule
from data.buyer_book_s import Book_buyer
from forms.add_book import BookForm
from forms.add_buyer import BuyerForm
from forms.add_courier import CourierForm
from forms.add_genre import GenreForm
from forms.add_user import RegisterForm
from forms.login import LoginForm
from forms.add_region import RegionForm
from forms.add_order_shedule import Order_Shed_Form


db_session.global_init("db/store.sqlite")
app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)


def calc_1(we, re, kl, cour, bilo, mn):
    print(re, mn, kl)
    rr = sum([i[1] for i in re])
    kr = sum([i[1] for i in kl])
    if len(we) > 0:
        for i in range(len(we)):
            if bilo + we[i][1] == cour:
                re.append(we[i])
                if len(re) >= mn and sum(re) > sum(kl):
                    mn = len(re)
                    kl = re[:]
                    return (mn, kl)
            elif bilo + we[i][1] < cour:
                re.append(we[i])
                bilo += we[i][1]
                gt = we[:]
                del gt[i]
                mn, kl = calc_1(gt, re, kl, cour, bilo, mn)
    if len(re) >= mn and rr > kr:
        mn = len(re)
        kl = re[:]
        return (mn, kl)
    if len(kl) == 0 and bilo == 0:
        return [0]
    return (mn, kl)
    

def calc_2(we, re, kl, cour, bilo, mn):
    if len(we) > 0:
        for i in range(len(we)):
            if bilo - we[i][1] <= cour:
                re.append(we[i])
                if len(re) <= mn:
                    mn = len(re)
                    kl = re[:]
                    return (mn, kl)
            else:
                re.append(we[i])
                bilo -= we[i][1]
                gt = we[:]
                del gt[i]
                mn, kl = calc_1(gt, re, kl, cour, bilo, mn)
    if len(re) < mn:
        mn = len(re)
        kl = re[:]
        return (mn, kl)
    if len(kl) == 0 and bilo == 0:
        return [[0]]
    return (mn, kl)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)
    
@app.route('/')
def index():
    return redirect('/list_of_books')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            if user.user_type == 2 or user.user_type == 1:
                return redirect("/list_of_books")
            else:
                return redirect("/list_of_orders")
        return render_template('login.html',
                               message="Wrong in login or password",
                               form=form)
    return render_template('login.html', title='Autorization', form=form)

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Password mismatch")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="This user already exists")
        if form.user_type.data == "courier":
            c = 3
        elif form.user_type.data == "buyer":
            c = 2
        else:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="User type error ")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            user_type=c
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        if c == 2:
            return redirect(f'/add_buyer/{user.id}')
        elif c == 3:
            return redirect(f'/add_courier/{user.id}')
    return render_template('register.html', title='Registration', form=form)

@app.route("/add_buyer/<int:id>", methods=['GET', 'POST'])
def add_buy(id):
    form = BuyerForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        j = db_sess.query(Region).filter(Region.region_name == form.region.data).first()
        if j:
            gn = Buyer(region_id=j.id, user_id=id)
            db_sess.add(gn)
            db_sess.commit()
            return redirect("/login")
    return render_template('add_buyer.html', title='Add buyer', form=form)

@app.route('/add_like/<int:id>', methods=['GET', 'POST'])
def like(id):
    db_sess = db_session.create_session()
    bk = db_sess.query(Book).filter(Book.id == id).first()
    if bk:
        bk.like += 1
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_of_books')

@app.route('/add_dislike/<int:id>', methods=['GET', 'POST'])
def dislike(id):
    db_sess = db_session.create_session()
    bk = db_sess.query(Book).filter(Book.id == id).first()
    if bk:
        bk.dislike += 1
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_of_books')

@app.route("/basket")
def basket():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
        if q:
            j = db_sess.query(Book_buyer).filter(Book_buyer.buyer_id == q.id, Book_buyer.order_id == -1).all()
            f = []
            for i in j:
                f.append(db_sess.query(Book).filter(Book.id == i.book_id).first())
            return render_template("basket.html", j=j, q=q, f=f)
        else:
            abort(404)
    else:
        return redirect('/list_of_books')

@app.route('/add_in_basket/<int:id>', methods=['GET', 'POST'])
def add_basket(id):
    db_sess = db_session.create_session()
    q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    we = db_sess.query(Book_buyer).filter(q.id == Book_buyer.buyer_id, Book_buyer.book_id == id, Book_buyer.order_id == -1).all()
    if not we:
        bk = Book_buyer(
            book_id=id,
            buyer_id=q.id,
            order_id=-1,
            quantity=1
        )
        db_sess.add(bk)
        db_sess.commit()
    return redirect('/basket')

@app.route('/delete_in_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def deletebasket(id):
    db_sess = db_session.create_session()
    q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    bk = db_sess.query(Book_buyer).filter(Book_buyer.book_id == id, q.id == Book_buyer.buyer_id, Book_buyer.order_id == -1).first()
    if bk:
        db_sess.delete(bk)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/basket')

@app.route('/add_quantity/<int:id>', methods=['GET', 'POST'])
def addquan(id):
    db_sess = db_session.create_session()
    bk = db_sess.query(Book_buyer).filter(Book_buyer.id == id).first()
    if bk:
        book = db_sess.query(Book).filter(Book.id == bk.book_id).first()
        if book.quantity - bk.quantity - 1 >= 0:
            bk.quantity += 1
            db_sess.commit()
    else:
        abort(404)
    return redirect('/basket')

@app.route('/delete_quantity/<int:id>', methods=['GET', 'POST'])
def delquan(id):
    db_sess = db_session.create_session()
    bk = db_sess.query(Book_buyer).filter(Book_buyer.id == id).first()
    if bk:
        if bk.quantity - 1 >= 1:
            bk.quantity -= 1
            db_sess.commit()
    else:
        abort(404)
    return redirect('/basket')

@app.route('/create_order', methods=['GET', 'POST'])
def cr_order():
    db_sess = db_session.create_session()
    q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    bk = db_sess.query(Book_buyer).filter(Book_buyer.buyer_id == q.id, Book_buyer.order_id == -1).all()
    if bk:
        order = Order(buyer_id=q.id, complete=False, courier_id=-1, weight=0, region=q.region_id)
        db_sess.add(order)
        db_sess.commit()
        for i in bk:
            book = db_sess.query(Book).filter(Book.id == i.book_id).first()
            if book.quantity - i.quantity - 1 < 0:
                i.quantity = book.quantity
            book.quantity -= i.quantity
            i.order_id = order.id
            order.weight += i.quantity * book.weight
        db_sess.commit()
        return redirect(f'/create_order_shedules/{order.id}')
    else:
        abort(404)
    return redirect('/orders_buy')

@app.route('/create_order_shedules/<int:id>', methods=['GET', 'POST'])
def cr_order_shedule(id):
    db_sess = db_session.create_session()
    q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
    form = Order_Shed_Form()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        k = form.time.data.split()
        for i in k:
            tm = Shedule_order(order_id=id, time=i)
            db_sess.add(tm)
            db_sess.commit()
        return redirect("/orders_buy")
    return render_template('add_order_shedule.html', title="Add order's shedules", form=form)

@app.route("/orders_buy")
def orders_b():
    if current_user.is_authenticated:
        db_sess = db_session.create_session()
        q = db_sess.query(Buyer).filter(Buyer.user_id == current_user.id).first()
        if q:
            j = db_sess.query(Order).filter(Order.buyer_id == q.id).all()
            f = db_sess.query(Book_buyer).filter(Book_buyer.buyer_id == q.id).all()
            sh = []
            cour = []
            for i in j:
                sh.append(db_sess.query(Shedule_order).filter(Shedule_order.order_id == i.id).all())
                if i.courier_id != -1:
                    cr = db_sess.query(Courier).filter(Courier.id == i.courier_id).first()
                    cour.append([db_sess.query(User).filter(User.id == cr.user_id).first(), cr.id, i.id])
            return render_template("orders_buy.html", j=j, f=f, q=q, sh=sh, cour=cour)
        else:
            abort(404)
    else:
        return redirect('/list_of_books')

@app.route("/add_courier/<int:id>", methods=['GET', 'POST'])
def add_cour(id):
    form = CourierForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        cour = Courier(
            courier_type=form.courier_type.data,
            raz_type=form.courier_type.data,
            weight=0,
            earnings=0,
            start_time=dt.datetime.now())
        db_sess.add(cour)
        db_sess.commit()
        k = form.regions.data.split()
        for i in k:
            j = db_sess.query(Region).filter(Region.region_name == i).first()
            if j:
                cour.regions.append(j)
        k = form.time.data.split()
        for i in k:
            sh = Shedule(courier_id=cour.id, time=i)
            db_sess.add(sh)
            db_sess.commit()
        return redirect("/login")
    return render_template('add_courier.html', title='Add courier', form=form)

@app.route("/list_of_orders")
def list_order():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        h = db_sess.query(Courier).filter(Courier.user_id == current_user.id).first()
        j = db_sess.query(Order).filter(Order.courier_id == h.id, current_user.user_type == 3, Order.complete == 0).all()
        buyer = []
        rg = []
        f = []
        for i in j:
            buy = db_sess.query(Buyer).filter(Buyer.id == i.buyer_id).first()
            buyer.append([db_sess.query(User).filter(User.id == buy.user_id).first(), buy.id, i.id])
            rg.append(db_sess.query(Region).filter(Region.id == i.region).first().region_name)
            f += db_sess.query(Shedule_order).filter(Shedule_order.order_id == i.id).all()
        s = len(j)
        print(f)
        return render_template("orders_cour.html", j=j, h=h, s=s, rg=rg, buyer=buyer, f=f)

@app.route("/courier_account/<int:id>", methods=["GET", "POST"])
def courier_change(id):
    form = CourierForm()
    db_sess = db_session.create_session()
    cour = db_sess.query(Courier).filter(Courier.id == id, current_user.user_type == 3).first()
    if request.method == "GET":
        if cour:
            form.courier_type.data=cour.courier_type
            form.regions.data=" ".join([k.region_name for k in cour.regions])
            form.time.data=" ".join([i.time for i in db_sess.query(Shedule).filter(Shedule.courier_id == cour.id).all()])
        else:
            abort(404)
    if form.validate_on_submit():
        if not cour:
            return abort(404)
        cs = []
        if form.courier_type.data == "bike":
            k = 15
        elif form.courier_type.data == "foot":
            k = 10
        else:
            k = 50
        cour.courier_type = form.courier_type.data
        if cour.raz_type == "bike":
            e = 15
        elif cour.raz_type == "foot":
            e = 10
        else:
            e = 50
        if e > k:
            orw = [[i.id, i.weight] for i in db_sess.query(Order).filter(Order.courier_id == cour.id).all()]
            orw.sorted()
            fr = calc_2(orw, 0, 0, k, e, len(orw))
            if fr == 0:
                for i in orw:
                    k = db_sess.query(Order).get(i.id)
                    k.courier_id = -1
                    cs.append(k)
            else:
                for i in fr:
                    for j in orw:
                        if i[0] == j[0]:
                            k = db_sess.query(Order).get(i.id)
                            k.courier_id = -1
                            cs.append(k)
        cs.append(cour)
        if form.regions.data != " ".join([k.region_name for k in cour.regions]):
            for i in cour.regions:
                qw = [j for j in db_sess.query(Order).filter(Order.courier_id == cour.id, Order.region == i)]
                for j in qw:
                    j.courier_id = -1
                    cs.append(j)
                cour.regions.remove(i)
            k = form.regions.data.split()
            for i in k:
                j = db_sess.query(Region).filter(Region.region_name == i).first()
                if j:
                    cour.regions.append(j)
        if form.time.data != " ".join([i.time for i in db_sess.query(Shedule).filter(Shedule.courier_id == cour.id).all()]):
            k = db_sess.query(Shedule).filter(Shedule.courier_id == cour.id).all()
            for i in k:
                qw = [j for j in db_sess.query(Order).filter(Order.courier_id == cid)]
                for j in qw:
                    ty = [k for k in db_sess.query(Shedule_order).filter(Shedule_order.order_id == j.id, 
                            Shedule_order.time.split('-')[0] >= i.split('-')[0], Shedule_order.time.split('-')[0] < i.split('-')[1])]
                    if len(ty) == 0:
                        oe = db_sess.query(Order).filter(Order.id == j.id).first()
                        oe.courier_id = -1
                        cs.append(oe)
        for i in cs:
            db_sess.add(i)
            db_sess.commit()
        return redirect("/list_of_orders")
    return render_template('add_courier.html', title='Changing a courier', form=form)

@app.route("/take_orders/<int:id>", methods=["GET", "POST"])
def take_orders(id):
    db_sess = db_session.create_session()
    vf = db_sess.query(Courier).filter(Courier.id == id, current_user.user_type == 3).first()
    if not vf:
        abort(404)
    if len([i for i in db_sess.query(Order).filter(Order.courier_id == vf.id).all()]) == 0:
        ww = vf.weight
        vf.raz_type = vf.courier_type
        tt = vf.raz_type
        rr = [k.id for k in vf.regions]
        hh = [i.time for i in db_sess.query(Shedule).filter(Shedule.courier_id == vf.id).all()]
        rt = []
        for j in rr:
            t = [[i.id, i.weight] for i in db_sess.query(Order).filter(Order.region == j, Order.courier_id == -1).all()]
            for i in t:
                rt.append(i)
        we = []
        for j in rt:
            for k in hh:
                for i in db_sess.query(Shedule_order).filter(Shedule_order.order_id == j[0]):
                    gh = dt.time(hour=int(i.time.split('-')[0].split(":")[0]), minute=int(i.time.split('-')[0].split(":")[1]))
                    gf = dt.time(hour=int(k.split('-')[0].split(":")[0]), minute=int(k.split('-')[0].split(":")[1]))
                    gt = dt.time(hour=int(k.split('-')[1].split(":")[0]), minute=int(k.split('-')[1].split(":")[1]))
                    if gh >= gf and gh < gt:
                        if [i.order_id, j[1]] not in we:
                            we.append([i.order_id, j[1]])
        if tt == "foot":
            cour = 10
        if tt == "bike":
            cour = 15
        else:
            cour = 50
        tr = calc_1(we, [], [], cour, 0, 0)
        print(tr)
        if tr[0] == 0:
            vf.start_time = dt.datetime.now()
            vf.assign_time = vf.start_time
            db_sess.commit()
            return redirect("/list_of_orders")
        vf.start_time = dt.datetime.now()
        vf.assign_time = vf.start_time
        db_sess.add(vf)
        db_sess.commit()
        tr = tr[1]
        for i in tr:
            print(i[0])
            yy = db_sess.query(Order).filter(Order.id == i[0]).first()
            yy.courier_id = vf.id
            db_sess.add(yy)
            db_sess.commit()
        return redirect("/list_of_orders")
        abort(404)
    else:
        return redirect("/list_of_orders")

@app.route("/complete_order/<int:id>", methods=['GET', 'POST'])
def comp_order(id):
    db_sess = db_session.create_session()
    cour = db_sess.query(Courier).filter(Courier.user_id == current_user.id).first()
    order = db_sess.query(Order).filter(Order.id == id).first()
    reg = [k.id for k in cour.regions if k.id == order.region]
    cour.start_time = dt.datetime.now()
    order.complete = True
    if cour.raz_type == "foot":
        cour.earnings += 1000
    elif cour.raz_type == "bike":
        cour.earnings += 2500
    else:
        cour.earnings += 4500
    db_sess.commit()
    return redirect("/list_of_orders")

@app.route("/list_of_books")
def list_book():
    db_sess = db_session.create_session()
    j = db_sess.query(Book).all()
    return render_template("books.html", j=j)

@app.route('/add_book', methods=['GET', 'POST'])
def addb():
    form = BookForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():    
        f = request.files['file']
        img = url_for('static', filename=f'img/{f.filename}')
        book = Book(
            name=form.book.data,
            description=form.description.data,
            like=0,
            dislike=0,
            weight=form.weight.data,
            quantity=form.quantity.data,
            image=img
        )
        db_sess.add(book)
        db_sess.commit()
        k = form.genre.data.split()
        for i in range(len(k)):
            j = db_sess.query(Genre).filter(Genre.name == k[i]).first()
            if j:
                book.genres.append(j)
                db_sess.commit()
        return redirect('/list_of_books')
    j = db_sess.query(Genre).all()
    return render_template('add_book.html', title='Adding a book', form=form, j=j)

@app.route('/change_book/<int:id>', methods=['GET', 'POST'])
def changeb(id):
    form = BookForm()
    db_sess = db_session.create_session()
    bk = db_sess.query(Book).filter(Book.id == id, current_user.user_type == 1).first()
    if request.method == "GET":
        if bk:
            form.book.data=bk.name
            form.description.data=bk.description
            form.weight.data=bk.weight
            form.quantity.data=bk.quantity
            form.genre.data=" ".join([i.name for i in bk.genres])
        else:
            abort(404)
    if form.validate_on_submit():
        f = request.files['file']
        img = url_for('static', filename=f'img/{f.filename}')
        bk.name=form.book.data
        bk.description=form.description.data
        bk.weight=form.weight.data
        bk.quantity=form.quantity.data
        bk.image=img
        db_sess.commit()
        k = form.genre.data.split()
        for i in range(len(k)):
            j = db_sess.query(Genre).filter(Genre.name == k[i]).first()
            if j:
                bk.genres.append(j)
                db_sess.commit()
        return redirect('/list_of_books')
    return render_template('add_book.html', title='Changing a book', form=form)

@app.route('/delete_book/<int:id>', methods=['GET', 'POST'])
def deleteb(id):
    db_sess = db_session.create_session()
    bk = db_sess.query(Book).filter(Book.id == id, (current_user.user_type == 1)).first()
    if bk:
        db_sess.delete(bk)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_of_books')

@app.route("/list_of_genres")
def list_genre():
    db_sess = db_session.create_session()
    j = db_sess.query(Genre).all()
    return render_template("genres.html", j=j)

@app.route("/add_genre", methods=['GET', 'POST'])
def add_gen():
    form = GenreForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        gen = db_sess.query(Genre).filter(Genre.name == form.name.data).first()
        if not gen:
            gn = Genre(name=form.name.data)
            db_sess.add(gn)
            db_sess.commit()
            return redirect("/list_of_genres")
        return render_template('add_genre.html',
                               message="This genre already exists",
                               form=form)
    return render_template('add_genre.html', title='Add genre', form=form)

@app.route('/change_genre/<int:id>', methods=['GET', 'POST'])
def change_gen(id):
    form = GenreForm()
    db_sess = db_session.create_session()
    gen = db_sess.query(Genre).filter(Genre.id == id).first()
    if request.method == "GET":
        if gen:
            form.name.data=gen.name
        else:
            abort(404)
    if form.validate_on_submit():
        gen.name=form.name.data
        db_sess.commit()
        return redirect('/list_of_genres')
    return render_template('add_genre.html', title='Changing genre', form=form)

@app.route('/delete_genre/<int:id>', methods=['GET', 'POST'])
def delete_gen(id):
    db_sess = db_session.create_session()
    gen = db_sess.query(Genre).filter(Genre.id == id).first()
    if gen:
        db_sess.delete(gen)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_of_genres')

@app.route("/list_of_regions")
def list_reg():
    db_sess = db_session.create_session()
    j = db_sess.query(Region).all()
    return render_template("regions.html", j=j)

@app.route("/add_region", methods=['GET', 'POST'])
def add_reg():
    form = RegionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        reg = db_sess.query(Region).filter(Region.region_name == form.name.data).first()
        if not reg:
            rg = Region(region_name=form.name.data, address=form.address.data)
            db_sess.add(rg)
            db_sess.commit()
            return redirect("/list_of_regions")
        return render_template('add_region.html',
                               message="This genre already exists",
                               form=form)
    return render_template('add_region.html', title='Add region', form=form)

@app.route('/change_region/<int:id>', methods=['GET', 'POST'])
def change_reg(id):
    form = RegionForm()
    db_sess = db_session.create_session()
    reg = db_sess.query(Region).filter(Region.id == id).first()
    if request.method == "GET":
        if reg:
            form.name.data=reg.region_name
            form.address.data=reg.address
        else:
            abort(404)
    if form.validate_on_submit():
        reg.region_name=form.name.data
        reg.address=form.address.data
        db_sess.commit()
        return redirect('/list_of_regions')
    return render_template('add_region.html', title='Changing region', form=form)

@app.route('/delete_region/<int:id>', methods=['GET', 'POST'])
def delete_reg(id):
    db_sess = db_session.create_session()
    reg = db_sess.query(Region).filter(Region.id == id).first()
    if reg:
        db_sess.delete(reg)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/list_of_regions')


if __name__ == '__main__':
    serve(app, port=8080, host='127.0.0.1')