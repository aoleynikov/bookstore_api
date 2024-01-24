# Book store side hustle API

### A foreword

This is an implementation of a test project to showcase my development skills. This code uses a boilerplate I have collected during my career in software development service industry for this exact purpose - quickly building backend APIs while keeping them scalable and easy to change. The code is in python because my boilerplate is in python. However, I am capable of producing code that obeys SOLID principles and other OOP best practices in other popular languages as well (Ruby, TypeScript, C#, Java). 

In order to run the tests, just run `make unit && make integration`, the Makefile will take care of the rest. You can also do a `make up` and go to `http://localhost:8000/swagger/` to take a look at the API structure in a convenient place. Although, I wouldn't try actually calling anything from there, there are integration tests for it.

# Task

The focus was on implementation speed and simplicity. First of all, the task specifically mentioned this piece of software being rudimentary. Second, to my knowledge, book trading doesn't seem like a prosperous market at the moment, so the owner would probably appreciate her new tracking system being fast and cheap.

The API features standard sign in/sign up user management and uses JWT tokens. Inventory is managed using the /inventory endpoint. Inventory alerts are optional and added on top of exising inventory pieces. Every time book's quantity goes below the alert value (or alert value is decreased), a call is made to the notifications service with the iventory item causing the notification this particular time (`most_recent`) as well as ALL inventory with alerts tripped (`other`), becuase it's convenient to have the entire list in one place.

If updating inventory takes too long, we can introduce a celery job (+ rabbitmq in docker-compose.yml) to collect the notification service payload and run the heavy stuff in the background. However, I can't imagine a small book store having enough inventory to cause a performance problem here.

If it's possible, I'd like the notification service to also be a part of the same repository as this piece of software. This way my junior colleague and I can use the same infrastructure and keep track of each other's work. It could be that a separate service is not needed and a simple celery job would suffice.

# Notification service requirements

The notification service needs to provide the URL and accept a payload like this:
```
{
    "most_recent": {<iventory_item1>}, 
    "other": [{<inventory_item2>}, {<inventory_item3>}, ...]
}
```

InventoryItem objects are like this:
```
{
    "id": "",
    "author": "Lorem Ipsum",
    "title": "Dolor sit amet",
    "price": 10000,
    "quantity": 10,
    "alert": {"quantity": 5},
    "created_at": "2024-01-23 15:55:02",
}
```

The notifications channel is up to the requirements and I assume it will be implemented by the imaginary juniior developer along with a UX designer based on the shop owner's preferences. I'd go with emails, though.

# If and how your service could be improved in future versions?

There are several possible improvements to this solution, depending on the future business growth. The most obvious thing is to make this system multi-tennant, so that inventory is attached to a certain user account - store branch in a different location or another book trading network paying for the ability to use the system. Those inventories are isolated from each other and alerts are only sent about the exact user's inventory only to that user.

Another option is making the alerts more elaborate, may be using some color codes. I.e. a green alert suggests you keep an eye on your stock item, while a red alert means you need to go get another book like this right now. This would probably also require making the notification service to become a bit more complex (to support different notification channels), but nothing my junior buddy and I couldn't do.

I assume, even before the initial launch this API would get some frontend. I would go with Twitter Bootstrap and React, and use as many standard UI components as possible. Because Custom Dashboard UI doesn't sound like something rudimentary. User feedback is another important factor to define the most urgent changes. 

# If this challenge description would be a ticket/epic description is there something you are missing? If so, what?

This is an amazing task description ranking in my personal top ~5% of ticket/epic descriptions I have seen. Besides, each and every team sets their own rules regarding how detailed these descriptions should be. If I had to dream of something extra to make this description even better, it probably would be some "Definition of done" section expressed with several (one for a ticket, this one is more like an epic) user stories:
 - As a User I can keep track of my book inventory
 - As a User I can set the quantity after which I am notified
 - etc.
These examples are missing some classic user story parts, but this is enough to build a decent testing routine and better orient oneself regarding the overall progress ("I'm 5/9 done" works better than "I'm in progress"). But again, this is prertty cool already and it's the matter of team members' personal preferences at this point.
