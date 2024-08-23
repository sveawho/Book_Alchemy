import os
from random import choice

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError

from data_models import db, Author, Book

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Get the directory of the current script (app.py)
basedir = os.path.abspath(os.path.dirname(__file__))

# Set up the database URI using a relative path
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(basedir, 'data', 'library.sqlite')}"


# Initialize database and migration
db.init_app(app)
migrate = Migrate(app, db)  # Initialize Flask-Migrate

# Create database tables if they don't exist
with app.app_context():
    db.create_all()


@app.route('/')
def home():
    """
    Home page that displays a list of books with sorting and search functionality.
    """
    # Get sorting and search parameters from the request
    sort_by = request.args.get('sort_by', 'title')
    sort_order = request.args.get('sort_order', 'asc')
    search_query = request.args.get('search_query', '')

    # Create a query to fetch books and their corresponding authors
    query = db.session.query(Book).join(Author)

    # Filter the query based on the search query
    if search_query:
        query = query.filter(
            (Book.title.ilike(f'%{search_query}%')) |
            (Author.name.ilike(f'%{search_query}%'))
        )

    # Determine the column to sort by
    sort_columns = {
        'title': Book.title,
        'author': Author.name,
        'publication_year': Book.publication_year,
        'rating': Book.rating,
    }
    sort_column = sort_columns.get(sort_by, Book.title)

    # Apply sorting order (ascending or descending)
    sort_column = sort_column.asc() if sort_order == 'asc' else sort_column.desc()

    # Paginate the results (10 books per page)
    page = request.args.get('page', 1, type=int)
    per_page = 10
    paginated_books = query.order_by(sort_column).paginate(page=page, per_page=per_page, error_out=False)

    # Determine if no books were found
    no_books_found = not paginated_books.items

    return render_template(
        'home.html',
        books=paginated_books.items,
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=search_query,
        no_books_found=no_books_found,
        pagination=paginated_books
    )


@app.route('/add_author', methods=['GET', 'POST'])
def add_author():
    """
    Page for adding a new author to the database.
    """
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        birth_year_str = request.form.get('birth_year')
        death_year_str = request.form.get('death_year')

        birth_year = int(birth_year_str) if birth_year_str else None
        death_year = int(death_year_str) if death_year_str else None

        # Check if the author already exists
        existing_author = Author.query.filter_by(name=name).first()

        if existing_author:
            flash("Sorry! The author already exists in your database.", "error")
        else:
            # Create a new author
            new_author = Author(name=name, birth_year=birth_year, death_year=death_year)
            try:
                db.session.add(new_author)
                db.session.commit()
                flash("Author has been successfully added to your database!", "success")
            except IntegrityError:
                db.session.rollback()
                flash("The author has to be born... somehow ;D", "error")

    return render_template('add_author.html')


@app.route('/add_book', methods=['GET', 'POST'])
def add_book():
    """
    Page for adding a new book to the database.
    """
    success_message = None
    error_message = None
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')
        rating_str = request.form.get('rating')
        summary = request.form.get('summary')

        rating = int(rating_str) if rating_str else None

        # Create a new book
        new_book = Book(
            title=title,
            isbn=isbn,
            publication_year=publication_year,
            author_id=author_id,
            rating=rating,
            summary=summary
        )

        try:
            db.session.add(new_book)
            db.session.commit()
            flash("Book has been successfully added to your database!!", "success")
        except IntegrityError:
            db.session.rollback()
            error_message = "A book with this title or ISBN already exists in the database."
            flash(error_message, "error")
        except Exception as e:
            db.session.rollback()
            error_message = f"An error occurred: {e}"
            flash(error_message, "error")

    # Fetch all authors to populate the dropdown list in the form
    authors = Author.query.all()
    return render_template('add_book.html', authors=authors, success_message=success_message, error_message=error_message)


@app.route('/author/<int:author_id>/edit', methods=['GET', 'POST'])
def edit_author(author_id):
    """
    Page for editing an existing author.
    """
    # Fetch author by ID, 404 if not found
    author = Author.query.get_or_404(author_id)

    if request.method == 'POST':
        name = request.form.get('name')
        birth_year_str = request.form.get('birth_year')
        death_year_str = request.form.get('death_year')

        # Convert birth_year and death_year to integer if they are not empty
        birth_year = int(birth_year_str) if birth_year_str and birth_year_str.isdigit() else None
        death_year = int(death_year_str) if death_year_str and death_year_str.isdigit() else None

        # Update the author's information if there are changes
        updated = False
        if author.name != name:
            author.name = name
            updated = True
        if (author.birth_year is None and birth_year is not None) or (author.birth_year != birth_year):
            author.birth_year = birth_year
            updated = True
        if (author.death_year is None and death_year is not None) or (author.death_year != death_year):
            author.death_year = death_year
            updated = True

        if updated:
            try:
                db.session.commit()
                flash("Author updated successfully!", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {e}", "error")
        else:
            flash("No changes detected.", "info")

        return redirect(url_for('author_detail', author_id=author.id))

    return render_template('edit_author.html', author=author)


@app.route('/book/<int:book_id>/edit', methods=['GET', 'POST'])
def edit_book(book_id):
    """
    Page for editing an existing book.
    """
    # Fetch book by ID, 404 if not found
    book = Book.query.get_or_404(book_id)

    if request.method == 'POST':
        # Get form data
        title = request.form.get('title')
        isbn = request.form.get('isbn')
        publication_year = request.form.get('publication_year')
        author_id = request.form.get('author_id')
        rating_str = request.form.get('rating')
        summary = request.form.get('summary')

        # Update the book's information if there are changes
        updated = False
        try:
            if book.title != title:
                book.title = title
                updated = True
            if book.isbn != isbn:
                book.isbn = isbn
                updated = True
            if book.publication_year != int(publication_year):
                book.publication_year = int(publication_year)
                updated = True
            if book.author_id != int(author_id):
                book.author_id = int(author_id)
                updated = True
            if (book.rating is None and rating_str) or (book.rating != int(rating_str)):
                book.rating = int(rating_str) if rating_str else None
                updated = True
            if book.summary != summary:
                book.summary = summary
                updated = True

            if updated:
                db.session.commit()
                flash("Book updated successfully!", "success")
            else:
                flash("No changes detected.", "info")

        except Exception as e:
            db.session.rollback()
            print(f"Exception details: {e}")  # Print details to console or log
            flash(f"An error occurred: {e}", "error")

        return redirect(url_for('book_detail', book_id=book.id))

    # Fetch all authors to populate the dropdown list in the form
    authors = Author.query.all()
    return render_template('edit_book.html', book=book, authors=authors)


@app.route('/book/<int:book_id>/delete', methods=['POST'])
def delete_book(book_id):
    """
    Handle the deletion of a book. If the author has no other books, delete the author as well.
    """
    book = Book.query.get_or_404(book_id)
    author = book.author

    try:
        db.session.delete(book)
        db.session.commit()

        # If the author has no more books, delete the author
        if not author.books:
            db.session.delete(author)
            db.session.commit()

        flash(f"Book '{book.title}' has been deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "error")

    return redirect(url_for('home'))

@app.route('/author/<int:author_id>/delete', methods=['POST'])
def delete_author(author_id):
    """
    Handle the deletion of an author.
    """
    author = Author.query.get_or_404(author_id)

    try:
        db.session.delete(author)
        db.session.commit()
        flash(f"Author '{author.name}' has been deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"An error occurred: {e}", "error")

    return redirect(url_for('home'))

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    """
    Page to display details of a specific book.
    """
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/author/<int:author_id>')
def author_detail(author_id):
    """
    Page to display details of a specific author and their books.
    """
    author = Author.query.get_or_404(author_id)
    books = Book.query.filter_by(author_id=author_id).all()
    return render_template('author_detail.html', author=author, books=books)


@app.route('/suggest_book')
def suggest_book():
    """
    Suggest a high-rated book to the user.
    """
    high_rated_books = Book.query.filter(Book.rating > 7).all()
    suggested_book = choice(high_rated_books) if high_rated_books else None
    return render_template('suggest_book.html', suggested_book=suggested_book)


if __name__ == '__main__':
    app.run(debug=True)
