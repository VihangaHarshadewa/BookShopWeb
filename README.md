# Chapter One — Premium Bookshop

<img src="https://github.com/user-attachments/assets/548ee4b5-8d90-44b4-97e6-e48503e91f09" width="45%" />
<img src="https://github.com/user-attachments/assets/95eb3ff2-31ac-4475-ac26-4ed4ee63f3a1" width="45%" />

A full-stack Flask + PostgreSQL bookshop with the warm brown/gold design you provided, admin panel, and full CURL API documentation.

## Features

- **Warm Bookshop Design** — Brown/gold palette matching your uploaded design exactly
- **PostgreSQL Database** — Books, Cart, Orders with full relationships
- **Admin Panel** — Dashboard stats, CRUD books, view all orders at `/admin`
- **Payment UI** — Interactive credit card with Visa/MC/Amex detection
- **REST API** — Complete endpoints with CURL examples below

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:** Download from [postgresql.org/download](https://www.postgresql.org/download/windows/)

### 2. Create Database
```bash
psql postgres -c "CREATE DATABASE bookshop;"
psql postgres -c "CREATE USER bookshop_user WITH PASSWORD 'bookshop_pass';"
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE bookshop TO bookshop_user;"
```

### 3. Setup & Run
```bash
cd bookshop
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env

# Initialize database
python -c "from app import app; from models import db; app.app_context().push(); db.create_all()"

# Seed sample books
python seed.py

# Run server
python app.py
```

Open **http://localhost:5000**

Admin Panel: **http://localhost:5000/admin** (default: `admin` / `admin123`)

---

## API Endpoints & CURL Operations

### PUBLIC ENDPOINTS

#### List Books
```bash
curl -X GET "http://localhost:5000/api/books"

# Filter by category
curl -X GET "http://localhost:5000/api/books?category=classic"

# Search
curl -X GET "http://localhost:5000/api/books?search=gatsby"

# Featured only
curl -X GET "http://localhost:5000/api/books?featured=true"
```

#### Get Single Book
```bash
curl -X GET "http://localhost:5000/api/books/1"
```

#### Get Categories
```bash
curl -X GET "http://localhost:5000/api/categories"
```

#### Get Cart
```bash
curl -X GET "http://localhost:5000/api/cart"   -H "Cookie: session=<your_session_cookie>"
```

#### Add to Cart
```bash
curl -X POST "http://localhost:5000/api/cart"   -H "Content-Type: application/json"   -d '{"book_id": 1, "quantity": 1}'
```

#### Update Cart Quantity
```bash
curl -X PUT "http://localhost:5000/api/cart/1"   -H "Content-Type: application/json"   -d '{"quantity": 3}'
```

#### Remove from Cart
```bash
curl -X DELETE "http://localhost:5000/api/cart/1"
```

#### Checkout (Payment)
```bash
curl -X POST "http://localhost:5000/api/checkout"   -H "Content-Type: application/json"   -d '{
    "payment_method": "card",
    "customer_name": "John Doe",
    "customer_email": "john@example.com"
  }'
```

#### Get My Orders
```bash
curl -X GET "http://localhost:5000/api/orders"
```

#### Get Shop Stats
```bash
curl -X GET "http://localhost:5000/api/stats"
```

---

### ADMIN ENDPOINTS (Requires Login)

#### Admin Login
```bash
curl -X POST "http://localhost:5000/admin/login"   -H "Content-Type: application/json"   -d '{"username": "admin", "password": "admin123"}'   -c cookies.txt
```

#### Get All Books (Admin)
```bash
curl -X GET "http://localhost:5000/api/admin/books"   -b cookies.txt
```

#### Create Book
```bash
curl -X POST "http://localhost:5000/api/admin/books"   -H "Content-Type: application/json"   -b cookies.txt   -d '{
    "title": "New Book",
    "author": "Author Name",
    "price": 19.99,
    "category": "fiction",
    "stock": 15,
    "rating": 4.5,
    "image_url": "https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80",
    "description": "A great book description",
    "featured": true
  }'
```

#### Update Book
```bash
curl -X PUT "http://localhost:5000/api/admin/books/1"   -H "Content-Type: application/json"   -b cookies.txt   -d '{
    "title": "Updated Title",
    "price": 24.99,
    "stock": 20
  }'
```

#### Delete Book
```bash
curl -X DELETE "http://localhost:5000/api/admin/books/1"   -b cookies.txt
```

#### Get All Orders (Admin)
```bash
curl -X GET "http://localhost:5000/api/admin/orders"   -b cookies.txt
```

#### Get Dashboard Stats
```bash
curl -X GET "http://localhost:5000/api/admin/dashboard-stats"   -b cookies.txt
```

---

## Project Structure

```
bookshop/
├── app.py                 # Flask app + API routes + admin
├── models.py              # SQLAlchemy models
├── config.py              # Configuration
├── seed.py                # Database seeding
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
├── setup.sh               # Auto setup script
├── Makefile               # Common commands
├── README.md              # This file
├── templates/
│   ├── index.html         # Shop (matches your design)
│   ├── admin_login.html   # Admin login page
│   └── admin.html         # Admin dashboard
└── static/
    ├── css/
    │   └── style.css      # Warm brown/gold styles
    └── js/
        └── app.js         # Frontend logic
```

## Database Schema

```
books
├── id, title, author, price, category
├── image_url, description, stock
├── rating, featured, created_at

cart_items
├── id, session_id, book_id, quantity

orders
├── id, session_id, total_amount, status
├── payment_method, customer_name, email
├── created_at

order_items
├── id, order_id, book_id, quantity, price
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql://... | PostgreSQL connection |
| SECRET_KEY | dev-secret-key | Flask session key |
| ADMIN_USERNAME | admin | Admin login |
| ADMIN_PASSWORD | admin123 | Admin password |

## Makefile Commands

```bash
make dev      # Setup DB, seed, run
make seed     # Re-seed database
make clean    # Clean cache
```

## Troubleshooting

**"psycopg2 not found"**
```bash
# macOS
brew install postgresql

# Ubuntu
sudo apt-get install libpq-dev
```

**"Connection refused"**
- Start PostgreSQL: `brew services start postgresql` or `sudo systemctl start postgresql`
- Check `.env` DATABASE_URL matches your credentials

## License

MIT
