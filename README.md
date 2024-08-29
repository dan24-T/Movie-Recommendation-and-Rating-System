Movie Recommendation and Rating System
Overview

The Movie Recommendation and Rating System is a web application designed to provide users with personalized movie recommendations based on their viewing history, ratings, and reviews. It leverages content-based filtering techniques to suggest movies similar to those the user has rated or searched for. Additionally, the system includes features for users to review movies, upvote or downvote reviews, and manage movie studios. Administrators have the ability to manage users, studios, and review system logs.
Features
User Functionality

    User Authentication: Secure login and signup system with password hashing.
    Personalized Recommendations: Movies recommended based on user ratings and content features like genres and overview.
    Movie Search: A dynamic search bar that provides movie suggestions as you type.
    Review and Rating: Users can add, edit, and delete their movie reviews. They can also upvote or downvote other users' reviews.
    Profile and Movie History: Users can view their movie history and personalized recommendations on their profile.

Studio Management

    Studio Creation: Users can create and manage their movie studios.
    Movie Management: Studio owners can add, edit, and delete movies associated with their studio.
    Studio Dashboard: A dedicated dashboard for studio owners to manage their movies and studio details.

Admin Functionality

    User Management: Administrators can manage users, including promoting users to admins or deleting accounts.
    Studio Verification: Admins can verify studios created by users.
    Movie Management: Admins have full control over all movies in the database, with options to add, edit, or delete.
    System Logs: A logging system to track various activities within the system for monitoring and auditing purposes.

Technology Stack

    Backend: Python (Flask)
    Database: SQLite
    Frontend: HTML, CSS, JavaScript (with Jinja2 templating)
    Recommendation System: Pandas, Scikit-learn (TF-IDF and content-based filtering)

