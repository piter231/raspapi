# 🐸 Public Library API Docs 

Welcome to Frog Library! 🎉 A simple API to manage books, users, and book loans.  
**Live URL**: http://frog01.mikr.us:40762  

---

## 📘 Book Operations

### Add New Book
```bash
POST /books
```
**Example**:  
```json
{
  "title": "Harry Potter",
  "author": "J.K. Rowling",
  "isbn": "123456",
  "publication_year": 1997,
  "genre": "Fantasy"
}
```

### List All Books
```bash
GET /books
```
Filter by availability:  
`GET /books?available=true`

### Search Books 🔍
```bash
GET /search/books?title=potter&author=rowling&genre=fantasy
```

---

## 👥 Patron (User) Management

### Register New User
```bash
POST /patrons
```
**Example**:  
```json
{
  "name": "Alice Frog",
  "email": "alice@froglib.com",
  "phone": "555-1234"
}
```

### Find Users
```bash
GET /search/patrons?name=alice
```

---

## 🔄 Borrow & Return Books

### Borrow a Book 📥
```bash
POST /checkouts
```
**Example**:  
```json
{
  "book_id": "BOOK-UUID-HERE",
  "patron_id": "USER-UUID-HERE"
}
```
*Books auto-return in 14 days! 📅*

### Return a Book 📤
```bash
POST /checkouts/{book_id}/return
```

### View All Loans
```bash
GET /checkouts
```

---

## ❗ Rules
1. Only **active users** can borrow books
2. Books marked as `available: false` are already borrowed
3. Return books to make them available again ♻️

---

## 🛠️ Troubleshooting

Common errors:  
- 🔴 **404 Error**: Book/user not found (check UUIDs)
- 🔴 **400 Error**: Trying to borrow unavailable book
- 🔴 **400 Error**: Inactive user trying to borrow

Always check:  
1. UUIDs are correct
2. User is `active: true`
3. Book is `available: true`

---

## 🐍 For Developers

**Tech stack**:  
- FastAPI (Python)
- Runs on Uvicorn server

**Code example**:  
```python
# Get all fantasy books
import requests
response = requests.get("http://frog01.mikr.us:40762/search/books?genre=fantasy")
print(response.json())
```
