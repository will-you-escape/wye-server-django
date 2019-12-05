# wye-server-django

## Configuration details for production

### Database

Hosted on Amazon RDS.
Security group configured to give access to Heroku web server.

### Web server

Hosted on Heroku.
Deployment process driven by `Procfile`

Run `Procfile` locally (except release section):

```shell
heroku local
```

SSH access to the dynos:

```shell
heroku ps:exec
```

Database hosted by Heroku.

## API spec

The server exposes a GraphQL-based API.

### Create user [mutation]

```js
mutation {
    createUser(email: "romain@wye.com", pseudo: "Romain", password: "pass") {
        user {
            email,
            pseudo
        }
    }
}
```

### Log user in [mutation]

```js
mutation {
    loginUser(email: "romain@wye.com", password: "pass") {
        user {
            email,
            pseudo
        }
    }
}
```
