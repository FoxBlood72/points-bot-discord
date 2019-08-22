# Configuring
You just need to place the bot_token in config.json file.

# Commands
## Basics
There are 3 available commands that this bot can understand:
```
!points [add/remove] <User/UserList> <points>
!leaderboard
!reset
```

## Example:
The following command will add 90 points for every gived users, you must separate them using comma.
The points will be gived just if the user is admin or has "Manager" role, otherwise, an approval will be needed using :thumbsup:  reaction.
```
!points add @Name, "Name with space#4132", name_without_space#1513 90
```

The following command will remove 90 points from the user. This command doesn't work with multiple users!
The points will be removed just if the user is admin or has "Manager" role, otherwise, an approval will be needed using :thumbsup:  reaction.

```
!points remove 90
```

The following command will show all players using an embeded table, and reaction page changer

```
!leaderboard
```

The following command will reset the database:

```
!reset
```
