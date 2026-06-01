from app import app
from models import db, Book

def seed_database():
    with app.app_context():
        db.drop_all()
        db.create_all()

        books_data = [
            {
                'title': 'The Great Gatsby',
                'author': 'F. Scott Fitzgerald',
                'price': 14.99,
                'category': 'classic',
                'image_url': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?auto=format&fit=crop&w=600&q=80',
                'description': 'A story of the fabulously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan.',
                'stock': 15,
                'rating': 4.5,
                'featured': True
            },
            {
                'title': 'To Kill a Mockingbird',
                'author': 'Harper Lee',
                'price': 12.99,
                'category': 'classic',
                'image_url': 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=600&q=80',
                'description': 'A gripping, heart-wrenching tale of a young girl confronting prejudice and injustice.',
                'stock': 20,
                'rating': 4.8,
                'featured': True
            },
            {
                'title': 'Atomic Habits',
                'author': 'James Clear',
                'price': 16.99,
                'category': 'non-fiction',
                'image_url': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?auto=format&fit=crop&w=600&q=80',
                'description': 'Transform your life with tiny changes in behavior that lead to remarkable results.',
                'stock': 30,
                'rating': 4.9,
                'featured': True
            },
            {
                'title': 'The Design of Everyday Things',
                'author': 'Don Norman',
                'price': 18.99,
                'category': 'design',
                'image_url': 'https://images.unsplash.com/photo-1507842217343-583bb7270b66?auto=format&fit=crop&w=600&q=80',
                'description': 'The ultimate guide to human-centered design and usability.',
                'stock': 12,
                'rating': 4.7,
                'featured': False
            },
            {
                'title': 'The Midnight Library',
                'author': 'Matt Haig',
                'price': 15.99,
                'category': 'fiction',
                'image_url': 'https://images.unsplash.com/photo-1495446815901-a7297e633e8d?auto=format&fit=crop&w=600&q=80',
                'description': 'Between life and death there is a library with infinite possibilities.',
                'stock': 18,
                'rating': 4.3,
                'featured': True
            },
            {
                'title': 'Sapiens: A Brief History',
                'author': 'Yuval Noah Harari',
                'price': 19.99,
                'category': 'non-fiction',
                'image_url': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?auto=format&fit=crop&w=600&q=80',
                'description': 'A brief history of humankind, from the Stone Age to the Silicon Age.',
                'stock': 25,
                'rating': 4.6,
                'featured': False
            },
            {
                'title': 'The Alchemist',
                'author': 'Paulo Coelho',
                'price': 13.99,
                'category': 'fiction',
                'image_url': 'https://images.unsplash.com/photo-1720465593250-5f1faa11245b?auto=format&fit=crop&w=600&q=80',
                'description': 'A magical story about following your dreams and listening to your heart.',
                'stock': 22,
                'rating': 4.4,
                'featured': False
            },
            {
                'title': 'Thinking with Type',
                'author': 'Ellen Lupton',
                'price': 21.99,
                'category': 'design',
                'image_url': 'https://images.unsplash.com/photo-1555252333-9f8e92e65df4?auto=format&fit=crop&w=600&q=80',
                'description': 'The definitive guide to using typography in visual communication.',
                'stock': 10,
                'rating': 4.5,
                'featured': False
            },
            {
                'title': 'Dune',
                'author': 'Frank Herbert',
                'price': 17.99,
                'category': 'fiction',
                'image_url': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?auto=format&fit=crop&w=600&q=80',
                'description': 'Set on the desert planet Arrakis, the epic story of Paul Atreides.',
                'stock': 14,
                'rating': 4.7,
                'featured': True
            },
            {
                'title': 'Educated',
                'author': 'Tara Westover',
                'price': 15.49,
                'category': 'non-fiction',
                'image_url': 'https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?auto=format&fit=crop&w=600&q=80',
                'description': 'A memoir about a young girl who leaves her survivalist family to pursue education.',
                'stock': 16,
                'rating': 4.6,
                'featured': False
            },
            {
                'title': '1984',
                'author': 'George Orwell',
                'price': 11.99,
                'category': 'classic',
                'image_url': 'https://images.unsplash.com/photo-1532012197267-da84d127e765?auto=format&fit=crop&w=600&q=80',
                'description': 'A dystopian masterpiece about totalitarianism and surveillance.',
                'stock': 28,
                'rating': 4.9,
                'featured': True
            },
            {
                'title': 'Grid Systems',
                'author': 'Josef Müller-Brockmann',
                'price': 24.99,
                'category': 'design',
                'image_url': 'https://images.unsplash.com/photo-1561070791-2526d30994b5?auto=format&fit=crop&w=600&q=80',
                'description': 'A classic manual for understanding and using grid systems in graphic design.',
                'stock': 8,
                'rating': 4.4,
                'featured': False
            }
        ]

        for book_data in books_data:
            book = Book(**book_data)
            db.session.add(book)

        db.session.commit()
        print(f"✅ Seeded {len(books_data)} books successfully!")

if __name__ == '__main__':
    seed_database()
