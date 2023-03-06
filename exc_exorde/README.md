# Exorde client configuration
## internal.yaml
Persitant memory for the client. It shouldn't be tempered with.

## protocol.yaml
Configuration elements provided by Exorde. It shouldn't be tempered with.

## network.json
Network configuration elements provided by Exorde. It shouldn't be tempered with.


    if not kwargs['wallet']:
        message = """

! WALLET ADDRESS NOT PROVIDED !

・use --configme to run trough the configuration maker
・use --wallet or -w to provide your wallet address
・specify it trough an env variable at "WALLET"
・specify your wallet address in your configuration file at "WALLET"

        """
        st = style.Style(color="red", bold=True)
        pan = panel.Panel(message, style=st, title="", border_style="red")
        print('')
        cons.print(pan, justify="center")
        print('')
