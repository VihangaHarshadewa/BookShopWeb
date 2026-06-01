const API_BASE = '';

const app = {
    state: {
        books: [],
        cart: { items: [], total: 0, count: 0 },
        currentFilter: 'all'
    },

    init() {
        this.loadBooks();
        this.loadCart();
        this.setupSearch();
        this.setupScroll();
    },

    // API Helper
    async api(endpoint, options = {}) {
        try {
            const res = await fetch(`${API_BASE}${endpoint}`, {
                headers: { 'Content-Type': 'application/json' },
                ...options,
                body: options.body ? JSON.stringify(options.body) : undefined
            });
            if (!res.ok) throw new Error(await res.text());
            return await res.json();
        } catch (err) {
            this.showToast(err.message || 'Network error', 'error');
            throw err;
        }
    },

    // Toast
    showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
        toast.innerHTML = `<i class="fas ${icons[type]}"></i> <span>${message}</span>`;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 3000);
    },

    // Books
    async loadBooks() {
        try {
            const data = await this.api('/api/books');
            this.state.books = data.books;
            this.renderBooks();
        } catch (err) {
            console.error('Failed to load books:', err);
        }
    },

    renderBooks() {
        const grid = document.getElementById('booksGrid');
        const books = this.state.currentFilter === 'all' 
            ? this.state.books 
            : this.state.books.filter(b => b.category === this.state.currentFilter);

        if (books.length === 0) {
            grid.innerHTML = '<div class="empty-cart" style="grid-column: 1/-1;"><i class="fas fa-search"></i><p>No books found</p></div>';
            return;
        }

        grid.innerHTML = books.map(book => `
            <div class="book-card">
                <div style="overflow: hidden;">
                    <img src="${book.image_url}" alt="${book.title}" class="book-image" loading="lazy">
                </div>
                <div class="book-info">
                    <div class="book-category">${book.category}</div>
                    <div class="book-title">${book.title}</div>
                    <div class="book-author">by ${book.author}</div>
                    <div class="book-footer">
                        <div class="book-price">$${book.price.toFixed(2)}</div>
                        <button class="add-to-cart" onclick="app.addToCart(${book.id})" title="Add to cart">
                            <i class="fas fa-plus"></i>
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    },

    filterBooks(category) {
        this.state.currentFilter = category;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.category === category);
        });
        this.renderBooks();
    },

    setupSearch() {
        // Simple client-side search via URL params
        const searchInput = document.createElement('input');
        searchInput.type = 'text';
        searchInput.placeholder = 'Search...';
        searchInput.style.cssText = 'position:fixed;top:90px;right:24px;z-index:999;padding:8px 16px;border:2px solid var(--border);border-radius:50px;background:white;width:200px;font-family:Inter;display:none;';
        document.body.appendChild(searchInput);

        let timeout;
        searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(async () => {
                const query = e.target.value.trim();
                try {
                    const data = await this.api(`/api/books?search=${encodeURIComponent(query)}`);
                    this.state.books = data.books;
                    this.renderBooks();
                } catch (err) {
                    console.error('Search failed:', err);
                }
            }, 300);
        });
    },

    // Cart
    async loadCart() {
        try {
            const cart = await this.api('/api/cart');
            this.state.cart = cart;
            this.updateCartUI();
        } catch (err) {
            console.error('Failed to load cart:', err);
        }
    },

    async addToCart(bookId, qty = 1) {
        try {
            await this.api('/api/cart', {
                method: 'POST',
                body: { book_id: bookId, quantity: qty }
            });
            await this.loadCart();
            this.showToast('Added to cart!', 'success');
            this.toggleCart();
        } catch (err) {
            console.error('Add to cart failed:', err);
        }
    },

    async updateCartItem(itemId, qty) {
        try {
            if (qty <= 0) {
                await this.api(`/api/cart/${itemId}`, { method: 'DELETE' });
            } else {
                await this.api(`/api/cart/${itemId}`, {
                    method: 'PUT',
                    body: { quantity: qty }
                });
            }
            await this.loadCart();
        } catch (err) {
            console.error('Update cart failed:', err);
        }
    },

    updateCartUI() {
        const badge = document.getElementById('cartCount');
        const itemsContainer = document.getElementById('cartItems');
        const footer = document.getElementById('cartFooter');
        const totalEl = document.getElementById('cartTotal');

        badge.textContent = this.state.cart.count;
        badge.style.display = this.state.cart.count > 0 ? 'flex' : 'none';

        if (this.state.cart.items.length === 0) {
            itemsContainer.innerHTML = `
                <div class="empty-cart">
                    <i class="fas fa-shopping-bag"></i>
                    <p>Your cart is empty</p>
                    <button class="btn" onclick="app.toggleCart(); app.scrollToBooks();">Start Shopping</button>
                </div>
            `;
            footer.style.display = 'none';
            return;
        }

        itemsContainer.innerHTML = this.state.cart.items.map(item => `
            <div class="cart-item">
                <img src="${item.book.image_url}" alt="${item.book.title}">
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.book.title}</div>
                    <div class="cart-item-price">$${item.book.price.toFixed(2)}</div>
                    <div class="quantity-controls">
                        <button class="qty-btn" onclick="app.updateCartItem(${item.id}, ${item.quantity - 1})">-</button>
                        <span>${item.quantity}</span>
                        <button class="qty-btn" onclick="app.updateCartItem(${item.id}, ${item.quantity + 1})">+</button>
                    </div>
                </div>
                <button class="remove-item" onclick="app.updateCartItem(${item.id}, 0)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `).join('');

        footer.style.display = 'block';
        totalEl.textContent = '$' + this.state.cart.total.toFixed(2);
        document.getElementById('payAmount').textContent = '$' + this.state.cart.total.toFixed(2);
    },

    toggleCart() {
        document.getElementById('cartOverlay').classList.toggle('active');
        document.getElementById('cartSidebar').classList.toggle('active');
    },

    clearCart() {
        this.state.cart = { items: [], total: 0, count: 0 };
        this.updateCartUI();
    },

    // Payment
    openPayment() {
        if (this.state.cart.items.length === 0) {
            this.showToast('Your cart is empty!', 'error');
            return;
        }
        document.getElementById('paymentModal').classList.add('active');
        this.toggleCart();
    },

    closePayment() {
        document.getElementById('paymentModal').classList.remove('active');
        document.getElementById('paymentForm').style.display = 'block';
        document.getElementById('successMessage').classList.remove('active');

        setTimeout(() => {
            document.getElementById('cardNumber').value = '';
            document.getElementById('cardHolder').value = '';
            document.getElementById('expiryDate').value = '';
            document.getElementById('cvv').value = '';
            this.updateCardDisplay();
            // Reset card style
            document.getElementById('creditCard').className = 'credit-card';
            document.getElementById('cardLogo').innerHTML = '<i class="fab fa-cc-visa"></i>';
            document.querySelectorAll('.card-type').forEach(t => t.classList.remove('active'));
            document.querySelector('.card-type').classList.add('active');
        }, 300);
    },

    formatCardNumber(input) {
        let value = input.value.replace(/\D/g, '').substring(0, 16);
        const parts = value.match(/.{1,4}/g) || [];
        input.value = parts.join(' ');
        this.updateCardDisplay();
        this.detectCardBrand(value);
    },

    detectCardBrand(number) {
        const card = document.getElementById('creditCard');
        const logo = document.getElementById('cardLogo');
        card.className = 'credit-card';

        if (number.startsWith('4')) {
            logo.innerHTML = '<i class="fab fa-cc-visa"></i>';
        } else if (/^5[1-5]/.test(number)) {
            card.classList.add('gold');
            logo.innerHTML = '<i class="fab fa-cc-mastercard"></i>';
        } else if (/^3[47]/.test(number)) {
            card.classList.add('platinum');
            logo.innerHTML = '<i class="fab fa-cc-amex"></i>';
        } else {
            logo.innerHTML = '<i class="fab fa-cc-visa"></i>';
        }
    },

    formatExpiry(input) {
        let value = input.value.replace(/\D/g, '').substring(0, 4);
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        input.value = value;
        this.updateCardDisplay();
    },

    updateCardDisplay() {
        const number = document.getElementById('cardNumber').value || '#### #### #### ####';
        const holder = document.getElementById('cardHolder').value || 'YOUR NAME';
        const expiry = document.getElementById('expiryDate').value || 'MM/YY';

        document.getElementById('displayNumber').textContent = number;
        document.getElementById('displayHolder').textContent = holder.toUpperCase();
        document.getElementById('displayExpiry').textContent = expiry;
    },

    selectCardType(type, element) {
        document.querySelectorAll('.card-type').forEach(el => el.classList.remove('active'));
        element.classList.add('active');

        const card = document.getElementById('creditCard');
        const logo = document.getElementById('cardLogo');
        card.className = 'credit-card';

        switch(type) {
            case 'visa':
                logo.innerHTML = '<i class="fab fa-cc-visa"></i>';
                break;
            case 'mastercard':
                card.classList.add('gold');
                logo.innerHTML = '<i class="fab fa-cc-mastercard"></i>';
                break;
            case 'amex':
                card.classList.add('platinum');
                logo.innerHTML = '<i class="fab fa-cc-amex"></i>';
                break;
        }
    },

    async processPayment(e) {
        e.preventDefault();
        const btn = e.target.querySelector('.pay-btn');
        const originalHTML = btn.innerHTML;

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';

        try {
            await this.api('/api/checkout', {
                method: 'POST',
                body: {
                    payment_method: 'card',
                    customer_name: document.getElementById('cardHolder').value || 'Guest'
                }
            });

            document.getElementById('paymentForm').style.display = 'none';
            document.getElementById('successMessage').classList.add('active');
            this.showToast('Payment successful!', 'success');
        } catch (err) {
            btn.disabled = false;
            btn.innerHTML = originalHTML;
        }
    },

    scrollToBooks() {
        document.getElementById('books').scrollIntoView({ behavior: 'smooth' });
    },

    setupScroll() {
        window.addEventListener('scroll', () => {
            const nav = document.querySelector('nav');
            if (window.scrollY > 50) {
                nav.style.boxShadow = '0 2px 20px rgba(0,0,0,0.1)';
            } else {
                nav.style.boxShadow = 'none';
            }
        });
    }
};

// Smooth scroll for nav links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    });
});

// Initialize
document.addEventListener('DOMContentLoaded', () => app.init());
