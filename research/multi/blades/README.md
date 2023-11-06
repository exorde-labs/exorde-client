# Blades

A Blade is a generic aiohttp server wrapper that insure different endpoints.

Blades have async background task capabilities and can have different goals.

They are used like components parts of the clustered-exorde-client.

They have a common API defined in blade.py

```
    /               -> hello
    /kill           -> os._exit
    /parameters     -> static configuration
    /status         -> orchestrator's configuration
    /status (post)  -> set configuration
```

We can reason of blades as of an Upper classes for our different modules.

note : usage of the node word has been avoided in order to reserve it to a
spotting blade (a node is a web3 controler)

Nodes can have their own supply of blades which are owned by the user.
