from datetime import date, timedelta
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(
    title="Public Library API",
    description="A REST API for managing library operations",
    version="1.0.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory database
db = {
    "books": [],
    "patrons": [],
    "checkouts": []
}

# ----------- Models -----------
class BookCreate(BaseModel):
    title: str = Field(..., example="The Great Gatsby")
    author: str = Field(..., example="F. Scott Fitzgerald")
    isbn: str = Field(..., example="9780743273565")
    publication_year: int = Field(..., example=1925)
    genre: str = Field(..., example="Classic Literature")

class Book(BookCreate):
    id: UUID
    available: bool = True

class PatronCreate(BaseModel):
    name: str = Field(..., example="John Doe")
    email: str = Field(..., example="john@example.com")
    phone: Optional[str] = Field(None, example="555-0100")

class Patron(PatronCreate):
    id: UUID
    active: bool = True

class Checkout(BaseModel):
    book_id: UUID
    patron_id: UUID
    checkout_date: date
    due_date: date
    returned: bool = False

class CheckoutCreate(BaseModel):
    book_id: UUID
    patron_id: UUID

# ----------- Helper Functions -----------
def find_book(book_id: UUID):
    for book in db["books"]:
        if book.id == book_id:
            return book
    return None

def find_patron(patron_id: UUID):
    for patron in db["patrons"]:
        if patron.id == patron_id:
            return patron
    return None

def find_active_checkout(book_id: UUID):
    for checkout in db["checkouts"]:
        if checkout.book_id == book_id and not checkout.returned:
            return checkout
    return None

# ----------- Book Endpoints -----------
@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED)
def add_book(book_data: BookCreate):
    """Add a new book to the library"""
    book = Book(
        id=uuid4(),
        **book_data.dict(),
        available=True
    )
    db["books"].append(book)
    return book

@app.get("/books", response_model=List[Book])
def list_books(available: Optional[bool] = None):
    """List all books, optionally filtered by availability"""
    if available is not None:
        return [b for b in db["books"] if b.available == available]
    return db["books"]

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: UUID):
    """Get details about a specific book"""
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: UUID, book_data: BookCreate):
    """Update book information"""
    book = find_book(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Update book fields
    for key, value in book_data.dict().items():
        setattr(book, key, value)
    return book

@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: UUID):
    """Remove a book from the library"""
    global db
    initial_count = len(db["books"])
    db["books"] = [b for b in db["books"] if b.id != book_id]
    if len(db["books"]) == initial_count:
        raise HTTPException(status_code=404, detail="Book not found")

# ----------- Patron Endpoints -----------
@app.post("/patrons", response_model=Patron, status_code=status.HTTP_201_CREATED)
def add_patron(patron_data: PatronCreate):
    """Register a new library patron"""
    patron = Patron(
        id=uuid4(),
        **patron_data.dict(),
        active=True
    )
    db["patrons"].append(patron)
    return patron

@app.get("/patrons", response_model=List[Patron])
def list_patrons(active: Optional[bool] = None):
    """List all patrons, optionally filtered by status"""
    if active is not None:
        return [p for p in db["patrons"] if p.active == active]
    return db["patrons"]

@app.get("/patrons/{patron_id}", response_model=Patron)
def get_patron(patron_id: UUID):
    """Get details about a specific patron"""
    patron = find_patron(patron_id)
    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")
    return patron

# ----------- Checkout Endpoints -----------
@app.post("/checkouts", response_model=Checkout, status_code=status.HTTP_201_CREATED)
def checkout_book(checkout_data: CheckoutCreate):
    """Check out a book to a patron"""
    book = find_book(checkout_data.book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    patron = find_patron(checkout_data.patron_id)
    if not patron:
        raise HTTPException(status_code=404, detail="Patron not found")
    
    if not patron.active:
        raise HTTPException(status_code=400, detail="Patron account is inactive")
    
    if not book.available:
        raise HTTPException(status_code=400, detail="Book is already checked out")
    
    checkout = Checkout(
        book_id=book.id,
        patron_id=patron.id,
        checkout_date=date.today(),
        due_date=date.today() + timedelta(days=14)
    )
    
    book.available = False
    db["checkouts"].append(checkout)
    return checkout

@app.post("/checkouts/{book_id}/return", response_model=Checkout)
def return_book(book_id: UUID):
    """Return a checked-out book"""
    checkout = find_active_checkout(book_id)
    if not checkout:
        raise HTTPException(status_code=404, detail="No active checkout found for this book")
    
    book = find_book(book_id)
    if book:
        book.available = True
    
    checkout.returned = True
    return checkout

@app.get("/checkouts", response_model=List[Checkout])
def list_checkouts(returned: Optional[bool] = None):
    """List all checkouts, optionally filtered by return status"""
    if returned is not None:
        return [c for c in db["checkouts"] if c.returned == returned]
    return db["checkouts"]

# ----------- Search Endpoints -----------
@app.get("/search/books", response_model=List[Book])
def search_books(
    title: Optional[str] = None,
    author: Optional[str] = None,
    genre: Optional[str] = None
):
    """Search books by title, author, or genre"""
    results = db["books"]
    
    if title:
        results = [b for b in results if title.lower() in b.title.lower()]
    if author:
        results = [b for b in results if author.lower() in b.author.lower()]
    if genre:
        results = [b for b in results if genre.lower() == b.genre.lower()]
    
    return results

@app.get("/search/patrons", response_model=List[Patron])
def search_patrons(name: Optional[str] = None):
    """Search patrons by name"""
    if not name:
        return []
    return [p for p in db["patrons"] if name.lower() in p.name.lower()]
