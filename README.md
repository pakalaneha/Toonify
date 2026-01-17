# Toonify

**AI-Based Image Transformation Tool for Cartoon Effects**

Toonify is a Python-based application that transforms images into cartoon-style and artistic effects using AI and image processing techniques. The project provides multiple visual filters and an interactive web interface built with Streamlit, allowing users to easily upload images and view transformed results in real time.

This project focuses on modular design, clean structure, and practical usage of image processing concepts.

---

## Features
- AI-powered image cartoon transformation
- Multiple artistic filters:
  - Anime
  - Watercolor
  - Oil painting
  - Low-poly
  - Tiled mosaic
- Streamlit-based interactive web interface
- Modular and extensible codebase

---

## Project Structure

```
.
├── .env.example
├── README.md
├── anime_filter.py
├── app.py
├── auth.py
├── config.toml
├── database.py
├── image_processor.py
├── low_poly.py
├── oil.py
├── requirements.txt
├── tiled_mosaic.py
└── watercolor_filter.py
```


---

## Installation

1. Clone the repository:
```bash
git clone https://github.com/pakalaneha/Toonify.git
cd Toonify
```
2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
```
3. Install the required dependencies:
```bash
pip install -r requirements.txt
```
4. Set up environment variables:
```bash
cp .env.example .env
```
Update the .env file with your database credentials.
## Running the Application
Start the Streamlit app using:
```bash
streamlit run app.py
```

The application follows a simple and structured flow.

Users must first **sign up or log in** to access the platform. Authentication ensures that only registered users can upload images and use the transformation features.

After logging in:
- Users can upload an image
- Choose a cartoon or artistic filter
- Each image transformation consumes **one credit**

The application follows a **credit-based model** to simulate real-world usage. Users purchase a fixed number of credits through a demo payment system. For every successful image transformation, **one credit is automatically deducted** from the user’s account.

If the user runs out of credits, they are prompted to purchase additional credits before continuing. This approach demonstrates how paid access and usage limits can be integrated into an AI-based image transformation application.




