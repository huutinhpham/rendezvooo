Rendezvooo
==========

## Description

collaborative music web application that uses YouTube API to create playlists. Users are able to collaboratively build and share playlists by using youtube URLs. Webapp includes an upvote system, where songs can be played and sorted by likes.

## Objective

To improve on all aspects of fullstack development: UI/UX design, security/authentication, backend design. To build an application from the ground without any frameworks to understand every aspects within a webapp.

## Languages

* **javaScript**
* **Python**
* **HTML**
* **CSS**

## Tools

* **Flask**
* **Postgresql**
* **jQuery**
* **Ajax**
* **YouTube API**
* **Bleach**
* **passlib**

## Roadblocks/Problems

* YouTube API has many legal and copyright issues that go along with it. Many videos are not able to play outside of YouTube domain. This proved to be outside of my control, and negatively affected U/X since a good number of songs are not available to build a playlist with.

* Getting users for the application is difficult, people have little incentive to use a new app especially it's a collaborative application with little users to start with. This is neccessary however, for feedbacks and new feature ideas.

## Successes

* By forcing every interactions between the view and the backend goes through javaScript, I was able to send GET/POST requests (ajax) to the app API without refreshing the page (unlike html forms). This led to a major U/X improvement, eliminating the need to refresh playing music.

* By spending the time to refactor the code after every few features I was able to keep the code clean and readable. This proved to save time as the application gets bigger.

## Future Improvements

* There are many requests to the database, and majority of them requires the database to be sorted. Views/cache can be made to optimize these requests.

## Credits

Aside from libraries that were used in the application, all code were writen by me.


