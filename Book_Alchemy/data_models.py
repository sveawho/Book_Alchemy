from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Defining Author model
class Author(db.Model):
    __tablename__ = 'authors'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    birth_year = db.Column(db.Integer, nullable=False)
    death_year = db.Column(db.Integer, nullable=True)
    books = db.relationship('Book', backref='author', lazy=True, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Author(id={self.id}, name='{self.name}')>"

    def __str__(self):
        return f"Author: {self.name} (Born: {self.birth_year}, Died: {self.death_year})"


# Defining Book model
class Book(db.Model):
    __tablename__ = 'books'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn = db.Column(db.String(13), unique=True, nullable=False)
    title = db.Column(db.String(200),unique=True, nullable=False)
    publication_year = db.Column(db.Integer, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=True)
    summary = db.Column(db.Text, nullable=True)  # Adding summary field

    def __repr__(self):
        return f"<Book(id={self.id}, title='{self.title}', author_id={self.author_id})>"

    def __str__(self):
        return f"Book: {self.title} (ISBN: {self.isbn}, Year: {self.publication_year})"