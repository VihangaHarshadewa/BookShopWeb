from flask import Flask, render_template, jsonify, request, session, redirect, url_for, abort
from functools import wraps
from config import Config
from models import db, Book, CartItem, Order, OrderItem
from decimal import Decimal
import uuid

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

def get_session_id():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ========== PUBLIC ROUTES ==========

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/books')
def get_books():
    category = request.args.get('category', 'all')
    search = request.args.get('search', '').strip().lower()
    featured = request.args.get('featured', 'false').lower() == 'true'

    query = Book.query
    if category != 'all':
        query = query.filter(Book.category == category)
    if search:
        query = query.filter(
            db.or_(
                db.func.lower(Book.title).contains(search),
                db.func.lower(Book.author).contains(search)
            )
        )
    if featured:
        query = query.filter(Book.featured == True)

    books = query.order_by(Book.created_at.desc()).all()
    return jsonify({'books': [b.to_dict() for b in books], 'count': len(books)})

@app.route('/api/books/<int:book_id>')
def get_book(book_id):
    book = Book.query.get_or_404(book_id)
    return jsonify(book.to_dict())

@app.route('/api/categories')
def get_categories():
    categories = db.session.query(Book.category).distinct().all()
    return jsonify([c[0] for c in categories])

@app.route('/api/cart', methods=['GET'])
def get_cart():
    session_id = get_session_id()
    items = CartItem.query.filter_by(session_id=session_id).all()
    total = sum(float(item.book.price) * item.quantity for item in items)
    return jsonify({
        'items': [item.to_dict() for item in items],
        'total': round(total, 2),
        'count': sum(item.quantity for item in items)
    })

@app.route('/api/cart', methods=['POST'])
def add_to_cart():
    data = request.get_json()
    session_id = get_session_id()
    book_id = data.get('book_id')
    quantity = data.get('quantity', 1)

    book = Book.query.get_or_404(book_id)
    if book.stock < quantity:
        return jsonify({'error': 'Not enough stock available'}), 400

    cart_item = CartItem.query.filter_by(session_id=session_id, book_id=book_id).first()
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(session_id=session_id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)

    db.session.commit()
    return jsonify({'message': 'Added to cart', 'item': cart_item.to_dict()})

@app.route('/api/cart/<int:item_id>', methods=['PUT'])
def update_cart_item(item_id):
    data = request.get_json()
    session_id = get_session_id()
    item = CartItem.query.filter_by(id=item_id, session_id=session_id).first_or_404()

    new_qty = data.get('quantity', 1)
    if new_qty <= 0:
        db.session.delete(item)
    else:
        if item.book.stock < new_qty:
            return jsonify({'error': 'Not enough stock'}), 400
        item.quantity = new_qty

    db.session.commit()
    return jsonify({'message': 'Cart updated'})

@app.route('/api/cart/<int:item_id>', methods=['DELETE'])
def remove_from_cart(item_id):
    session_id = get_session_id()
    item = CartItem.query.filter_by(id=item_id, session_id=session_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Item removed'})

@app.route('/api/checkout', methods=['POST'])
def checkout():
    data = request.get_json()
    session_id = get_session_id()

    cart_items = CartItem.query.filter_by(session_id=session_id).all()
    if not cart_items:
        return jsonify({'error': 'Cart is empty'}), 400

    total = sum(float(item.book.price) * item.quantity for item in cart_items)

    order = Order(
        session_id=session_id,
        total_amount=Decimal(str(total)),
        payment_method=data.get('payment_method', 'card'),
        customer_name=data.get('customer_name', 'Guest'),
        customer_email=data.get('customer_email', ''),
        status='completed'
    )
    db.session.add(order)
    db.session.flush()

    for cart_item in cart_items:
        order_item = OrderItem(
            order_id=order.id,
            book_id=cart_item.book_id,
            quantity=cart_item.quantity,
            price=cart_item.book.price
        )
        db.session.add(order_item)
        cart_item.book.stock -= cart_item.quantity

    CartItem.query.filter_by(session_id=session_id).delete()
    db.session.commit()

    return jsonify({'message': 'Payment successful', 'order': order.to_dict()})

@app.route('/api/orders')
def get_orders():
    session_id = get_session_id()
    orders = Order.query.filter_by(session_id=session_id).order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/stats')
def get_stats():
    book_count = Book.query.count()
    categories = db.session.query(Book.category).distinct().count()
    order_count = Order.query.count()
    return jsonify({'books': book_count, 'categories': categories, 'orders': order_count})

# ========== ADMIN ROUTES ==========

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        data = request.get_json() or request.form
        username = data.get('username', '')
        password = data.get('password', '')

        if username == app.config['ADMIN_USERNAME'] and password == app.config['ADMIN_PASSWORD']:
            session['admin_logged_in'] = True
            return jsonify({'success': True, 'redirect': '/admin'})
        return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/api/admin/books', methods=['GET'])
@admin_required
def admin_get_books():
    books = Book.query.order_by(Book.created_at.desc()).all()
    return jsonify([b.to_dict() for b in books])

@app.route('/api/admin/books', methods=['POST'])
@admin_required
def admin_create_book():
    data = request.get_json()
    book = Book(
        title=data['title'],
        author=data['author'],
        price=Decimal(str(data['price'])),
        category=data['category'],
        image_url=data.get('image_url', ''),
        description=data.get('description', ''),
        stock=data.get('stock', 10),
        rating=Decimal(str(data.get('rating', 5.0))),
        featured=data.get('featured', False)
    )
    db.session.add(book)
    db.session.commit()
    return jsonify({'message': 'Book created', 'book': book.to_dict()}), 201

@app.route('/api/admin/books/<int:book_id>', methods=['PUT'])
@admin_required
def admin_update_book(book_id):
    book = Book.query.get_or_404(book_id)
    data = request.get_json()

    book.title = data.get('title', book.title)
    book.author = data.get('author', book.author)
    book.price = Decimal(str(data['price'])) if 'price' in data else book.price
    book.category = data.get('category', book.category)
    book.image_url = data.get('image_url', book.image_url)
    book.description = data.get('description', book.description)
    book.stock = data.get('stock', book.stock)
    book.rating = Decimal(str(data['rating'])) if 'rating' in data else book.rating
    book.featured = data.get('featured', book.featured)

    db.session.commit()
    return jsonify({'message': 'Book updated', 'book': book.to_dict()})

@app.route('/api/admin/books/<int:book_id>', methods=['DELETE'])
@admin_required
def admin_delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    db.session.delete(book)
    db.session.commit()
    return jsonify({'message': 'Book deleted'})

@app.route('/api/admin/orders')
@admin_required
def admin_get_all_orders():
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return jsonify([order.to_dict() for order in orders])

@app.route('/api/admin/dashboard-stats')
@admin_required
def admin_dashboard_stats():
    total_books = Book.query.count()
    total_orders = Order.query.count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    low_stock = Book.query.filter(Book.stock < 5).count()

    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()

    return jsonify({
        'total_books': total_books,
        'total_orders': total_orders,
        'total_revenue': float(total_revenue),
        'low_stock': low_stock,
        'recent_orders': [o.to_dict() for o in recent_orders]
    })

@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def server_error(e):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000, debug=True)
