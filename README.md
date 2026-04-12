# Reasonable Or Not

Reasonable Or Not is a refreshed Django demo project for mobile phone recommendation. It started as an earlier coursework-style project, and this upgrade keeps the original idea while improving the product flow, visual presentation, and repository quality so it can better represent my development ability on GitHub.

## Project Overview

This project helps users describe what kind of phone they want, then recommends the most suitable device from a small iPhone dataset. The upgrade focuses on two goals:

- preserve the original recommendation idea and scoring concept
- turn the project into a cleaner, more portfolio-ready web application

## What I Upgraded

### Product Experience

- redesigned the homepage into a clearer product-style landing page
- rebuilt login and registration pages with a unified visual system
- improved the requirement form so user preferences are easier to understand and submit
- created a recommendation result page that highlights the best match and nearby alternatives
- added a methodology page to explain the recommendation logic in a presentation-friendly way

### Engineering Improvements

- reorganized the Django views into a more maintainable structure
- removed the older one-off output style and replaced it with template-driven result rendering
- added a weighted recommendation model based on budget, performance, charging, screen size, storage, battery, and camera preferences
- improved route naming and session-based login flow
- fixed template directory configuration for a more standard Django setup
- added project documentation and repository hygiene files

## Tech Stack

- Python
- Django
- HTML templates
- CSS
- SQLite

## Recommendation Logic

The recommendation engine uses a weighted scoring approach:

1. Read the user's target profile from the requirement form.
2. Compare each phone against the selected budget and capability preferences.
3. Calculate closeness scores for each dimension.
4. Apply weights to important factors such as budget and storage.
5. Rank all phones by total match score.
6. Return the strongest recommendation plus several alternatives.

This makes the project easy to extend later with:

- larger datasets
- more phone brands
- user history
- saved comparisons
- visualization of score breakdowns

## Pages

- `/` or `/user/index`: project landing page
- `/user/login`: sign in page
- `/user/register`: account creation page
- `/user/requirement`: phone preference form
- `/user/recommend`: recommendation result page
- `/user/result`: methodology and value ranking page

## Local Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Run migrations:

```bash
python manage.py migrate
```

4. Start the development server:

```bash
python manage.py runserver
```

5. Open:

```text
http://127.0.0.1:8000/
```

## Why This Project Is Useful In My Portfolio

This project demonstrates that I can:

- refactor and upgrade an existing codebase instead of only creating new ones
- improve both the interface and the back-end logic
- turn an early prototype into a more complete product demo
- explain implementation ideas clearly through documentation
- prepare a project for GitHub presentation and technical discussion

## Future Directions

- connect the recommendation system to a richer database
- add admin-side device management
- support more brands and more detailed filters
- store recommendation history per user
- add charts or explanation views for scoring transparency
